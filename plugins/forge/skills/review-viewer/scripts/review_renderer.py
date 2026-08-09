"""Deterministic adaptive renderer for requested Forge Review Viewers."""

from __future__ import annotations

import hashlib
import html
import json
from dataclasses import asdict
from pathlib import Path
import re
from typing import Mapping

from review_components import render_components
from review_ir import SemanticIR, build_semantic_ir
from review_planner import (
    PresentationPlan,
    ViewContext,
    select_presentation_plan,
    validate_presentation_plan,
)
from review_sources import PlanDocument, ReviewBundle, ReviewSource


SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = SKILL_DIR / "assets/viewer-template.html"
FRESHNESS_RUNTIME_PATH = SKILL_DIR / "assets/viewer-freshness.mjs"
WRITING_SPECS_ASSETS = SKILL_DIR.parent / "writing-specs" / "assets"
MERMAID_PATH = WRITING_SPECS_ASSETS / "mermaid.min.js"
MERMAID_CHECKSUM_PATH = WRITING_SPECS_ASSETS / "mermaid.sha256"
MERMAID_URL = "https://cdn.jsdelivr.net/npm/mermaid@11.16.0/dist/mermaid.min.js"


LABELS = {
    "en": {
        "generated": "Generated",
        "nav": "Review sections",
        "diagram": "Diagram",
        "mermaid_error": "Diagram could not be rendered",
        "freshness": "Freshness",
        "source_picker": "Verify this source locally",
    },
    "ko": {
        "generated": "생성",
        "nav": "검토 섹션",
        "diagram": "다이어그램",
        "mermaid_error": "다이어그램을 렌더링하지 못했습니다",
        "freshness": "최신성",
        "source_picker": "이 source를 로컬에서 검증",
    },
}

ORIGINS = {
    "primary_spec": "Current spec source",
    "comparison_spec": "Comparison source",
    "primary_plan": "Plan source",
    "plan_progress": "Plan source",
    "plan_task": "Plan source",
    "related_spec_context": "Related spec context",
}


def _source_sequence(bundle: ReviewBundle) -> tuple[ReviewSource, ...]:
    return (*bundle.primary, *bundle.comparison, *bundle.context)


def _json_for_html(value: object) -> str:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


def _internal_source_key(source: ReviewSource) -> str:
    identity = f"{source.namespace}\0{source.path}".encode("utf-8")
    return "source-" + hashlib.sha256(identity).hexdigest()[:20]


def _source_group(role: str) -> str:
    if role == "comparison_spec":
        return "comparison"
    if role == "related_spec_context":
        return "context"
    return "primary"


def _bundle_rows(bundle: ReviewBundle) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for source in _source_sequence(bundle):
        spec_bundle = source.spec_bundle
        if spec_bundle is None:
            continue
        identity = (source.role, source.bundle_path)
        if identity in seen:
            continue
        seen.add(identity)
        rows.append(
            {
                "role": source.role,
                "path": source.bundle_path,
                "root_path": spec_bundle.root_path.as_posix(),
                "title": source.bundle_title,
                "sha256": source.bundle_sha256,
            }
        )
    return rows


def _member_rows(bundle: ReviewBundle) -> list[dict[str, object]]:
    return [
        {
            "key": _internal_source_key(source),
            "role": source.role,
            "namespace": source.namespace,
            "bundle_path": source.bundle_path,
            "bundle_title": source.bundle_title,
            "bundle_sha256": source.bundle_sha256,
            "path": source.path,
            "title": source.member_title,
            "member_role": source.member_role,
            "sha256": source.sha256,
            "status": source.status,
        }
        for source in _source_sequence(bundle)
        if source.spec_bundle is not None
    ]


def _plan_source_rows(bundle: ReviewBundle) -> list[dict[str, object]]:
    return [
        {
            "key": _internal_source_key(source),
            "role": source.role,
            "namespace": source.namespace,
            "path": source.path,
            "title": source.title,
            "sha256": source.sha256,
            "status": source.status,
        }
        for source in _source_sequence(bundle)
        if source.spec_bundle is None
    ]


