"""Reusable component grammar for adaptive Forge Review Viewers."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import html
from pathlib import Path
import sys
from typing import Mapping

from review_ir import SemanticBlock, SemanticDocument, SemanticEntity, SemanticIR
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


DOCUMENT_ROLE_LABELS = {
    "primary_spec": "Current spec source",
    "comparison_spec": "Comparison source",
    "related_spec_context": "Related spec context",
    "primary_plan": "Plan source",
    "plan_progress": "Plan source",
    "plan_task": "Plan source",
}


def _document_label(document: SemanticDocument) -> str:
    bundle_title = document.metadata.get("bundle_title")
    member_title = document.metadata.get("member_title")
    if isinstance(bundle_title, str) and isinstance(member_title, str):
        return " · ".join((bundle_title, member_title, document.path))
    title = document.metadata.get("title")
    if isinstance(title, str) and title:
        return " · ".join((title, document.path))
    return document.path


def _internal_id(prefix: str, value: str) -> str:
    return f"{prefix}-{hashlib.sha256(value.encode('utf-8')).hexdigest()[:20]}"


def _statement_markup(
    entity: SemanticEntity,
    document: SemanticDocument,
    review_id: str,
    coverage_targets: Mapping[str, tuple[SemanticEntity, ...]],
) -> str:
    heading = entity.attributes.get("heading")
    label = heading if isinstance(heading, str) else entity.entity_id
    target = _internal_id("statement", entity.key)
    provenance = html.escape(_document_label(document))
    if entity.entity_type == "acceptance":
        storage = f"{review_id}:statement:{hashlib.sha256(entity.key.encode('utf-8')).hexdigest()[:24]}"
        links = " · ".join(
            f'<a data-relation="covers" href="#{_internal_id("statement", target.key)}">'
            f'{html.escape(str(target.attributes.get("heading", target.entity_id)))}</a>'
            for target in coverage_targets.get(entity.key, ())
        )
        coverage = f'<p>Verifies: {links}</p>' if links else ""
        return (
            f'<article id="{target}" data-statement-kind="acceptance" '
            f'data-storage-key="{html.escape(storage, quote=True)}" class="source-block">'
            f'<p class="provenance">{provenance}</p>'
            '<label class="review-check-item">'
            f'<input type="checkbox" data-review-check data-kind="acceptance" '
            f'data-storage-key="{html.escape(storage, quote=True)}" '
            f'aria-label="{html.escape(label, quote=True)}">'
            f'<span><a href="#{target}">{html.escape(label)}</a></span>'
            f"</label>{coverage}</article>"
        )
    return (
        f'<article id="{target}" data-statement-kind="requirement" class="source-block">'
        f'<p class="provenance">{provenance}</p>'
        f'<h3><a href="#{target}">{html.escape(label)}</a></h3></article>'
    )


def _statement_reference_markup(
    entity: SemanticEntity,
    document: SemanticDocument,
) -> str:
    heading = entity.attributes.get("heading")
    label = heading if isinstance(heading, str) else entity.entity_id
    target = _internal_id("statement", entity.key)
    return (
        '<article data-statement-reference class="source-block">'
        f'<p class="provenance">{html.escape(_document_label(document))}</p>'
        f'<a href="#{target}">{html.escape(label)}</a></article>'
    )


def _step_markup(
    entities: tuple[SemanticEntity, ...],
    document: SemanticDocument,
    review_id: str,
    rendered_entities: set[str],
) -> str:
    rows: list[str] = []
    for entity in entities:
        text = entity.attributes.get("text")
        label = text if isinstance(text, str) else entity.entity_id
        target = _internal_id("step", entity.key)
        if entity.key in rendered_entities:
            rows.append(f'<a href="#{target}">{html.escape(label)}</a>')
            continue
        rendered_entities.add(entity.key)
        storage = f"{review_id}:step:{hashlib.sha256(entity.key.encode('utf-8')).hexdigest()[:24]}"
        rows.append(
            f'<label class="review-check-item" id="{target}" data-step>'
            f'<input type="checkbox" data-review-check data-kind="step" '
            f'data-storage-key="{html.escape(storage, quote=True)}" '
            f'aria-label="{html.escape(label, quote=True)}">'
            f'<span><a href="#{target}">{html.escape(label)}</a></span></label>'
        )
    return (
        '<article class="source-block">'
        f'<p class="provenance">{html.escape(_document_label(document))}</p>'
        f'{"".join(rows)}</article>'
    )


def _block_markup(
    block: SemanticBlock,
    document: SemanticDocument,
    entities: tuple[SemanticEntity, ...],
    review_id: str,
    rendered_entities: set[str],
    coverage_targets: Mapping[str, tuple[SemanticEntity, ...]],
) -> str:
    statement = next(
        (item for item in entities if item.entity_type in {"requirement", "acceptance"}),
        None,
    )
    if statement is not None:
        if statement.key in rendered_entities:
            return _statement_reference_markup(statement, document)
        rendered_entities.add(statement.key)
        return _statement_markup(
            statement, document, review_id, coverage_targets
        )
    steps = tuple(item for item in entities if item.entity_type == "step")
    if steps:
        return _step_markup(steps, document, review_id, rendered_entities)
    provenance = html.escape(_document_label(document))
    if block.kind == "mermaid":
        digest = hashlib.sha256(block.body.encode("utf-8")).hexdigest()
        return (
            '<article class="diagram-card" data-origin="Source" '
            f'data-source-path="{html.escape(block.source_path, quote=True)}" '
            f'data-mermaid-sha256="{digest}">'
            f'<h3>{html.escape(block.heading)}</h3>'
            '<p><strong>What to confirm:</strong> The nodes and arrows match the source.</p>'
            '<p><strong>How to read:</strong> Follow the source-defined direction.</p>'
            f'<p class="provenance">{provenance}</p>'
            '<div class="diagram-scroll" role="region" tabindex="0">'
            f'<pre class="mermaid">{html.escape(block.body)}</pre></div></article>'
        )
    if block.kind == "code":
        body = f'<pre><code>{html.escape(block.body)}</code></pre>'
    else:
        body = render_markdown(block.body)
    return (
        '<article class="source-block">'
        f'<p class="provenance">{provenance} · lines {block.line}–{block.end_line}</p>'
        f"{body}</article>"
    )


def _referenced_blocks(
    ir: SemanticIR, refs: tuple[str, ...]
) -> tuple[tuple[SemanticBlock, SemanticDocument, tuple[SemanticEntity, ...]], ...]:
    documents = {document.namespace: document for document in ir.documents}
    blocks = {block.key: block for document in ir.documents for block in document.blocks}
    entities = {entity.key: entity for document in ir.documents for entity in document.entities}
    entities_by_block: dict[str, list[SemanticEntity]] = {}
    for entity in entities.values():
        entities_by_block.setdefault(entity.block_key, []).append(entity)
    result: list[tuple[SemanticBlock, SemanticDocument, tuple[SemanticEntity, ...]]] = []
    seen: set[str] = set()
    for reference in refs:
        key = reference if reference in blocks else entities.get(reference).block_key if reference in entities else ""
        if not key or key in seen:
            continue
        seen.add(key)
        block = blocks[key]
        result.append(
            (block, documents[block.source_namespace], tuple(entities_by_block.get(key, ())))
        )
    return tuple(result)


def _summary(ir: SemanticIR) -> str:
    rows = "".join(
        f'<li>{html.escape(_document_label(document))} · '
        f'{len(document.blocks)} blocks · {len(document.entities)} entities</li>'
        for document in ir.documents
    )
    return f'<ul class="component-summary">{rows}</ul>'


def _outline(ir: SemanticIR) -> str:
    return "".join(
        '<article class="source-block">'
        f'<p class="provenance">{html.escape(_document_label(document))}</p>'
        f'<ol>{"".join(f"<li>{html.escape(item)}</li>" for item in document.outline)}</ol></article>'
        for document in ir.documents
    )


def _provenance(ir: SemanticIR) -> str:
    return '<ul class="provenance-list">' + "".join(
        f'<li>{html.escape(_document_label(document))} · '
        f'{html.escape(DOCUMENT_ROLE_LABELS.get(document.role, "Source"))}</li>'
        for document in ir.documents
    ) + "</ul>"


def _details(
    ir: SemanticIR,
    refs: tuple[str, ...],
    review_id: str,
    rendered_entities: set[str],
    coverage_targets: Mapping[str, tuple[SemanticEntity, ...]],
) -> str:
    return "".join(
        _block_markup(
            block,
            document,
            entities,
            review_id,
            rendered_entities,
            coverage_targets,
        )
        for block, document, entities in _referenced_blocks(ir, refs)
    )


def _coverage_targets(ir: SemanticIR) -> Mapping[str, tuple[SemanticEntity, ...]]:
    entities = {
        entity.key: entity
        for document in ir.documents
        for entity in document.entities
    }
    targets: dict[str, list[SemanticEntity]] = {}
    for relation in ir.relations:
        if relation.relation_type != "covers" or relation.to_entity not in entities:
            continue
        targets.setdefault(relation.from_entity, []).append(entities[relation.to_entity])
    return {key: tuple(value) for key, value in targets.items()}


def _orientation(title: str, korean: bool) -> str:
    if korean:
        return f"{title}에서 무엇을 확인할까? 각 항목을 source path로 추적합니다."
    return f"What should this {title.lower()} confirm? Trace each item to its source path."


def render_components(
    ir: SemanticIR,
    plan: PresentationPlan,
    context: ViewContext,
    review_id: str,
) -> tuple[RenderedComponent, ...]:
    rendered: list[RenderedComponent] = []
    rendered_entities: set[str] = set()
    coverage_targets = _coverage_targets(ir)
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
            markup = _details(
                ir,
                component.refs,
                review_id,
                rendered_entities,
                coverage_targets,
            )
        rendered.append(
            RenderedComponent(
                component_id=f"component-{index}-{component.component}",
                title=title,
                orientation=_orientation(title, korean),
                markup=markup or '<p class="empty-component">No source-owned content.</p>',
            )
        )
    return tuple(rendered)
