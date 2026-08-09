"""Typed source model for requested Forge Visual Docs."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import sys
from types import MappingProxyType
from typing import Mapping, Sequence

from project_map import ProjectMap, load_project_map


def _load_shared_parser() -> None:
    scripts = Path(__file__).resolve().parents[1].parent / "writing-specs" / "scripts"
    if not (scripts / "spec_model.py").is_file() or not (scripts / "spec_validate.py").is_file():
        raise RuntimeError(f"writing-specs sibling parser not found: {scripts}")
    value = str(scripts)
    if value not in sys.path:
        sys.path.insert(0, value)


_load_shared_parser()

from spec_model import (  # noqa: E402
    MermaidBlock,
    SpecBundle,
    SpecMember,
    load_spec_bundle,
    statement_anchor,
)
from spec_validate import (  # noqa: E402
    PlanBundleRef,
    PlanStatementRef,
    parse_plan_governing_statements,
    parse_plan_related_specs,
)


_REVIEW_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_H1_RE = re.compile(r"^# (\S.*)$")
_H2_RE = re.compile(r"^## (\S.*)$")
_GOAL_RE = re.compile(r"^\*\*(?:Goal|목표):\*\*[ \t]+(\S.*)$")
_TASK_RE = re.compile(r"^### Task ([0-9]+): (.+?)(?: \(([^()]*)\))?$")
_STEP_RE = re.compile(r"^- \[([ xX])\] \*\*Step ([0-9]+): (.+)\*\*$")
_ROUTE_RE = re.compile(r"^- Route: ([a-z0-9][a-z0-9-]{0,63})$")
_DEPENDENCY_RE = re.compile(r"^- (?:Dependencies|의존성): (\S.*)$")


@dataclass(frozen=True)
class PlanStep:
    id: str
    text: str
    checked: bool


@dataclass(frozen=True)
class PlanTask:
    id: str
    title: str
    route: str | None
    governing_statements: tuple[PlanStatementRef, ...]
    steps: tuple[PlanStep, ...]


@dataclass(frozen=True)
class PlanRoute:
    id: str
    title: str
    dependencies: tuple[str, ...]
    task_ids: tuple[str, ...]


@dataclass(frozen=True)
class PlanDependency:
    from_task: str
    to_task: str
    reason: str


@dataclass(frozen=True)
class VerificationEvidence:
    id: str
    task_ids: tuple[str, ...]
    governing_statements: tuple[PlanStatementRef, ...]
    command: str
    expected: str


@dataclass(frozen=True)
class PlanAuxiliaryDocument:
    path: str
    mermaid: tuple[MermaidBlock, ...]


@dataclass(frozen=True)
class PlanDocument:
    path: str
    plan_id: str
    title: str
    status: str
    goal: str
    sections: Mapping[str, str]
    related_specs: tuple[PlanBundleRef, ...]
    routes: tuple[PlanRoute, ...]
    tasks: tuple[PlanTask, ...]
    dependencies: tuple[PlanDependency, ...]
    checkpoints: tuple[str, ...]
    verification: tuple[VerificationEvidence, ...]
    progress_path: str | None
    task_paths: tuple[str, ...]
    mermaid: tuple[MermaidBlock, ...]


@dataclass(frozen=True)
class BriefDocument:
    path: str
    title: str
    goal: str
    scope: tuple[str, ...]
    out_of_scope: tuple[str, ...]
    done_checks: tuple[str, ...]
    mermaid: tuple[MermaidBlock, ...]


@dataclass(frozen=True)
class RepositoryEvidence:
    files: tuple[str, ...]
    text: str
    mermaid: tuple[MermaidBlock, ...] = ()


@dataclass(frozen=True)
class ReviewSource:
    role: str
    path: str
    namespace: str
    sha256: str
    text: str
    source_bytes: bytes = b""
    title: str = ""
    bundle_path: str = ""
    bundle_title: str = ""
    bundle_sha256: str = ""
    member_title: str = ""
    member_role: str = ""
    status: str = ""
    document: (
        SpecMember
        | PlanDocument
        | PlanAuxiliaryDocument
        | BriefDocument
        | ProjectMap
        | RepositoryEvidence
        | None
    ) = None
    spec_bundle: SpecBundle | None = None


@dataclass(frozen=True)
class ReviewBundle:
    kind: str
    primary: tuple[ReviewSource, ...]
    comparison: tuple[ReviewSource, ...]
    context: tuple[ReviewSource, ...]
    counts: Mapping[str, object]

    @property
    def sources(self) -> tuple[ReviewSource, ...]:
        return (*self.primary, *self.comparison, *self.context)

    @property
    def mermaid(self) -> tuple[MermaidBlock, ...]:
        return tuple(
            block
            for source in (*self.primary, *self.comparison, *self.context)
            if source.document is not None
            for block in getattr(source.document, "mermaid", ())
        )


def repository_relative(path: Path, repo_root: Path) -> Path:
    """Return a resolved repository-relative path or reject an escape."""

    repository = repo_root.resolve()
    supplied = path.resolve() if path.is_absolute() else (repository / path).resolve()
    try:
        return supplied.relative_to(repository)
    except ValueError as error:
        raise ValueError(f"path must remain inside repository: {path}") from error


def validate_view_id(value: str) -> str:
    if _REVIEW_ID_RE.fullmatch(value) is None:
        raise ValueError(
            "view-id must start with a lowercase letter or digit and contain at most 64 lowercase letters, digits, or hyphens"
        )
    return value


def validate_review_id(value: str) -> str:
    """Internal compatibility shim; the public CLI only exposes view-id."""

    return validate_view_id(value)


def _read_source(path: Path, repo_root: Path) -> tuple[Path, str, str]:
    relative = repository_relative(path, repo_root)
    source = (repo_root.resolve() / relative).read_bytes()
    try:
        text = source.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"source must be readable UTF-8: {relative.as_posix()}") from error
    return relative, text, hashlib.sha256(source).hexdigest()


def _load_structured_bundle(path: Path, repo_root: Path) -> SpecBundle:
    relative = repository_relative(path, repo_root)
    bundle, diagnostics = load_spec_bundle(
        repo_root.resolve() / relative,
        repo_root.resolve(),
    )
    if bundle is None or diagnostics:
        detail = "; ".join(
            f"{item.path}:{item.line}: {item.code} {item.message}" for item in diagnostics
        )
        raise ValueError(f"invalid structured Spec Bundle: {detail}")
    return bundle


def _spec_counts(bundle: SpecBundle) -> dict[str, int]:
    return {
        "requirement": sum(item.kind == "requirement" for item in bundle.statements),
        "acceptance": sum(item.kind == "acceptance" for item in bundle.statements),
        "mermaid": sum(len(member.mermaid) for member in bundle.members),
    }


def _bundle_member_sources(
    bundle: SpecBundle,
    role: str,
    group: str,
) -> tuple[ReviewSource, ...]:
    return tuple(
        ReviewSource(
            role=role,
            path=member.path.as_posix(),
            namespace=(
                f"{group}--{bundle.path.as_posix()}--"
                f"{member.path.relative_to(bundle.path).as_posix()}"
            ),
            sha256=member.source_sha256,
            text=member.source_text,
            source_bytes=member.source_bytes,
            title=member.title,
            bundle_path=bundle.path.as_posix(),
            bundle_title=bundle.title,
            bundle_sha256=bundle.bundle_sha256,
            member_title=member.title,
            member_role=member.role,
            status=bundle.metadata.status,
            document=member,
            spec_bundle=bundle,
        )
        for member in bundle.members
    )


def collect_spec_sources(
    primary: Path, comparisons: Sequence[Path], repo_root: Path
) -> ReviewBundle:
    primary_bundle = _load_structured_bundle(primary, repo_root)
    primary_sources = _bundle_member_sources(primary_bundle, "primary_spec", "primary")
    comparison_sources: list[ReviewSource] = []
    comparison_counts: dict[str, object] = {}
    seen_paths = {primary_bundle.path}
    for index, comparison in enumerate(comparisons, 1):
        comparison_bundle = _load_structured_bundle(comparison, repo_root)
        if comparison_bundle.path in seen_paths:
            raise ValueError(
                f"comparison Spec Bundle is duplicated: {comparison_bundle.path.as_posix()}"
            )
        seen_paths.add(comparison_bundle.path)
        sources = _bundle_member_sources(
            comparison_bundle,
            "comparison_spec",
            f"comparison-{index}",
        )
        comparison_sources.extend(sources)
        comparison_counts[comparison_bundle.path.as_posix()] = _spec_counts(
            comparison_bundle
        )
    counts: Mapping[str, object] = MappingProxyType(
        {
            "primary": MappingProxyType(_spec_counts(primary_bundle)),
            "comparison": MappingProxyType(comparison_counts),
            "context": MappingProxyType({}),
        }
    )
    return ReviewBundle("spec", primary_sources, tuple(comparison_sources), (), counts)


def _required_brief_section(
    sections: Mapping[str, str], name: str, source: str
) -> str:
    value = sections.get(name, "").strip()
    if not value:
        raise ValueError(f"{source}: Brief requires a non-empty {name} section")
    return value


def _markdown_items(value: str, name: str, source: str) -> tuple[str, ...]:
    items = tuple(
        line[2:].strip()
        for line in value.splitlines()
        if line.startswith("- ") and line[2:].strip()
    )
    if not items:
        raise ValueError(f"{source}: Brief {name} requires at least one list item")
    return items


def collect_brief_sources(brief: Path, repo_root: Path) -> ReviewBundle:
    relative, text, digest = _read_source(brief, repo_root)
    lines = text.splitlines()
    title_matches = [
        match.group(1)
        for _, line in _outside_fences(lines)
        if (match := _H1_RE.fullmatch(line))
    ]
    if len(title_matches) != 1:
        raise ValueError(f"{relative.as_posix()}: Brief requires exactly one H1 title")
    sections = _sections(lines)
    source = relative.as_posix()
    goal = _required_brief_section(sections, "Goal", source)
    scope = _markdown_items(
        _required_brief_section(sections, "Scope", source), "Scope", source
    )
    out_of_scope = _markdown_items(
        _required_brief_section(sections, "Out of Scope", source),
        "Out of Scope",
        source,
    )
    done_checks = _markdown_items(
        _required_brief_section(sections, "Done Checks", source),
        "Done Checks",
        source,
    )
    document = BriefDocument(
        source,
        title_matches[0],
        goal,
        scope,
        out_of_scope,
        done_checks,
        _mermaid_blocks(text),
    )
    record = ReviewSource(
        "brief_source",
        source,
        f"brief--{relative.parent.name}",
        digest,
        text,
        source_bytes=text.encode("utf-8"),
        title=document.title,
        document=document,
    )
    counts: Mapping[str, object] = MappingProxyType(
        {
            "primary": MappingProxyType(
                {
                    "scope": len(scope),
                    "out_of_scope": len(out_of_scope),
                    "done_check": len(done_checks),
                    "mermaid": len(document.mermaid),
                }
            ),
            "comparison": MappingProxyType({}),
            "context": MappingProxyType({}),
        }
    )
    return ReviewBundle("brief", (record,), (), (), counts)


def _repository_files(project: ProjectMap, repo_root: Path) -> tuple[Path, ...]:
    root = repo_root.resolve()
    files: dict[str, Path] = {}
    for entry in project.structure:
        selected = root / entry.path
        candidates = (
            (selected,)
            if selected.is_file()
            else tuple(path for path in selected.rglob("*") if path.is_file())
        )
        for path in candidates:
            relative = path.resolve().relative_to(root).as_posix()
            if ".git" not in Path(relative).parts:
                files[relative] = path
    return tuple(files[key] for key in sorted(files))


def collect_project_sources(project_map: Path, repo_root: Path) -> ReviewBundle:
    project = load_project_map(project_map, repo_root)
    relative, text, digest = _read_source(project_map, repo_root)
    primary = ReviewSource(
        "project_map",
        relative.as_posix(),
        "project-map",
        digest,
        text,
        source_bytes=text.encode("utf-8"),
        title=project.title,
        document=project,
    )

    context: list[ReviewSource] = []
    context_counts: dict[str, object] = {}
    declared_bundles: list[SpecBundle] = []
    for spec_path in project.spec_paths:
        spec_bundle = _load_structured_bundle(repo_root.resolve() / spec_path, repo_root)
        if spec_bundle.metadata.status not in {"approved", "implemented"}:
            raise ValueError(
                f"{project.path}: declared Spec Bundle must be approved or implemented: "
                f"{spec_path} ({spec_bundle.metadata.status})"
            )
        context.extend(
            _bundle_member_sources(spec_bundle, "declared_spec", "project-spec")
        )
        declared_bundles.append(spec_bundle)
        context_counts[spec_bundle.path.as_posix()] = _spec_counts(spec_bundle)

    statements = {
        (
            statement.member_path.as_posix(),
            statement.heading,
            statement_anchor(statement.heading),
        )
        for spec_bundle in declared_bundles
        for statement in spec_bundle.statements
    }
    for entry in project.structure:
        for reference in entry.governing_statements:
            identity = (
                reference.member_path,
                reference.heading,
                reference.anchor,
            )
            if identity not in statements:
                raise ValueError(
                    f"{project.path}: Structure {entry.path} Governing Statements "
                    f"link is dangling: {reference.member_path}#{reference.anchor}"
                )

    authoritative_paths = {project.path, *(source.path for source in context)}
    evidence_paths = tuple(
        path
        for path in _repository_files(project, repo_root)
        if path.resolve().relative_to(repo_root.resolve()).as_posix()
        not in authoritative_paths
    )
    evidence_files = tuple(
        path.resolve().relative_to(repo_root.resolve()).as_posix()
        for path in evidence_paths
    )
    evidence_document = RepositoryEvidence(
        evidence_files,
        "\n".join(evidence_files),
    )
    for index, path in enumerate(evidence_paths, 1):
        source_bytes = path.read_bytes()
        relative_path = path.resolve().relative_to(repo_root.resolve()).as_posix()
        context.append(
            ReviewSource(
                "repository_evidence",
                relative_path,
                f"repository-evidence--{index}",
                hashlib.sha256(source_bytes).hexdigest(),
                "",
                source_bytes=source_bytes,
                title=relative_path,
                document=evidence_document,
            )
        )
    counts: Mapping[str, object] = MappingProxyType(
        {
            "primary": MappingProxyType(
                {
                    "capability": len(project.capabilities),
                    "structure": len(project.structure),
                    "declared_spec": len(project.spec_paths),
                }
            ),
            "comparison": MappingProxyType({}),
            "context": MappingProxyType(
                {**context_counts, "repository_evidence": len(evidence_files)}
            ),
        }
    )
    return ReviewBundle("project", (primary,), (), tuple(context), counts)


def _sections(lines: list[str]) -> Mapping[str, str]:
    headings = [
        (index, match.group(1))
        for index, line in _outside_fences(lines)
        if (match := _H2_RE.fullmatch(line))
    ]
    result: dict[str, str] = {}
    for offset, (index, heading) in enumerate(headings):
        end = headings[offset + 1][0] if offset + 1 < len(headings) else len(lines)
        result[heading] = "\n".join(lines[index + 1 : end]).strip("\n")
    return MappingProxyType(result)


def _plan_goal(lines: list[str]) -> str:
    goals = [
        match.group(1)
        for _, line in _outside_fences(lines)
        if (match := _GOAL_RE.fullmatch(line))
    ]
    if len(goals) > 1:
        raise ValueError("plan must contain at most one canonical Goal")
    return goals[0] if goals else ""


_FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)$")


def _fence_open(line: str) -> tuple[str, int, str] | None:
    match = _FENCE_OPEN_RE.fullmatch(line)
    if match is None:
        return None
    marker, raw_info = match.groups()
    if marker[0] == "`" and "`" in raw_info:
        return None
    return marker[0], len(marker), raw_info.strip()


def _fence_close(line: str, fence: tuple[str, int, str]) -> bool:
    character, length, _ = fence
    return (
        re.fullmatch(rf" {{0,3}}{re.escape(character)}{{{length},}}[ \t]*", line)
        is not None
    )


def _mermaid_blocks(text: str) -> tuple[MermaidBlock, ...]:
    lines = text.splitlines()
    result: list[MermaidBlock] = []
    section = ""
    index = 0
    while index < len(lines):
        if match := _H2_RE.fullmatch(lines[index]):
            section = match.group(1)
        fence = _fence_open(lines[index])
        if fence is None:
            index += 1
            continue
        is_mermaid = fence[2] == "mermaid"
        opening_index = index
        content: list[str] = []
        index += 1
        while index < len(lines) and not _fence_close(lines[index], fence):
            if is_mermaid:
                content.append(lines[index])
            index += 1
        if index == len(lines):
            if is_mermaid:
                raise ValueError(
                    f"unclosed Mermaid fence at line {opening_index + 1}"
                )
            break
        if is_mermaid:
            result.append(
                MermaidBlock("\n".join(content), opening_index + 1, section)
            )
        index += 1
    return tuple(result)


def _dependency_ids(raw: str) -> tuple[tuple[str, ...], str]:
    value = raw.strip()
    if value in {"none", "없음"}:
        return (), ""
    dependency_part, separator, reason = value.partition(";")
    result: list[str] = []
    for first_raw, last_raw in re.findall(r"\bTasks ([0-9]+)–([0-9]+)\b", dependency_part):
        first, last = int(first_raw), int(last_raw)
        if first > last:
            raise ValueError(f"descending Task dependency range: Tasks {first}–{last}")
        result.extend(f"Task{number}" for number in range(first, last + 1))
    without_ranges = re.sub(r"\bTasks [0-9]+–[0-9]+\b", "", dependency_part)
    result.extend(f"Task{number}" for number in re.findall(r"\bTask ([0-9]+)\b", without_ranges))
    residual = re.sub(r"\bTask [0-9]+\b", "", without_ranges)
    residual = residual.replace(",", "").strip()
    if residual or not result:
        raise ValueError(f"invalid Task dependency metadata: {raw}")
    return tuple(dict.fromkeys(result)), reason.strip() if separator else ""


def _outside_fences(lines: list[str]) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    fence: tuple[str, int, str] | None = None
    for index, line in enumerate(lines):
        if fence is not None:
            if _fence_close(line, fence):
                fence = None
            continue
        fence = _fence_open(line)
        if fence is not None:
            continue
        result.append((index, line))
    return result


def _inline_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == "`" and value[-1] == "`":
        return value[1:-1]
    return value


@dataclass(frozen=True)
class _ParsedTask:
    task: PlanTask
    dependencies: tuple[str, ...]
    dependency_reason: str
    verification: tuple[VerificationEvidence, ...]


def _parse_tasks(
    text: str,
    governing_statements: tuple[PlanStatementRef, ...] = (),
) -> tuple[_ParsedTask, ...]:
    lines = text.splitlines()
    visible_lines = _outside_fences(lines)
    headings = [
        (index, match)
        for index, line in visible_lines
        if (match := _TASK_RE.fullmatch(line))
    ]
    h2_indices = {
        index for index, line in visible_lines if _H2_RE.fullmatch(line)
    }
    result: list[_ParsedTask] = []
    for offset, (start, match) in enumerate(headings):
        next_task = headings[offset + 1][0] if offset + 1 < len(headings) else len(lines)
        next_h2 = next(
            (index for index in range(start + 1, next_task) if index in h2_indices),
            next_task,
        )
        block = lines[start + 1 : next_h2]
        visible_block = [line for _, line in _outside_fences(block)]
        number, title, trace = match.groups()
        task_id = f"Task{int(number)}"
        if trace:
            raise ValueError(
                f"{task_id} uses an unsupported parenthetical trace; use exact Governing statements links"
            )
        task_governing = tuple(
            reference
            for reference in governing_statements
            if start + 1 <= reference.line <= next_h2
        )

        routes = [
            route.group(1)
            for line in visible_block
            if (route := _ROUTE_RE.fullmatch(line))
        ]
        if len(routes) > 1:
            raise ValueError(f"{task_id} declares Route more than once")
        dependency_values = [
            dependency.group(1)
            for line in visible_block
            if (dependency := _DEPENDENCY_RE.fullmatch(line))
        ]
        if len(dependency_values) > 1:
            raise ValueError(f"{task_id} declares dependencies more than once")
        dependencies, reason = (
            _dependency_ids(dependency_values[0]) if dependency_values else ((), "")
        )

        steps: list[PlanStep] = []
        seen_steps: set[str] = set()
        for line in visible_block:
            if step := _STEP_RE.fullmatch(line):
                checked, step_number, step_text = step.groups()
                step_id = f"{task_id}-Step{int(step_number)}"
                if step_id in seen_steps:
                    raise ValueError(f"duplicate plan Step: {step_id}")
                seen_steps.add(step_id)
                steps.append(PlanStep(step_id, step_text, checked.lower() == "x"))

        verification: list[VerificationEvidence] = []
        visible = _outside_fences(block)
        for visible_offset, (_, line) in enumerate(visible):
            command_match = re.fullmatch(r"(?:실행|Run): (\S.*)", line)
            if command_match is None:
                continue
            expected_match = None
            for _, candidate in visible[visible_offset + 1 :]:
                if not candidate.strip():
                    continue
                expected_match = re.fullmatch(r"(?:예상|Expected): (\S.*)", candidate)
                break
            if expected_match is None:
                raise ValueError(f"{task_id} Run command has no following Expected result")
            evidence_id = f"{task_id}-V{len(verification) + 1}"
            verification.append(
                VerificationEvidence(
                    evidence_id,
                    (task_id,),
                    task_governing,
                    _inline_value(command_match.group(1)),
                    _inline_value(expected_match.group(1)),
                )
            )
        result.append(
            _ParsedTask(
                PlanTask(
                    task_id,
                    title,
                    routes[0] if routes else None,
                    task_governing,
                    tuple(steps),
                ),
                dependencies,
                reason,
                tuple(verification),
            )
        )
    return tuple(result)


def _validate_dependencies(
    parsed: tuple[_ParsedTask, ...]
) -> tuple[tuple[PlanDependency, ...], tuple[PlanRoute, ...]]:
    tasks = {item.task.id: item for item in parsed}
    dependencies: list[PlanDependency] = []
    for item in parsed:
        for prerequisite in item.dependencies:
            if prerequisite not in tasks:
                raise ValueError(f"missing Task dependency: {prerequisite}")
            if prerequisite == item.task.id:
                raise ValueError(f"self Task dependency: {item.task.id}")
            dependencies.append(
                PlanDependency(prerequisite, item.task.id, item.dependency_reason)
            )

    outgoing: dict[str, list[str]] = {task_id: [] for task_id in tasks}
    for dependency in dependencies:
        outgoing[dependency.from_task].append(dependency.to_task)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise ValueError("Task dependency cycle detected")
        if task_id in visited:
            return
        visiting.add(task_id)
        for target in outgoing[task_id]:
            visit(target)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in tasks:
        visit(task_id)

    route_order: list[str] = []
    route_tasks: dict[str, list[str]] = {}
    for item in parsed:
        route = item.task.route
        if route is None:
            continue
        if route not in route_tasks:
            route_order.append(route)
            route_tasks[route] = []
        route_tasks[route].append(item.task.id)
    task_routes = {
        task_id: route
        for route, task_ids in route_tasks.items()
        for task_id in task_ids
    }
    route_dependencies: dict[str, list[str]] = {route: [] for route in route_order}
    for dependency in dependencies:
        source_route = task_routes.get(dependency.from_task)
        target_route = task_routes.get(dependency.to_task)
        if source_route and target_route and source_route != target_route:
            if source_route not in route_dependencies[target_route]:
                route_dependencies[target_route].append(source_route)
    routes = tuple(
        PlanRoute(route, route, tuple(route_dependencies[route]), tuple(route_tasks[route]))
        for route in route_order
    )
    return tuple(dependencies), routes


def _plan_document(
    plan: Path,
    repo_root: Path,
    related: tuple[PlanBundleRef, ...],
    governing_statements: tuple[PlanStatementRef, ...],
    progress: Path | None,
    task_paths: tuple[Path, ...],
) -> tuple[PlanDocument, dict[Path, tuple[str, str]]]:
    plan_relative, plan_text, plan_digest = _read_source(plan, repo_root)
    selected_paths: list[tuple[str, Path]] = [("primary plan", plan_relative)]
    if progress is not None:
        selected_paths.append(("progress", repository_relative(progress, repo_root)))
    selected_paths.extend(
        (f"task {path.name}", repository_relative(path, repo_root))
        for path in task_paths
    )
    seen_paths: dict[Path, str] = {}
    for role, relative in selected_paths:
        previous = seen_paths.get(relative)
        if previous is not None:
            raise ValueError(
                f"plan source alias: {role} and {previous} resolve to {relative.as_posix()}"
            )
        seen_paths[relative] = role

    source_data: dict[Path, tuple[str, str]] = {plan_relative: (plan_text, plan_digest)}
    if progress is not None:
        relative, text, digest = _read_source(progress, repo_root)
        source_data[relative] = (text, digest)
    for task_path in task_paths:
        relative, text, digest = _read_source(task_path, repo_root)
        source_data[relative] = (text, digest)

    plan_lines = plan_text.splitlines()
    title_match = next((_H1_RE.fullmatch(line) for line in plan_lines if _H1_RE.fullmatch(line)), None)
    if title_match is None:
        raise ValueError("plan must contain one H1 title")
    status_match = next((re.fullmatch(r"Status: (\S+)", line) for line in plan_lines if line.startswith("Status: ")), None)
    status = status_match.group(1) if status_match else ""

    parsed_tasks: list[_ParsedTask] = []
    for relative, (text, _) in source_data.items():
        parsed_tasks.extend(
            _parse_tasks(
                text,
                governing_statements if relative == plan_relative else (),
            )
        )
    task_ids = [item.task.id for item in parsed_tasks]
    if len(set(task_ids)) != len(task_ids):
        raise ValueError("duplicate plan Task across primary and task fragments")
    ordered_tasks = tuple(sorted(parsed_tasks, key=lambda item: int(item.task.id[4:])))
    dependencies, routes = _validate_dependencies(ordered_tasks)

    section_map = dict(_sections(plan_lines))
    checkpoints: list[str] = []
    if progress is not None:
        progress_relative = repository_relative(progress, repo_root)
        progress_text = source_data[progress_relative][0]
        section_map[f"progress:{progress_relative.as_posix()}"] = progress_text
        checkpoints.extend(
            match.group(1)
            for line in progress_text.splitlines()
            if (match := re.fullmatch(r"Checkpoint: (\S.*)", line))
        )
    for task_path in task_paths:
        relative = repository_relative(task_path, repo_root)
        section_map[f"task:{relative.as_posix()}"] = source_data[relative][0]

    document = PlanDocument(
        path=plan_relative.as_posix(),
        plan_id=plan_relative.parent.name,
        title=title_match.group(1),
        status=status,
        goal=_plan_goal(plan_lines),
        sections=MappingProxyType(section_map),
        related_specs=related,
        routes=routes,
        tasks=tuple(item.task for item in ordered_tasks),
        dependencies=dependencies,
        checkpoints=tuple(checkpoints),
        verification=tuple(
            evidence for item in ordered_tasks for evidence in item.verification
        ),
        progress_path=(
            repository_relative(progress, repo_root).as_posix() if progress else None
        ),
        task_paths=tuple(repository_relative(path, repo_root).as_posix() for path in task_paths),
        mermaid=_mermaid_blocks(plan_text),
    )
    return document, source_data


def _collect_plan_sources(
    plan: Path,
    repo_root: Path,
    *,
    progress_override: Path | None = None,
    tasks_directory_override: Path | None = None,
) -> ReviewBundle:
    plan_relative = repository_relative(plan, repo_root)
    resolved_plan = repo_root.resolve() / plan_relative
    if not resolved_plan.is_file():
        raise ValueError(f"plan source does not exist: {plan_relative.as_posix()}")
    related, diagnostics = parse_plan_related_specs(resolved_plan, repo_root.resolve())
    if diagnostics:
        detail = "; ".join(
            f"{item.path}:{item.line}: {item.code} {item.message}" for item in diagnostics
        )
        raise ValueError(f"invalid plan Related Specs: {detail}")
    governing_statements, statement_diagnostics = parse_plan_governing_statements(
        resolved_plan,
        repo_root.resolve(),
        related,
    )
    if statement_diagnostics:
        detail = "; ".join(
            f"{item.path}:{item.line}: {item.code} {item.message}"
            for item in statement_diagnostics
        )
        raise ValueError(f"invalid plan Governing statements: {detail}")

    progress_candidate = (
        progress_override
        if progress_override is not None
        else resolved_plan.parent / "progress.md"
    )
    if progress_override is not None:
        progress_candidate = repo_root.resolve() / repository_relative(
            progress_override, repo_root
        )
    progress = progress_candidate if progress_candidate.is_file() else None
    tasks_directory = (
        tasks_directory_override
        if tasks_directory_override is not None
        else resolved_plan.parent / "tasks"
    )
    if tasks_directory_override is not None:
        tasks_directory = repo_root.resolve() / repository_relative(
            tasks_directory_override, repo_root
        )
    task_paths = (
        tuple(sorted(tasks_directory.glob("*.md"), key=lambda path: path.as_posix()))
        if tasks_directory.is_dir()
        else ()
    )
    document, source_data = _plan_document(
        resolved_plan,
        repo_root,
        related,
        governing_statements,
        progress,
        task_paths,
    )

    primary: list[ReviewSource] = []
    plan_sha = source_data[plan_relative][1]
    plan_text = source_data[plan_relative][0]
    primary.append(
        ReviewSource(
            "primary_plan",
            plan_relative.as_posix(),
            f"plan--{document.plan_id}",
            plan_sha,
            plan_text,
            source_bytes=plan_text.encode("utf-8"),
            title=document.title,
            status=document.status,
            document=document,
        )
    )
    if progress is not None:
        relative = repository_relative(progress, repo_root)
        primary.append(
            ReviewSource(
                "plan_progress",
                relative.as_posix(),
                f"progress--{document.plan_id}",
                source_data[relative][1],
                source_data[relative][0],
                source_bytes=source_data[relative][0].encode("utf-8"),
                title=relative.name,
                document=PlanAuxiliaryDocument(
                    relative.as_posix(), _mermaid_blocks(source_data[relative][0])
                ),
            )
        )
    for task_path in task_paths:
        relative = repository_relative(task_path, repo_root)
        primary.append(
            ReviewSource(
                "plan_task",
                relative.as_posix(),
                f"task--{relative.stem}",
                source_data[relative][1],
                source_data[relative][0],
                source_bytes=source_data[relative][0].encode("utf-8"),
                title=relative.stem,
                document=PlanAuxiliaryDocument(
                    relative.as_posix(), _mermaid_blocks(source_data[relative][0])
                ),
            )
        )

    context: list[ReviewSource] = []
    context_counts: dict[str, object] = {}
    for selected in related:
        spec_bundle = _load_structured_bundle(
            repo_root.resolve() / selected.bundle_path,
            repo_root,
        )
        context.extend(
            _bundle_member_sources(
                spec_bundle,
                "related_spec_context",
                "context",
            )
        )
        context_counts[spec_bundle.path.as_posix()] = _spec_counts(spec_bundle)

    primary_counts = {
        "task": len(document.tasks),
        "step": sum(len(task.steps) for task in document.tasks),
        "mermaid": sum(
            len(source.document.mermaid)
            for source in primary
            if source.document is not None
        ),
    }
    counts: Mapping[str, object] = MappingProxyType(
        {
            "primary": MappingProxyType(primary_counts),
            "comparison": MappingProxyType({}),
            "context": MappingProxyType(context_counts),
        }
    )
    return ReviewBundle("plan", tuple(primary), (), tuple(context), counts)


def collect_plan_sources(plan: Path, repo_root: Path) -> ReviewBundle:
    return _collect_plan_sources(plan, repo_root)
