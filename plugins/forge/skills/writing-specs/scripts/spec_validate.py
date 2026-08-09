"""Repository-wide validation for ``forge/spec@2`` sources and plan references."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata

from spec_model import (
    BUNDLE_SCHEMA,
    Diagnostic,
    SpecBundle,
    SpecDocument,
    load_spec,
    load_spec_bundle,
    parse_frontmatter,
    statement_anchor,
)
from spec_transitions import (
    MANIFEST_NAME as TRANSITION_MANIFEST_NAME,
    SpecTransition,
    TransitionManifest,
    load_transition_manifest,
)


MERMAID_VALIDATOR_BUNDLE = (
    Path(__file__).resolve().parent.parent / "assets" / "mermaid-validator.bundle.mjs"
)
_MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
_PLAN_ID_RE = re.compile(r"^[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*$")
_ITEM_RE = re.compile(r"^(?:R|AC)[0-9]+$")
_SEMANTIC_DIRECTORY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SEMANTIC_MARKDOWN_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
_NUMERIC_PREFIX_RE = re.compile(r"^[0-9]+[-_.]")
_GENERIC_MEMBER_FILENAMES = frozenset(
    (
        "spec.md",
        "index.md",
        "document.md",
        "requirements.md",
        "acceptance-criteria.md",
        "history.md",
    )
)


@dataclass(frozen=True)
class PlanSpecRef:
    id: str
    path: Path
    requirements: tuple[str, ...]
    acceptance: tuple[str, ...]


@dataclass(frozen=True)
class ValidationResult:
    documents: tuple[SpecDocument, ...]
    diagnostics: tuple[Diagnostic, ...]
    bundles: tuple[SpecBundle, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.diagnostics


def _normalized_statement_heading(heading: str) -> str:
    return " ".join(unicodedata.normalize("NFC", heading).casefold().split())


def _bundle_repository_mode(spec_root: Path) -> bool:
    if not spec_root.is_dir():
        return False
    for directory in sorted(spec_root.iterdir(), key=lambda item: item.name):
        if directory.is_symlink() or not directory.is_dir():
            continue
        for member in sorted(directory.glob("*.md"), key=lambda item: item.name):
            if member.is_symlink():
                continue
            try:
                text = member.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if not text.startswith("---\n") and not text.startswith("---\r\n"):
                continue
            values, _, diagnostics = parse_frontmatter(text, member)
            if not diagnostics and values.get("schema") == BUNDLE_SCHEMA:
                return True
    return False


def _mapped_bundle_diagnostic(
    diagnostic: Diagnostic,
    repo_root: Path,
) -> Diagnostic:
    code_map = {
        "BUNDLE_DOCUMENT_UNDECLARED": "BUNDLE_MEMBER_UNDECLARED",
        "BUNDLE_DOCUMENT_MISSING": "BUNDLE_MEMBER_MISSING",
        "BUNDLE_DOCUMENT_DUPLICATE": "BUNDLE_MEMBER_DUPLICATE",
        "BUNDLE_DOCUMENT_ROOT": "BUNDLE_ROOT_INVENTORY_ROLE",
    }
    code = code_map.get(diagnostic.code, diagnostic.code)
    if diagnostic.code == "BUNDLE_MEMBER_PATH":
        candidate = repo_root / diagnostic.path
        code = "BUNDLE_MEMBER_SYMLINK" if candidate.is_symlink() else "BUNDLE_MEMBER_PATH_ESCAPE"
    return Diagnostic(diagnostic.path, diagnostic.line, code, diagnostic.message)


def _bundle_path_diagnostics(
    directory: Path,
    relative_directory: Path,
) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    name = directory.name
    if _NUMERIC_PREFIX_RE.match(name):
        diagnostics.append(
            _diagnostic(
                relative_directory,
                1,
                "BUNDLE_DIRECTORY_NUMERIC_PREFIX",
                "A spec bundle directory must not start with a numeric sorting prefix.",
            )
        )
    if _SEMANTIC_DIRECTORY_RE.fullmatch(name) is None:
        diagnostics.append(
            _diagnostic(
                relative_directory,
                1,
                "BUNDLE_DIRECTORY_NAME",
                "A spec bundle directory must use a semantic lowercase kebab-case name.",
            )
        )
    for member in sorted(directory.glob("*.md"), key=lambda item: item.name):
        relative_member = relative_directory / member.name
        if _NUMERIC_PREFIX_RE.match(member.name):
            diagnostics.append(
                _diagnostic(
                    relative_member,
                    1,
                    "BUNDLE_FILENAME_NUMERIC_PREFIX",
                    "A spec member filename must not start with a numeric sorting prefix.",
                )
            )
        if _SEMANTIC_MARKDOWN_RE.fullmatch(member.name) is None:
            diagnostics.append(
                _diagnostic(
                    relative_member,
                    1,
                    "BUNDLE_FILENAME_NAME",
                    "A spec member filename must use a semantic lowercase kebab-case name.",
                )
            )
        if member.name in _GENERIC_MEMBER_FILENAMES:
            diagnostics.append(
                _diagnostic(
                    relative_member,
                    1,
                    "BUNDLE_FILENAME_GENERIC",
                    f"Generic spec member filename '{member.name}' is not allowed.",
                )
            )
    return tuple(diagnostics)


def _non_root_frontmatter_diagnostics(
    directory: Path,
    relative_directory: Path,
) -> tuple[Diagnostic, ...]:
    roots: set[str] = set()
    frontmatter_members: set[str] = set()
    for member in sorted(directory.glob("*.md"), key=lambda item: item.name):
        if member.is_symlink():
            continue
        try:
            text = member.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not text.startswith("---\n") and not text.startswith("---\r\n"):
            continue
        frontmatter_members.add(member.name)
        values, _, diagnostics = parse_frontmatter(text, relative_directory / member.name)
        if not diagnostics and values.get("schema") == BUNDLE_SCHEMA and values.get("role") == "root":
            roots.add(member.name)
    if len(roots) != 1:
        return ()
    return tuple(
        _diagnostic(
            relative_directory / filename,
            1,
            "BUNDLE_MEMBER_FRONTMATTER",
            "Only the bundle root may contain Forge frontmatter.",
        )
        for filename in sorted(frontmatter_members - roots)
    )


def _validate_bundle_statements(bundle: SpecBundle, errors: list[Diagnostic]) -> None:
    requirements = tuple(item for item in bundle.statements if item.kind == "requirement")
    acceptance = tuple(item for item in bundle.statements if item.kind == "acceptance")
    if not requirements:
        errors.append(
            _diagnostic(
                bundle.root_path,
                1,
                "BUNDLE_REQUIREMENTS_MISSING",
                "A spec bundle must contain at least one Requirement statement.",
            )
        )
    if not acceptance:
        errors.append(
            _diagnostic(
                bundle.root_path,
                1,
                "BUNDLE_ACCEPTANCE_MISSING",
                "A spec bundle must contain at least one Acceptance statement.",
            )
        )

    history_count = sum(
        member.section_order.count("Decisions & History") for member in bundle.members
    )
    if history_count != 1:
        errors.append(
            _diagnostic(
                bundle.root_path,
                1,
                "BUNDLE_HISTORY_COUNT",
                "A spec bundle must contain exactly one Decisions & History section.",
            )
        )

    for kind in ("requirement", "acceptance"):
        exact: dict[str, object] = {}
        normalized: dict[str, object] = {}
        for statement in (item for item in bundle.statements if item.kind == kind):
            if statement.heading in exact:
                errors.append(
                    _diagnostic(
                        statement.member_path,
                        statement.line,
                        "STATEMENT_DUPLICATE",
                        f"The {kind} statement heading must be unique inside its bundle.",
                    )
                )
            else:
                exact[statement.heading] = statement
            key = _normalized_statement_heading(statement.heading)
            previous = normalized.get(key)
            if previous is not None and getattr(previous, "heading", None) != statement.heading:
                errors.append(
                    _diagnostic(
                        statement.member_path,
                        statement.line,
                        "STATEMENT_NORMALIZED_DUPLICATE",
                        f"The normalized {kind} statement heading must be unique inside its bundle.",
                    )
                )
            else:
                normalized[key] = statement

    all_by_path_heading = {
        (statement.member_path, statement.heading): statement
        for statement in bundle.statements
    }
    by_path_anchor = {
        (statement.member_path, statement_anchor(statement.heading)): statement
        for statement in bundle.statements
    }
    member_paths = {member.path for member in bundle.members}
    covered: set[tuple[Path, str]] = set()
    for criterion in acceptance:
        for reference in criterion.references:
            if (
                reference.member_path.is_absolute()
                or ".." in reference.member_path.parts
                or reference.member_path not in member_paths
            ):
                errors.append(
                    _diagnostic(
                        criterion.member_path,
                        reference.line,
                        "STATEMENT_REFERENCE_PATH",
                        "An acceptance reference must target a declared member in the same bundle.",
                    )
                )
                continue
            target = all_by_path_heading.get((reference.member_path, reference.heading))
            if target is None:
                anchor_target = by_path_anchor.get((reference.member_path, reference.anchor))
                errors.append(
                    _diagnostic(
                        criterion.member_path,
                        reference.line,
                        "STATEMENT_REFERENCE_TEXT" if anchor_target is not None else "STATEMENT_REFERENCE_PATH",
                        "Acceptance link text must equal the exact target statement heading.",
                    )
                )
                continue
            if target.kind != "requirement":
                errors.append(
                    _diagnostic(
                        criterion.member_path,
                        reference.line,
                        "STATEMENT_REFERENCE_KIND",
                        "An acceptance statement may verify only Requirement statements.",
                    )
                )
                continue
            expected_anchor = statement_anchor(target.heading)
            if reference.anchor != expected_anchor:
                errors.append(
                    _diagnostic(
                        criterion.member_path,
                        reference.line,
                        "STATEMENT_REFERENCE_ANCHOR",
                        "The statement link anchor must match the target Requirement heading.",
                    )
                )
                continue
            covered.add((target.member_path, target.heading))

    for requirement in requirements:
        if (requirement.member_path, requirement.heading) not in covered:
            errors.append(
                _diagnostic(
                    requirement.member_path,
                    requirement.line,
                    "STATEMENT_COVERAGE",
                    "Every Requirement statement must be verified by an Acceptance statement.",
                )
            )


def _validate_bundle_relations(
    bundles: tuple[SpecBundle, ...],
    errors: list[Diagnostic],
) -> None:
    known = {bundle.path.as_posix(): bundle for bundle in bundles}
    for bundle in bundles:
        for relation in bundle.metadata.related_specs:
            target = relation.path.rstrip("/")
            if target == bundle.path.as_posix():
                errors.append(
                    _diagnostic(
                        bundle.root_path,
                        1,
                        "BUNDLE_RELATED_SELF",
                        "A spec bundle cannot relate to itself.",
                    )
                )
            elif target not in known:
                errors.append(
                    _diagnostic(
                        bundle.root_path,
                        1,
                        "BUNDLE_RELATED_MISSING",
                        f"Related spec bundle '{relation.path}' does not exist.",
                    )
                )


def _validate_bundle_baseline(
    repository: Path,
    relative_root: Path,
    baseline_ref: str,
    bundles: tuple[SpecBundle, ...],
    current_manifest: TransitionManifest | None,
    errors: list[Diagnostic],
) -> None:
    if not (repository / ".git").exists():
        errors.append(
            _diagnostic(
                relative_root,
                1,
                "SPEC_BASELINE_UNAVAILABLE",
                "A Git repository is required for baseline validation.",
            )
        )
        return
    listing = _git_output(
        repository,
        ["ls-tree", "-r", "--name-only", baseline_ref, "--", relative_root.as_posix()],
    )
    if listing is None or listing.returncode != 0:
        errors.append(
            _diagnostic(
                relative_root,
                1,
                "SPEC_BASELINE_UNAVAILABLE",
                "The requested Git baseline cannot be read.",
            )
        )
        return

    try:
        baseline_paths = tuple(
            sorted(Path(item.decode("utf-8")) for item in listing.stdout.splitlines())
        )
    except UnicodeDecodeError:
        errors.append(
            _diagnostic(
                relative_root,
                1,
                "SPEC_BASELINE_UNAVAILABLE",
                "The Git baseline contains a path that is not valid UTF-8.",
            )
        )
        return

    manifest_path = relative_root / TRANSITION_MANIFEST_NAME
    baseline_manifest_source = _git_blob(repository, baseline_ref, manifest_path)
    if baseline_manifest_source is None:
        baseline_manifest = TransitionManifest(())
        baseline_manifest_valid = True
    else:
        parsed_manifest, diagnostics = load_transition_manifest(
            repository,
            relative_root,
            source=baseline_manifest_source,
        )
        errors.extend(diagnostics)
        baseline_manifest_valid = parsed_manifest is not None
        baseline_manifest = parsed_manifest or TransitionManifest(())

    current_transitions = current_manifest.transitions if current_manifest else ()
    prefix_valid = (
        baseline_manifest_valid
        and current_transitions[: len(baseline_manifest.transitions)]
        == baseline_manifest.transitions
    )
    if not prefix_valid:
        errors.append(
            _diagnostic(
                manifest_path,
                1,
                "SPEC_TRANSITION_BASELINE_PREFIX",
                "Current bundle transitions must preserve the baseline sequence as an exact prefix.",
            )
        )
        appended: tuple[SpecTransition, ...] = ()
    else:
        appended = current_transitions[len(baseline_manifest.transitions) :]

    appended_sources = {item.from_source_path for item in appended}
    if any(item.to_bundle_path in appended_sources for item in appended):
        errors.append(
            _diagnostic(
                manifest_path,
                1,
                "SPEC_TRANSITION_CHAIN",
                "Transitions appended together must not form a multi-hop chain.",
            )
        )

    bundle_index = {bundle.path: bundle for bundle in bundles}
    root_depth = len(relative_root.parts)
    baseline_bundle_members: dict[Path, list[Path]] = {}
    for path in baseline_paths:
        if len(path.parts) != root_depth + 2 or path.suffix != ".md":
            continue
        bundle_path = Path(*path.parts[: root_depth + 1])
        baseline_bundle_members.setdefault(bundle_path, []).append(path)
    baseline_bundle_paths = set(baseline_bundle_members)
    authorizations: dict[Path, SpecTransition] = {
        transition.from_source_path: transition for transition in appended
    }
    used_authorizations: set[Path] = set()

    for bundle_path, member_paths in sorted(baseline_bundle_members.items()):
        root_status: str | None = None
        root_count = 0
        member_sources: list[tuple[Path, bytes]] = []
        for member_path in sorted(member_paths):
            source = _git_blob(repository, baseline_ref, member_path)
            if source is None:
                continue
            member_sources.append((member_path, source))
            try:
                text = source.decode("utf-8")
            except UnicodeDecodeError:
                continue
            values, _, diagnostics = parse_frontmatter(text, member_path)
            if (
                not diagnostics
                and values.get("schema") == BUNDLE_SCHEMA
                and values.get("role") == "root"
            ):
                root_count += 1
                status = values.get("status")
                root_status = status if isinstance(status, str) else None
        if root_count != 1 or root_status not in {"approved", "implemented"}:
            continue
        if bundle_path in bundle_index:
            for member_path, source in member_sources:
                try:
                    baseline_text = source.decode("utf-8")
                except UnicodeDecodeError:
                    continue
                baseline_history = _history_lines(baseline_text)
                if baseline_history is None:
                    continue
                try:
                    current_text = (repository / member_path).read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    current_text = ""
                current_history = _history_lines(current_text)
                if (
                    current_history is None
                    or current_history[: len(baseline_history)] != baseline_history
                ):
                    errors.append(
                        _diagnostic(
                            member_path,
                            1,
                            "SPEC_HISTORY_NOT_APPEND_ONLY",
                            "Decisions & History must preserve the baseline line sequence as an exact prefix.",
                        )
                    )
            continue

        digest = hashlib.sha256()

        def add_frame(value: bytes) -> None:
            digest.update(len(value).to_bytes(8, "big"))
            digest.update(value)

        add_frame(bundle_path.as_posix().encode("utf-8"))
        for member_path, source in sorted(member_sources, key=lambda item: item[0].as_posix()):
            add_frame(member_path.relative_to(bundle_path).as_posix().encode("utf-8"))
            add_frame(source)

        transition = authorizations.get(bundle_path)
        if transition is None:
            errors.append(
                _diagnostic(
                    bundle_path,
                    1,
                    "SPEC_HISTORY_NOT_APPEND_ONLY",
                    "An approved baseline Spec Bundle cannot be removed without a path transition.",
                )
            )
            continue
        used_authorizations.add(bundle_path)
        target = bundle_index.get(transition.to_bundle_path)
        binding_valid = (
            digest.hexdigest() == transition.from_source_sha256
            and target is not None
            and target.metadata.status in {"approved", "implemented"}
            and transition.to_bundle_path not in baseline_bundle_paths
            and not (repository / transition.from_source_path).exists()
        )
        if not binding_valid:
            errors.append(
                _diagnostic(
                    manifest_path,
                    1,
                    "SPEC_TRANSITION_FROM_BINDING",
                    "Transition bundle path, exact baseline bundle SHA-256, and active target must match.",
                )
            )

    for transition in baseline_manifest.transitions:
        if (repository / transition.from_source_path).exists():
            errors.append(
                _diagnostic(
                    transition.from_source_path,
                    1,
                    "SPEC_TRANSITION_OLD_SOURCE",
                    "A previously superseded source must not reappear in the current tree.",
                )
            )

    for path in baseline_paths:
        if path.name != "spec.md":
            continue
        source = _git_blob(repository, baseline_ref, path)
        if source is None:
            continue
        try:
            text = source.decode("utf-8")
        except UnicodeDecodeError:
            continue
        schema, _, status = _baseline_metadata(text, path)
        if schema != "forge/spec@2" or status not in {"approved", "implemented"}:
            continue
        if (repository / path).is_file():
            continue

        transition = authorizations.get(path)
        if transition is None:
            errors.append(
                _diagnostic(
                    path,
                    1,
                    "SPEC_HISTORY_NOT_APPEND_ONLY",
                    "An approved baseline source cannot be removed without a path transition.",
                )
            )
            continue
        used_authorizations.add(path)
        target = bundle_index.get(transition.to_bundle_path)
        binding_valid = (
            hashlib.sha256(source).hexdigest() == transition.from_source_sha256
            and target is not None
            and target.metadata.status in {"approved", "implemented"}
            and transition.to_bundle_path not in baseline_bundle_paths
            and not (repository / transition.from_source_path).exists()
        )
        if not binding_valid:
            errors.append(
                _diagnostic(
                    manifest_path,
                    1,
                    "SPEC_TRANSITION_FROM_BINDING",
                    "Transition source path, exact baseline SHA-256, and active target bundle must match.",
                )
            )

    for transition in appended:
        if transition.from_source_path not in used_authorizations:
            errors.append(
                _diagnostic(
                    manifest_path,
                    1,
                    "SPEC_TRANSITION_FROM_BINDING",
                    "Each appended transition must authorize one active source from the exact baseline.",
                )
            )


def _validate_bundle_repository(
    repository: Path,
    resolved_root: Path,
    relative_root: Path,
    baseline_ref: str | None = None,
) -> ValidationResult:
    bundles: list[SpecBundle] = []
    errors: list[Diagnostic] = []
    if resolved_root.is_dir():
        for directory in sorted(resolved_root.iterdir(), key=lambda item: item.name):
            if directory.name.startswith(".") or not directory.is_dir():
                continue
            relative_directory = relative_root / directory.name
            if directory.is_symlink():
                errors.append(
                    _diagnostic(
                        relative_directory,
                        1,
                        "BUNDLE_SOURCE_PATH_ESCAPE",
                        "A spec bundle directory must not be a symbolic link.",
                    )
                )
                continue
            errors.extend(_bundle_path_diagnostics(directory, relative_directory))
            errors.extend(_non_root_frontmatter_diagnostics(directory, relative_directory))
            bundle, diagnostics = load_spec_bundle(directory, repository)
            errors.extend(_mapped_bundle_diagnostic(item, repository) for item in diagnostics)
            if bundle is None:
                continue
            bundles.append(bundle)
            _validate_bundle_statements(bundle, errors)
            for member in bundle.members:
                _validate_links(member, repository, errors)
                _validate_mermaid(member, errors)

    ordered_bundles = tuple(sorted(bundles, key=lambda item: item.path.as_posix()))
    _validate_bundle_relations(ordered_bundles, errors)
    manifest, transition_diagnostics = load_transition_manifest(repository, relative_root)
    errors.extend(transition_diagnostics)
    if manifest is not None:
        known_paths = {bundle.path for bundle in ordered_bundles}
        for transition in manifest.transitions:
            if transition.to_bundle_path not in known_paths:
                errors.append(
                    _diagnostic(
                        relative_root / TRANSITION_MANIFEST_NAME,
                        1,
                        "SPEC_TRANSITION_TARGET_BUNDLE",
                        "Transition toBundlePath must identify one current Spec Bundle.",
                    )
                )
    if baseline_ref is not None:
        _validate_bundle_baseline(
            repository,
            relative_root,
            baseline_ref,
            ordered_bundles,
            manifest,
            errors,
        )
    return ValidationResult((), tuple(sorted(set(errors))), ordered_bundles)


def _diagnostic(path: Path | str, line: int, code: str, message: str) -> Diagnostic:
    value = path.as_posix() if isinstance(path, Path) else path
    return Diagnostic(value, line, code, message)


def _repository_path(path: Path, repo_root: Path) -> Path:
    try:
        return path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return path


def _resolved_spec_root(repo_root: Path, spec_root: Path) -> tuple[Path | None, Path | None]:
    repository = repo_root.resolve()
    candidate = spec_root.resolve() if spec_root.is_absolute() else (repository / spec_root).resolve()
    try:
        relative = candidate.relative_to(repository)
    except ValueError:
        return None, None
    return candidate, relative


def _validate_relations(
    documents: tuple[SpecDocument, ...], errors: list[Diagnostic]
) -> None:
    by_id: dict[str, list[SpecDocument]] = {}
    for document in documents:
        by_id.setdefault(document.metadata.id, []).append(document)

    for spec_id, matches in sorted(by_id.items()):
        if len(matches) > 1:
            for document in matches:
                errors.append(
                    _diagnostic(
                        document.path,
                        3,
                        "SPEC_DUPLICATE_ID",
                        f"Spec id '{spec_id}' appears more than once in the repository.",
                    )
                )

    known_ids = set(by_id)
    for document in documents:
        for relation in document.metadata.related_specs:
            if relation.id == document.metadata.id:
                errors.append(
                    _diagnostic(
                        document.path,
                        9,
                        "SPEC_RELATED_SELF",
                        f"Spec '{relation.id}' cannot relate to itself.",
                    )
                )
            elif relation.id not in known_ids:
                errors.append(
                    _diagnostic(
                        document.path,
                        9,
                        "SPEC_RELATED_MISSING",
                        f"Related spec '{relation.id}' does not exist.",
                    )
                )


def _validate_coverage(document: SpecDocument, errors: list[Diagnostic]) -> None:
    requirements = {item.id: item for item in document.requirements}
    covered: set[str] = set()
    for criterion in document.acceptance:
        for requirement_id in criterion.requirements:
            requirement = requirements.get(requirement_id)
            if requirement is None:
                errors.append(
                    _diagnostic(
                        document.path,
                        criterion.line,
                        "SPEC_AC_REFERENCE_MISSING",
                        f"Acceptance criterion '{criterion.id}' references missing '{requirement_id}'.",
                    )
                )
            elif requirement.removed:
                errors.append(
                    _diagnostic(
                        document.path,
                        criterion.line,
                        "SPEC_AC_REFERENCE_REMOVED",
                        f"Acceptance criterion '{criterion.id}' references removed '{requirement_id}'.",
                    )
                )
            else:
                covered.add(requirement_id)

    for requirement in document.requirements:
        if not requirement.removed and requirement.id not in covered:
            errors.append(
                _diagnostic(
                    document.path,
                    requirement.line,
                    "SPEC_REQUIREMENT_UNCOVERED",
                    f"Active requirement '{requirement.id}' is not covered by an acceptance criterion.",
                )
            )


def _validate_links(
    document: SpecDocument, repo_root: Path, errors: list[Diagnostic]
) -> None:
    source_path = repo_root / document.path
    try:
        lines = source_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return

    fence: str | None = None
    for line_number, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is not None:
            continue
        link_source = re.sub(r"`[^`]*`", "", line)
        for match in _MARKDOWN_LINK_RE.finditer(link_source):
            raw_target = match.group(1).strip()
            if raw_target.startswith("<") and raw_target.endswith(">"):
                raw_target = raw_target[1:-1]
            target = raw_target.split("#", 1)[0].split("?", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            candidate = (source_path.parent / target).resolve()
            try:
                candidate.relative_to(repo_root.resolve())
            except ValueError:
                exists = False
            else:
                exists = candidate.exists()
            if not exists:
                errors.append(
                    _diagnostic(
                        document.path,
                        line_number,
                        "SPEC_LINK_BROKEN",
                        f"Internal Markdown link target '{raw_target}' does not exist.",
                    )
                )


def _validate_mermaid(document: SpecDocument, errors: list[Diagnostic]) -> None:
    for block in document.mermaid:
        if not MERMAID_VALIDATOR_BUNDLE.is_file():
            errors.append(
                _diagnostic(
                    document.path,
                    block.line,
                    "SPEC_MERMAID_RUNTIME_UNAVAILABLE",
                    "The deployed Mermaid validator bundle is unavailable.",
                )
            )
            continue
        try:
            result = subprocess.run(
                [
                    "node",
                    str(MERMAID_VALIDATOR_BUNDLE),
                    "--stdin",
                    "--format",
                    "json",
                ],
                input=block.text.encode("utf-8"),
                capture_output=True,
                check=False,
            )
        except OSError:
            result = None
        if result is None:
            errors.append(
                _diagnostic(
                    document.path,
                    block.line,
                    "SPEC_MERMAID_RUNTIME_UNAVAILABLE",
                    "The deployed Mermaid validator runtime is unavailable.",
                )
            )
            continue
        if result.returncode not in {0, 1}:
            errors.append(
                _diagnostic(
                    document.path,
                    block.line,
                    "SPEC_MERMAID_RUNTIME_UNAVAILABLE",
                    "The deployed Mermaid validator returned an unsupported exit status.",
                )
            )
            continue
        try:
            encoded_output = result.stdout
            if not isinstance(encoded_output, (bytes, bytearray)):
                raise TypeError
            payload = json.loads(bytes(encoded_output).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError):
            payload = None
        if not isinstance(payload, dict) or not isinstance(payload.get("diagnostics"), list):
            errors.append(
                _diagnostic(
                    document.path,
                    block.line,
                    "SPEC_MERMAID_RUNTIME_UNAVAILABLE",
                    "The deployed Mermaid validator returned an invalid response.",
                )
            )
            continue
        if result.returncode == 0 and payload.get("valid") is True:
            continue
        diagnostics = payload["diagnostics"]
        if not diagnostics:
            errors.append(
                _diagnostic(
                    document.path,
                    block.line,
                    "SPEC_MERMAID_SYNTAX",
                    "Mermaid syntax is invalid.",
                )
            )
            continue
        for item in diagnostics:
            relative_line = item.get("line", 1) if isinstance(item, dict) else 1
            if not isinstance(relative_line, int) or relative_line < 1:
                relative_line = 1
            errors.append(
                _diagnostic(
                    document.path,
                    block.line + relative_line,
                    "SPEC_MERMAID_SYNTAX",
                    "Mermaid syntax is invalid.",
                )
            )


def _git_output(repo_root: Path, arguments: list[str]) -> subprocess.CompletedProcess[bytes] | None:
    try:
        return subprocess.run(
            ["git", "-C", str(repo_root), *arguments],
            capture_output=True,
            check=False,
        )
    except OSError:
        return None


def _baseline_metadata(
    text: str, path: Path
) -> tuple[str | None, str | None, str | None]:
    values, _, errors = parse_frontmatter(text, path)
    if errors or values.get("schema") != "forge/spec@2":
        return None, None, None
    spec_id = values.get("id")
    status = values.get("status")
    return (
        "forge/spec@2",
        spec_id if isinstance(spec_id, str) else None,
        status if isinstance(status, str) else None,
    )


def _history_lines(text: str) -> tuple[str, ...] | None:
    lines = text.splitlines()
    try:
        start = lines.index("## Decisions & History") + 1
    except ValueError:
        return None
    return tuple(lines[start:])


def _git_blob(repo_root: Path, baseline_ref: str, path: Path) -> bytes | None:
    result = _git_output(repo_root, ["show", f"{baseline_ref}:{path.as_posix()}"])
    if result is None or result.returncode != 0:
        return None
    return result.stdout


def _transition_structure_diagnostics(
    manifest: TransitionManifest,
    manifest_path: Path,
    errors: list[Diagnostic],
) -> None:
    source_ids: set[str] = set()
    source_paths: set[Path] = set()
    target_ids: set[str] = set()
    target_paths: set[Path] = set()
    for transition in manifest.transitions:
        if transition.from_id in source_ids or transition.from_path in source_paths:
            errors.append(
                _diagnostic(
                    manifest_path,
                    1,
                    "SPEC_TRANSITION_DUPLICATE_SOURCE",
                    "Transition source identities and paths must be unique.",
                )
            )
        if transition.to_id in target_ids or transition.to_path in target_paths:
            errors.append(
                _diagnostic(
                    manifest_path,
                    1,
                    "SPEC_TRANSITION_DUPLICATE_TARGET",
                    "Transition target identities and paths must be unique.",
                )
            )
        source_ids.add(transition.from_id)
        source_paths.add(transition.from_path)
        target_ids.add(transition.to_id)
        target_paths.add(transition.to_path)

def _old_identity_references(
    repo_root: Path,
    documents: tuple[SpecDocument, ...],
    transition: SpecTransition,
) -> tuple[Path, ...]:
    references: set[Path] = set()
    old_directory = transition.from_path.parent.as_posix()
    for document in documents:
        if document.metadata.status not in {"approved", "implemented"}:
            continue
        if any(
            relation.id == transition.from_id
            for relation in document.metadata.related_specs
        ):
            references.add(document.path)
        try:
            source = (repo_root / document.path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for match in _MARKDOWN_LINK_RE.finditer(source):
            raw_target = match.group(1).strip().strip("<>")
            target = raw_target.split("#", 1)[0].split("?", 1)[0]
            if transition.from_id in target or old_directory in target:
                references.add(document.path)
                break
    return tuple(sorted(references))


def _validate_baseline(
    repo_root: Path,
    spec_root: Path,
    baseline_ref: str,
    documents: tuple[SpecDocument, ...],
    current_manifest: TransitionManifest | None,
    errors: list[Diagnostic],
) -> None:
    if not (repo_root / ".git").exists():
        errors.append(
            _diagnostic(
                spec_root,
                1,
                "SPEC_BASELINE_UNAVAILABLE",
                "A Git repository is required for baseline validation.",
            )
        )
        return
    listing = _git_output(
        repo_root,
        ["ls-tree", "-r", "--name-only", baseline_ref, "--", spec_root.as_posix()],
    )
    if listing is None or listing.returncode != 0:
        errors.append(
            _diagnostic(
                spec_root,
                1,
                "SPEC_BASELINE_UNAVAILABLE",
                "The requested Git baseline cannot be read.",
            )
        )
        return

    baseline_paths = sorted(
        Path(item.decode("utf-8"))
        for item in listing.stdout.splitlines()
        if item.decode("utf-8").endswith("/spec.md")
    )
    manifest_path = spec_root / ".transitions.json"
    baseline_manifest_source = _git_blob(repo_root, baseline_ref, manifest_path)
    if baseline_manifest_source is None:
        baseline_manifest = TransitionManifest(())
        baseline_manifest_ok = True
    else:
        baseline_manifest, manifest_diagnostics = load_transition_manifest(
            repo_root,
            spec_root,
            source=baseline_manifest_source,
        )
        errors.extend(manifest_diagnostics)
        baseline_manifest_ok = baseline_manifest is not None
        if baseline_manifest is None:
            baseline_manifest = TransitionManifest(())

    if current_manifest is None:
        current_transitions: tuple[SpecTransition, ...] = ()
    else:
        current_transitions = current_manifest.transitions

    prefix_ok = (
        baseline_manifest_ok
        and current_transitions[: len(baseline_manifest.transitions)]
        == baseline_manifest.transitions
    )
    if not prefix_ok:
        errors.append(
            _diagnostic(
                manifest_path,
                1,
                "SPEC_TRANSITION_BASELINE_PREFIX",
                "Current transitions must preserve the canonical baseline sequence as an exact prefix.",
            )
        )
        appended: tuple[SpecTransition, ...] = ()
    else:
        appended = current_transitions[len(baseline_manifest.transitions) :]
    if len(appended) > 1:
        errors.append(
            _diagnostic(
                manifest_path,
                1,
                "SPEC_TRANSITION_APPEND",
                "A change may append at most one spec transition record.",
            )
        )

    appended_source_ids = {transition.from_id for transition in appended}
    appended_source_paths = {transition.from_path for transition in appended}
    if any(
        transition.to_id in appended_source_ids
        or transition.to_path in appended_source_paths
        for transition in appended
    ):
        errors.append(
            _diagnostic(
                manifest_path,
                1,
                "SPEC_TRANSITION_CHAIN",
                "Transition records appended in the same change cannot form a multi-hop chain.",
            )
        )

    baseline_path_set = set(baseline_paths)
    documents_by_path = {document.path: document for document in documents}
    newly_authorized = appended if len(appended) == 1 else ()
    valid_authorizations: set[Path] = set()

    for transition in baseline_manifest.transitions:
        if (repo_root / transition.from_path).is_file():
            errors.append(
                _diagnostic(
                    transition.from_path,
                    1,
                    "SPEC_TRANSITION_OLD_SOURCE",
                    f"Superseded source '{transition.from_id}' cannot reappear in the current tree.",
                )
            )
        for reference in _old_identity_references(repo_root, documents, transition):
            errors.append(
                _diagnostic(
                    reference,
                    1,
                    "SPEC_TRANSITION_OLD_REFERENCE",
                    f"Active spec references superseded identity '{transition.from_id}'.",
                )
            )

    for transition in newly_authorized:
        transition_valid = True
        from_source = _git_blob(repo_root, baseline_ref, transition.from_path)
        if from_source is None:
            transition_valid = False
            errors.append(
                _diagnostic(
                    manifest_path,
                    1,
                    "SPEC_TRANSITION_FROM_BINDING",
                    "Transition fromPath must identify an exact baseline spec source.",
                )
            )
        else:
            try:
                from_text = from_source.decode("utf-8")
            except UnicodeDecodeError:
                from_text = ""
            from_schema, from_id, from_status = _baseline_metadata(
                from_text, transition.from_path
            )
            if (
                from_schema != "forge/spec@2"
                or from_status not in {"approved", "implemented"}
                or from_id != transition.from_id
                or transition.from_path.parent.name != transition.from_id
                or hashlib.sha256(from_source).hexdigest()
                != transition.from_source_sha256
            ):
                transition_valid = False
                errors.append(
                    _diagnostic(
                        manifest_path,
                        1,
                        "SPEC_TRANSITION_FROM_BINDING",
                        "Transition source ID, path, status, and SHA-256 must match the exact baseline bytes.",
                    )
                )

        if (repo_root / transition.from_path).is_file():
            transition_valid = False
            errors.append(
                _diagnostic(
                    manifest_path,
                    1,
                    "SPEC_TRANSITION_FROM_BINDING",
                    "A superseded source must be absent from the current tree.",
                )
            )

        if transition.to_path in baseline_path_set:
            transition_valid = False
            errors.append(
                _diagnostic(
                    manifest_path,
                    1,
                    "SPEC_TRANSITION_TARGET_BASELINE",
                    "A supersession target must not already exist in the baseline.",
                )
            )

        target = documents_by_path.get(transition.to_path)
        if (
            target is None
            or target.metadata.id != transition.to_id
            or transition.to_path.parent.name != transition.to_id
            or target.metadata.status not in {"approved", "implemented"}
        ):
            transition_valid = False
            errors.append(
                _diagnostic(
                    manifest_path,
                    1,
                    "SPEC_TRANSITION_TO_BINDING",
                    "Transition target ID, path, directory, and active status must match the current source.",
                )
            )

        old_references = _old_identity_references(repo_root, documents, transition)
        for reference in old_references:
            transition_valid = False
            errors.append(
                _diagnostic(
                    reference,
                    1,
                    "SPEC_TRANSITION_OLD_REFERENCE",
                    f"Active spec references superseded identity '{transition.from_id}'.",
                )
            )

        if transition_valid:
            valid_authorizations.add(transition.from_path)

    for path in baseline_paths:
        baseline_source = _git_blob(repo_root, baseline_ref, path)
        if baseline_source is None:
            continue
        try:
            baseline_text = baseline_source.decode("utf-8")
        except UnicodeDecodeError:
            continue
        schema, baseline_id, status = _baseline_metadata(baseline_text, path)
        if schema != "forge/spec@2" or status not in {"approved", "implemented"}:
            continue
        current_path = repo_root / path
        if not current_path.is_file():
            if path in valid_authorizations:
                continue
            if any(
                transition.from_path == path
                for transition in baseline_manifest.transitions
            ):
                errors.append(
                    _diagnostic(
                        manifest_path,
                        1,
                        "SPEC_TRANSITION_REPLAY",
                        "A baseline transition record cannot be reused to authorize a new deletion.",
                    )
                )
            errors.append(
                _diagnostic(
                    path,
                    1,
                    "SPEC_HISTORY_NOT_APPEND_ONLY",
                    "An approved or implemented baseline spec cannot be deleted or renamed.",
                )
            )
            continue
        try:
            current_text = current_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        baseline_history = _history_lines(baseline_text)
        current_history = _history_lines(current_text)
        if (
            baseline_history is None
            or current_history is None
            or current_history[: len(baseline_history)] != baseline_history
        ):
            errors.append(
                _diagnostic(
                    path,
                    1,
                    "SPEC_HISTORY_NOT_APPEND_ONLY",
                    "Decisions & History must preserve the baseline line sequence as an exact prefix.",
                )
            )


def validate_repository(
    repo_root: Path,
    spec_root: Path = Path("docs/specs"),
    baseline_ref: str | None = None,
) -> ValidationResult:
    """Validate every structured spec below ``spec_root`` in ``repo_root``."""

    repository = repo_root.resolve()
    resolved_root, relative_root = _resolved_spec_root(repository, spec_root)
    if resolved_root is None or relative_root is None:
        diagnostic = _diagnostic(
            spec_root,
            1,
            "SPEC_ROOT_PATH_ESCAPE",
            "The spec root must remain inside the repository root.",
        )
        return ValidationResult((), (diagnostic,))

    if _bundle_repository_mode(resolved_root):
        return _validate_bundle_repository(
            repository,
            resolved_root,
            relative_root,
            baseline_ref,
        )

    documents: list[SpecDocument] = []
    errors: list[Diagnostic] = []
    if resolved_root.is_dir():
        for path in sorted(resolved_root.rglob("spec.md")):
            lexical_path = relative_root / path.relative_to(resolved_root)
            try:
                path.resolve().relative_to(repository)
                path.resolve().relative_to(resolved_root)
            except ValueError:
                errors.append(
                    _diagnostic(
                        lexical_path,
                        1,
                        "SPEC_SOURCE_PATH_ESCAPE",
                        "A structured spec source must resolve inside its repository spec root.",
                    )
                )
                continue
            document, parse_errors = load_spec(path, repository)
            errors.extend(parse_errors)
            if document is not None:
                documents.append(document)
                relative_to_spec_root = path.resolve().relative_to(resolved_root)
                if len(relative_to_spec_root.parts) != 2:
                    errors.append(
                        _diagnostic(
                            document.path,
                            1,
                            "SPEC_PATH_LAYOUT",
                            "A structured spec must be located directly at NNN-slug/spec.md below the spec root.",
                        )
                    )

    ordered_documents = tuple(sorted(documents, key=lambda item: item.path.as_posix()))
    current_manifest, transition_diagnostics = load_transition_manifest(
        repository, relative_root
    )
    errors.extend(transition_diagnostics)
    if current_manifest is not None:
        _transition_structure_diagnostics(
            current_manifest,
            relative_root / ".transitions.json",
            errors,
        )
    _validate_relations(ordered_documents, errors)
    for document in ordered_documents:
        _validate_coverage(document, errors)
        _validate_links(document, repository, errors)
        _validate_mermaid(document, errors)

    if baseline_ref is not None:
        _validate_baseline(
            repository,
            relative_root,
            baseline_ref,
            ordered_documents,
            current_manifest,
            errors,
        )

    return ValidationResult(ordered_documents, tuple(sorted(errors)))


def _plan_path(plan: Path, repo_root: Path) -> Path:
    try:
        return plan.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return plan


def _parse_item_array(
    raw: str,
    prefix: str,
    path: Path,
    line: int,
    errors: list[Diagnostic],
) -> tuple[str, ...]:
    match = re.fullmatch(r"\[(.*)\]", raw)
    if match is None:
        errors.append(
            _diagnostic(path, line, "PLAN_SPEC_FORMAT", f"{prefix} must use a bracketed ID list.")
        )
        return ()
    content = match.group(1).strip()
    if not content:
        return ()
    result: list[str] = []
    for token in (item.strip() for item in content.split(",")):
        if "–" in token or "-" in token:
            errors.append(
                _diagnostic(
                    path,
                    line,
                    "PLAN_SPEC_RANGE_FORBIDDEN",
                    "Top-level Related Specs arrays must list explicit IDs.",
                )
            )
        elif _ITEM_RE.fullmatch(token) is None or not token.startswith(prefix):
            errors.append(
                _diagnostic(
                    path,
                    line,
                    "PLAN_SPEC_ITEM_FORMAT",
                    f"{prefix} references must use explicit {prefix}<number> IDs.",
                )
            )
        else:
            result.append(token)
    return tuple(result)


def parse_plan_related_specs(
    plan: Path, repo_root: Path
) -> tuple[tuple[PlanSpecRef, ...], tuple[Diagnostic, ...]]:
    """Parse and resolve the canonical Related Specs block from one plan."""

    repository = repo_root.resolve()
    try:
        relative_plan = plan.resolve().relative_to(repository)
    except ValueError:
        diagnostic_path = Path(plan.name)
        return (), (
            _diagnostic(
                diagnostic_path,
                1,
                "PLAN_SPEC_PATH_ESCAPE",
                "The plan source must resolve inside the repository root.",
            ),
        )
    errors: list[Diagnostic] = []
    try:
        lines = plan.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return (), (
            _diagnostic(relative_plan, 1, "PLAN_SPEC_READ", "The plan must be readable UTF-8."),
        )

    marker_index = next(
        (index for index, line in enumerate(lines) if line.startswith("**Related Specs:**")),
        None,
    )
    if marker_index is None:
        return (), (
            _diagnostic(
                relative_plan,
                1,
                "PLAN_SPEC_BLOCK_MISSING",
                "The canonical Related Specs block is missing.",
            ),
        )
    marker = lines[marker_index]
    if re.fullmatch(r"\*\*Related Specs:\*\* None — \S.*", marker):
        return (), ()
    if marker != "**Related Specs:**":
        return (), (
            _diagnostic(
                relative_plan,
                marker_index + 1,
                "PLAN_SPEC_FORMAT",
                "The Related Specs marker is malformed.",
            ),
        )

    refs: list[PlanSpecRef] = []
    seen: set[str] = set()
    index = marker_index + 1
    while index < len(lines) and lines[index].startswith("- id: "):
        start_line = index + 1
        if index + 3 >= len(lines):
            errors.append(
                _diagnostic(relative_plan, start_line, "PLAN_SPEC_FORMAT", "Related Specs entry is incomplete.")
            )
            break
        id_line, path_line, requirements_line, acceptance_line = lines[index : index + 4]
        if not (
            path_line.startswith("  path: ")
            and requirements_line.startswith("  requirements: ")
            and acceptance_line.startswith("  acceptance: ")
        ):
            errors.append(
                _diagnostic(relative_plan, start_line, "PLAN_SPEC_FORMAT", "Related Specs fields are malformed.")
            )
            index += 4
            continue
        spec_id = id_line.removeprefix("- id: ")
        raw_path = path_line.removeprefix("  path: ")
        requirements = _parse_item_array(
            requirements_line.removeprefix("  requirements: "),
            "R",
            relative_plan,
            index + 3,
            errors,
        )
        acceptance = _parse_item_array(
            acceptance_line.removeprefix("  acceptance: "),
            "AC",
            relative_plan,
            index + 4,
            errors,
        )
        if _PLAN_ID_RE.fullmatch(spec_id) is None:
            errors.append(
                _diagnostic(relative_plan, start_line, "PLAN_SPEC_ID", "Related spec id is invalid.")
            )
        if spec_id in seen:
            errors.append(
                _diagnostic(
                    relative_plan,
                    start_line,
                    "PLAN_SPEC_DUPLICATE",
                    f"Related spec '{spec_id}' is duplicated.",
                )
            )
        seen.add(spec_id)

        supplied_path = Path(raw_path)
        target = supplied_path.resolve() if supplied_path.is_absolute() else (repository / supplied_path).resolve()
        try:
            repository_path = target.relative_to(repository)
        except ValueError:
            errors.append(
                _diagnostic(
                    relative_plan,
                    index + 2,
                    "PLAN_SPEC_PATH_ESCAPE",
                    "Related spec path must remain inside the repository.",
                )
            )
            index += 4
            continue
        if not target.is_file():
            errors.append(
                _diagnostic(
                    relative_plan,
                    index + 2,
                    "PLAN_SPEC_MISSING",
                    f"Related spec path '{repository_path.as_posix()}' does not exist.",
                )
            )
            index += 4
            continue
        document, parse_errors = load_spec(target, repository)
        if document is None:
            errors.append(
                _diagnostic(
                    relative_plan,
                    index + 2,
                    "PLAN_SPEC_INVALID",
                    f"Related spec '{repository_path.as_posix()}' is invalid.",
                )
            )
            errors.extend(parse_errors)
            index += 4
            continue
        if document.metadata.id != spec_id:
            errors.append(
                _diagnostic(
                    relative_plan,
                    start_line,
                    "PLAN_SPEC_ID_PATH_MISMATCH",
                    f"Related spec id '{spec_id}' does not match '{document.metadata.id}'.",
                )
            )
        if document.metadata.status not in {"approved", "implemented"}:
            errors.append(
                _diagnostic(
                    relative_plan,
                    start_line,
                    "PLAN_SPEC_STATUS",
                    f"Related spec '{spec_id}' must be approved or implemented.",
                )
            )
        requirement_ids = {item.id for item in document.requirements if not item.removed}
        acceptance_ids = {item.id for item in document.acceptance}
        for item_id in requirements:
            if item_id not in requirement_ids:
                errors.append(
                    _diagnostic(
                        relative_plan,
                        index + 3,
                        "PLAN_SPEC_REQUIREMENT_MISSING",
                        f"Related spec '{spec_id}' has no active '{item_id}'.",
                    )
                )
        for item_id in acceptance:
            if item_id not in acceptance_ids:
                errors.append(
                    _diagnostic(
                        relative_plan,
                        index + 4,
                        "PLAN_SPEC_ACCEPTANCE_MISSING",
                        f"Related spec '{spec_id}' has no '{item_id}'.",
                    )
                )
        refs.append(PlanSpecRef(spec_id, repository_path, requirements, acceptance))
        index += 4

    if not refs and not errors:
        errors.append(
            _diagnostic(
                relative_plan,
                marker_index + 1,
                "PLAN_SPEC_FORMAT",
                "A bare Related Specs block must contain an entry or use 'None — <reason>'.",
            )
        )

    sorted_errors = tuple(sorted(errors))
    return (() if sorted_errors else tuple(refs)), sorted_errors
