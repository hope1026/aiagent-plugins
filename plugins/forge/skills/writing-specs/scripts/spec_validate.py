"""Repository-wide validation for semantic Spec Bundles."""

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
    SpecMember,
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
class ValidationResult:
    bundles: tuple[SpecBundle, ...]
    diagnostics: tuple[Diagnostic, ...]

    @property
    def ok(self) -> bool:
        return not self.diagnostics


def _normalized_statement_heading(heading: str) -> str:
    return " ".join(unicodedata.normalize("NFC", heading).casefold().split())


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
    acceptance_section_count = sum(
        member.section_order.count("Acceptance Criteria") for member in bundle.members
    )
    if not requirements:
        errors.append(
            _diagnostic(
                bundle.root_path,
                1,
                "BUNDLE_REQUIREMENTS_MISSING",
                "A spec bundle must contain at least one Requirement statement.",
            )
        )
    if acceptance_section_count and not acceptance:
        errors.append(
            _diagnostic(
                bundle.root_path,
                1,
                "BUNDLE_ACCEPTANCE_EMPTY",
                "An Acceptance Criteria section must contain at least one Acceptance statement.",
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

    if acceptance:
        for requirement in requirements:
            if (requirement.member_path, requirement.heading) not in covered:
                errors.append(
                    _diagnostic(
                        requirement.member_path,
                        requirement.line,
                        "STATEMENT_COVERAGE",
                        "Every Requirement statement must be verified when Acceptance Criteria is present.",
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
        current_bundle = bundle_index.get(bundle_path)
        if current_bundle is not None:
            if current_bundle.metadata.status == "draft":
                errors.append(
                    _diagnostic(
                        current_bundle.root_path,
                        1,
                        "SPEC_ACTIVE_STATUS_DOWNGRADE",
                        "An approved or implemented baseline Spec Bundle cannot be demoted to draft at the same path.",
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
                    "SPEC_TRANSITION_REQUIRED",
                    "An approved baseline Spec Bundle cannot be removed without an exact path transition.",
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
    return ValidationResult(ordered_bundles, tuple(sorted(set(errors))))


def _diagnostic(path: Path | str, line: int, code: str, message: str) -> Diagnostic:
    value = path.as_posix() if isinstance(path, Path) else path
    return Diagnostic(value, line, code, message)


def _resolved_spec_root(repo_root: Path, spec_root: Path) -> tuple[Path | None, Path | None]:
    repository = repo_root.resolve()
    candidate = spec_root.resolve() if spec_root.is_absolute() else (repository / spec_root).resolve()
    try:
        relative = candidate.relative_to(repository)
    except ValueError:
        return None, None
    return candidate, relative


def _validate_links(
    document: SpecMember, repo_root: Path, errors: list[Diagnostic]
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


def _validate_mermaid(document: SpecMember, errors: list[Diagnostic]) -> None:
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


def _git_blob(repo_root: Path, baseline_ref: str, path: Path) -> bytes | None:
    result = _git_output(repo_root, ["show", f"{baseline_ref}:{path.as_posix()}"])
    if result is None or result.returncode != 0:
        return None
    return result.stdout


def validate_repository(
    repo_root: Path,
    spec_root: Path = Path("docs/specs"),
    baseline_ref: str | None = None,
) -> ValidationResult:
    """Validate every semantic Spec Bundle below ``spec_root``."""

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
    return _validate_bundle_repository(
        repository,
        resolved_root,
        relative_root,
        baseline_ref,
    )
