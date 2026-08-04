"""Lossless semantic intermediate representation for requested Review Viewers."""

from __future__ import annotations

from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Mapping

from review_sources import PlanAuxiliaryDocument, PlanDocument, ReviewBundle, ReviewSource
from spec_model import SpecDocument


_HEADING_RE = re.compile(r"^(#{1,6}) (\S.*)$")
_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)$")
_LIST_RE = re.compile(r"^\s*(?:[-*+] |[0-9]+\. )")
_GENERIC_RE = re.compile(r"^\s*(?:<[^>]+>|>|-{3,}\s*$|_{3,}\s*$|\*{3,}\s*$)")
_TASK_RE = re.compile(r"^### Task ([0-9]+): (.+?)(?: \(([^()]*)\))?$")
_STEP_RE = re.compile(r"^- \[([ xX])\] \*\*Step ([0-9]+): (.+)\*\*$")


@dataclass(frozen=True)
class SemanticBlock:
    key: str
    source_namespace: str
    source_path: str
    kind: str
    heading: str
    body: str
    line: int
    end_line: int


@dataclass(frozen=True)
class SemanticEntity:
    key: str
    source_namespace: str
    entity_type: str
    entity_id: str
    block_key: str
    attributes: Mapping[str, object]


@dataclass(frozen=True)
class SemanticRelation:
    key: str
    relation_type: str
    from_entity: str
    to_entity: str
    source_namespace: str
    line: int


@dataclass(frozen=True)
class SemanticDocument:
    namespace: str
    role: str
    path: str
    metadata: Mapping[str, object]
    outline: tuple[str, ...]
    blocks: tuple[SemanticBlock, ...]
    entities: tuple[SemanticEntity, ...]


@dataclass(frozen=True)
class ContentCoverage:
    total_blocks: int
    represented_blocks: int


@dataclass(frozen=True)
class SemanticIR:
    mode: str
    documents: tuple[SemanticDocument, ...]
    relations: tuple[SemanticRelation, ...]
    coverage: ContentCoverage


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "document"


def _frontmatter_end(lines: list[str]) -> int:
    if not lines or lines[0] != "---":
        return 0
    try:
        return lines.index("---", 1) + 1
    except ValueError:
        return 0


def _fence_close(line: str, marker: str) -> bool:
    return re.fullmatch(
        rf" {{0,3}}{re.escape(marker[0])}{{{len(marker)},}}[ \t]*", line
    ) is not None


def _starts_structural_block(line: str) -> bool:
    return bool(
        _HEADING_RE.fullmatch(line)
        or _FENCE_RE.fullmatch(line)
        or line.lstrip().startswith("|")
        or _LIST_RE.match(line)
        or _GENERIC_RE.match(line)
    )


