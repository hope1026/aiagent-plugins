#!/usr/bin/env python3
"""Stable command-line interface for Forge structured spec tooling."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from spec_model import Diagnostic, SpecBundle, load_spec_bundle, parse_frontmatter
from spec_validate import validate_repository


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="spec-docs.sh")
    parser.add_argument("--repo-root", help="Explicit repository or overlay root")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate")
    validate.add_argument("--root", required=True, help="Repository-relative spec root")
    validate.add_argument("--baseline-ref")

    inspect = commands.add_parser("inspect")
    inspect.add_argument("--spec", required=True, help="Repository-relative spec bundle")
    inspect.add_argument("--format", required=True, choices=("json",))

    return parser


def _discover_repository(start: Path) -> Path | None:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def _repository_root(arguments: argparse.Namespace, parser: argparse.ArgumentParser) -> Path:
    if arguments.repo_root is not None:
        root = Path(arguments.repo_root).resolve()
        if not root.is_dir():
            parser.error("--repo-root must name an existing directory")
        return root
    discovered = _discover_repository(Path.cwd())
    if discovered is None:
        parser.error("could not discover a repository root; pass --repo-root explicitly")
    return discovered


def _contained_path(
    root: Path,
    raw: str,
    option: str,
    parser: argparse.ArgumentParser,
    *,
    relative_only: bool = False,
) -> tuple[Path, Path]:
    supplied = Path(raw)
    if relative_only and supplied.is_absolute():
        parser.error(f"{option} must be relative to the repository root")
    resolved = supplied.resolve() if supplied.is_absolute() else (root / supplied).resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        parser.error(f"{option} must remain inside the repository root")
    return resolved, relative


def _print_diagnostics(diagnostics: tuple[Diagnostic, ...]) -> None:
    for item in diagnostics:
        print(f"{item.path}:{item.line}: {item.code} {item.message}")


def _baseline_contains_legacy_source(
    repo_root: Path, spec_root: Path, baseline_ref: str
) -> bool:
    listing = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "ls-tree",
            "-r",
            "--name-only",
            baseline_ref,
            "--",
            spec_root.as_posix(),
        ],
        capture_output=True,
        check=False,
    )
    if listing.returncode != 0:
        return False
    for encoded_path in listing.stdout.splitlines():
        try:
            path_text = encoded_path.decode("utf-8")
        except UnicodeDecodeError:
            return True
        if not path_text.endswith("/spec.md"):
            continue
        shown = subprocess.run(
            ["git", "-C", str(repo_root), "show", f"{baseline_ref}:{path_text}"],
            capture_output=True,
            check=False,
        )
        if shown.returncode != 0:
            continue
        try:
            source = shown.stdout.decode("utf-8")
        except UnicodeDecodeError:
            return True
        values, _, diagnostics = parse_frontmatter(source, Path(path_text))
        if diagnostics or values.get("schema") != "forge/spec@2":
            return True
    return False


def _inspect_payload(
    repo_root: Path,
    spec_path: Path,
    relative_spec: Path,
) -> tuple[dict[str, object], int]:
    if spec_path.is_dir():
        bundle, bundle_diagnostics = load_spec_bundle(spec_path, repo_root)
        repository_result = validate_repository(repo_root, Path("docs/specs"))
        bundle_prefix = relative_spec.as_posix().rstrip("/") + "/"
        repository_diagnostics = tuple(
            item
            for item in repository_result.diagnostics
            if item.path == relative_spec.as_posix() or item.path.startswith(bundle_prefix)
        )
        diagnostics = tuple(sorted(set(bundle_diagnostics + repository_diagnostics)))
        return _inspect_bundle_payload(relative_spec, bundle, diagnostics)

    result = validate_repository(repo_root, Path("docs/specs"))
    document = next((item for item in result.documents if item.path == relative_spec), None)
    diagnostics = tuple(item for item in result.diagnostics if item.path == relative_spec.as_posix())
    if document is None and not diagnostics:
        diagnostics = (
            Diagnostic(
                relative_spec.as_posix(),
                1,
                "SPEC_SOURCE_READ",
                "The requested spec does not exist or is not a structured source.",
            ),
        )

    payload: dict[str, object] = {
        "schema": document.metadata.schema if document else None,
        "id": document.metadata.id if document else None,
        "status": document.metadata.status if document else None,
        "language": document.metadata.language if document else None,
        "kind": document.metadata.kind if document else None,
        "path": relative_spec.as_posix(),
        "sourceSha256": document.source_sha256 if document else None,
        "requirements": [
            {
                "id": item.id,
                "text": item.text,
                "line": item.line,
                "removed": item.removed,
            }
            for item in document.requirements
        ]
        if document
        else [],
        "acceptance": [
            {
                "id": item.id,
                "requirements": list(item.requirements),
                "text": item.text,
                "line": item.line,
            }
            for item in document.acceptance
        ]
        if document
        else [],
        "diagnostics": [
            {
                "path": item.path,
                "line": item.line,
                "code": item.code,
                "message": item.message,
            }
            for item in diagnostics
        ],
    }
    return payload, 0 if document is not None and not diagnostics else 1


def _inspect_bundle_payload(
    relative_bundle: Path,
    bundle: SpecBundle | None,
    diagnostics: tuple[Diagnostic, ...],
) -> tuple[dict[str, object], int]:
    payload: dict[str, object] = {
        "schema": bundle.metadata.schema if bundle else None,
        "bundlePath": bundle.path.as_posix() if bundle else relative_bundle.as_posix(),
        "rootPath": bundle.root_path.as_posix() if bundle else None,
        "title": bundle.title if bundle else None,
        "status": bundle.metadata.status if bundle else None,
        "language": bundle.metadata.language if bundle else None,
        "kind": bundle.metadata.kind if bundle else None,
        "subtype": bundle.metadata.subtype if bundle else None,
        "areas": list(bundle.metadata.areas) if bundle else [],
        "components": list(bundle.metadata.components) if bundle else [],
        "relatedSpecs": [
            {"path": item.path, "relation": item.relation}
            for item in bundle.metadata.related_specs
        ]
        if bundle
        else [],
        "bundleSha256": bundle.bundle_sha256 if bundle else None,
        "members": [
            {
                "path": member.path.as_posix(),
                "title": member.title,
                "role": member.role,
                "sourceSha256": member.source_sha256,
            }
            for member in bundle.members
        ]
        if bundle
        else [],
        "statements": [
            {
                "kind": statement.kind,
                "path": statement.member_path.as_posix(),
                "heading": statement.heading,
                "line": statement.line,
                "references": [
                    {
                        "path": reference.member_path.as_posix(),
                        "heading": reference.heading,
                        "anchor": reference.anchor,
                        "line": reference.line,
                    }
                    for reference in statement.references
                ],
            }
            for statement in bundle.statements
        ]
        if bundle
        else [],
        "diagnostics": [
            {
                "path": item.path,
                "line": item.line,
                "code": item.code,
                "message": item.message,
            }
            for item in diagnostics
        ],
    }
    return payload, 0 if bundle is not None and not diagnostics else 1


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    arguments = parser.parse_args(argv)
    repo_root = _repository_root(arguments, parser)

    if arguments.command == "validate":
        _, relative_root = _contained_path(repo_root, arguments.root, "--root", parser)
        if arguments.baseline_ref is not None and not (repo_root / ".git").exists():
            parser.error("--baseline-ref requires a Git repository")
        result = validate_repository(repo_root, relative_root, arguments.baseline_ref)
        _print_diagnostics(result.diagnostics)
        return 0 if result.ok else 1

    if arguments.command == "inspect":
        spec_path, relative_spec = _contained_path(
            repo_root, arguments.spec, "--spec", parser
        )
        default_spec_root = (repo_root / "docs/specs").resolve()
        try:
            spec_path.relative_to(default_spec_root)
        except ValueError:
            parser.error("--spec must be below docs/specs")
        payload, status = _inspect_payload(repo_root, spec_path, relative_spec)
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        return status

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    sys.exit(main())
