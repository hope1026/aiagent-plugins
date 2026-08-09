"""Strict source model for forge/project-map@1 Project Handbooks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from urllib.parse import unquote


_STATEMENT_LINK_RE = re.compile(r"^\[(.+)\]\(([^)#]+\.md)#([^)]+)\)$")


@dataclass(frozen=True)
class ProjectStatementRef:
    heading: str
    member_path: str
    anchor: str


@dataclass(frozen=True)
class StructureEntry:
    path: str
    purpose: str
    owns: str
    entry_points: tuple[str, ...]
    depends_on: tuple[str, ...]
    related_specs: tuple[str, ...]
    governing_statements: tuple[ProjectStatementRef, ...]


@dataclass(frozen=True)
class ProjectMap:
    path: str
    title: str
    overview: str
    capabilities: tuple[str, ...]
    spec_paths: tuple[str, ...]
    structure: tuple[StructureEntry, ...]


def _relative(value: str, root: Path, source: str, label: str, require_exists: bool = True) -> str:
    resolved = (root / value).resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"{source}: {label} escapes repository: {value}") from error
    if require_exists and not resolved.exists():
        raise ValueError(f"{source}: {label} is missing: {relative}")
    return relative.rstrip("/")


def _section(lines: list[str], name: str, source: str) -> list[str]:
    marker = f"## {name}"
    try:
        start = lines.index(marker) + 1
    except ValueError as error:
        raise ValueError(f"{source}: missing section {name}") from error
    end = next((index for index in range(start, len(lines)) if lines[index].startswith("## ")), len(lines))
    return lines[start:end]


def _list(lines: list[str], prefix: str | None = None) -> tuple[str, ...]:
    values = []
    for line in lines:
        if not line.startswith("- "):
            continue
        value = line[2:].strip()
        if prefix is not None:
            if not value.startswith(prefix):
                continue
            value = value[len(prefix):].strip()
        values.append(value)
    return tuple(values)


def _field(block: list[str], label: str, source: str, entry: str) -> str:
    prefix = f"**{label}:**"
    for line in block:
        if line.startswith(prefix):
            value = line[len(prefix):].strip()
            if value:
                return value
    raise ValueError(f"{source}: Structure {entry} requires {label}")


def _field_list(block: list[str], label: str) -> tuple[str, ...]:
    marker = f"**{label}:**"
    for index, line in enumerate(block):
        if line != marker:
            continue
        values = []
        for candidate in block[index + 1:]:
            if candidate.startswith("**") or candidate.startswith("### "):
                break
            if candidate.startswith("- "):
                values.append(candidate[2:].strip())
        return tuple(values)
    return ()


def _statement_refs(
    values: tuple[str, ...],
    source_path: Path,
    root: Path,
    source: str,
    entry_path: str,
    related_specs: tuple[str, ...],
) -> tuple[ProjectStatementRef, ...]:
    references: list[ProjectStatementRef] = []
    for value in values:
        match = _STATEMENT_LINK_RE.fullmatch(value)
        if match is None:
            raise ValueError(
                f"{source}: Structure {entry_path} has invalid Governing Statements link: {value}"
            )
        heading, raw_member, raw_anchor = match.groups()
        resolved = (source_path.parent / raw_member).resolve()
        try:
            member_path = resolved.relative_to(root).as_posix()
        except ValueError as error:
            raise ValueError(
                f"{source}: Governing Statements link escapes repository: {raw_member}"
            ) from error
        if not resolved.is_file():
            raise ValueError(
                f"{source}: Governing Statements member is missing: {member_path}"
            )
        matching_bundles = tuple(
            spec_path
            for spec_path in related_specs
            if member_path.startswith(spec_path.rstrip("/") + "/")
        )
        if not matching_bundles:
            raise ValueError(
                f"{source}: Structure {entry_path} Governing Statements member is not in Related Specs: {member_path}"
            )
        references.append(
            ProjectStatementRef(heading, member_path, unquote(raw_anchor))
        )
    identities = {
        (reference.member_path, reference.heading, reference.anchor)
        for reference in references
    }
    if len(identities) != len(references):
        raise ValueError(
            f"{source}: Structure {entry_path} has duplicate Governing Statements links"
        )
    return tuple(references)


def load_project_map(path: Path, repo_root: Path) -> ProjectMap:
    root = repo_root.resolve()
    relative = path.resolve().relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or lines[0] != "---" or "schema: forge/project-map@1" not in lines[1:3]:
        raise ValueError(f"{relative}: frontmatter schema must be forge/project-map@1")
    title = next((line[2:].strip() for line in lines if line.startswith("# ")), "")
    if not title:
        raise ValueError(f"{relative}: project H1 is required")
    overview_lines = _section(lines, "Project Overview", relative)
    overview = "\n".join(line for line in overview_lines if line.strip()).strip()
    if not overview:
        raise ValueError(f"{relative}: Project Overview is empty")
    capabilities = _list(_section(lines, "Key Capabilities", relative))
    if not capabilities:
        raise ValueError(f"{relative}: Key Capabilities requires at least one item")
    raw_specs = _list(_section(lines, "Specs", relative), "bundle:")
    spec_paths = tuple(_relative(value, root, relative, "Spec Bundle") for value in raw_specs)
    if len(set(spec_paths)) != len(spec_paths):
        raise ValueError(f"{relative}: Specs contains duplicate bundle paths")
    structure_lines = _section(lines, "Structure", relative)
    starts = [index for index, line in enumerate(structure_lines) if line.startswith("### ")]
    if not starts:
        raise ValueError(f"{relative}: Structure requires at least one entry")
    entries = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(structure_lines)
        raw_path = structure_lines[start][4:].strip().rstrip("/")
        block = structure_lines[start + 1:end]
        entry_path = _relative(raw_path, root, relative, "Structure path")
        purpose = _field(block, "Purpose", relative, entry_path)
        owns = _field(block, "Owns", relative, entry_path)
        entry_points = tuple(
            _relative(value, root, relative, "Entry Point")
            for value in _field_list(block, "Entry Points")
        )
        depends_on = tuple(
            _relative(value, root, relative, "Depends On", require_exists=False)
            for value in _field_list(block, "Depends On")
        )
        related_specs = tuple(value.rstrip("/") for value in _field_list(block, "Related Specs"))
        unknown_specs = sorted(set(related_specs) - set(spec_paths))
        if unknown_specs:
            raise ValueError(f"{relative}: Structure {entry_path} has undeclared Related Specs: {', '.join(unknown_specs)}")
        governing_statements = _statement_refs(
            _field_list(block, "Governing Statements"),
            path.resolve(),
            root,
            relative,
            entry_path,
            related_specs,
        )
        if related_specs and not governing_statements:
            raise ValueError(
                f"{relative}: Structure {entry_path} requires Governing Statements for Related Specs"
            )
        entries.append(
            StructureEntry(
                entry_path,
                purpose,
                owns,
                entry_points,
                depends_on,
                related_specs,
                governing_statements,
            )
        )
    if len({entry.path for entry in entries}) != len(entries):
        raise ValueError(f"{relative}: Structure contains duplicate paths")
    return ProjectMap(relative, title, overview, capabilities, spec_paths, tuple(entries))
