"""Reusable component grammar for adaptive Forge Visual Docs."""

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
    "brief-overview": ("At a glance", "한눈에 보기"),
    "brief-scope": ("Scope", "범위"),
    "brief-done": ("Done checks", "완료 조건"),
    "project-overview": ("Project at a glance", "프로젝트 한눈에"),
    "capability-map": ("Capabilities", "핵심 기능"),
    "spec-index": ("Spec", "Spec"),
    "structure-responsibility": ("Structure", "구조"),
    "developer-information": ("Developer information", "개발자 정보"),
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
    "brief_source": "Brief source",
    "project_map": "Project Map",
    "declared_spec": "Declared spec source",
    "repository_evidence": "Derived repository evidence",
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


def _entities_for_refs(
    ir: SemanticIR, refs: tuple[str, ...]
) -> tuple[SemanticEntity, ...]:
    entities = {
        entity.key: entity
        for document in ir.documents
        for entity in document.entities
    }
    return tuple(entities[reference] for reference in refs if reference in entities)


def _project_overview(ir: SemanticIR, refs: tuple[str, ...]) -> str:
    entities = _entities_for_refs(ir, refs)
    overview = next(
        (entity for entity in entities if entity.entity_type == "project-overview"),
        None,
    )
    if overview is None:
        return ""
    title = overview.attributes.get("title", overview.entity_id)
    body = overview.attributes.get("overview", "")
    raw_capabilities = overview.attributes.get("capabilities", ())
    capabilities = raw_capabilities if isinstance(raw_capabilities, tuple) else ()
    return (
        '<article class="project-intro">'
        f'<p class="project-kicker">{html.escape(str(title))}</p>'
        f'<p class="project-lede">{html.escape(str(body))}</p>'
        '<ul class="capability-list">'
        + "".join(f"<li>{html.escape(str(item))}</li>" for item in capabilities)
        + "</ul></article>"
    )


def _project_structure(ir: SemanticIR, refs: tuple[str, ...]) -> str:
    entities = tuple(
        entity
        for entity in _entities_for_refs(ir, refs)
        if entity.entity_type == "project-structure"
    )
    evidence_files = sorted(
        {
            str(path)
            for document in ir.documents
            if document.role == "repository_evidence"
            for path in document.metadata.get("files", ())
        }
    )
    statement_targets = {
        (
            str(entity.attributes.get("member_path", "")),
            str(entity.attributes.get("heading", entity.entity_id)),
            str(entity.attributes.get("anchor", "")),
        ): entity
        for document in ir.documents
        for entity in document.entities
        if entity.entity_type in {"requirement", "acceptance"}
    }
    cards: list[str] = []
    for entity in entities:
        path = str(entity.attributes.get("path", entity.entity_id))
        purpose = str(entity.attributes.get("purpose", ""))
        owns = str(entity.attributes.get("owns", ""))
        entry_points = tuple(entity.attributes.get("entry_points", ()))
        depends_on = tuple(entity.attributes.get("depends_on", ()))
        related_specs = tuple(entity.attributes.get("related_specs", ()))
        governing_statements = tuple(
            entity.attributes.get("governing_statements", ())
        )
        prefix = path.rstrip("/") + "/"
        evidence = tuple(
            item for item in evidence_files if item == path or item.startswith(prefix)
        )
        cards.append(
            '<article class="structure-card">'
            f'<h3><code>{html.escape(path)}</code></h3>'
            '<dl class="structure-ownership">'
            f'<div><dt>Purpose</dt><dd>{html.escape(purpose)}</dd></div>'
            f'<div><dt>Owns</dt><dd>{html.escape(owns)}</dd></div>'
            '</dl>'
            + '<details class="structure-support"><summary>Entry points and evidence</summary>'
            + (
                '<div class="structure-links"><h4>Entry Points</h4><ul>'
                + "".join(f"<li><code>{html.escape(str(item))}</code></li>" for item in entry_points)
                + "</ul></div>"
                if entry_points
                else ""
            )
            + (
                '<div class="structure-links"><h4>Depends On</h4><ul>'
                + "".join(f"<li><code>{html.escape(str(item))}</code></li>" for item in depends_on)
                + "</ul></div>"
                if depends_on
                else ""
            )
            + (
                '<div class="structure-links"><h4>Related Specs</h4><ul>'
                + "".join(f"<li><code>{html.escape(str(item))}</code></li>" for item in related_specs)
                + "</ul></div>"
                if related_specs
                else ""
            )
            + (
                '<div class="structure-links"><h4>Governing Statements</h4><ul>'
                + "".join(
                    (
                        '<li><a href="#'
                        + _internal_id(
                            "statement",
                            statement_targets[
                                (
                                    str(item["member_path"]),
                                    str(item["heading"]),
                                    str(item["anchor"]),
                                )
                            ].key,
                        )
                        + '">'
                        + html.escape(str(item["heading"]))
                        + "</a></li>"
                    )
                    for item in governing_statements
                    if (
                        str(item["member_path"]),
                        str(item["heading"]),
                        str(item["anchor"]),
                    )
                    in statement_targets
                )
                + "</ul></div>"
                if governing_statements
                else ""
            )
            + (
                '<details class="derived-evidence"><summary>Derived file evidence</summary><ul>'
                + "".join(f"<li><code>{html.escape(item)}</code></li>" for item in evidence)
                + "</ul></details>"
                if evidence
                else ""
            )
            + "</details>"
            + "</article>"
        )
    return '<div class="structure-grid">' + "".join(cards) + "</div>"


