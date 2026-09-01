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
    "system-overview": ("System overview", "시스템 개요"),
    "state-map": ("State Map", "상태 흐름"), "sequence": ("Sequence", "시퀀스"),
    "interface-table": ("Interfaces", "인터페이스"), "exception-matrix": ("Exceptions", "예외"),
    "runtime-responsibility": ("Runtime responsibilities", "실행 책임"),
    "relation-graph": ("Relations", "관계"), "route-map": ("Routes", "Route"),
    "dependency-map": ("Dependencies", "의존성"), "runtime-atlas": ("Runtime Atlas", "Runtime Atlas"),
    "progress": ("Progress", "진행 상태"), "blockers": ("Blockers", "차단 요소"),
    "next-actions": ("Next Actions", "다음 작업"), "acceptance-coverage": ("Acceptance Coverage", "승인 기준 추적"),
    "decision-matrix": ("Decisions", "결정"), "change-route": ("Change Route", "변경 경로"),
    "verification": ("Verification", "검증"), "delta-matrix": ("Comparison", "비교"),
    "provenance": ("Provenance", "출처"), "source-detail": ("Source Detail", "Source 상세"),
    "spec-navigator": ("Spec contents", "설계 기준 탐색"),
    "brief-overview": ("At a glance", "한눈에 보기"),
    "brief-scope": ("Scope", "범위"),
    "brief-done": ("Done checks", "완료 조건"),
    "project-overview": ("Overview", "개요"),
    "capability-map": ("Capabilities", "핵심 기능"),
    "spec-index": ("Design criteria", "설계 기준"),
    "structure-responsibility": ("Project structure", "프로젝트 구조"),
    "developer-information": ("Source & verification", "출처·검증"),
}


@dataclass(frozen=True)
class RenderedComponent:
    component_id: str
    title: str
    orientation: str
    markup: str


@dataclass(frozen=True)
class ProjectNavNode:
    route: str
    kind: str
    label: str
    children: tuple["ProjectNavNode", ...] = ()


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


def _entity_count(ir: SemanticIR, entity_type: str) -> int:
    return sum(
        1
        for document in ir.documents
        for entity in document.entities
        if entity.entity_type == entity_type
    )


def _system_overview(ir: SemanticIR, *, korean: bool) -> str:
    primary = ir.documents[0]
    metadata = primary.metadata
    areas = tuple(metadata.get("areas", ()))
    components = tuple(metadata.get("components", ()))
    labels = (
        ("문서", "필수 사항", "완료 기준", "담당 영역", "구성 요소")
        if korean
        else ("Documents", "Requirements", "Completion criteria", "Areas", "Components")
    )
    metrics = (
        (labels[0], len(ir.documents)),
        (labels[1], _entity_count(ir, "requirement")),
        (labels[2], _entity_count(ir, "acceptance")),
    )
    return (
        '<article class="system-overview" data-component="system-overview">'
        '<dl class="system-metrics">'
        + "".join(
            f'<div class="system-metric"><dt>{html.escape(label)}</dt><dd>{value}</dd></div>'
            for label, value in metrics
        )
        + "</dl>"
        + (
            f'<section class="system-taxonomy"><h3>{html.escape(labels[3])}</h3><ul>'
            + "".join(f"<li>{html.escape(str(item))}</li>" for item in areas)
            + "</ul></section>"
            if areas
            else ""
        )
        + (
            f'<section class="system-taxonomy"><h3>{html.escape(labels[4])}</h3><ul>'
            + "".join(f"<li><code>{html.escape(str(item))}</code></li>" for item in components)
            + "</ul></section>"
            if components
            else ""
        )
        + "</article>"
    )