def manifest_source_records(bundle: ReviewBundle) -> dict[str, list[dict[str, object]]]:
    """Return the bundle, member, and plan source manifest records."""

    return {
        "bundles": _bundle_rows(bundle),
        "member_sources": _member_rows(bundle),
        "plan_sources": _plan_source_rows(bundle),
    }


def _manifest(
    bundle: ReviewBundle,
    *,
    review_id: str,
    locale: str,
    generated_at: str,
    checkpoint: str,
    commit: str | None,
    rebuild_command: str,
    source_base: str,
    offline: bool,
    view_context: ViewContext,
    presentation_plan: PresentationPlan,
) -> dict[str, object]:
    return {
        "review_id": review_id,
        "mode": bundle.mode,
        "locale": locale,
        "generated_at": generated_at,
        "checkpoint": checkpoint,
        "commit": commit,
        "rebuild_command": rebuild_command,
        "source_base": source_base,
        "offline": offline,
        "counts": _plain(bundle.counts),
        "freshness": "unverified",
        **manifest_source_records(bundle),
        "view_context": asdict(view_context),
        "presentation_plan": asdict(presentation_plan),
    }


def _source_label(source: ReviewSource) -> str:
    if source.spec_bundle is not None:
        return " · ".join(
            (source.bundle_title, source.member_title, source.path)
        )
    return " · ".join(value for value in (source.title, source.path) if value)


def _source_summary(bundle: ReviewBundle, labels: Mapping[str, str]) -> str:
    aggregates = "".join(
        '<span class="freshness-aggregate" '
        f'data-freshness-group="{group}">{html.escape(group)} '
        '<strong class="freshness-state freshness-unverified">unverified</strong></span>'
        for group in ("primary", "comparison", "context")
    )
    rows: list[str] = []
    for source in _source_sequence(bundle):
        key = _internal_source_key(source)
        rows.append(
            '<li class="source-row" '
            f'data-source-key="{key}" data-source-path="{html.escape(source.path, quote=True)}" '
            f'data-source-group="{_source_group(source.role)}">'
            f'<span class="source-role">{html.escape(ORIGINS[source.role])}</span> '
            f'<span>{html.escape(_source_label(source))}</span> '
            '<span class="freshness-state freshness-unverified" data-source-state>unverified</span>'
            '<span class="source-error" data-source-error aria-live="polite"></span>'
            f'<label class="source-picker-label">{html.escape(labels["source_picker"])}'
            f'<input type="file" accept=".md,text/markdown" data-source-picker data-source-key="{key}"></label>'
            "</li>"
        )
    return (
        '<details class="source-summary">'
        f'<summary>{html.escape(labels["freshness"])}: '
        '<span class="freshness-state freshness-unverified" data-freshness-overall>unverified</span></summary>'
        f'<div class="freshness-aggregates">{aggregates}</div>'
        f'<ul>{"".join(rows)}</ul></details>'
    )


def _primary_title(bundle: ReviewBundle) -> str:
    source = bundle.primary[0]
    if source.spec_bundle is not None:
        return source.bundle_title
    if isinstance(source.document, PlanDocument):
        return source.document.title
    return source.title


def _view_context(bundle: ReviewBundle, locale: str) -> ViewContext:
    source = bundle.primary[0]
    if source.spec_bundle is not None:
        kind = source.spec_bundle.metadata.kind
        subtype = source.spec_bundle.metadata.subtype
    else:
        kind = "plan"
        subtype = None
    return ViewContext(
        bundle.mode,
        kind,
        subtype,
        "execution" if bundle.mode == "plan" else "review",
        "mixed",
        locale,
        "standalone",
    )


def bundle_needs_mermaid(bundle: ReviewBundle) -> bool:
    """Return whether the snapshot renders at least one source diagram."""

    return bool(bundle.mermaid)


def _offline_mermaid() -> str:
    source = MERMAID_PATH.read_bytes()
    expected = None
    for line in MERMAID_CHECKSUM_PATH.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("*") == MERMAID_PATH.name:
            expected = parts[0]
            break
    actual = hashlib.sha256(source).hexdigest()
    if expected is None or actual != expected:
        raise ValueError("vendored Mermaid checksum verification failed")
    text = source.decode("utf-8")
    if "</script" in text.lower():
        raise ValueError("vendored Mermaid contains an unsafe inline script terminator")
    return f'<script data-mermaid-delivery="offline">\n{text}\n</script>'


