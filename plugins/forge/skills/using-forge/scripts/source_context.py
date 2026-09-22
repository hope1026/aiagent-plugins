#!/usr/bin/env python3
"""Capture selected source bytes and check them without imposing document layout."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

SCHEMA = "forge/source-context@1"
DEFAULT_SOURCE_BYTES = 256 * 1024
DEFAULT_TOTAL_BYTES = 1024 * 1024


class ContextError(ValueError):
    """An invalid input, rather than a change in a previously captured source."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized_path(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ContextError("paths must be normalized repository-relative POSIX paths")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {".", "..", ""} for part in value.split("/")):
        raise ContextError("paths must be normalized repository-relative POSIX paths")
    if re.match(r"^[A-Za-z]:", value):
        raise ContextError("absolute drive paths are not supported")
    return value


def contained_file(root: Path, value: str) -> Path:
    """Validate the path before opening; never read an outside symlink target."""
    relative = normalized_path(value)
    candidate = root / relative
    try:
        candidate.resolve().relative_to(root)
    except (ValueError, RuntimeError):
        raise ContextError(f"path escapes repository: {relative}") from None
    # A stable file path, rather than a mutable symlink alias, identifies a record.
    current = root
    for part in PurePosixPath(relative).parts:
        current /= part
        if current.is_symlink():
            raise ContextError(f"use the regular file path instead of a symlink: {relative}")
    return candidate


def file_hash(path: Path) -> str:
    if not path.is_file():
        raise OSError("not a regular file")
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            result.update(chunk)
    return result.hexdigest()


def capture(root: Path, sources: list[str], artifacts: list[str], task: str = "",
            max_source_bytes: int = DEFAULT_SOURCE_BYTES,
            max_total_bytes: int = DEFAULT_TOTAL_BYTES) -> dict:
    if not sources:
        raise ContextError("select at least one source")
    if max_source_bytes <= 0 or max_total_bytes <= 0:
        raise ContextError("byte limits must be positive")
    selected = [normalized_path(p) for p in sources + artifacts]
    if len(set(selected)) != len(selected):
        raise ContextError("a file may appear only once across sources and artifacts")
    records = []
    total = 0
    for relative in sorted(sources):
        path = contained_file(root, relative)
        try:
            if not path.is_file():
                raise OSError("not a regular file")
            with path.open("rb") as stream:
                raw = stream.read(min(max_source_bytes, max_total_bytes - total) + 1)
            if len(raw) > max_source_bytes or total + len(raw) > max_total_bytes:
                raise ContextError(f"source byte budget exceeded; no content truncated: {relative}")
            content = raw.decode("utf-8")
        except (OSError, UnicodeError):
            raise ContextError(f"source must be a readable UTF-8 regular file: {relative}") from None
        total += len(raw)
        records.append({"path": relative, "sha256": digest(raw), "content": content})
    outputs = []
    for relative in sorted(artifacts):
        path = contained_file(root, relative)
        try:
            outputs.append({"path": relative, "sha256": file_hash(path)})
        except OSError:
            raise ContextError(f"artifact must be a readable regular file: {relative}") from None
    return {"schema": SCHEMA, "task": task, "sources": records, "artifacts": outputs}


def validate_snapshot(snapshot: object) -> dict:
    if not isinstance(snapshot, dict) or set(snapshot) != {"schema", "task", "sources", "artifacts"}:
        raise ContextError("invalid snapshot fields")
    if snapshot["schema"] != SCHEMA or not isinstance(snapshot["task"], str):
        raise ContextError("invalid snapshot schema or task")
    seen = set()
    for group in ("sources", "artifacts"):
        records = snapshot[group]
        if not isinstance(records, list) or (group == "sources" and not records):
            raise ContextError(f"invalid {group} list")
        fields = {"path", "sha256", "content"} if group == "sources" else {"path", "sha256"}
        for record in records:
            if not isinstance(record, dict) or set(record) != fields:
                raise ContextError(f"invalid {group} record")
            relative = normalized_path(record["path"])
            if relative in seen:
                raise ContextError("duplicate snapshot path")
            seen.add(relative)
            sha = record["sha256"]
            if not isinstance(sha, str) or re.fullmatch(r"[0-9a-f]{64}", sha) is None:
                raise ContextError(f"invalid SHA-256: {relative}")
            if group == "sources":
                content = record["content"]
                if not isinstance(content, str):
                    raise ContextError(f"source content must be text: {relative}")
                try:
                    matches = digest(content.encode("utf-8")) == sha
                except UnicodeError:
                    matches = False
                if not matches:
                    raise ContextError(f"source content does not match recorded hash: {relative}")
    return snapshot


def check(root: Path, snapshot: object) -> tuple[dict, int]:
    snapshot = validate_snapshot(snapshot)
    # Validate every path before reading any selected file.
    paths = {row["path"]: contained_file(root, row["path"])
             for group in ("sources", "artifacts") for row in snapshot[group]}
    results = []
    for group in ("sources", "artifacts"):
        for row in sorted(snapshot[group], key=lambda item: item["path"]):
            path = paths[row["path"]]
            result = {"kind": "source" if group == "sources" else "artifact",
                      "path": row["path"], "recorded_sha256": row["sha256"]}
            try:
                actual = file_hash(path)
                result.update(state="unchanged" if actual == row["sha256"] else "changed",
                              current_sha256=actual)
            except FileNotFoundError:
                result.update(state="missing", current_sha256=None)
            except OSError:
                result.update(state="unavailable" if path.exists() else "missing",
                              current_sha256=None)
            results.append(result)
    states = {row["state"] for row in results}
    state = ("unavailable" if states & {"missing", "unavailable"}
             else "changed" if "changed" in states else "unchanged")
    return {"state": state, "files": results,
            "scope": "Selected file bytes only; not semantic correctness, approval, or dependency completeness."}, int(state != "unchanged")


def no_duplicate_keys(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContextError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    collect = commands.add_parser("capture", help="print selected UTF-8 sources and optional artifact hashes")
    collect.add_argument("--source", action="append", required=True)
    collect.add_argument("--artifact", action="append", default=[])
    collect.add_argument("--task", default="")
    collect.add_argument("--max-source-bytes", type=int, default=DEFAULT_SOURCE_BYTES)
    collect.add_argument("--max-total-bytes", type=int, default=DEFAULT_TOTAL_BYTES)
    verify = commands.add_parser("check", help="compare a saved snapshot with current file bytes")
    verify.add_argument("--snapshot", required=True, help="repository-relative snapshot file")
    arguments = parser.parse_args(argv)
    try:
        root = arguments.repo_root.resolve()
        if not root.is_dir():
            raise ContextError("repository root must be an existing directory")
        if arguments.command == "capture":
            payload = capture(root, arguments.source, arguments.artifact, arguments.task,
                              arguments.max_source_bytes, arguments.max_total_bytes)
            status = 0
        else:
            snapshot_path = contained_file(root, arguments.snapshot)
            try:
                if not snapshot_path.is_file():
                    raise ContextError("snapshot must be a regular file")
                snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"),
                                      object_pairs_hook=no_duplicate_keys)
            except (OSError, UnicodeError, json.JSONDecodeError):
                raise ContextError("snapshot must be readable UTF-8 JSON") from None
            payload, status = check(root, snapshot)
    except ContextError as error:
        payload, status = {"error": str(error)}, 2
    except (OSError, RuntimeError, ValueError):
        payload, status = {"error": "could not resolve or read inputs inside the supplied repository"}, 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    sys.exit(main())