def _semantic_table(
    ir: SemanticIR,
    refs: tuple[str, ...],
    *,
    css_class: str,
    korean: bool,
) -> str:
    del refs
    tables = [
        (block, document)
        for document in ir.documents
        for block in document.blocks
        if block.kind == "table"
    ]

    def responsibility(block: SemanticBlock) -> bool:
        value = f"{block.heading}\n{block.body}".casefold()
        return any(
            token in value
            for token in ("책임", "서버", "클라이언트", "responsibility", "authority", "owner")
        )

    if css_class == "responsibility-table":
        selected = [(block, document) for block, document in tables if responsibility(block)]
    else:
        selected = [
            (block, document)
            for block, document in tables
            if not responsibility(block)
            and any(
                token in f"{block.heading}\n{block.body}".casefold()
                for token in ("interface", "schema", "remote", "계약", " id ", "stat id")
            )
        ]
    empty = "표시할 source 항목이 없습니다." if korean else "No source entries are available."
    if not selected:
        return f'<div class="{css_class}" data-component="{css_class}"><p class="empty-component">{empty}</p></div>'
    return (
        f'<div class="{css_class}" data-component="{css_class}">'
        + "".join(
            '<article class="semantic-table-card">'
            f'<h3>{html.escape(block.heading)}</h3>'
            f'{render_markdown(block.body)}'
            f'<p class="provenance"><code>{html.escape(document.path)}</code></p>'
            "</article>"
            for block, document in selected
        )
        + "</div>"
    )


def _acceptance_coverage(
    ir: SemanticIR,
    refs: tuple[str, ...],
    review_id: str,
    rendered_entities: set[str],
    coverage_targets: Mapping[str, tuple[SemanticEntity, ...]],
    *,
    korean: bool,
    summary_only: bool = False,
) -> str:
    documents = {document.namespace: document for document in ir.documents}
    entities = {
        entity.key: entity
        for document in ir.documents
        for entity in document.entities
    }
    accepted = [
        entities[reference]
        for reference in refs
        if reference in entities and entities[reference].entity_type == "acceptance"
    ]
    if not accepted:
        empty = "완료 기준이 없습니다." if korean else "No completion criteria are available."
        return f'<div class="coverage-groups" data-component="acceptance-coverage"><p class="empty-component">{empty}</p></div>'
    groups = []
    for entity in accepted:
        document = documents[entity.source_namespace]
        targets = coverage_targets.get(entity.key, ())
        if summary_only:
            heading = str(entity.attributes.get("heading", entity.entity_id))
            target = _internal_id("statement", entity.key)
            count_label = (
                f"필수 사항 {len(targets)}개"
                if korean
                else f"{len(targets)} required behaviors"
            )
            groups.append(
                '<article class="coverage-summary">'
                f'<h3><a href="#{target}">{html.escape(heading)}</a></h3>'
                f'<p>{html.escape(count_label)}</p>'
                "</article>"
            )
            continue
        requirements = "".join(
            (
                _statement_reference_markup(target, documents[target.source_namespace])
                if target.key in rendered_entities
                else _statement_markup(
                    target,
                    documents[target.source_namespace],
                    review_id,
                    coverage_targets,
                )
            )
            for target in targets
        )
        rendered_entities.update(target.key for target in targets)
        statement = (
            _statement_reference_markup(entity, document)
            if entity.key in rendered_entities
            else _statement_markup(entity, document, review_id, coverage_targets)
        )
        groups.append(
            '<section class="coverage-group">'
            + requirements
            + statement
            + "</section>"
        )
        rendered_entities.add(entity.key)
    return '<div class="coverage-groups" data-component="acceptance-coverage">' + "".join(groups) + "</div>"


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


def _project_term(value: str, korean: bool) -> str:
    if not korean:
        return {
            "Requirements": "Required behavior",
            "Acceptance Criteria": "Completion criteria",
            "Behavior & Flows": "Behavior and flows",
            "Behaviour & Flows": "Behavior and flows",
            "Launch Baseline": "Release baseline",
            "Purpose": "Role",
            "Owns": "Responsibilities",
            "Entry Points": "Key files",
            "Developer information": "Source & verification",
        }.get(value, value)
    return {
        "Overview": "개요",
        "Documents": "문서 구성",
        "Requirements": "필수 사항",
        "Acceptance Criteria": "완료 기준",
        "Behavior & Flows": "동작과 흐름",
        "Behaviour & Flows": "동작과 흐름",
        "Launch Baseline": "출시 기준",
        "Purpose": "역할",
        "Owns": "담당 범위",
        "Entry Points": "주요 파일",
        "Depends On": "의존 대상",
        "Related Specs": "관련 설계 기준",
        "Governing Statements": "근거 문장",
        "Derived file evidence": "계산된 파일 근거",
        "Developer information": "출처·검증",
    }.get(value, value)