def _source_blocks(source: ReviewSource) -> tuple[tuple[str, ...], tuple[SemanticBlock, ...]]:
    lines = source.text.splitlines()
    outline: list[str] = []
    blocks: list[SemanticBlock] = []
    counters: dict[str, int] = {}
    section = "Document"
    index = _frontmatter_end(lines)

    def append(kind: str, start: int, end: int, body: str) -> None:
        section_slug = _slug(section)
        offset = counters.get(section_slug, 0)
        counters[section_slug] = offset + 1
        blocks.append(
            SemanticBlock(
                key=f"{source.namespace}:{section_slug}:{offset}",
                source_namespace=source.namespace,
                source_path=source.path,
                kind=kind,
                heading=section,
                body=body,
                line=start + 1,
                end_line=end,
            )
        )

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if heading := _HEADING_RE.fullmatch(line):
            level, title = heading.groups()
            outline.append(title)
            if len(level) == 2:
                section = title
            index += 1
            continue
        if fence := _FENCE_RE.fullmatch(line):
            marker, raw_info = fence.groups()
            start = index
            index += 1
            content: list[str] = []
            while index < len(lines) and not _fence_close(lines[index], marker):
                content.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            info = raw_info.strip().split(maxsplit=1)[0] if raw_info.strip() else ""
            append("mermaid" if info == "mermaid" else "code", start, index, "\n".join(content))
            continue
        if line.lstrip().startswith("|"):
            start = index
            while index < len(lines) and lines[index].lstrip().startswith("|"):
                index += 1
            append("table", start, index, "\n".join(lines[start:index]))
            continue
        if _LIST_RE.match(line):
            start = index
            index += 1
            while index < len(lines) and lines[index].strip() and not _starts_structural_block(lines[index]):
                index += 1
            while index < len(lines) and _LIST_RE.match(lines[index]):
                index += 1
            append("list", start, index, "\n".join(lines[start:index]))
            continue
        if _GENERIC_RE.match(line):
            start = index
            index += 1
            while index < len(lines) and lines[index].strip() and not _starts_structural_block(lines[index]):
                index += 1
            append("generic", start, index, "\n".join(lines[start:index]))
            continue

        start = index
        index += 1
        while index < len(lines) and lines[index].strip() and not _starts_structural_block(lines[index]):
            index += 1
        append("prose", start, index, "\n".join(lines[start:index]))
    return tuple(outline), tuple(blocks)


def _metadata(source: ReviewSource) -> Mapping[str, object]:
    document = source.document
    if isinstance(document, SpecDocument):
        metadata: dict[str, object] = {
            "schema": document.metadata.schema,
            "id": document.metadata.id,
            "status": document.metadata.status,
            "language": document.metadata.language,
            "kind": document.metadata.kind,
            "subtype": document.metadata.subtype,
            "areas": document.metadata.areas,
            "components": document.metadata.components,
        }
    elif isinstance(document, PlanDocument):
        metadata = {
            "plan_id": document.plan_id,
            "status": document.status,
            "goal": document.goal,
        }
    elif isinstance(document, PlanAuxiliaryDocument):
        metadata = {"path": document.path}
    else:
        metadata = {}
    return MappingProxyType(metadata)


def _block_at_line(
    blocks: tuple[SemanticBlock, ...], line: int
) -> SemanticBlock | None:
    return next(
        (block for block in blocks if block.line <= line <= block.end_line), None
    )


def _block_at_or_after(
    blocks: tuple[SemanticBlock, ...], line: int
) -> SemanticBlock | None:
    direct = _block_at_line(blocks, line)
    if direct is not None:
        return direct
    return next((block for block in blocks if block.line >= line), None)


def _entity(
    source: ReviewSource,
    entity_type: str,
    entity_id: str,
    block: SemanticBlock,
    attributes: Mapping[str, object],
) -> SemanticEntity:
    return SemanticEntity(
        key=f"{source.namespace}:{entity_type}:{entity_id}",
        source_namespace=source.namespace,
        entity_type=entity_type,
        entity_id=entity_id,
        block_key=block.key,
        attributes=MappingProxyType(dict(attributes)),
    )


