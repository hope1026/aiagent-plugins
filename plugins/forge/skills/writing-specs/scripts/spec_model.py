"""Dependency-free typed parsers for Forge Canonical Spec sources."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from types import MappingProxyType
from typing import Mapping
import unicodedata
from urllib.parse import unquote


BUNDLE_SCHEMA = "forge/spec@3"
BUNDLE_REQUIRED_FRONTMATTER_KEYS = (
    "schema",
    "role",
    "status",
    "language",
    "kind",
    "areas",
    "components",
    "relatedSpecs",
)
BUNDLE_OPTIONAL_FRONTMATTER_KEYS = ("subtype",)
BUNDLE_MEMBER_ROLES = frozenset(("root", "contract", "acceptance", "history", "reference"))
BUNDLE_SEMANTIC_SECTIONS = frozenset(
    ("Documents", "Requirements", "Acceptance Criteria", "Decisions & History")
)
STATUSES = frozenset(("draft", "approved", "implemented"))
LANGUAGES = frozenset(("en", "ko"))
KINDS = frozenset(("feature", "system", "interface", "policy"))
RELATIONS = frozenset(("dependsOn", "refines", "supersedes", "relatedTo"))
_SUBTYPE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_FRONTMATTER_LINE_RE = re.compile(r"^([A-Za-z][A-Za-z0-9]*): (.+)$")
_IMPLICIT_SCALAR_RE = re.compile(
    r"^(?:true|false|null|~|[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)|"
    r"[0-9]{4}-[0-9]{2}-[0-9]{2})$",
    re.IGNORECASE,
)
_H1_RE = re.compile(r"^# (\S.*)$")
_H2_RE = re.compile(r"^## (\S.*)$")
_H3_RE = re.compile(r"^### (\S.*)$")
_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_DOCUMENT_RE = re.compile(
    r"^- (root|contract|acceptance|history|reference): \[([^\]]+)\]\(([^)]+\.md)\)$"
)
_STATEMENT_LINK_RE = re.compile(r"^- \[(.+)\]\(([^)#]+\.md)#([^)]+)\)$")


@dataclass(frozen=True, order=True)
class Diagnostic:
    path: str
    line: int
    code: str
    message: str


@dataclass(frozen=True)
class MermaidBlock:
    text: str
    line: int
    section: str


@dataclass(frozen=True)
class RelatedBundle:
    path: str
    relation: str


@dataclass(frozen=True)
class SpecBundleMetadata:
    schema: str
    role: str
    status: str
    language: str
    kind: str
    subtype: str | None
    areas: tuple[str, ...]
    components: tuple[str, ...]
    related_specs: tuple[RelatedBundle, ...]


@dataclass(frozen=True)
class StatementReference:
    member_path: Path
    heading: str
    anchor: str
    line: int


@dataclass(frozen=True)
class SpecStatement:
    kind: str
    heading: str
    member_path: Path
    line: int
    references: tuple[StatementReference, ...] = ()


@dataclass(frozen=True)
class SpecMember:
    path: Path
    role: str
    title: str
    source_text: str
    source_bytes: bytes
    source_sha256: str
    sections: Mapping[str, str]
    section_order: tuple[str, ...]
    mermaid: tuple[MermaidBlock, ...]


@dataclass(frozen=True)
class SpecBundle:
    path: Path
    root_path: Path
    metadata: SpecBundleMetadata
    title: str
    members: tuple[SpecMember, ...]
    statements: tuple[SpecStatement, ...]
    bundle_sha256: str


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


def _related_bundles(
    values: dict[str, object], path: Path, errors: list[Diagnostic]
) -> tuple[RelatedBundle, ...]:
    value = values.get("relatedSpecs")
    if not isinstance(value, list):
        errors.append(
            _diagnostic(
                path,
                1,
                "BUNDLE_RELATED_TYPE",
                "Frontmatter 'relatedSpecs' must be a JSON array.",
            )
        )
        return ()

    result: list[RelatedBundle] = []
    for item in value:
        if not isinstance(item, dict) or set(item) != {"path", "relation"}:
            errors.append(
                _diagnostic(
                    path,
                    1,
                    "BUNDLE_RELATED_TYPE",
                    "Each relatedSpecs entry must contain only string path and relation fields.",
                )
            )
            continue
        bundle_path = item.get("path")
        relation = item.get("relation")
        if not isinstance(bundle_path, str) or not bundle_path.startswith("docs/specs/"):
            errors.append(
                _diagnostic(
                    path,
                    1,
                    "BUNDLE_RELATED_PATH",
                    "A related spec path must name a bundle below docs/specs/.",
                )
            )
            continue
        if not isinstance(relation, str) or relation not in RELATIONS:
            errors.append(
                _diagnostic(
                    path,
                    1,
                    "BUNDLE_RELATED_RELATION",
                    "A related spec relation must be dependsOn, refines, supersedes, or relatedTo.",
                )
            )
            continue
        result.append(RelatedBundle(bundle_path.rstrip("/"), relation))
    return tuple(result)


def statement_anchor(heading: str) -> str:
    """Return the deterministic human-readable anchor for a statement heading."""

    rendered = re.sub(r"`([^`]*)`", r"\1", heading)
    normalized = unicodedata.normalize("NFC", rendered).casefold()
    characters: list[str] = []
    pending_separator = False
    for character in normalized:
        if character.isspace():
            pending_separator = bool(characters)
            continue
        if character.isalnum() or character == "_":
            if pending_separator and characters[-1] != "-":
                characters.append("-")
            characters.append(character)
            pending_separator = False
            continue
        if character == "-":
            if characters and characters[-1] != "-":
                characters.append("-")
            pending_separator = False
    return "".join(characters).strip("-")


def _bundle_headings(
    lines: list[str],
    body_start: int,
    path: Path,
    errors: list[Diagnostic],
) -> tuple[str, dict[str, tuple[int, int]], tuple[str, ...]]:
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
        errors.append(
            _diagnostic(path, body_start + 1, "BUNDLE_TITLE_MISSING", "One H1 title is required.")
        )
        title = ""
    else:
        title = h1[0][1]
        for index, _ in h1[1:]:
            errors.append(
                _diagnostic(path, index + 1, "BUNDLE_TITLE_DUPLICATE", "Only one H1 title is allowed.")
            )

    positions: dict[str, int] = {}
    section_order: list[str] = []
    section_occurrences: list[tuple[int, str]] = []
    for index, heading in h2:
        if heading in positions:
            if heading in BUNDLE_SEMANTIC_SECTIONS:
                errors.append(
                    _diagnostic(
                        path,
                        index + 1,
                        "BUNDLE_SECTION_DUPLICATE",
                        f"Semantic H2 section '{heading}' is duplicated in one member.",
                    )
                )
        else:
            positions[heading] = index
        section_order.append(heading)
        section_occurrences.append((index, heading))

    spans: dict[str, tuple[int, int]] = {}
    for offset, (position, heading) in enumerate(section_occurrences):
        start = position + 1
        end = (
            section_occurrences[offset + 1][0]
            if offset + 1 < len(section_occurrences)
            else len(lines)
        )
        spans.setdefault(heading, (start, end))
    return title, spans, tuple(section_order)


def _unfenced_line_indexes(lines: list[str], start: int, end: int):
    """Yield source indexes outside Markdown fences in one top-level section."""

    fence: str | None = None
    for index in range(start, end):
        fence_match = _FENCE_RE.match(lines[index])
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            continue
        if fence is None:
            yield index


def _document_inventory(
    lines: list[str],
    span: tuple[int, int],
    path: Path,
    errors: list[Diagnostic],
) -> tuple[tuple[str, str, str, int], ...]:
    result: list[tuple[str, str, str, int]] = []
    for index in _unfenced_line_indexes(lines, *span):
        line = lines[index]
        if not line.startswith("- "):
            continue
        match = _DOCUMENT_RE.fullmatch(line)
        if match is None:
            errors.append(
                _diagnostic(
                    path,
                    index + 1,
                    "BUNDLE_DOCUMENT_FORMAT",
                    "Document entries must use '- <role>: [<H1>](<filename>.md)'.",
                )
            )
            continue
        role, title, member_path = match.groups()
        result.append((role, title, member_path, index + 1))
    return tuple(result)


def _statement_references(
    lines: list[str],
    start: int,
    end: int,
    member_path: Path,
    language: str,
    errors: list[Diagnostic],
) -> tuple[StatementReference, ...]:
    label = "검증하는 요구사항:" if language == "ko" else "Verifies:"
    label_index: int | None = None
    for index in _unfenced_line_indexes(lines, start, end):
        if lines[index] == label:
            label_index = index
            break
    if label_index is None:
        errors.append(
            _diagnostic(
                member_path,
                start + 1,
                "STATEMENT_REFERENCE_LABEL",
                f"An acceptance statement must include '{label}'.",
            )
        )
        return ()

    references: list[StatementReference] = []
    for index in _unfenced_line_indexes(lines, label_index + 1, end):
        line = lines[index]
        if not line.startswith("- "):
            continue
        match = _STATEMENT_LINK_RE.fullmatch(line)
        if match is None:
            errors.append(
                _diagnostic(
                    member_path,
                    index + 1,
                    "STATEMENT_REFERENCE_FORMAT",
                    "Requirement references must be Markdown links to a member heading.",
                )
            )
            continue
        heading, raw_path, raw_anchor = match.groups()
        target_path = member_path.parent / raw_path
        references.append(
            StatementReference(
                member_path=target_path,
                heading=heading,
                anchor=unquote(raw_anchor),
                line=index + 1,
            )
        )
    if not references:
        errors.append(
            _diagnostic(
                member_path,
                label_index + 1,
                "STATEMENT_REFERENCE_MISSING",
                "An acceptance statement must reference at least one requirement.",
            )
        )
    return tuple(references)


def _bundle_statements(
    lines: list[str],
    spans: Mapping[str, tuple[int, int]],
    member_path: Path,
    language: str,
    errors: list[Diagnostic],
) -> tuple[SpecStatement, ...]:
    result: list[SpecStatement] = []
    for section, kind in (("Requirements", "requirement"), ("Acceptance Criteria", "acceptance")):
        span = spans.get(section)
        if span is None:
            continue
        headings: list[tuple[int, str]] = []
        fence: str | None = None
        for index in range(*span):
            line = lines[index]
            fence_match = _FENCE_RE.match(line)
            if fence_match:
                marker = fence_match.group(1)
                if fence is None:
                    fence = marker
                elif marker == fence:
                    fence = None
                continue
            if fence is None and (match := _H3_RE.fullmatch(line)):
                headings.append((index, match.group(1)))
        for offset, (index, heading) in enumerate(headings):
            next_heading = headings[offset + 1][0] if offset + 1 < len(headings) else span[1]
            references = (
                _statement_references(
                    lines,
                    index + 1,
                    next_heading,
                    member_path,
                    language,
                    errors,
                )
                if kind == "acceptance"
                else ()
            )
            result.append(
                SpecStatement(
                    kind=kind,
                    heading=heading,
                    member_path=member_path,
                    line=index + 1,
                    references=references,
                )
            )
    return tuple(sorted(result, key=lambda statement: statement.line))


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
        result.append(MermaidBlock("\n".join(content), opening + 1, section))
        index += 1
    return tuple(result)


def bundle_sha256(bundle_path: Path, members: tuple[SpecMember, ...]) -> str:
    """Hash normalized bundle identity and exact member bytes deterministically."""

    def normalized_repository_path(path: Path, label: str) -> str:
        rendered = path.as_posix()
        if (
            path.is_absolute()
            or not path.parts
            or any(part in ("", ".", "..") for part in path.parts)
            or "\\" in rendered
            or unicodedata.normalize("NFC", rendered) != rendered
        ):
            raise ValueError(f"{label} must be a normalized repository-relative path")
        return rendered

    normalized_bundle = normalized_repository_path(bundle_path, "bundle_path")
    normalized_members: list[tuple[str, SpecMember]] = []
    seen_member_paths: set[str] = set()
    for member in members:
        normalized_member = normalized_repository_path(member.path, "member.path")
        try:
            relative_member = member.path.relative_to(bundle_path)
        except ValueError as error:
            raise ValueError("member.path must be contained by bundle_path") from error
        normalized_relative = normalized_repository_path(relative_member, "member relative path")
        if normalized_member in seen_member_paths:
            raise ValueError("member.path values must be unique")
        seen_member_paths.add(normalized_member)
        normalized_members.append((normalized_relative, member))

    digest = hashlib.sha256()

    def add_frame(value: bytes) -> None:
        digest.update(len(value).to_bytes(8, "big"))
        digest.update(value)

    add_frame(normalized_bundle.encode("utf-8"))
    for relative_member, member in sorted(normalized_members, key=lambda item: item[0]):
        add_frame(relative_member.encode("utf-8"))
        add_frame(member.source_bytes)
    return digest.hexdigest()


def load_spec_bundle(path: Path, root: Path) -> tuple[SpecBundle | None, tuple[Diagnostic, ...]]:
    """Load one ``forge/spec@3`` bundle without repository-wide inference."""

    try:
        resolved_path = path.resolve(strict=True)
        resolved_root = root.resolve(strict=True)
        bundle_path = resolved_path.relative_to(resolved_root)
    except (OSError, ValueError):
        bundle_path = path
        diagnostic = _diagnostic(
            bundle_path,
            1,
            "BUNDLE_SOURCE_PATH",
            "The spec bundle must be a readable directory inside the repository root.",
        )
        return None, (diagnostic,)

    if not resolved_path.is_dir():
        return None, (
            _diagnostic(
                bundle_path,
                1,
                "BUNDLE_SOURCE_PATH",
                "The spec bundle source must be a directory.",
            ),
        )

    markdown_paths = tuple(sorted(resolved_path.glob("*.md"), key=lambda item: item.name))
    member_path_errors: list[Diagnostic] = []
    for markdown_path in markdown_paths:
        relative_member = markdown_path.relative_to(resolved_root)
        try:
            resolved_member = markdown_path.resolve(strict=True)
            resolved_member.relative_to(resolved_path)
        except (OSError, ValueError):
            member_path_errors.append(
                _diagnostic(
                    relative_member,
                    1,
                    "BUNDLE_MEMBER_PATH",
                    "A bundle member must resolve to a regular file inside the bundle directory.",
                )
            )
            continue
        if markdown_path.is_symlink() or not resolved_member.is_file():
            member_path_errors.append(
                _diagnostic(
                    relative_member,
                    1,
                    "BUNDLE_MEMBER_PATH",
                    "A bundle member must be a regular file, not a symbolic link.",
                )
            )
    if member_path_errors:
        return None, tuple(sorted(member_path_errors))

    root_candidates: list[tuple[Path, bytes, str, dict[str, object], int]] = []
    read_errors: list[Diagnostic] = []
    for markdown_path in markdown_paths:
        relative_member = markdown_path.relative_to(resolved_root)
        try:
            source = markdown_path.read_bytes()
            text = source.decode("utf-8")
        except (OSError, UnicodeDecodeError) as error:
            read_errors.append(
                _diagnostic(
                    relative_member,
                    1,
                    "BUNDLE_SOURCE_READ",
                    f"A bundle member must be readable UTF-8: {error.__class__.__name__}.",
                )
            )
            continue
        if not text.splitlines() or text.splitlines()[0] != "---":
            continue
        values, body_start, frontmatter_errors = parse_frontmatter(text, relative_member)
        if frontmatter_errors:
            read_errors.extend(frontmatter_errors)
            continue
        if values.get("schema") == BUNDLE_SCHEMA and values.get("role") == "root":
            root_candidates.append((markdown_path, source, text, values, body_start))

    if read_errors:
        return None, tuple(sorted(read_errors))
    if len(root_candidates) != 1:
        return None, (
            _diagnostic(
                bundle_path,
                1,
                "BUNDLE_ROOT_COUNT",
                "A spec bundle must contain exactly one forge/spec@3 root document.",
            ),
        )

    root_file, root_source, root_text, values, body_start = root_candidates[0]
    root_relative = root_file.relative_to(resolved_root)
    errors: list[Diagnostic] = []
    keys = set(values)
    for key in BUNDLE_REQUIRED_FRONTMATTER_KEYS:
        if key not in keys:
            errors.append(
                _diagnostic(
                    root_relative,
                    1,
                    "BUNDLE_FRONTMATTER_KEY",
                    f"Required root frontmatter key '{key}' is missing.",
                )
            )
    allowed_keys = set(BUNDLE_REQUIRED_FRONTMATTER_KEYS) | set(BUNDLE_OPTIONAL_FRONTMATTER_KEYS)
    for key in sorted(keys - allowed_keys):
        errors.append(
            _diagnostic(
                root_relative,
                1,
                "BUNDLE_FRONTMATTER_KEY",
                f"Unexpected root frontmatter key '{key}'.",
            )
        )
    if errors:
        return None, tuple(sorted(errors))

    scalar_keys = ("schema", "role", "status", "language", "kind")
    for key in scalar_keys:
        if not isinstance(values.get(key), str):
            errors.append(
                _diagnostic(
                    root_relative,
                    1,
                    "BUNDLE_FRONTMATTER_TYPE",
                    f"Root frontmatter '{key}' must be a scalar string.",
                )
            )
    subtype = values.get("subtype")
    if subtype is not None and not isinstance(subtype, str):
        errors.append(
            _diagnostic(
                root_relative,
                1,
                "BUNDLE_FRONTMATTER_TYPE",
                "Root frontmatter 'subtype' must be a scalar string.",
            )
        )
    if errors:
        return None, tuple(sorted(errors))

    schema = str(values["schema"])
    role = str(values["role"])
    status = str(values["status"])
    language = str(values["language"])
    kind = str(values["kind"])
    if schema != BUNDLE_SCHEMA:
        errors.append(
            _diagnostic(root_relative, 1, "BUNDLE_SCHEMA", f"Schema must be '{BUNDLE_SCHEMA}'.")
        )
    if role != "root":
        errors.append(
            _diagnostic(root_relative, 1, "BUNDLE_ROLE", "Root frontmatter role must be 'root'.")
        )
    if status not in STATUSES:
        errors.append(
            _diagnostic(
                root_relative,
                1,
                "BUNDLE_STATUS",
                "Status must be draft, approved, or implemented.",
            )
        )
    if language not in LANGUAGES:
        errors.append(
            _diagnostic(root_relative, 1, "BUNDLE_LANGUAGE", "Language must be en or ko.")
        )
    if kind not in KINDS:
        errors.append(
            _diagnostic(
                root_relative,
                1,
                "BUNDLE_KIND",
                "Kind must be feature, system, interface, or policy.",
            )
        )
    if isinstance(subtype, str) and _SUBTYPE_RE.fullmatch(subtype) is None:
        errors.append(
            _diagnostic(
                root_relative,
                1,
                "BUNDLE_SUBTYPE",
                "Subtype must use lowercase kebab-case.",
            )
        )

    areas = _string_list(values, "areas", root_relative, errors)
    components = _string_list(values, "components", root_relative, errors)
    related_specs = _related_bundles(values, root_relative, errors)

    root_lines = root_text.splitlines()
    root_title, root_spans, _ = _bundle_headings(
        root_lines, body_start, root_relative, errors
    )
    documents_span = root_spans.get("Documents")
    if documents_span is None:
        errors.append(
            _diagnostic(
                root_relative,
                body_start + 1,
                "BUNDLE_DOCUMENTS_MISSING",
                "The root must contain one Documents section.",
            )
        )
        inventory: tuple[tuple[str, str, str, int], ...] = ()
    else:
        inventory = _document_inventory(root_lines, documents_span, root_relative, errors)

    valid_inventory: list[tuple[str, str, str, int]] = []
    declared_lines: dict[str, int] = {}
    for item in inventory:
        member_role, declared_title, filename, inventory_line = item
        filename_path = Path(filename)
        if (
            filename_path.is_absolute()
            or len(filename_path.parts) != 1
            or any(part in ("", ".", "..") for part in filename_path.parts)
        ):
            errors.append(
                _diagnostic(
                    root_relative,
                    inventory_line,
                    "BUNDLE_MEMBER_PATH",
                    "A declared member must be a direct Markdown file inside the bundle directory.",
                )
            )
            continue
        if filename in declared_lines:
            errors.append(
                _diagnostic(
                    root_relative,
                    inventory_line,
                    "BUNDLE_DOCUMENT_DUPLICATE",
                    f"Declared member '{filename}' appears more than once in Documents.",
                )
            )
            continue
        declared_lines[filename] = inventory_line
        valid_inventory.append(item)

    actual_filenames = {markdown_path.name for markdown_path in markdown_paths}
    for filename in sorted(actual_filenames - set(declared_lines)):
        errors.append(
            _diagnostic(
                root_relative,
                documents_span[0] + 1 if documents_span is not None else body_start + 1,
                "BUNDLE_DOCUMENT_UNDECLARED",
                f"Markdown member '{filename}' must be declared exactly once in Documents.",
            )
        )
    for filename, inventory_line in sorted(declared_lines.items()):
        if filename not in actual_filenames:
            errors.append(
                _diagnostic(
                    root_relative,
                    inventory_line,
                    "BUNDLE_DOCUMENT_MISSING",
                    f"Declared member '{filename}' must exist in the bundle directory.",
                )
            )

    root_entries = [item for item in valid_inventory if item[0] == "root"]
    if len(root_entries) != 1 or root_entries[0][2] != root_file.name:
        errors.append(
            _diagnostic(
                root_relative,
                root_entries[0][3] if root_entries else body_start + 1,
                "BUNDLE_DOCUMENT_ROOT",
                "Documents must declare the forge/spec@3 root file exactly once with role 'root'.",
            )
        )

    inventory = tuple(valid_inventory)
    if errors:
        return None, tuple(sorted(errors))

    members: list[SpecMember] = []
    statements: list[SpecStatement] = []
    for member_role, declared_title, filename, inventory_line in inventory:
        member_file = resolved_path / filename
        member_relative = bundle_path / filename
        try:
            member_source = root_source if member_file == root_file else member_file.read_bytes()
            member_text = root_text if member_file == root_file else member_source.decode("utf-8")
        except (OSError, UnicodeDecodeError) as error:
            errors.append(
                _diagnostic(
                    root_relative,
                    inventory_line,
                    "BUNDLE_MEMBER_READ",
                    f"Declared member '{filename}' must be readable UTF-8: {error.__class__.__name__}.",
                )
            )
            continue

        member_body_start = body_start if member_file == root_file else 0
        member_lines = member_text.splitlines()
        member_title, member_spans, member_section_order = _bundle_headings(
            member_lines,
            member_body_start,
            member_relative,
            errors,
        )
        if member_title != declared_title:
            errors.append(
                _diagnostic(
                    root_relative,
                    inventory_line,
                    "BUNDLE_DOCUMENT_TITLE",
                    f"Declared title '{declared_title}' must match member H1 '{member_title}'.",
                )
            )
        sections = MappingProxyType(
            {
                heading: "\n".join(member_lines[start:end]).strip("\n")
                for heading, (start, end) in member_spans.items()
            }
        )
        member = SpecMember(
            path=member_relative,
            role=member_role,
            title=member_title,
            source_text=member_text,
            source_bytes=member_source,
            source_sha256=hashlib.sha256(member_source).hexdigest(),
            sections=sections,
            section_order=member_section_order,
            mermaid=_mermaid_blocks(
                member_lines,
                member_body_start,
                member_relative,
                errors,
            ),
        )
        members.append(member)
        statements.extend(
            _bundle_statements(
                member_lines,
                member_spans,
                member_relative,
                language,
                errors,
            )
        )

    sorted_errors = tuple(sorted(errors))
    if sorted_errors:
        return None, sorted_errors

    metadata = SpecBundleMetadata(
        schema=schema,
        role=role,
        status=status,
        language=language,
        kind=kind,
        subtype=str(subtype) if subtype is not None else None,
        areas=areas,
        components=components,
        related_specs=related_specs,
    )
    member_tuple = tuple(members)
    bundle = SpecBundle(
        path=bundle_path,
        root_path=root_relative,
        metadata=metadata,
        title=root_title,
        members=member_tuple,
        statements=tuple(statements),
        bundle_sha256=bundle_sha256(bundle_path, member_tuple),
    )
    return bundle, ()
