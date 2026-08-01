"""Dependency-free typed parser for the ``forge/spec@1`` source contract."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from types import MappingProxyType
from typing import Mapping


SCHEMA = "forge/spec@1"
FRONTMATTER_KEYS = (
    "schema",
    "id",
    "status",
    "language",
    "kind",
    "areas",
    "components",
    "relatedSpecs",
)
STATUSES = frozenset(("draft", "approved", "implemented"))
LANGUAGES = frozenset(("en", "ko"))
KINDS = frozenset(("feature", "system", "interface", "policy"))
RELATIONS = frozenset(("dependsOn", "refines", "supersedes", "relatedTo"))
CANONICAL_SECTIONS = (
    "Overview",
    "Requirements",
    "Behavior & Flows",
    "Data & Interfaces",
    "Acceptance Criteria",
    "Decisions & History",
)

_ID_RE = re.compile(r"^[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*$")
_FRONTMATTER_LINE_RE = re.compile(r"^([A-Za-z][A-Za-z0-9]*): (.+)$")
_IMPLICIT_SCALAR_RE = re.compile(
    r"^(?:true|false|null|~|[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)|"
    r"[0-9]{4}-[0-9]{2}-[0-9]{2})$",
    re.IGNORECASE,
)
_H1_RE = re.compile(r"^# (\S.*)$")
_H2_RE = re.compile(r"^## (\S.*)$")
_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_REQUIREMENT_RE = re.compile(r"^- R([0-9]+)\. (\S.*)$")
_AC_RE = re.compile(r"^- AC([0-9]+) \(([^)]+)\): (\S.*)$")
_REFERENCE_RE = re.compile(r"^R([0-9]+)$")
_REFERENCE_RANGE_RE = re.compile(r"^R([0-9]+)–R?([0-9]+)$")


@dataclass(frozen=True, order=True)
class Diagnostic:
    path: str
    line: int
    code: str
    message: str


@dataclass(frozen=True)
class RelatedSpec:
    id: str
    relation: str


@dataclass(frozen=True)
class SpecMetadata:
    schema: str
    id: str
    status: str
    language: str
    kind: str
    areas: tuple[str, ...]
    components: tuple[str, ...]
    related_specs: tuple[RelatedSpec, ...]


@dataclass(frozen=True)
class Requirement:
    id: str
    text: str
    line: int
    removed: bool


@dataclass(frozen=True)
class AcceptanceCriterion:
    id: str
    requirements: tuple[str, ...]
    text: str
    line: int


@dataclass(frozen=True)
class MermaidBlock:
    text: str
    line: int
    section: str


@dataclass(frozen=True)
class SpecDocument:
    path: Path
    metadata: SpecMetadata
    title: str
    sections: Mapping[str, str]
    requirements: tuple[Requirement, ...]
    acceptance: tuple[AcceptanceCriterion, ...]
    mermaid: tuple[MermaidBlock, ...]
    source_sha256: str


def _diagnostic(path: Path, line: int, code: str, message: str) -> Diagnostic:
    return Diagnostic(path.as_posix(), line, code, message)


def parse_frontmatter(
    text: str, path: Path
) -> tuple[dict[str, object], int, tuple[Diagnostic, ...]]:
    """Parse the restricted frontmatter and return its body line offset.

    The offset is the zero-based index of the first body line in ``splitlines()``.
    Collections are JSON; all other accepted values remain strings.
    """

    lines = text.splitlines()
    errors: list[Diagnostic] = []
    if not lines or lines[0] != "---":
        errors.append(
            _diagnostic(path, 1, "SPEC_FRONTMATTER_MISSING", "The spec must start with '---'.")
        )
        return {}, 0, tuple(errors)

    try:
        closing = lines.index("---", 1)
    except ValueError:
        errors.append(
            _diagnostic(
                path,
                1,
                "SPEC_FRONTMATTER_UNCLOSED",
                "The frontmatter closing '---' is missing.",
            )
        )
        return {}, len(lines), tuple(errors)

    values: dict[str, object] = {}
    for index in range(1, closing):
        line = lines[index]
        line_number = index + 1
        match = _FRONTMATTER_LINE_RE.fullmatch(line)
        if match is None:
            errors.append(
                _diagnostic(
                    path,
                    line_number,
                    "SPEC_FRONTMATTER_VALUE",
                    "Frontmatter must use top-level 'key: value' lines.",
                )
            )
            continue

        key, raw_value = match.groups()
        if key in values:
            errors.append(
                _diagnostic(
                    path,
                    line_number,
                    "SPEC_FRONTMATTER_KEY",
                    f"Frontmatter key '{key}' is duplicated.",
                )
            )
            continue

        if raw_value.startswith(("&", "*", "!", "|", ">")) or _IMPLICIT_SCALAR_RE.fullmatch(
            raw_value
        ):
            errors.append(
                _diagnostic(
                    path,
                    line_number,
                    "SPEC_FRONTMATTER_VALUE",
                    f"Frontmatter value for '{key}' is not a canonical string or JSON collection.",
                )
            )
            continue

        if raw_value.startswith(("[", "{")):
            try:
                value = json.loads(raw_value)
            except (json.JSONDecodeError, TypeError):
                errors.append(
                    _diagnostic(
                        path,
                        line_number,
                        "SPEC_FRONTMATTER_VALUE",
                        f"Frontmatter collection '{key}' must be valid single-line JSON.",
                    )
                )
                continue
        else:
            value = raw_value
        values[key] = value

    return values, closing + 1, tuple(sorted(errors))


def _string_list(
    values: dict[str, object], key: str, path: Path, errors: list[Diagnostic]
) -> tuple[str, ...]:
    value = values.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(
            _diagnostic(
                path,
                1,
                "SPEC_FRONTMATTER_TYPE",
                f"Frontmatter '{key}' must be a JSON array of strings.",
            )
        )
        return ()
    return tuple(value)


def _related_specs(
    values: dict[str, object], path: Path, errors: list[Diagnostic]
) -> tuple[RelatedSpec, ...]:
    value = values.get("relatedSpecs")
    if not isinstance(value, list):
        errors.append(
            _diagnostic(
                path,
                1,
                "SPEC_RELATED_TYPE",
                "Frontmatter 'relatedSpecs' must be a JSON array.",
            )
        )
        return ()

    result: list[RelatedSpec] = []
    for item in value:
        if not isinstance(item, dict) or set(item) != {"id", "relation"}:
            errors.append(
                _diagnostic(
                    path,
                    1,
                    "SPEC_RELATED_TYPE",
                    "Each relatedSpecs entry must contain only string id and relation fields.",
                )
            )
            continue
        spec_id = item.get("id")
        relation = item.get("relation")
        if not isinstance(spec_id, str) or _ID_RE.fullmatch(spec_id) is None:
            errors.append(
                _diagnostic(
                    path,
                    1,
                    "SPEC_RELATED_ID",
                    "A related spec id must use NNN-slug form.",
                )
            )
            continue
        if not isinstance(relation, str) or relation not in RELATIONS:
            errors.append(
                _diagnostic(
                    path,
                    1,
                    "SPEC_RELATED_RELATION",
                    "A related spec relation must be dependsOn, refines, supersedes, or relatedTo.",
                )
            )
            continue
        result.append(RelatedSpec(spec_id, relation))
    return tuple(result)


def _headings(
    lines: list[str], body_start: int, path: Path, errors: list[Diagnostic]
) -> tuple[str, dict[str, tuple[int, int]]]:
    h1: list[tuple[int, str]] = []
    h2: list[tuple[int, str]] = []
    fence: str | None = None
    for index in range(body_start, len(lines)):
        line = lines[index]
        fence_match = _FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            continue
        if fence is not None:
            continue
        if match := _H1_RE.fullmatch(line):
            h1.append((index, match.group(1)))
        elif match := _H2_RE.fullmatch(line):
            h2.append((index, match.group(1)))

    if not h1:
        errors.append(_diagnostic(path, body_start + 1, "SPEC_TITLE_MISSING", "One H1 title is required."))
        title = ""
    else:
        title = h1[0][1]
        for index, _ in h1[1:]:
            errors.append(
                _diagnostic(path, index + 1, "SPEC_TITLE_DUPLICATE", "Only one H1 title is allowed.")
            )

    positions: dict[str, int] = {}
    for index, heading in h2:
        if heading not in CANONICAL_SECTIONS:
            errors.append(
                _diagnostic(
                    path,
                    index + 1,
                    "SPEC_HEADING_EXTRA",
                    f"Unexpected H2 heading '{heading}'.",
                )
            )
        elif heading in positions:
            errors.append(
                _diagnostic(
                    path,
                    index + 1,
                    "SPEC_HEADING_EXTRA",
                    f"Canonical H2 heading '{heading}' is duplicated.",
                )
            )
        else:
            positions[heading] = index

    for heading in CANONICAL_SECTIONS:
        if heading not in positions:
            errors.append(
                _diagnostic(
                    path,
                    body_start + 1,
                    "SPEC_HEADING_MISSING",
                    f"Canonical H2 heading '{heading}' is missing.",
                )
            )

    present = [heading for _, heading in h2 if heading in CANONICAL_SECTIONS]
    if len(positions) == len(CANONICAL_SECTIONS) and present != list(CANONICAL_SECTIONS):
        errors.append(
            _diagnostic(
                path,
                min(positions.values()) + 1,
                "SPEC_HEADING_ORDER",
                "Canonical H2 headings are not in the required order.",
            )
        )

    spans: dict[str, tuple[int, int]] = {}
    if all(heading in positions for heading in CANONICAL_SECTIONS):
        for offset, heading in enumerate(CANONICAL_SECTIONS):
            start = positions[heading] + 1
            if offset + 1 < len(CANONICAL_SECTIONS):
                end = positions[CANONICAL_SECTIONS[offset + 1]]
            else:
                end = len(lines)
            spans[heading] = (start, end)
    return title, spans


def _requirements(
    lines: list[str], span: tuple[int, int], path: Path, errors: list[Diagnostic]
) -> tuple[Requirement, ...]:
    result: list[Requirement] = []
    seen: set[str] = set()
    expected_number = 1
    for index in range(*span):
        line = lines[index]
        if not line.startswith("- R"):
            continue
        match = _REQUIREMENT_RE.fullmatch(line)
        if match is None:
            errors.append(
                _diagnostic(
                    path,
                    index + 1,
                    "SPEC_REQUIREMENT_FORMAT",
                    "Requirement lines must use '- R<number>. <text>'.",
                )
            )
            continue
        number, text = match.groups()
        requirement_id = f"R{number}"
        if requirement_id in seen:
            errors.append(
                _diagnostic(
                    path,
                    index + 1,
                    "SPEC_REQUIREMENT_DUPLICATE",
                    f"Requirement '{requirement_id}' is duplicated.",
                )
            )
            continue
        seen.add(requirement_id)
        parsed_number = int(number)
        if parsed_number != expected_number:
            errors.append(
                _diagnostic(
                    path,
                    index + 1,
                    "SPEC_REQUIREMENT_SEQUENCE",
                    f"Requirement '{requirement_id}' must be R{expected_number} at this position.",
                )
            )
        expected_number = parsed_number + 1
        removed = text.startswith("REMOVED")
        if removed and re.fullmatch(r"REMOVED — \S.*", text) is None:
            errors.append(
                _diagnostic(
                    path,
                    index + 1,
                    "SPEC_REQUIREMENT_TOMBSTONE",
                    "A removed requirement must use 'REMOVED — <reason>'.",
                )
            )
        result.append(Requirement(requirement_id, text, index + 1, removed))
    return tuple(result)


def _expand_references(
    raw: str, path: Path, line: int, errors: list[Diagnostic]
) -> tuple[str, ...]:
    result: list[str] = []
    for token in raw.split(","):
        token = token.strip()
        if match := _REFERENCE_RE.fullmatch(token):
            result.append(f"R{int(match.group(1))}")
            continue
        if match := _REFERENCE_RANGE_RE.fullmatch(token):
            first, last = (int(value) for value in match.groups())
            if first <= last:
                result.extend(f"R{number}" for number in range(first, last + 1))
                continue
        errors.append(
            _diagnostic(
                path,
                line,
                "SPEC_AC_REFERENCE_FORMAT",
                "AC references must be comma-separated R IDs or ascending R-ID ranges.",
            )
        )
        return ()
    if not result:
        errors.append(
            _diagnostic(
                path,
                line,
                "SPEC_AC_REFERENCE_FORMAT",
                "An AC must reference at least one requirement.",
            )
        )
    return tuple(result)


def _acceptance(
    lines: list[str], span: tuple[int, int], path: Path, errors: list[Diagnostic]
) -> tuple[AcceptanceCriterion, ...]:
    result: list[AcceptanceCriterion] = []
    seen: set[str] = set()
    expected_number = 1
    for index in range(*span):
        line = lines[index]
        if not line.startswith("- AC"):
            continue
        match = _AC_RE.fullmatch(line)
        if match is None:
            errors.append(
                _diagnostic(
                    path,
                    index + 1,
                    "SPEC_AC_FORMAT",
                    "Acceptance criteria must use '- AC<number> (<R references>): <text>'.",
                )
            )
            continue
        number, raw_references, criterion_text = match.groups()
        criterion_id = f"AC{number}"
        if criterion_id in seen:
            errors.append(
                _diagnostic(
                    path,
                    index + 1,
                    "SPEC_AC_DUPLICATE",
                    f"Acceptance criterion '{criterion_id}' is duplicated.",
                )
            )
            continue
        seen.add(criterion_id)
        parsed_number = int(number)
        if parsed_number != expected_number:
            errors.append(
                _diagnostic(
                    path,
                    index + 1,
                    "SPEC_AC_SEQUENCE",
                    f"Acceptance criterion '{criterion_id}' must be AC{expected_number} at this position.",
                )
            )
        expected_number = parsed_number + 1
        references = _expand_references(raw_references, path, index + 1, errors)
        result.append(
            AcceptanceCriterion(criterion_id, references, criterion_text, index + 1)
        )
    return tuple(result)


def _mermaid_blocks(
    lines: list[str], body_start: int, path: Path, errors: list[Diagnostic]
) -> tuple[MermaidBlock, ...]:
    result: list[MermaidBlock] = []
    section = ""
    index = body_start
    while index < len(lines):
        line = lines[index]
        if match := _H2_RE.fullmatch(line):
            section = match.group(1)
        if line.strip() != "```mermaid":
            index += 1
            continue
        opening = index
        index += 1
        content: list[str] = []
        while index < len(lines) and lines[index].strip() != "```":
            content.append(lines[index])
            index += 1
        if index == len(lines):
            errors.append(
                _diagnostic(
                    path,
                    opening + 1,
                    "SPEC_MERMAID_FENCE",
                    "The Mermaid fence is not closed.",
                )
            )
            break
        if section != "Behavior & Flows":
            errors.append(
                _diagnostic(
                    path,
                    opening + 1,
                    "SPEC_MERMAID_SECTION",
                    "Mermaid fences belong in Behavior & Flows.",
                )
            )
        result.append(MermaidBlock("\n".join(content), opening + 1, section))
        index += 1
    return tuple(result)


def load_spec(path: Path, root: Path) -> tuple[SpecDocument | None, tuple[Diagnostic, ...]]:
    """Load and validate one structured spec without repository-wide inference."""

    try:
        relative_path = path.resolve().relative_to(root.resolve())
    except ValueError:
        relative_path = path

    try:
        source = path.read_bytes()
        text = source.decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        diagnostic = _diagnostic(
            relative_path,
            1,
            "SPEC_SOURCE_READ",
            f"The spec must be readable UTF-8: {error.__class__.__name__}.",
        )
        return None, (diagnostic,)

    values, body_start, frontmatter_errors = parse_frontmatter(text, relative_path)
    if frontmatter_errors:
        return None, frontmatter_errors

    errors: list[Diagnostic] = []
    keys = set(values)
    for key in FRONTMATTER_KEYS:
        if key not in keys:
            errors.append(
                _diagnostic(
                    relative_path,
                    1,
                    "SPEC_FRONTMATTER_KEY",
                    f"Required frontmatter key '{key}' is missing.",
                )
            )
    for key in sorted(keys - set(FRONTMATTER_KEYS)):
        errors.append(
            _diagnostic(
                relative_path,
                1,
                "SPEC_FRONTMATTER_KEY",
                f"Unexpected frontmatter key '{key}'.",
            )
        )
    if errors:
        return None, tuple(sorted(errors))

    schema = values["schema"]
    spec_id = values["id"]
    status = values["status"]
    language = values["language"]
    kind = values["kind"]

    metadata_lines: dict[str, int] = {}
    for index in range(1, body_start):
        match = _FRONTMATTER_LINE_RE.fullmatch(text.splitlines()[index])
        if match is not None:
            metadata_lines[match.group(1)] = index + 1

    scalar_values = {
        "schema": schema,
        "id": spec_id,
        "status": status,
        "language": language,
        "kind": kind,
    }
    invalid_scalar_keys = {
        key for key, value in scalar_values.items() if not isinstance(value, str)
    }
    for key in sorted(invalid_scalar_keys):
        errors.append(
            _diagnostic(
                relative_path,
                metadata_lines.get(key, 1),
                "SPEC_FRONTMATTER_TYPE",
                f"Frontmatter '{key}' must be a scalar string.",
            )
        )

    if "schema" not in invalid_scalar_keys and schema != SCHEMA:
        errors.append(
            _diagnostic(
                relative_path,
                metadata_lines.get("schema", 1),
                "SPEC_SCHEMA",
                f"Schema must be '{SCHEMA}'.",
            )
        )
    if "id" not in invalid_scalar_keys and _ID_RE.fullmatch(spec_id) is None:
        errors.append(
            _diagnostic(
                relative_path,
                metadata_lines.get("id", 1),
                "SPEC_ID",
                "Spec id must use NNN-slug form.",
            )
        )
    elif "id" not in invalid_scalar_keys and path.parent.name != spec_id:
        errors.append(
            _diagnostic(
                relative_path,
                metadata_lines.get("id", 1),
                "SPEC_ID_PATH",
                "Spec id must match its enclosing directory.",
            )
        )
    if "status" not in invalid_scalar_keys and status not in STATUSES:
        errors.append(
            _diagnostic(
                relative_path,
                metadata_lines.get("status", 1),
                "SPEC_STATUS",
                "Status must be draft, approved, or implemented.",
            )
        )
    if "language" not in invalid_scalar_keys and language not in LANGUAGES:
        errors.append(
            _diagnostic(
                relative_path,
                metadata_lines.get("language", 1),
                "SPEC_LANGUAGE",
                "Language must be en or ko.",
            )
        )
    if "kind" not in invalid_scalar_keys and kind not in KINDS:
        errors.append(
            _diagnostic(
                relative_path,
                metadata_lines.get("kind", 1),
                "SPEC_KIND",
                "Kind must be feature, system, interface, or policy.",
            )
        )

    areas = _string_list(values, "areas", relative_path, errors)
    components = _string_list(values, "components", relative_path, errors)
    related_specs = _related_specs(values, relative_path, errors)

    lines = text.splitlines()
    title, spans = _headings(lines, body_start, relative_path, errors)

    for index in range(body_start, len(lines)):
        if re.fullmatch(r"Status:\s*.*", lines[index]):
            errors.append(
                _diagnostic(
                    relative_path,
                    index + 1,
                    "SPEC_STATUS_BODY",
                    "Lifecycle status must exist only in frontmatter.",
                )
            )
        if (
            isinstance(status, str)
            and status in {"approved", "implemented"}
            and "[NEEDS CLARIFICATION:" in lines[index]
        ):
            errors.append(
                _diagnostic(
                    relative_path,
                    index + 1,
                    "SPEC_CLARIFICATION_STATUS",
                    "Approved or implemented specs cannot contain unresolved clarification markers.",
                )
            )

    requirements: tuple[Requirement, ...] = ()
    acceptance: tuple[AcceptanceCriterion, ...] = ()
    if "Requirements" in spans:
        requirements = _requirements(lines, spans["Requirements"], relative_path, errors)
    if "Acceptance Criteria" in spans:
        acceptance = _acceptance(lines, spans["Acceptance Criteria"], relative_path, errors)
    mermaid = _mermaid_blocks(lines, body_start, relative_path, errors)

    sorted_errors = tuple(sorted(errors))
    if sorted_errors:
        return None, sorted_errors

    metadata = SpecMetadata(
        schema=str(schema),
        id=str(spec_id),
        status=str(status),
        language=str(language),
        kind=str(kind),
        areas=areas,
        components=components,
        related_specs=related_specs,
    )
    sections = MappingProxyType(
        {
            heading: "\n".join(lines[start:end]).strip("\n")
            for heading, (start, end) in spans.items()
        }
    )
    document = SpecDocument(
        path=relative_path,
        metadata=metadata,
        title=title,
        sections=sections,
        requirements=requirements,
        acceptance=acceptance,
        mermaid=mermaid,
        source_sha256=hashlib.sha256(source).hexdigest(),
    )
    return document, ()