def _project_route(kind: str, identity: str) -> str:
    return _internal_id(kind, identity)


def _project_detail(
    route: str,
    kind: str,
    title: str,
    body: str,
    *,
    active: bool = False,
) -> str:
    classes = "project-detail is-active" if active else "project-detail"
    hidden = "" if active else " hidden"
    return (
        f'<article class="{classes}" id="{html.escape(route, quote=True)}" '
        f'data-project-detail data-route="{html.escape(route, quote=True)}" '
        f'data-detail-kind="{html.escape(kind, quote=True)}"{hidden}>'
        f'<h2>{html.escape(title)}</h2>{body}</article>'
    )


def _project_tree_node(
    node: ProjectNavNode,
    *,
    level: int,
    korean: bool,
    root: bool = False,
    first: bool = False,
) -> str:
    expandable = bool(node.children)
    expanded = first
    route = html.escape(node.route, quote=True)
    item_attributes = (
        f'role="treeitem" aria-level="{level}" '
        f'aria-selected="{"true" if first else "false"}" '
        f'tabindex="{0 if first else -1}" '
        f'data-route="{route}" '
        f'data-node-kind="{html.escape(node.kind, quote=True)}" '
        + ('data-project-root="true" ' if root else "")
        + (f'aria-expanded="{"true" if expanded else "false"}" ' if expandable else "")
    )
    children = ""
    toggle = ""
    if expandable:
        action = "접기" if expanded and korean else "펼치기" if korean else "Collapse" if expanded else "Expand"
        expand_label = f"{node.label} 펼치기" if korean else f"Expand {node.label}"
        collapse_label = f"{node.label} 접기" if korean else f"Collapse {node.label}"
        toggle = (
            '<button class="project-tree-toggle" type="button" '
            f'data-tree-toggle data-route="{route}" '
            f'aria-controls="project-tree-group-{route}" '
            f'aria-expanded="{"true" if expanded else "false"}" '
            f'aria-label="{html.escape(node.label + " " + action, quote=True)}" '
            f'data-expand-label="{html.escape(expand_label, quote=True)}" '
            f'data-collapse-label="{html.escape(collapse_label, quote=True)}"></button>'
        )
        children = (
            f'<div class="project-tree-group" id="project-tree-group-{route}" role="group" '
            f'data-parent-route="{route}">'
            + "".join(
                _project_tree_node(child, level=level + 1, korean=korean)
                for child in node.children
            )
            + "</div>"
        )
    return (
        '<div class="project-tree-branch" role="none" data-tree-branch>'
        f'{toggle}<a class="project-tree-item" href="#{route}" '
        f'{item_attributes}>'
        f'<span class="project-tree-label">{html.escape(node.label)}</span></a>'
        f"{children}</div>"
    )


