#!/usr/bin/env python3
"""Assemble a Forge lifecycle review Viewer from source-owned content."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shlex
import sys
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

MERMAID_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"
PANELS = ("overview", "requirements", "flows", "data", "acceptance", "history")
LABELS = {
    "en": {
        "overview": "Overview",
        "requirements": "Requirements",
        "flows": "Flows",
        "data": "Data & Interfaces",
        "acceptance": "Acceptance",
        "history": "History",
        "nav": "Review sections",
        "generated": "generated",
        "sources": "Sources",
        "diagram": "Diagram",
        "mermaid_error": "Mermaid error",
        "freshness": "Freshness",
        "select_sources": "Select Markdown files to verify locally",
    },
    "ko": {
        "overview": "개요",
        "requirements": "요구사항",
        "flows": "흐름",
        "data": "데이터와 인터페이스",
        "acceptance": "승인 기준",
        "history": "변경 이력",
        "nav": "검토 항목",
        "generated": "생성",
        "sources": "Source",
        "diagram": "다이어그램",
        "mermaid_error": "Mermaid 오류",
        "freshness": "최신성",
        "select_sources": "로컬 검증용 Markdown 파일 선택",
    },
}


@dataclass(frozen=True)
class ViewerManifest:
    mode: str
    locale: str
    sources: list[dict[str, str]]
    generated_at: str
    counts: dict[str, int]
    freshness: str
    rebuild_command: str


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="build-viewer.sh",
        description="Build a Forge lifecycle review Viewer.",
    )
    parser.add_argument("--check", type=Path)
    parser.add_argument("-c", "--content", type=Path)
    parser.add_argument("-t", "--title")
    parser.add_argument("-s", "--status", default="draft")
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--mode", choices=("spec", "plan"), default="spec")
    parser.add_argument("--locale", choices=tuple(LABELS), default="en")
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--progress", type=Path)
    parser.add_argument("--tasks-dir", type=Path)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args(argv)

    if args.check:
        if not args.check.is_file():
            parser.error(f"file not found: {args.check}")
        if any((args.content, args.title, args.output, args.spec, args.plan, args.progress, args.tasks_dir)):
            parser.error("--check cannot be combined with build arguments")
        return args

    if not args.content or not args.title:
        parser.error("-c/--content and -t/--title are required when building")

    if args.mode == "spec":
        if not args.spec:
            parser.error("--spec is required for spec mode")
        if args.plan or args.progress or args.tasks_dir:
            parser.error("--plan, --progress, and --tasks-dir are invalid for spec mode")
    if args.mode == "plan":
        if not args.plan:
            parser.error("--plan is required for plan mode")
        if args.spec:
            parser.error("--spec is invalid for plan mode; use Related Specs as links")
    for path in (args.content, args.spec, args.plan, args.progress):
        if path is not None and not path.is_file():
            parser.error(f"file not found: {path}")
    if args.tasks_dir is not None and not args.tasks_dir.is_dir():
        parser.error(f"directory not found: {args.tasks_dir}")
    if args.output is None:
        anchor = args.spec or args.plan
        if anchor is None:
            parser.error("--output is required when no source path can determine a name")
        args.output = derive_output(anchor)
    return args


def derive_output(anchor: Path) -> Path:
    return anchor.parent / "view.html"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def selected_sources(args: argparse.Namespace) -> list[tuple[str, Path]]:
    result: list[tuple[str, Path]] = []
    if args.spec:
        result.append(("spec", args.spec))
    if args.plan:
        result.append(("plan", args.plan))
    if args.progress:
        result.append(("progress", args.progress))
    if args.tasks_dir:
        result.extend(("task", path) for path in sorted(args.tasks_dir.glob("*.md")))
    return result


def source_records(
    sources: list[tuple[str, Path]], output_directory: Path
) -> list[dict[str, str]]:
    return [
        {
            "role": role,
            "path": Path(os.path.relpath(path, output_directory)).as_posix(),
            "sha256": sha256(path),
        }
        for role, path in sources
    ]


def collect_counts(paths: list[Path]) -> dict[str, int]:
    tasks: set[str] = set()
    requirements: set[str] = set()
    acceptance: set[str] = set()
    steps = 0
    mermaid = 0
    for path in paths:
        text = path.read_text(encoding="utf-8")
        tasks.update(re.findall(r"(?m)^### Task\s+(\d+)\b", text))
        steps += len(re.findall(r"(?m)^\s*- \[[ xX]\] \*\*Step\s+\d+\b", text))
        requirements.update(re.findall(r"\bR(\d+)\b", text))
        acceptance.update(re.findall(r"\bAC(\d+)\b", text))
        mermaid += len(re.findall(r"(?m)^```mermaid\s*$", text))
    return {
        "task": len(tasks),
        "step": steps,
        "requirement": len(requirements),
        "acceptance": len(acceptance),
        "mermaid": mermaid,
    }


def validate_fragment(content: str) -> None:
    ids = re.findall(
        r'<section\s+class="tab-panel"\s+id="([^"]+)"', content, re.IGNORECASE
    )
    if tuple(ids) != PANELS:
        raise ValueError(f"content fragment must contain panels in order: {', '.join(PANELS)}")
    if re.search(r"<!doctype|<html\b|<head\b|<style\b|<script\b", content, re.IGNORECASE):
        raise ValueError("content fragment must not contain shell markup, style, or script")


def mermaid_tag(offline: bool) -> str:
    if not offline:
        return f'<script src="{MERMAID_URL}"></script>'
    bundle_path = os.environ.get("FORGE_MERMAID_BUNDLE")
    if bundle_path:
        bundle = Path(bundle_path).read_text(encoding="utf-8")
    else:
        with urllib.request.urlopen(MERMAID_URL, timeout=30) as response:
            bundle = response.read().decode("utf-8")
    return f"<script>\n{bundle}\n</script>"


def source_summary(manifest: ViewerManifest, labels: dict[str, str]) -> str:
    count_text = " · ".join(
        f"{key} {value}" for key, value in manifest.counts.items()
    )


def extract_manifest(viewer: Path) -> ViewerManifest:
    document = viewer.read_text(encoding="utf-8")
    match = re.search(
        r'<script\s+type="application/json"\s+id="forge-source-manifest">(.*?)</script>',
        document,
        re.DOTALL,
    )
    if not match:
        raise ValueError("source manifest not found")
    try:
        data = json.loads(match.group(1))
        manifest = ViewerManifest(**data)
    except (json.JSONDecodeError, TypeError) as error:
        raise ValueError(f"invalid source manifest: {error}") from error
    if not isinstance(manifest.sources, list) or not manifest.sources:
        raise ValueError("invalid source manifest: sources must be a non-empty list")
    return manifest


def check_viewer(viewer: Path) -> list[str]:
    try:
        manifest = extract_manifest(viewer)
    except (OSError, ValueError) as error:
        return [str(error)]
    base = viewer.parent.resolve()
    errors: list[str] = []
    for source in manifest.sources:
        if not isinstance(source, dict) or not isinstance(source.get("path"), str):
            errors.append("manifest source has no valid path")
            continue
        expected = source.get("sha256")
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            errors.append(f"{source['path']}: invalid SHA-256")
            continue
        path = (base / source["path"]).resolve()
        if path != base and base not in path.parents:
            errors.append(f"{source['path']}: path escapes Viewer directory")
            continue
        if not path.is_file():
            errors.append(f"{source['path']}: source missing")
            continue
        actual = sha256(path)
        if actual != expected:
            errors.append(
                f"{source['path']}: stale (expected {expected[:12]}, actual {actual[:12]})"
            )
    return errors
    items = "".join(
        '<li data-source-path="{}"><code>{}</code> <span>{}</span> <code>{}</code> '
        '<span class="freshness-state freshness-unverified" data-source-state>unverified</span> '
        '<span class="source-error" data-source-error></span></li>'.format(
            html.escape(source["path"], quote=True),
            html.escape(source["role"]),
            html.escape(source["path"]),
            html.escape(source["sha256"][:12]),
        )
        for source in manifest.sources
    )
    return (
        f'<details class="source-summary"><summary>{html.escape(labels["sources"])} · '
        f'{html.escape(manifest.mode)} · {html.escape(labels["freshness"])} '
        f'<span class="freshness-state freshness-unverified" data-freshness-overall>{html.escape(manifest.freshness)}</span> · '
        f'{html.escape(count_text)}</summary><ul>{items}</ul>'
        f'<label class="source-picker-label" for="forge-source-picker">{html.escape(labels["select_sources"])}</label>'
        f'<input id="forge-source-picker" type="file" accept=".md,text/markdown" multiple>'
        f'<code>{html.escape(manifest.rebuild_command)}</code></details>'
    )


def build(args: argparse.Namespace, argv: list[str]) -> str:
    script_root = Path(__file__).resolve().parent.parent
    template = (script_root / "assets" / "viewer-template.html").read_text(encoding="utf-8")
    freshness_runtime = (script_root / "assets" / "viewer-freshness.mjs").read_text(encoding="utf-8")
    content = args.content.read_text(encoding="utf-8")
    validate_fragment(content)
    sources = selected_sources(args)
    labels = LABELS[args.locale]
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest = ViewerManifest(
        mode=args.mode,
        locale=args.locale,
        sources=source_records(sources, args.output.parent),
        generated_at=generated_at,
        counts=collect_counts([path for _, path in sources]),
        freshness="unverified",
        rebuild_command=" ".join(shlex.quote(part) for part in ["build-viewer.sh", *argv]),
    )
    manifest_json = json.dumps(asdict(manifest), ensure_ascii=False, indent=2).replace("</", "<\\/")
    replacements = {
        "{{LANG}}": args.locale,
        "{{TITLE}}": html.escape(args.title),
        "{{STATUS}}": html.escape(args.status),
        "{{GENERATED}}": html.escape(generated_at),
        "{{GENERATED_LABEL}}": html.escape(labels["generated"]),
        "{{NAV_LABEL}}": html.escape(labels["nav"]),
        "{{SOURCE_SUMMARY}}": source_summary(manifest, labels),
        "{{SOURCE_MANIFEST}}": manifest_json,
        "{{DIAGRAM_LABEL}}": html.escape(labels["diagram"]),
        "{{MERMAID_ERROR}}": html.escape(labels["mermaid_error"]),
        "{{CONTENT}}": content,
        "{{MERMAID}}": mermaid_tag(args.offline),
        "{{FRESHNESS_RUNTIME}}": freshness_runtime,
    }
    for panel in PANELS:
        replacements[f"{{{{TAB_{panel.upper()}}}}}"] = html.escape(labels[panel])
    token_pattern = re.compile(r"\{\{[A-Z0-9_]+\}\}")
    unresolved = sorted(set(token_pattern.findall(template)) - replacements.keys())
    if unresolved:
        raise ValueError(f"unresolved template tokens: {', '.join(unresolved)}")
    return token_pattern.sub(lambda match: replacements[match.group(0)], template)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        if args.check:
            errors = check_viewer(args.check)
            if errors:
                for error in errors:
                    print(f"build-viewer: {error}", file=sys.stderr)
                return 1
            print(f"viewer current: {args.check}")
            return 0
        output = build(args, argv)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"build-viewer: {error}", file=sys.stderr)
        return 1
    print(f"built: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