def _mermaid_loader(offline: bool, bundle: ReviewBundle) -> str:
    if not bundle_needs_mermaid(bundle):
        return ""
    if offline:
        return _offline_mermaid()
    return (
        '<script data-mermaid-delivery="cdn" '
        f'src="{html.escape(MERMAID_URL, quote=True)}"></script>'
    )


def _fill_template(template: str, values: Mapping[str, str]) -> str:
    placeholders = set(re.findall(r"\{\{([A-Z][A-Z0-9_]*)\}\}", template))
    missing = placeholders - set(values)
    extra = set(values) - placeholders
    if missing or extra:
        raise ValueError(
            f"viewer template contract mismatch: missing={sorted(missing)}, extra={sorted(extra)}"
        )
    return re.sub(
        r"\{\{([A-Z][A-Z0-9_]*)\}\}",
        lambda match: values[match.group(1)],
        template,
    )


def render_review(
    bundle: ReviewBundle,
    review_id: str,
    locale: str,
    generated_at: str,
    checkpoint: str,
    commit: str | None,
    rebuild_command: str,
    source_base: str,
    offline: bool,
    view_context: ViewContext | None = None,
    semantic_ir: SemanticIR | None = None,
    presentation_plan: PresentationPlan | None = None,
) -> str:
    """Render one deterministic Review Viewer from validated source models."""

    if bundle.mode not in {"spec", "plan"}:
        raise ValueError("Review Viewer mode must be spec or plan")
    if locale not in LABELS:
        raise ValueError("Review Viewer locale must be en or ko")
    if source_base != "../../../":
        raise ValueError("Review Viewer source_base must be ../../../")
    if not _source_sequence(bundle):
        raise ValueError("Review Viewer requires at least one source")
    labels = LABELS[locale]
    ir = semantic_ir or build_semantic_ir(bundle)
    context = view_context or _view_context(bundle, locale)
    plan = presentation_plan or select_presentation_plan(ir, context)
    diagnostics = validate_presentation_plan(ir, plan)
    if diagnostics:
        raise ValueError(
            "invalid Presentation Plan: " + "; ".join(item.code for item in diagnostics)
        )
    components = render_components(ir, plan, context, review_id)
    navigation = "".join(
        f'<a href="#{html.escape(component.component_id, quote=True)}">{html.escape(component.title)}</a>'
        for component in components
    )
    content = "\n".join(
        '<section class="review-component" '
        f'id="{html.escape(component.component_id, quote=True)}" '
        f'data-component="{html.escape(plan.components[index].component, quote=True)}">'
        f'<h2>{html.escape(component.title)}</h2>'
        f'<p class="panel-orientation">{html.escape(component.orientation)}</p>'
        f"{component.markup}</section>"
        for index, component in enumerate(components)
    )
    manifest = _manifest(
        bundle,
        review_id=review_id,
        locale=locale,
        generated_at=generated_at,
        checkpoint=checkpoint,
        commit=commit,
        rebuild_command=rebuild_command,
        source_base=source_base,
        offline=offline,
        view_context=context,
        presentation_plan=plan,
    )
    title = _primary_title(bundle)
    status = bundle.primary[0].status or bundle.mode
    values = {
        "LANG": locale,
        "TITLE": html.escape(title),
        "STATUS": html.escape(status),
        "GENERATED_LABEL": html.escape(labels["generated"]),
        "GENERATED": html.escape(generated_at),
        "SOURCE_SUMMARY": _source_summary(bundle, labels),
        "NAV_LABEL": html.escape(labels["nav"], quote=True),
        "NAVIGATION": navigation,
        "CONTENT": content,
        "SOURCE_MANIFEST": _json_for_html(manifest),
        "FRESHNESS_RUNTIME": FRESHNESS_RUNTIME_PATH.read_text(encoding="utf-8"),
        "MERMAID": _mermaid_loader(offline, bundle),
        "DIAGRAM_LABEL": html.escape(labels["diagram"], quote=True),
        "MERMAID_ERROR": html.escape(labels["mermaid_error"], quote=True),
    }
    result = _fill_template(TEMPLATE_PATH.read_text(encoding="utf-8"), values)
    return result.rstrip("\n") + "\n"