def _project_structure_parts(
    ir: SemanticIR,
    refs: tuple[str, ...],
    *,
    korean: bool,
) -> tuple[tuple[ProjectNavNode, ...], tuple[str, ...], str]:
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
    nodes: list[ProjectNavNode] = []
    details: list[str] = []
    overview_rows: list[str] = []
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
        route = _project_route("structure-entry", path)
        nodes.append(ProjectNavNode(route, "structure-entry", path))
        overview_rows.append(
            f'<li><a href="#{route}"><code>{html.escape(path)}</code></a>'
            f'<span>{html.escape(purpose)}</span></li>'
        )
        details.append(
            _project_detail(
                route,
                "structure-entry",
                path,
                ('<p class="project-detail-kicker">프로젝트 구조</p>' if korean else '<p class="project-detail-kicker">Project structure</p>')
                + '<dl class="structure-ownership">'
                f'<div><dt>{html.escape(_project_term("Purpose", korean))}</dt><dd>{html.escape(purpose)}</dd></div>'
                f'<div><dt>{html.escape(_project_term("Owns", korean))}</dt><dd>{html.escape(owns)}</dd></div>'
                '</dl>'
                + (
                    '<section class="structure-key-files">'
                    f'<h3>{html.escape(_project_term("Entry Points", korean))}</h3><ul>'
                    + "".join(f"<li><code>{html.escape(str(item))}</code></li>" for item in entry_points)
                    + "</ul></section>"
                    if entry_points
                    else ""
                )
                + '<details class="project-evidence"><summary>'
                + html.escape(_project_term("Developer information", korean))
                + "</summary>"
                + (
                    '<div class="structure-links"><h3>'
                    + html.escape(_project_term("Depends On", korean))
                    + "</h3><ul>"
                    + "".join(f"<li><code>{html.escape(str(item))}</code></li>" for item in depends_on)
                    + "</ul></div>"
                    if depends_on
                    else ""
                )
                + (
                    '<div class="structure-links"><h3>'
                    + html.escape(_project_term("Related Specs", korean))
                    + "</h3><ul>"
                    + "".join(f"<li><code>{html.escape(str(item))}</code></li>" for item in related_specs)
                    + "</ul></div>"
                    if related_specs
                    else ""
                )
                + (
                    '<div class="structure-links"><h3>'
                    + html.escape(_project_term("Governing Statements", korean))
                    + "</h3><ul>"
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
                    '<div class="derived-evidence"><h3>'
                    + html.escape(_project_term("Derived file evidence", korean))
                    + "</h3><ul>"
                    + "".join(f"<li><code>{html.escape(item)}</code></li>" for item in evidence)
                    + "</ul></div>"
                    if evidence
                    else ""
                )
                + "</details>",
            )
        )
    overview = (
        '<p class="project-section-lede">'
        + ("상위 영역을 선택하면 역할과 담당 범위를 먼저 확인할 수 있습니다." if korean else "Select an area to see its role and responsibilities first.")
        + '</p><ul class="project-index-list">'
        + "".join(overview_rows)
        + "</ul>"
    )
    return tuple(nodes), tuple(details), overview


def _section_path_for_block(
    block: SemanticBlock,
    entities: tuple[SemanticEntity, ...],
) -> tuple[str, ...]:
    if any(entity.entity_type == "requirement" for entity in entities):
        return ("Requirements",)
    if any(entity.entity_type == "acceptance" for entity in entities):
        return ("Acceptance Criteria",)
    return block.heading_path or (block.heading,)


