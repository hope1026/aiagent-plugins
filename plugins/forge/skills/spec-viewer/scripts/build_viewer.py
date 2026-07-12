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
    parser.add_argument("-c", "--content", required=True, type=Path)
    parser.add_argument("-t", "--title", required=True)
    parser.add_argument("-s", "--status", default="draft")
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--mode", choices=("spec", "plan", "combined"), default="spec")
    parser.add_argument("--locale", choices=tuple(LABELS), default="en")
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--progress", type=Path)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args(argv)

    if args.mode in ("spec", "combined") and not args.spec:
        parser.error(f"--spec is required for {args.mode} mode")
    if args.mode in ("plan", "combined") and not args.plan:
        parser.error(f"--plan is required for {args.mode} mode")
    for path in (args.content, args.spec, args.plan, args.progress):
        if path is not None and not path.is_file():
            parser.error(f"file not found: {path}")
    if args.output is None:
        anchor = args.spec or args.plan
        if anchor is None:
            parser.error("--output is required when no source path can determine a name")
        args.output = derive_output(anchor, args.mode)
    return args


def derive_output(anchor: Path, mode: str) -> Path:
    if anchor.name == "spec.md":
        slug = anchor.parent.name
    else:
        slug = anchor.stem
    suffix = {"spec": "", "plan": "-plan", "combined": "-review"}[mode]
    return Path(".forge/viewer") / f"{slug}{suffix}.html"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def selected_sources(args: argparse.Namespace) -> list[tuple[str, Path]]:
    result: list[tuple[str, Path]] = []
    if args.spec:
        result.append(("spec" if args.mode != "plan" else "approved-spec", args.spec))
    if args.plan:
        result.append(("plan", args.plan))
    if args.progress:
        result.append(("progress", args.progress))
    return result


def source_records(sources: list[tuple[str, Path]]) -> list[dict[str, str]]:
    return [
        {"role": role, "path": str(path), "sha256": sha256(path)}
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


def freshness(content_path: Path, sources: list[tuple[str, Path]]) -> str:
    content_mtime = content_path.stat().st_mtime_ns
    return "stale" if any(path.stat().st_mtime_ns > content_mtime for _, path in sources) else "current"


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
    items = "".join(
        "<li><code>{}</code> <span>{}</span> <code>{}</code></li>".format(
            html.escape(source["role"]),
            html.escape(source["path"]),
            html.escape(source["sha256"][:12]),
        )
        for source in manifest.sources
    )
    return (
        f'<details class="source-summary"><summary>{html.escape(labels["sources"])} · '
        f'{html.escape(manifest.mode)} · {html.escape(manifest.freshness)} · '
        f'{html.escape(count_text)}</summary><ul>{items}</ul>'
        f'<code>{html.escape(manifest.rebuild_command)}</code></details>'
    )


def build(args: argparse.Namespace, argv: list[str]) -> str:
    script_root = Path(__file__).resolve().parent.parent
    template = (script_root / "assets" / "viewer-template.html").read_text(encoding="utf-8")
    content = args.content.read_text(encoding="utf-8")
    validate_fragment(content)
    sources = selected_sources(args)
    labels = LABELS[args.locale]
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest = ViewerManifest(
        mode=args.mode,
        locale=args.locale,
        sources=source_records(sources),
        generated_at=generated_at,
        counts=collect_counts([path for _, path in sources]),
        freshness=freshness(args.content, sources),
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
        "{{CONTENT}}": content,
        "{{MERMAID}}": mermaid_tag(args.offline),
    }
    for panel in PANELS:
        replacements[f"{{{{TAB_{panel.upper()}}}}}"] = html.escape(labels[panel])
    for token, value in replacements.items():
        template = template.replace(token, value)
    unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", template)))
    if unresolved:
        raise ValueError(f"unresolved template tokens: {', '.join(unresolved)}")
    return template


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
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