def _spec_entities(
    source: ReviewSource,
    document: SpecDocument,
    blocks: tuple[SemanticBlock, ...],
) -> tuple[SemanticEntity, ...]:
    entities: list[SemanticEntity] = []
    for requirement in document.requirements:
        block = _block_at_line(blocks, requirement.line)
        if block is not None:
            entities.append(
                _entity(
                    source,
                    "requirement",
                    requirement.id,
                    block,
                    {
                        "text": requirement.text,
                        "line": requirement.line,
                        "removed": requirement.removed,
                    },
                )
            )
    for criterion in document.acceptance:
        block = _block_at_line(blocks, criterion.line)
        if block is not None:
            entities.append(
                _entity(
                    source,
                    "acceptance",
                    criterion.id,
                    block,
                    {
                        "text": criterion.text,
                        "line": criterion.line,
                        "requirements": criterion.requirements,
                    },
                )
            )
    for offset, mermaid in enumerate(document.mermaid, 1):
        block = _block_at_line(blocks, mermaid.line)
        if block is not None:
            entities.append(
                _entity(
                    source,
                    "mermaid",
                    f"M{offset}",
                    block,
                    {"line": mermaid.line, "section": mermaid.section},
                )
            )

    decision_number = 0
    interface_number = 0
    for block in blocks:
        if block.heading == "Decisions & History":
            for line_offset, line in enumerate(block.body.splitlines()):
                if not line.lstrip().startswith("-"):
                    continue
                decision_number += 1
                entities.append(
                    _entity(
                        source,
                        "decision",
                        f"D{decision_number}",
                        block,
                        {"text": line.lstrip()[1:].strip(), "line": block.line + line_offset},
                    )
                )
        heading = block.heading.lower()
        if any(token in heading for token in ("interface", "endpoint", "schema", "data")):
            interface_number += 1
            entities.append(
                _entity(
                    source,
                    "interface",
                    f"I{interface_number}",
                    block,
                    {"heading": block.heading, "line": block.line},
                )
            )
    return tuple(entities)


def _spec_relations(
    source: ReviewSource,
    document: SpecDocument,
    entities: tuple[SemanticEntity, ...],
) -> tuple[SemanticRelation, ...]:
    by_identity = {
        (entity.entity_type, entity.entity_id): entity for entity in entities
    }
    relations: list[SemanticRelation] = []
    for criterion in document.acceptance:
        acceptance = by_identity.get(("acceptance", criterion.id))
        if acceptance is None:
            continue
        for requirement_id in criterion.requirements:
            requirement = by_identity.get(("requirement", requirement_id))
            if requirement is None:
                continue
            relations.append(
                SemanticRelation(
                    key=f"{source.namespace}:covers:{criterion.id}:{requirement_id}",
                    relation_type="covers",
                    from_entity=acceptance.key,
                    to_entity=requirement.key,
                    source_namespace=source.namespace,
                    line=criterion.line,
                )
            )
    return tuple(relations)


def _plan_entities(
    source: ReviewSource, blocks: tuple[SemanticBlock, ...]
) -> tuple[SemanticEntity, ...]:
    entities: list[SemanticEntity] = []
    current_task = ""
    mermaid_number = 0
    for line_number, line in enumerate(source.text.splitlines(), 1):
        if task_match := _TASK_RE.fullmatch(line):
            number, title, _ = task_match.groups()
            current_task = f"Task{int(number)}"
            block = _block_at_or_after(blocks, line_number)
            if block is not None:
                entities.append(
                    _entity(
                        source,
                        "task",
                        current_task,
                        block,
                        {"title": title, "line": line_number},
                    )
                )
            continue
        if step_match := _STEP_RE.fullmatch(line):
            checked, number, text = step_match.groups()
            if not current_task:
                continue
            block = _block_at_line(blocks, line_number)
            if block is not None:
                entities.append(
                    _entity(
                        source,
                        "step",
                        f"{current_task}-Step{int(number)}",
                        block,
                        {
                            "task_id": current_task,
                            "text": text,
                            "checked": checked.lower() == "x",
                            "line": line_number,
                        },
                    )
                )
    document = source.document
    if isinstance(document, (PlanDocument, PlanAuxiliaryDocument)):
        for mermaid in document.mermaid:
            mermaid_number += 1
            block = _block_at_line(blocks, mermaid.line)
            if block is not None:
                entities.append(
                    _entity(
                        source,
                        "mermaid",
                        f"M{mermaid_number}",
                        block,
                        {"line": mermaid.line, "section": mermaid.section},
                    )
                )
    return tuple(entities)