def _project_spec_parts(
    ir: SemanticIR,
    refs: tuple[str, ...],
    review_id: str,
    rendered_entities: set[str],
    coverage_targets: Mapping[str, tuple[SemanticEntity, ...]],
    *,
    korean: bool,
    roles: frozenset[str] = frozenset(("declared_spec",)),
) -> tuple[tuple[ProjectNavNode, ...], tuple[str, ...], str]:
    allowed_blocks = {
        block.key
        for block, _, _ in _referenced_blocks(ir, refs)
    }
    entities_by_block: dict[str, tuple[SemanticEntity, ...]] = {}
    for document in ir.documents:
        for entity in document.entities:
            entities_by_block.setdefault(entity.block_key, ())
            entities_by_block[entity.block_key] = (*entities_by_block[entity.block_key], entity)
    bundles: dict[str, list[SemanticDocument]] = {}
    for document in ir.documents:
        if document.role not in roles:
            continue
        bundle_path = document.metadata.get("bundle_path")
        if isinstance(bundle_path, str):
            bundles.setdefault(bundle_path, []).append(document)

    bundle_nodes: list[ProjectNavNode] = []
    details: list[str] = []
    overview_rows: list[str] = []
    for bundle_path, documents in bundles.items():
        root = documents[0]
        bundle_title = str(root.metadata.get("bundle_title", bundle_path))
        bundle_route = _project_route("spec-bundle", bundle_path)
        overview_rows.append(
            f'<li><a href="#{bundle_route}">{html.escape(bundle_title)}</a>'
            f'<code>{html.escape(bundle_path)}</code></li>'
        )
        member_nodes: list[ProjectNavNode] = []
        member_links: list[str] = []
        for document in documents:
            member_title = str(document.metadata.get("member_title", document.path))
            member_route = _project_route("spec-member", document.path)
            sections: dict[tuple[str, ...], list[SemanticBlock]] = {}
            section_order: list[tuple[str, ...]] = []
            for block in document.blocks:
                if block.key not in allowed_blocks:
                    continue
                path = _section_path_for_block(
                    block, entities_by_block.get(block.key, ())
                )
                for depth in range(1, len(path) + 1):
                    prefix = path[:depth]
                    if prefix not in sections:
                        sections[prefix] = []
                        section_order.append(prefix)
                sections[path].append(block)
            children_by_path: dict[
                tuple[str, ...], list[tuple[str, ...]]
            ] = {path: [] for path in section_order}
            root_paths: list[tuple[str, ...]] = []
            for path in section_order:
                parent = path[:-1]
                if parent and parent in children_by_path:
                    children_by_path[parent].append(path)
                else:
                    root_paths.append(path)

            def section_route(path: tuple[str, ...]) -> str:
                return _project_route(
                    "spec-section", f"{document.path}\0" + "\0".join(path)
                )

            def section_node(path: tuple[str, ...]) -> ProjectNavNode:
                return ProjectNavNode(
                    section_route(path),
                    "spec-section",
                    _project_term(path[-1], korean),
                    tuple(
                        section_node(child) for child in children_by_path[path]
                    ),
                )

            section_nodes = [section_node(path) for path in root_paths]
            section_links: list[str] = []
            for path in root_paths:
                route = section_route(path)
                label = _project_term(path[-1], korean)
                section_links.append(
                    f'<li><a href="#{route}">{html.escape(label)}</a></li>'
                )
            for path in section_order:
                blocks = sections[path]
                route = section_route(path)
                section_label = _project_term(path[-1], korean)
                visible_blocks = [
                    block
                    for block in blocks
                    if block.kind != "heading"
                    or any(
                        entity.entity_type in {"requirement", "acceptance"}
                        for entity in entities_by_block.get(block.key, ())
                    )
                ]
                block_markup = "".join(
                    _block_markup(
                        block,
                        document,
                        entities_by_block.get(block.key, ()),
                        review_id,
                        rendered_entities,
                        coverage_targets,
                    )
                    for block in visible_blocks
                )
                child_paths = children_by_path[path]
                child_index = (
                    '<h3>'
                    + ("하위 항목" if korean else "Topics")
                    + '</h3><ul class="project-index-list">'
                    + "".join(
                        '<li><a href="#'
                        + section_route(child)
                        + '">'
                        + html.escape(_project_term(child[-1], korean))
                        + "</a></li>"
                        for child in child_paths
                    )
                    + "</ul>"
                    if child_paths
                    else ""
                )
                if not block_markup and not child_index:
                    block_markup = (
                        '<p class="project-section-lede">'
                        + (
                            "이 항목에는 별도 본문이 없습니다."
                            if korean
                            else "This topic has no separate body content."
                        )
                        + "</p>"
                    )
                subtree_blocks = [
                    block
                    for candidate, candidate_blocks in sections.items()
                    if candidate[: len(path)] == path
                    for block in candidate_blocks
                ]
                line_start = min(block.line for block in subtree_blocks)
                line_end = max(block.end_line for block in subtree_blocks)
                details.append(
                    _project_detail(
                        route,
                        "spec-section",
                        section_label,
                        f'<p class="project-detail-kicker">{html.escape(member_title)}</p>'
                        + block_markup
                        + child_index
                        + '<details class="project-evidence"><summary>'
                        + html.escape(_project_term("Developer information", korean))
                        + '</summary><p class="provenance"><code>'
                        + html.escape(document.path)
                        + f"</code> · lines {line_start}–{line_end}</p></details>",
                    )
                )
            member_nodes.append(ProjectNavNode(member_route, "spec-member", member_title, tuple(section_nodes)))
            member_links.append(f'<li><a href="#{member_route}">{html.escape(member_title)}</a><code>{html.escape(document.path)}</code></li>')
            details.append(
                _project_detail(
                    member_route,
                    "spec-member",
                    member_title,
                    '<p class="project-detail-kicker">'
                    + ("설계 기준 문서" if korean else "Design criteria document")
                    + '</p><p class="provenance"><code>'
                    + html.escape(document.path)
                    + '</code></p><ul class="project-index-list">'
                    + "".join(section_links)
                    + "</ul>",
                )
            )
        bundle_nodes.append(ProjectNavNode(bundle_route, "spec-bundle", bundle_title, tuple(member_nodes)))
        overview = str(root.metadata.get("overview", "")).strip()
        areas = tuple(root.metadata.get("areas", ()))
        related_specs = tuple(root.metadata.get("related_specs", ()))
        details.append(
            _project_detail(
                bundle_route,
                "spec-bundle",
                bundle_title,
                f'<p class="provenance"><code>{html.escape(bundle_path)}</code></p>'
                + (f'<p class="project-section-lede">{html.escape(overview)}</p>' if overview else "")
                + (
                    '<p><strong>' + ("담당 영역" if korean else "Areas") + ':</strong> '
                    + ", ".join(html.escape(str(area)) for area in areas) + "</p>"
                    if areas else ""
                )
                + (
                    '<div><strong>' + ("관련 설계 기준" if korean else "Related design criteria") + ':</strong><ul>'
                    + "".join(
                        f'<li><code>{html.escape(str(item.get("path", "")))}</code> · '
                        f'{html.escape(str(item.get("relation", "")))}</li>'
                        for item in related_specs
                    )
                    + "</ul></div>"
                    if related_specs else ""
                )
                + '<h3>' + ("문서" if korean else "Documents") + '</h3><ul class="project-index-list">'
                + "".join(member_links)
                + "</ul>",
            )
        )
    overview = (
        '<p class="project-section-lede">'
        + ("설계 기준을 묶음, 문서, 섹션 순서로 선택해 확인합니다." if korean else "Browse design criteria by bundle, document, and section.")
        + '</p><ul class="project-index-list">'
        + "".join(overview_rows)
        + "</ul>"
    )
    return tuple(bundle_nodes), tuple(details), overview


