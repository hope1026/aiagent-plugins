#!/usr/bin/env python3
"""Source selection and read-only checks for requested Forge Review Viewers."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Mapping

from review_freshness import CheckResult, check_review, find_repository_root
from review_sources import (
    ReviewBundle,
    ReviewSource,
    _collect_plan_sources,
    collect_spec_sources,
    repository_relative,
    validate_review_id,
)


MERMAID_URL = "https://cdn.jsdelivr.net/npm/mermaid@11.16.0/dist/mermaid.min.js"


def parse_args(argv: list[str]) -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser(
        prog="build-review-viewer.sh",
        description="Collect Review Viewer sources or check an existing review.",
    )
    parser.add_argument("--check", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--format", choices=("json",))
    parser.add_argument("--mode", choices=("spec", "plan"))
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--comparison", action="append", type=Path, default=[])
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--progress", type=Path)
    parser.add_argument("--tasks-dir", type=Path)
    parser.add_argument("--review-id")
    parser.add_argument("--locale", choices=("en", "ko"))
    parser.add_argument("--checkpoint")
    parser.add_argument("--generated-at")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser, parser.parse_args(argv)


def _error(parser: argparse.ArgumentParser, message: str) -> None:
    parser.error(message)


def _repository_root(parser: argparse.ArgumentParser, explicit: Path | None) -> Path:
    try:
        root = explicit.resolve() if explicit is not None else find_repository_root(Path.cwd())
    except ValueError as error:
        _error(parser, str(error))
    marker = root / ".git"
    if not (marker.is_dir() or marker.is_file()):
        _error(parser, f"repository root has no .git marker: {root}")
    return root


def _normalize_generated_at(parser: argparse.ArgumentParser, value: str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        )
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _error(parser, f"--generated-at must be RFC3339: {value}")
    if parsed.tzinfo is None:
        _error(parser, "--generated-at must include a timezone")
    return value


def _contained_file(
    parser: argparse.ArgumentParser, value: Path, repo_root: Path, label: str
) -> Path:
    try:
        relative = repository_relative(value, repo_root)
    except ValueError as error:
        _error(parser, str(error))
    resolved = repo_root / relative
    if not resolved.is_file():
        _error(parser, f"{label} file not found: {relative.as_posix()}")
    return resolved


def _contained_directory(
    parser: argparse.ArgumentParser, value: Path, repo_root: Path, label: str
) -> Path:
    try:
        relative = repository_relative(value, repo_root)
    except ValueError as error:
        _error(parser, str(error))
    resolved = repo_root / relative
    if not resolved.is_dir():
        _error(parser, f"{label} directory not found: {relative.as_posix()}")
    return resolved


def _git_commit(parser: argparse.ArgumentParser, repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        _error(parser, "repository has no current commit")
    return result.stdout.strip()


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


def _source_record(source: ReviewSource) -> dict[str, object]:
    return {
        "role": source.role,
        "path": source.path,
        "namespace": source.namespace,
        "sha256": source.sha256,
        "requirements": list(source.requirements),
        "acceptance": list(source.acceptance),
        "status": source.status,
    }


def _normalized_rebuild_command(
    args: argparse.Namespace,
    bundle: ReviewBundle,
    generated_at: str,
    repo_root: Path,
) -> str:
    command = [
        "build-review-viewer.sh",
        "--mode",
        bundle.mode,
    ]
    if bundle.mode == "spec":
        command.extend(("--spec", bundle.primary[0].path))
        for source in bundle.comparison:
            command.extend(("--comparison", source.path))
    else:
        command.extend(("--plan", bundle.primary[0].path))
        if args.progress is not None:
            command.extend(
                (
                    "--progress",
                    repository_relative(args.progress, repo_root).as_posix(),
                )
            )
        if args.tasks_dir is not None:
            command.extend(
                (
                    "--tasks-dir",
                    repository_relative(args.tasks_dir, repo_root).as_posix(),
                )
            )
    command.extend(
        (
            "--review-id",
            args.review_id,
            "--locale",
            args.locale or "en",
            "--checkpoint",
            args.checkpoint or "working-tree",
            "--generated-at",
            generated_at,
        )
    )
    if args.offline:
        command.append("--offline")
    return shlex.join(command)


def _dry_run_payload(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
    bundle: ReviewBundle,
    repo_root: Path,
) -> dict[str, object]:
    generated_at = _normalize_generated_at(parser, args.generated_at)
    sources = (*bundle.primary, *bundle.comparison, *bundle.context)
    return {
        "mode": bundle.mode,
        "locale": args.locale or "en",
        "review_id": args.review_id,
        "sources": [_source_record(source) for source in sources],
        "generated_at": generated_at,
        "counts": _plain(bundle.counts),
        "freshness": "unverified",
        "checkpoint": args.checkpoint or "working-tree",
        "commit": _git_commit(parser, repo_root),
        "rebuild_command": _normalized_rebuild_command(
            args, bundle, generated_at, repo_root
        ),
        "mermaid_url": MERMAID_URL,
        "source_base": "../../../",
        "offline": args.offline,
        "output": f".forge/reviews/{args.review_id}/view.html",
    }


def _check_payload(result: CheckResult) -> dict[str, object]:
    return {
        "viewer": result.viewer,
        "sources": [list(source) for source in result.sources],
        "aggregates": dict(result.aggregates),
        "overall": result.overall,
        "diagnostics": list(result.diagnostics),
    }


def _run_check(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    if any(
        (
            args.mode,
            args.spec,
            args.comparison,
            args.plan,
            args.progress,
            args.tasks_dir,
            args.review_id,
            args.locale,
            args.checkpoint,
            args.generated_at,
            args.offline,
            args.dry_run,
        )
    ):
        _error(parser, "--check cannot be combined with build arguments")
    repo_root = _repository_root(parser, args.repo_root)
    result = check_review(args.check, repo_root)
    payload = _check_payload(result)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"{result.overall}: {result.viewer}")
        for diagnostic in result.diagnostics:
            print(diagnostic)
    return 0 if result.overall == "current" else 1


def _collect_build_bundle(
    parser: argparse.ArgumentParser, args: argparse.Namespace, repo_root: Path
) -> ReviewBundle:
    if args.mode is None:
        _error(parser, "--mode is required when building")
    if args.review_id is None:
        _error(parser, "--review-id is required when building")
    try:
        args.review_id = validate_review_id(args.review_id)
    except ValueError as error:
        _error(parser, str(error))
    if args.mode == "spec":
        if args.spec is None:
            _error(parser, "--spec is required for spec mode")
        if any((args.plan, args.progress, args.tasks_dir)):
            _error(parser, "plan inputs are invalid for spec mode")
        primary = _contained_file(parser, args.spec, repo_root, "spec")
        comparisons = [
            _contained_file(parser, value, repo_root, "comparison")
            for value in args.comparison
        ]
        try:
            return collect_spec_sources(primary, comparisons, repo_root)
        except ValueError as error:
            _error(parser, str(error))

    if args.plan is None:
        _error(parser, "--plan is required for plan mode")
    if args.spec is not None or args.comparison:
        _error(parser, "spec and comparison inputs are invalid for plan mode")
    plan = _contained_file(parser, args.plan, repo_root, "plan")
    progress = (
        _contained_file(parser, args.progress, repo_root, "progress")
        if args.progress is not None
        else None
    )
    tasks_directory = (
        _contained_directory(parser, args.tasks_dir, repo_root, "tasks")
        if args.tasks_dir is not None
        else None
    )
    try:
        return _collect_plan_sources(
            plan,
            repo_root,
            progress_override=progress,
            tasks_directory_override=tasks_directory,
        )
    except ValueError as error:
        _error(parser, str(error))


def main(argv: list[str] | None = None) -> int:
    parser, args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.check is not None:
        return _run_check(parser, args)
    if args.repo_root is not None:
        _error(parser, "--repo-root is only valid with --check")
    repo_root = _repository_root(parser, None)
    bundle = _collect_build_bundle(parser, args, repo_root)
    if not args.dry_run:
        _error(parser, "final Review Viewer rendering is enabled by Task 6")
    if args.format != "json":
        _error(parser, "--dry-run requires --format json")
    payload = _dry_run_payload(parser, args, bundle, repo_root)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