def _plan_relations(
    bundle: ReviewBundle, documents: tuple[SemanticDocument, ...]
) -> tuple[SemanticRelation, ...]:
    primary_plan = next(
        (
            source.document
            for source in bundle.primary
            if isinstance(source.document, PlanDocument)
        ),
        None,
    )
    if primary_plan is None:
        return ()

    entities = [entity for document in documents for entity in document.entities]
    tasks = {
        entity.entity_id: entity for entity in entities if entity.entity_type == "task"
    }
    targets: dict[tuple[str, str, str], SemanticEntity] = {}
    for document in documents:
        spec_id = document.metadata.get("id")
        if not isinstance(spec_id, str):
            continue
        for entity in document.entities:
            targets[(spec_id, entity.entity_type, entity.entity_id)] = entity

    relations: list[SemanticRelation] = []
    for step in (entity for entity in entities if entity.entity_type == "step"):
        task_id = step.attributes.get("task_id")
        task = tasks.get(task_id) if isinstance(task_id, str) else None
        if task is None:
            continue
        line = step.attributes.get("line")
        relations.append(
            SemanticRelation(
                key=f"{step.source_namespace}:belongs-to:{step.entity_id}:{task.entity_id}",
                relation_type="belongs-to",
                from_entity=step.key,
                to_entity=task.key,
                source_namespace=step.source_namespace,
                line=line if isinstance(line, int) else 1,
            )
        )
    for dependency in primary_plan.dependencies:
        source_task = tasks.get(dependency.from_task)
        target_task = tasks.get(dependency.to_task)
        if source_task is None or target_task is None:
            continue
        line = target_task.attributes.get("line")
        relations.append(
            SemanticRelation(
                key=f"{target_task.source_namespace}:depends-on:{dependency.from_task}:{dependency.to_task}",
                relation_type="depends-on",
                from_entity=target_task.key,
                to_entity=source_task.key,
                source_namespace=target_task.source_namespace,
                line=line if isinstance(line, int) else 1,
            )
        )
    for plan_task in primary_plan.tasks:
        task = tasks.get(plan_task.id)
        if task is None:
            continue
        line = task.attributes.get("line")
        references = (
            (("requirement", item) for item in plan_task.requirements),
            (("acceptance", item) for item in plan_task.acceptance),
        )
        for group in references:
            for entity_type, reference in group:
                target = targets.get((reference.spec_id, entity_type, reference.item_id))
                if target is None:
                    continue
                relations.append(
                    SemanticRelation(
                        key=f"{task.source_namespace}:traces:{task.entity_id}:{reference.spec_id}:{reference.item_id}",
                        relation_type="traces",
                        from_entity=task.key,
                        to_entity=target.key,
                        source_namespace=task.source_namespace,
                        line=line if isinstance(line, int) else 1,
                    )
                )
    return tuple(relations)


def build_semantic_ir(bundle: ReviewBundle) -> SemanticIR:
    documents: list[SemanticDocument] = []
    relations: list[SemanticRelation] = []
    for source in (*bundle.primary, *bundle.comparison, *bundle.context):
        outline, blocks = _source_blocks(source)
        if isinstance(source.document, SpecDocument):
            entities = _spec_entities(source, source.document, blocks)
        elif isinstance(source.document, (PlanDocument, PlanAuxiliaryDocument)):
            entities = _plan_entities(source, blocks)
        else:
            entities = ()
        if isinstance(source.document, SpecDocument):
            relations.extend(_spec_relations(source, source.document, entities))
        documents.append(
            SemanticDocument(
                namespace=source.namespace,
                role=source.role,
                path=source.path,
                metadata=_metadata(source),
                outline=outline,
                blocks=blocks,
                entities=entities,
            )
        )
    if bundle.mode == "plan":
        relations.extend(_plan_relations(bundle, tuple(documents)))
    total = sum(len(document.blocks) for document in documents)
    return SemanticIR(
        mode=bundle.mode,
        documents=tuple(documents),
        relations=tuple(relations),
        coverage=ContentCoverage(total, total),
    )