def render_project_workspace(
    ir: SemanticIR,
    plan: PresentationPlan,
    context: ViewContext,
    review_id: str,
    source_panels: Mapping[str, str],
) -> str:
    """Render the Project Handbook as a semantic tree and addressable details."""

    korean = context.locale == "ko"
    components = {component.component: component for component in plan.components}
    rendered_entities: set[str] = set()
    coverage_targets = _coverage_targets(ir)

    overview_component = components.get("project-overview")
    overview_markup = _project_overview(ir, overview_component.refs if overview_component else ())
    structure_component = components.get("structure-responsibility")
    structure_nodes, structure_details, structure_overview = _project_structure_parts(
        ir,
        structure_component.refs if structure_component else (),
        korean=korean,
    )
    spec_component = components.get("spec-index")
    spec_nodes, spec_details, spec_overview = _project_spec_parts(
        ir,
        spec_component.refs if spec_component else (),
        review_id,
        rendered_entities,
        coverage_targets,
        korean=korean,
    )
    evidence_component = components.get("developer-information")
    source_detail = _details(
        ir,
        evidence_component.refs if evidence_component else (),
        review_id,
        rendered_entities,
        coverage_targets,
    )

    overview_route = "project-overview"
    specs_route = "project-design-criteria"
    structure_route = "project-structure"
    overview_evidence_route = "project-overview-evidence"
    specs_evidence_route = "project-design-evidence"
    structure_evidence_route = "project-structure-evidence"
    source_label = _project_term("Developer information", korean)
    roots = (
        ProjectNavNode(
            overview_route,
            "project-overview",
            "개요" if korean else "Overview",
            (ProjectNavNode(overview_evidence_route, "source-evidence", source_label),),
        ),
        ProjectNavNode(
            specs_route,
            "design-criteria",
            "설계 기준" if korean else "Design criteria",
            (*spec_nodes, ProjectNavNode(specs_evidence_route, "source-evidence", source_label)),
        ),
        ProjectNavNode(
            structure_route,
            "project-structure",
            "프로젝트 구조" if korean else "Project structure",
            (*structure_nodes, ProjectNavNode(structure_evidence_route, "source-evidence", source_label)),
        ),
    )
    tree = "".join(
        _project_tree_node(node, level=1, korean=korean, root=True, first=index == 0)
        for index, node in enumerate(roots)
    )
    details = [
        _project_detail(overview_route, "project-overview", roots[0].label, overview_markup, active=True),
        _project_detail(
            overview_evidence_route,
            "source-evidence",
            source_label,
            source_panels.get("overview", "")
            + ('<details class="project-evidence"><summary>' + ("원문 근거" if korean else "Source details") + "</summary>" + source_detail + "</details>" if source_detail else ""),
        ),
        _project_detail(specs_route, "design-criteria", roots[1].label, spec_overview),
        *spec_details,
        _project_detail(specs_evidence_route, "source-evidence", source_label, source_panels.get("specs", "")),
        _project_detail(structure_route, "project-structure", roots[2].label, structure_overview),
        *structure_details,
        _project_detail(structure_evidence_route, "source-evidence", source_label, source_panels.get("structure", "")),
    ]
    return (
        '<div class="project-workspace" data-project-workspace data-default-route="project-overview" data-component="project-workspace">'
        '<aside class="project-master">'
        '<div class="project-master-header"><p class="project-master-title">'
        + ("프로젝트 목차" if korean else "Project contents")
        + "</p>"
        '<label class="project-search-label" for="project-search">'
        + ("목차 검색" if korean else "Search contents")
        + '</label><input id="project-search" class="project-search" type="search" data-workspace-search '
        + ('placeholder="설계 기준, 문서, 경로 검색"' if korean else 'placeholder="Search criteria, documents, or paths"')
        + ' autocomplete="off"><p class="project-search-empty" role="status" hidden>'
        + ("검색 결과가 없습니다." if korean else "No matching contents.")
        + "</p></div>"
        '<nav class="project-tree-navigation" aria-label="'
        + ("프로젝트 목차" if korean else "Project contents")
        + '"><div role="tree">'
        + tree
        + "</div></nav></aside>"
        '<section class="project-detail-pane" aria-live="polite">'
        '<button class="project-back" type="button">'
        + ("목록으로" if korean else "Back to contents")
        + "</button>"
        + "".join(details)
        + "</section></div>"
    )


