"""Lossless semantic intermediate representation for requested Visual Docs."""

from __future__ import annotations

from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Mapping

from project_map import ProjectMap
from review_sources import (
    BriefDocument,
    PlanAuxiliaryDocument,
    PlanDocument,
    RepositoryEvidence,
    ReviewBundle,
    ReviewSource,
)
from spec_model import SpecMember, statement_anchor


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
    heading_path: tuple[str, ...]
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

    @property
    def ratio(self) -> float:
        return 1.0 if self.total_blocks == 0 else self.represented_blocks / self.total_blocks


@dataclass(frozen=True)
class SemanticIR:
    kind: str
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
    heading_stack: list[tuple[int, str]] = []
    index = _frontmatter_end(lines)

    def append(
        kind: str,
        start: int,
        end: int,
        body: str,
        heading: str | None = None,
    ) -> None:
        block_heading = heading or (heading_stack[-1][1] if heading_stack else section)
        block_heading_path = tuple(title for _, title in heading_stack) or (
            block_heading,
        )
        section_slug = _slug(block_heading)
        offset = counters.get(section_slug, 0)
        counters[section_slug] = offset + 1
        blocks.append(
            SemanticBlock(
                key=f"{source.namespace}:{section_slug}:{offset}",
                source_namespace=source.namespace,
                source_path=source.path,
                kind=kind,
                heading=block_heading,
                heading_path=block_heading_path,
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
            heading_level = len(level)
            outline.append(title)
            if heading_level == 1:
                heading_stack.clear()
            else:
                while heading_stack and heading_stack[-1][0] >= heading_level:
                    heading_stack.pop()
                heading_stack.append((heading_level, title))
            if heading_level == 2:
                section = title
            elif heading_level == 3:
                append("heading", index, index + 1, line, title)
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
    if isinstance(document, SpecMember) and source.spec_bundle is not None:
        bundle = source.spec_bundle
        metadata: dict[str, object] = {
            "schema": bundle.metadata.schema,
            "status": bundle.metadata.status,
            "language": bundle.metadata.language,
            "kind": bundle.metadata.kind,
            "subtype": bundle.metadata.subtype,
            "areas": bundle.metadata.areas,
            "components": bundle.metadata.components,
            "related_specs": tuple(
                {"path": item.path, "relation": item.relation}
                for item in bundle.metadata.related_specs
            ),
            "overview": next(
                (
                    member.sections.get("Overview", "")
                    for member in bundle.members
                    if member.role == "root"
                ),
                "",
            ),
            "bundle_path": bundle.path.as_posix(),
            "bundle_title": bundle.title,
            "bundle_sha256": bundle.bundle_sha256,
            "member_path": document.path.as_posix(),
            "member_title": document.title,
            "member_role": document.role,
        }
    elif isinstance(document, PlanDocument):
        metadata = {
            "plan_id": document.plan_id,
            "status": document.status,
            "goal": document.goal,
        }
    elif isinstance(document, PlanAuxiliaryDocument):
        metadata = {"path": document.path}
    elif isinstance(document, BriefDocument):
        metadata = {
            "title": document.title,
            "goal": document.goal,
            "scope": document.scope,
            "out_of_scope": document.out_of_scope,
            "done_checks": document.done_checks,
        }
    elif isinstance(document, ProjectMap):
        metadata = {
            "title": document.title,
            "overview": document.overview,
            "capabilities": document.capabilities,
            "spec_paths": document.spec_paths,
            "structure": tuple(
                {
                    "path": entry.path,
                    "purpose": entry.purpose,
                    "owns": entry.owns,
                    "entry_points": entry.entry_points,
                    "depends_on": entry.depends_on,
                    "related_specs": entry.related_specs,
                    "governing_statements": tuple(
                        {
                            "heading": reference.heading,
                            "member_path": reference.member_path,
                            "anchor": reference.anchor,
                        }
                        for reference in entry.governing_statements
                    ),
                }
                for entry in document.structure
            ),
        }
    elif isinstance(document, RepositoryEvidence):
        metadata = {"files": document.files, "derived": True}
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
    document: SpecMember,
    blocks: tuple[SemanticBlock, ...],
) -> tuple[SemanticEntity, ...]:
    bundle = source.spec_bundle
    if bundle is None:
        return ()
    entities: list[SemanticEntity] = []
    for statement in bundle.statements:
        if statement.member_path != document.path:
            continue
        block = _block_at_line(blocks, statement.line)
        if block is not None:
            entities.append(
                _entity(
                    source,
                    statement.kind,
                    statement.heading,
                    block,
                    {
                        "heading": statement.heading,
                        "anchor": statement_anchor(statement.heading),
                        "line": statement.line,
                        "bundle_path": bundle.path.as_posix(),
                        "bundle_title": bundle.title,
                        "member_path": document.path.as_posix(),
                        "member_title": document.title,
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
                    f"{document.title} diagram at line {mermaid.line}",
                    block,
                    {
                        "line": mermaid.line,
                        "section": mermaid.section,
                        "bundle_path": bundle.path.as_posix(),
                        "member_path": document.path.as_posix(),
                    },
                )
            )

    for block in blocks:
        if block.heading == "Decisions & History":
            for line_offset, line in enumerate(block.body.splitlines()):
                if not line.lstrip().startswith("-"):
                    continue
                decision_text = line.lstrip()[1:].strip()
                entities.append(
                    _entity(
                        source,
                        "decision",
                        decision_text,
                        block,
                        {
                            "text": decision_text,
                            "line": block.line + line_offset,
                            "bundle_path": bundle.path.as_posix(),
                            "member_path": document.path.as_posix(),
                        },
                    )
                )
        heading = block.heading.lower()
        if any(token in heading for token in ("interface", "endpoint", "schema", "data")):
            entities.append(
                _entity(
                    source,
                    "interface",
                    block.heading,
                    block,
                    {
                        "heading": block.heading,
                        "line": block.line,
                        "bundle_path": bundle.path.as_posix(),
                        "member_path": document.path.as_posix(),
                    },
                )
            )
    return tuple(entities)


def _spec_relations(
    sources: tuple[ReviewSource, ...],
    documents: tuple[SemanticDocument, ...],
) -> tuple[SemanticRelation, ...]:
    source_by_namespace = {source.namespace: source for source in sources}
    targets: dict[tuple[str, str, str, str], SemanticEntity] = {}
    for document in documents:
        source = source_by_namespace.get(document.namespace)
        if source is None or source.spec_bundle is None:
            continue
        for entity in document.entities:
            if entity.entity_type not in {"requirement", "acceptance"}:
                continue
            targets[
                (
                    source.spec_bundle.path.as_posix(),
                    source.path,
                    entity.entity_type,
                    entity.entity_id,
                )
            ] = entity

    relations: list[SemanticRelation] = []
    for source in sources:
        bundle = source.spec_bundle
        document = source.document
        if bundle is None or not isinstance(document, SpecMember):
            continue
        for statement in bundle.statements:
            if statement.kind != "acceptance" or statement.member_path != document.path:
                continue
            acceptance = targets.get(
                (
                    bundle.path.as_posix(),
                    statement.member_path.as_posix(),
                    "acceptance",
                    statement.heading,
                )
            )
            if acceptance is None:
                continue
            for reference in statement.references:
                requirement = targets.get(
                    (
                        bundle.path.as_posix(),
                        reference.member_path.as_posix(),
                        "requirement",
                        reference.heading,
                    )
                )
                if requirement is None:
                    continue
                relations.append(
                    SemanticRelation(
                        key=(
                            f"{source.namespace}:covers:{statement.heading}:"
                            f"{reference.member_path.as_posix()}:{reference.heading}"
                        ),
                        relation_type="covers",
                        from_entity=acceptance.key,
                        to_entity=requirement.key,
                        source_namespace=source.namespace,
                        line=statement.line,
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


def _brief_entities(
    source: ReviewSource,
    document: BriefDocument,
    blocks: tuple[SemanticBlock, ...],
) -> tuple[SemanticEntity, ...]:
    entities: list[SemanticEntity] = []
    section_types = {
        "Goal": "brief-goal",
        "Scope": "brief-scope",
        "Out of Scope": "brief-out-of-scope",
        "Done Checks": "brief-done-check",
    }
    for block in blocks:
        entity_type = section_types.get(block.heading)
        if entity_type is not None:
            entities.append(
                _entity(
                    source,
                    entity_type,
                    block.heading,
                    block,
                    {"heading": block.heading},
                )
            )
    return tuple(entities)


def _project_entities(
    source: ReviewSource,
    document: ProjectMap,
    blocks: tuple[SemanticBlock, ...],
) -> tuple[SemanticEntity, ...]:
    entities: list[SemanticEntity] = []
    overview = next(
        (block for block in blocks if block.heading == "Project Overview"), None
    )
    if overview is not None:
        entities.append(
            _entity(
                source,
                "project-overview",
                document.title,
                overview,
                {
                    "title": document.title,
                    "overview": document.overview,
                    "capabilities": document.capabilities,
                },
            )
        )
    capabilities = next(
        (block for block in blocks if block.heading == "Key Capabilities"), None
    )
    if capabilities is not None:
        entities.append(
            _entity(
                source,
                "project-capabilities",
                "Key Capabilities",
                capabilities,
                {"capabilities": document.capabilities},
            )
        )
    for entry in document.structure:
        block = next(
            (item for item in blocks if item.heading.rstrip("/") == entry.path),
            None,
        )
        if block is None:
            continue
        entities.append(
            _entity(
                source,
                "project-structure",
                entry.path,
                block,
                {
                    "path": entry.path,
                    "purpose": entry.purpose,
                    "owns": entry.owns,
                    "entry_points": entry.entry_points,
                    "depends_on": entry.depends_on,
                    "related_specs": entry.related_specs,
                    "governing_statements": tuple(
                        {
                            "heading": reference.heading,
                            "member_path": reference.member_path,
                            "anchor": reference.anchor,
                        }
                        for reference in entry.governing_statements
                    ),
                },
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
    targets: dict[tuple[str, str, str, str], SemanticEntity] = {}
    for document in documents:
        bundle_path = document.metadata.get("bundle_path")
        member_path = document.metadata.get("member_path")
        if not isinstance(bundle_path, str) or not isinstance(member_path, str):
            continue
        for entity in document.entities:
            if entity.entity_type in {"requirement", "acceptance"}:
                targets[
                    (bundle_path, member_path, entity.entity_type, entity.entity_id)
                ] = entity

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
        for reference in plan_task.governing_statements:
            target = targets.get(
                (
                    reference.bundle_path.as_posix(),
                    reference.member_path.as_posix(),
                    reference.kind,
                    reference.heading,
                )
            )
            if target is None:
                continue
            relations.append(
                SemanticRelation(
                    key=(
                        f"{task.source_namespace}:traces:{task.entity_id}:"
                        f"{reference.bundle_path.as_posix()}:"
                        f"{reference.member_path.as_posix()}:"
                        f"{reference.kind}:{reference.heading}"
                    ),
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
    sources = bundle.sources
    for source in sources:
        outline, blocks = _source_blocks(source)
        if isinstance(source.document, SpecMember):
            entities = _spec_entities(source, source.document, blocks)
        elif isinstance(source.document, (PlanDocument, PlanAuxiliaryDocument)):
            entities = _plan_entities(source, blocks)
        elif isinstance(source.document, BriefDocument):
            entities = _brief_entities(source, source.document, blocks)
        elif isinstance(source.document, ProjectMap):
            entities = _project_entities(source, source.document, blocks)
        else:
            entities = ()
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
    semantic_documents = tuple(documents)
    relations = list(_spec_relations(sources, semantic_documents))
    if bundle.kind == "plan":
        relations.extend(_plan_relations(bundle, semantic_documents))
    total = sum(len(document.blocks) for document in documents)
    return SemanticIR(
        kind=bundle.kind,
        documents=semantic_documents,
        relations=tuple(relations),
        coverage=ContentCoverage(total, total),
    )
