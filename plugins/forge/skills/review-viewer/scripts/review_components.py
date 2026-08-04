"""Reusable component grammar for adaptive Forge Review Viewers."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import html
from pathlib import Path
import sys
from typing import Callable, Mapping

from review_ir import SemanticBlock, SemanticIR
from review_planner import PresentationPlan, ViewContext


def _load_markdown_renderer():
    scripts = Path(__file__).resolve().parents[1].parent / "writing-specs" / "scripts"
    value = str(scripts)
    if value not in sys.path:
        sys.path.insert(0, value)
    from markdown_render import render_markdown

    return render_markdown


render_markdown = _load_markdown_renderer()

TITLES = {
    "summary": ("Summary", "요약"), "outline": ("Outline", "목차"),
    "state-map": ("State Map", "상태 흐름"), "sequence": ("Sequence", "시퀀스"),
    "interface-table": ("Interfaces", "인터페이스"), "exception-matrix": ("Exceptions", "예외"),
    "relation-graph": ("Relations", "관계"), "route-map": ("Routes", "Route"),
    "dependency-map": ("Dependencies", "의존성"), "runtime-atlas": ("Runtime Atlas", "Runtime Atlas"),
    "progress": ("Progress", "진행 상태"), "blockers": ("Blockers", "차단 요소"),
    "next-actions": ("Next Actions", "다음 작업"), "acceptance-coverage": ("Acceptance Coverage", "승인 기준 추적"),
    "decision-matrix": ("Decisions", "결정"), "change-route": ("Change Route", "변경 경로"),
    "verification": ("Verification", "검증"), "delta-matrix": ("Comparison", "비교"),
    "provenance": ("Provenance", "출처"), "source-detail": ("Source Detail", "Source 상세"),
}


@dataclass(frozen=True)
class RenderedComponent:
    component_id: str
    title: str
    orientation: str
    markup: str


def _block_markup(block: SemanticBlock) -> str:
    if block.kind == "mermaid":
        digest = hashlib.sha256(block.body.encode("utf-8")).hexdigest()
        return (
            f'<div class="diagram-scroll" role="region" tabindex="0" data-mermaid-sha256="{digest}">'
            f'<pre class="mermaid">{html.escape(block.body)}</pre></div>'
        )
    if block.kind == "code":
        return f'<pre><code>{html.escape(block.body)}</code></pre>'
    return render_markdown(block.body)


def _referenced_blocks(ir: SemanticIR, refs: tuple[str, ...]) -> tuple[SemanticBlock, ...]:
    blocks = {block.key: block for document in ir.documents for block in document.blocks}
    entities = {entity.key: entity for document in ir.documents for entity in document.entities}
    result: list[SemanticBlock] = []
    seen: set[str] = set()
    for reference in refs:
        key = reference if reference in blocks else entities.get(reference).block_key if reference in entities else ""
        if key and key not in seen:
            seen.add(key)
            result.append(blocks[key])
    return tuple(result)


def _summary(ir: SemanticIR) -> str:
    rows = "".join(
        f'<li><code>{html.escape(document.namespace)}</code> · {len(document.blocks)} blocks · {len(document.entities)} entities</li>'
        for document in ir.documents
    )
    return f'<ul class="component-summary">{rows}</ul>'


def _outline(ir: SemanticIR) -> str:
    return "".join(
        '<article class="source-block">'
        f'<p class="provenance"><code>{html.escape(document.path)}</code> · <code>{html.escape(document.namespace)}</code></p>'
        f'<ol>{"".join(f"<li>{html.escape(item)}</li>" for item in document.outline)}</ol></article>'
        for document in ir.documents
    )


def _provenance(ir: SemanticIR) -> str:
    return '<ul class="provenance-list">' + "".join(
        f'<li><code>{html.escape(document.path)}</code> · <code>{html.escape(document.namespace)}</code> · {html.escape(document.role)}</li>'
        for document in ir.documents
    ) + "</ul>"


def _details(ir: SemanticIR, refs: tuple[str, ...]) -> str:
    blocks = _referenced_blocks(ir, refs)
    return "".join(
        '<article class="source-block" '
        f'data-source-block="{html.escape(block.key, quote=True)}" data-source-path="{html.escape(block.source_path, quote=True)}">'
        f'<p class="provenance"><code>{html.escape(block.source_path)}</code> · {html.escape(block.heading)} · lines {block.line}–{block.end_line}</p>'
        f'{_block_markup(block)}</article>'
        for block in blocks
    )


def render_components(
    ir: SemanticIR,
    plan: PresentationPlan,
    context: ViewContext,
    review_id: str,
) -> tuple[RenderedComponent, ...]:
    rendered: list[RenderedComponent] = []
    korean = context.locale == "ko"
    for index, component in enumerate(plan.components, 1):
        title_pair = TITLES.get(component.component, (component.component, component.component))
        title = title_pair[1 if korean else 0]
        if component.component == "summary":
            markup = _summary(ir)
        elif component.component == "outline":
            markup = _outline(ir)
        elif component.component == "provenance":
            markup = _provenance(ir)
        else:
            markup = _details(ir, component.refs)
        rendered.append(
            RenderedComponent(
                component_id=f"component-{index}-{component.component}",
                title=title,
                orientation=component.orientation_key,
                markup=markup or '<p class="empty-component">No source-owned content.</p>',
            )
        )
    return tuple(rendered)


COMPONENT_RENDERERS: Mapping[str, Callable[..., str]] = {
    component: _details for component in TITLES if component not in {"summary", "outline", "provenance"}
}