def render_spec_workspace(
    ir: SemanticIR,
    plan: PresentationPlan,
    context: ViewContext,
    review_id: str,
    source_panel: str,
) -> str:
    """Render a system Spec as overview plus member/section master-detail navigation."""

    korean = context.locale == "ko"
    components = {component.component: component for component in plan.components}
    rendered_entities: set[str] = set()
    coverage_targets = _coverage_targets(ir)
    navigator = components.get("spec-navigator")
    spec_nodes, spec_details, spec_overview = _project_spec_parts(
        ir,
        navigator.refs if navigator else (),
        review_id,
        rendered_entities,
        coverage_targets,
        korean=korean,
        roles=frozenset(("primary_spec",)),
    )

    overview_component = components.get("system-overview")
    responsibility = components.get("runtime-responsibility")
    interfaces = components.get("interface-table")
    coverage = components.get("acceptance-coverage")
    overview_markup = _system_overview(ir, korean=korean)
    if overview_component is not None:
        overview_markup += _semantic_table(
            ir,
            responsibility.refs if responsibility else (),
            css_class="responsibility-table",
            korean=korean,
        )
        overview_markup += _semantic_table(
            ir,
            interfaces.refs if interfaces else (),
            css_class="interface-table",
            korean=korean,
        )
        overview_markup += _acceptance_coverage(
            ir,
            coverage.refs if coverage else (),
            review_id,
            rendered_entities,
            coverage_targets,
            korean=korean,
            summary_only=True,
        )

    overview_route = "spec-overview"
    criteria_route = "spec-criteria"
    source_route = "spec-source"
    roots = (
        ProjectNavNode(overview_route, "system-overview", "시스템 개요" if korean else "System overview"),
        ProjectNavNode(
            criteria_route,
            "design-criteria",
            "설계 기준" if korean else "Design criteria",
            spec_nodes,
        ),
        ProjectNavNode(source_route, "source-evidence", "출처·검증" if korean else "Source & verification"),
    )
    tree = "".join(
        _project_tree_node(node, level=1, korean=korean, root=True, first=index == 0)
        for index, node in enumerate(roots)
    )
    details = [
        _project_detail(overview_route, "system-overview", roots[0].label, overview_markup, active=True),
        _project_detail(criteria_route, "design-criteria", roots[1].label, spec_overview),
        *spec_details,
        _project_detail(source_route, "source-evidence", roots[2].label, source_panel),
    ]
    return (
        '<div class="project-workspace spec-workspace" data-project-workspace data-spec-workspace '
        'data-default-route="spec-overview" data-component="spec-workspace">'
        '<aside class="project-master"><div class="project-master-header">'
        '<p class="project-master-title">'
        + ("설계 기준 목차" if korean else "Spec contents")
        + '</p><label class="project-search-label" for="spec-search">'
        + ("목차 검색" if korean else "Search contents")
        + '</label><input id="spec-search" class="project-search" type="search" data-workspace-search '
        + ('placeholder="문서, 섹션, 필수 사항 검색"' if korean else 'placeholder="Search documents, sections, or requirements"')
        + ' autocomplete="off"><p class="project-search-empty" role="status" hidden>'
        + ("검색 결과가 없습니다." if korean else "No matching contents.")
        + '</p></div><nav class="project-tree-navigation" aria-label="'
        + ("설계 기준 목차" if korean else "Spec contents")
        + '"><div role="tree">'
        + tree
        + '</div></nav></aside><section class="project-detail-pane" aria-live="polite">'
        '<button class="project-back" type="button">'
        + ("목록으로" if korean else "Back to contents")
        + "</button>"
        + "".join(details)
        + "</section></div>"
    )


def _project_structure(ir: SemanticIR, refs: tuple[str, ...]) -> str:
    _, details, overview = _project_structure_parts(ir, refs, korean=False)
    return overview + "".join(details)


def _project_specs(
    ir: SemanticIR,
    refs: tuple[str, ...],
    review_id: str,
    rendered_entities: set[str],
    coverage_targets: Mapping[str, tuple[SemanticEntity, ...]],
) -> str:
    _, details, overview = _project_spec_parts(
        ir,
        refs,
        review_id,
        rendered_entities,
        coverage_targets,
        korean=False,
    )
    return overview + "".join(details)


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
        elif component.component == "system-overview":
            markup = _system_overview(ir, korean=korean)
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
        elif component.component == "runtime-responsibility":
            markup = _semantic_table(
                ir,
                component.refs,
                css_class="responsibility-table",
                korean=korean,
            )
        elif component.component == "interface-table":
            markup = _semantic_table(
                ir,
                component.refs,
                css_class="interface-table",
                korean=korean,
            )
        elif component.component == "acceptance-coverage":
            markup = _acceptance_coverage(
                ir,
                component.refs,
                review_id,
                rendered_entities,
                coverage_targets,
                korean=korean,
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