def _project_specs(
    ir: SemanticIR,
    refs: tuple[str, ...],
    review_id: str,
    rendered_entities: set[str],
    coverage_targets: Mapping[str, tuple[SemanticEntity, ...]],
) -> str:
    bundles: dict[str, SemanticDocument] = {}
    for document in ir.documents:
        if document.role != "declared_spec":
            continue
        bundle_path = document.metadata.get("bundle_path")
        if isinstance(bundle_path, str):
            bundles.setdefault(bundle_path, document)
    index_cards: list[str] = []
    for bundle_path, document in bundles.items():
        title = str(document.metadata.get("bundle_title", bundle_path))
        overview = str(document.metadata.get("overview", "")).strip()
        areas = tuple(document.metadata.get("areas", ()))
        related_specs = tuple(document.metadata.get("related_specs", ()))
        index_cards.append(
            '<article class="spec-index-card">'
            f'<h3>{html.escape(title)}</h3>'
            f'<p class="provenance"><code>{html.escape(bundle_path)}</code></p>'
            + (f'<p>{html.escape(overview)}</p>' if overview else "")
            + (
                '<p><strong>Areas:</strong> '
                + ", ".join(html.escape(str(area)) for area in areas)
                + "</p>"
                if areas
                else ""
            )
            + (
                '<div><strong>Related Specs:</strong><ul>'
                + "".join(
                    f'<li><code>{html.escape(str(item.get("path", "")))}</code> · '
                    f'{html.escape(str(item.get("relation", "")))}</li>'
                    for item in related_specs
                )
                + "</ul></div>"
                if related_specs
                else ""
            )
            + "</article>"
        )
    detail = _details(
        ir,
        refs,
        review_id,
        rendered_entities,
        coverage_targets,
    )
    return (
        '<div class="spec-index">'
        + "".join(index_cards)
        + '</div><details class="spec-detail"><summary>Complete Spec details</summary>'
        + detail
        + "</details>"
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
        elif component.component == "project-overview":
            markup = _project_overview(ir, component.refs)
        elif component.component == "structure-responsibility":
            markup = _project_structure(ir, component.refs)
        elif component.component == "spec-index":
            markup = _project_specs(
                ir,
                component.refs,
                review_id,
                rendered_entities,
                coverage_targets,
            )
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
