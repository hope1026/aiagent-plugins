"""Strict parser for the append-only spec bundle transition manifest."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
import stat

from spec_model import Diagnostic


SCHEMA = "forge/spec-bundle-transitions@1"
MANIFEST_NAME = ".bundle-transitions.json"
TOP_LEVEL_KEYS = ("schema", "transitions")
RECORD_KEYS = (
    "fromSourcePath",
    "fromSourceSha256",
    "disposition",
    "toBundlePath",
    "evidencePath",
    "reason",
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SEMANTIC_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")
_ALLOWED_DISPOSITIONS = frozenset({"superseded", "merged"})


@dataclass(frozen=True)
class SpecBundleTransition:
    from_source_path: Path
    from_source_sha256: str
    disposition: str
    to_bundle_path: Path
    evidence_path: Path
    reason: str


# Keep the neutral public type name used by repository validation while its
# fields and manifest representation remain strictly path-based.
SpecTransition = SpecBundleTransition


@dataclass(frozen=True)
class TransitionManifest:
    transitions: tuple[SpecBundleTransition, ...]


class _ObjectPairs(list[tuple[str, object]]):
    """JSON object representation that preserves duplicate keys."""


def _diagnostic(path: Path, code: str, message: str) -> Diagnostic:
    return Diagnostic(path.as_posix(), 1, code, message)


def _path_has_symlink(repo_root: Path, relative_path: PurePosixPath) -> bool:
    current = repo_root
    for index, component in enumerate(relative_path.parts):
        current = current / component
        try:
            mode = current.lstat().st_mode
        except (FileNotFoundError, OSError):
            return False
        if stat.S_ISLNK(mode):
            return True
        if index < len(relative_path.parts) - 1 and not stat.S_ISDIR(mode):
            return False
    return False


def _manifest_source(
    repo_root: Path, manifest_path: Path
) -> tuple[bytes | None, tuple[Diagnostic, ...]]:
    relative = PurePosixPath(manifest_path.as_posix())
    absolute = repo_root / manifest_path

    if _path_has_symlink(repo_root, relative):
        return None, (
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_MANIFEST_PATH",
                "The transition manifest and its path components must not be symlinks.",
            ),
        )

    try:
        mode = absolute.lstat().st_mode
    except FileNotFoundError:
        return None, ()
    except OSError as error:
        return None, (
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_MANIFEST_PATH",
                f"The transition manifest cannot be inspected: {error.__class__.__name__}.",
            ),
        )

    if not stat.S_ISREG(mode):
        return None, (
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_MANIFEST_PATH",
                "The transition manifest must be a regular file.",
            ),
        )

    try:
        return absolute.read_bytes(), ()
    except OSError as error:
        return None, (
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_MANIFEST_PATH",
                f"The transition manifest cannot be read: {error.__class__.__name__}.",
            ),
        )


def _exact_object(
    value: object,
    keys: tuple[str, ...],
    manifest_path: Path,
    context: str,
    diagnostics: list[Diagnostic],
) -> dict[str, object] | None:
    if not isinstance(value, _ObjectPairs):
        diagnostics.append(
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_TYPE",
                f"{context} must be a JSON object.",
            )
        )
        return None

    names = [name for name, _ in value]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    missing = sorted(set(keys) - set(names))
    unknown = sorted(set(names) - set(keys))
    for name in duplicates:
        diagnostics.append(
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_KEY",
                f"{context} key '{name}' is duplicated.",
            )
        )
    for name in missing:
        diagnostics.append(
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_KEY",
                f"{context} key '{name}' is required.",
            )
        )
    for name in unknown:
        diagnostics.append(
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_KEY",
                f"{context} key '{name}' is not allowed.",
            )
        )
    if duplicates or missing or unknown:
        return None
    return dict(value)


def _normalized_path(
    raw_path: str,
    field: str,
    manifest_path: Path,
    diagnostics: list[Diagnostic],
) -> PurePosixPath | None:
    parts = raw_path.split("/")
    invalid_shape = (
        raw_path.startswith("/")
        or _WINDOWS_DRIVE_RE.match(raw_path) is not None
        or "\\" in raw_path
        or "\x00" in raw_path
        or any(component in ("", ".", "..") for component in parts)
    )
    if invalid_shape:
        diagnostics.append(
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_PATH",
                f"Transition field '{field}' must be a normalized repository-relative POSIX path.",
            )
        )
        return None
    return PurePosixPath(raw_path)


def _has_prefix(path: PurePosixPath, root: PurePosixPath) -> bool:
    return path.parts[: len(root.parts)] == root.parts


def _parse_path(
    raw_path: str,
    field: str,
    repo_root: Path,
    spec_root: PurePosixPath,
    manifest_path: Path,
    diagnostics: list[Diagnostic],
) -> Path | None:
    path = _normalized_path(raw_path, field, manifest_path, diagnostics)
    if path is None:
        return None

    if field == "fromSourcePath":
        allowed = _has_prefix(path, spec_root) and (
            len(path.parts) == len(spec_root.parts) + 1
            and _SEMANTIC_NAME_RE.fullmatch(path.name) is not None
        )
    elif field == "toBundlePath":
        allowed = (
            _has_prefix(path, spec_root)
            and len(path.parts) == len(spec_root.parts) + 1
            and _SEMANTIC_NAME_RE.fullmatch(path.name) is not None
        )
    else:
        allowed_roots = (
            PurePosixPath("docs/plans"),
            PurePosixPath("docs/adr"),
            PurePosixPath("docs/evidence"),
        )
        allowed = any(
            _has_prefix(path, root) and len(path.parts) > len(root.parts)
            for root in allowed_roots
        )

    if not allowed:
        diagnostics.append(
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_PATH",
                f"Transition field '{field}' is outside its allowed root or file layout.",
            )
        )
        return None

    if _path_has_symlink(repo_root, path):
        diagnostics.append(
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_PATH_SYMLINK",
                f"Transition field '{field}' contains a symlink path component.",
            )
        )
        return None

    absolute = repo_root / Path(*path.parts)
    if field == "evidencePath":
        try:
            mode = absolute.lstat().st_mode
        except OSError:
            mode = 0
        if not stat.S_ISREG(mode):
            diagnostics.append(
                _diagnostic(
                    manifest_path,
                    "SPEC_TRANSITION_EVIDENCE",
                    "Transition evidencePath must identify an existing regular file.",
                )
            )
            return None
    elif field == "toBundlePath":
        try:
            mode = absolute.lstat().st_mode
        except FileNotFoundError:
            mode = 0
        except OSError:
            mode = 0
        if mode and not stat.S_ISDIR(mode):
            diagnostics.append(
                _diagnostic(
                    manifest_path,
                    "SPEC_TRANSITION_PATH",
                    "Transition field 'toBundlePath' must identify a bundle directory when it exists.",
                )
            )
            return None

    return Path(*path.parts)


def load_transition_manifest(
    repo_root: Path,
    spec_root: Path,
    *,
    source: bytes | None = None,
) -> tuple[TransitionManifest | None, tuple[Diagnostic, ...]]:
    """Load and strictly validate a path-based bundle transition manifest.

    ``source`` lets repository validation parse exact Git-object bytes. When it
    is omitted, only a regular, non-symlink manifest file is read.
    """

    manifest_path = spec_root / MANIFEST_NAME
    if source is None:
        source, source_diagnostics = _manifest_source(repo_root, manifest_path)
        if source_diagnostics or source is None:
            return None, source_diagnostics

    diagnostics: list[Diagnostic] = []
    try:
        text = source.decode("utf-8")
        payload = json.loads(text, object_pairs_hook=_ObjectPairs)
    except (UnicodeDecodeError, json.JSONDecodeError):
        diagnostics.append(
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_JSON",
                "The transition manifest must be valid UTF-8 JSON.",
            )
        )
        return None, tuple(diagnostics)

    top_level = _exact_object(
        payload,
        TOP_LEVEL_KEYS,
        manifest_path,
        "Transition manifest",
        diagnostics,
    )
    if top_level is None:
        return None, tuple(sorted(diagnostics))

    schema = top_level["schema"]
    transitions = top_level["transitions"]
    if not isinstance(schema, str):
        diagnostics.append(
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_TYPE",
                "Transition manifest schema must be a string.",
            )
        )
    elif schema != SCHEMA:
        diagnostics.append(
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_SCHEMA",
                f"Transition manifest schema must be '{SCHEMA}'.",
            )
        )
    if not isinstance(transitions, list) or isinstance(transitions, _ObjectPairs):
        diagnostics.append(
            _diagnostic(
                manifest_path,
                "SPEC_TRANSITION_TYPE",
                "Transition manifest transitions must be a JSON array.",
            )
        )
        return None, tuple(sorted(diagnostics))

    parsed: list[SpecBundleTransition] = []
    spec_root_posix = PurePosixPath(spec_root.as_posix())
    seen_sources: set[Path] = set()
    for index, item in enumerate(transitions):
        context = f"Transition record {index}"
        record = _exact_object(
            item,
            RECORD_KEYS,
            manifest_path,
            context,
            diagnostics,
        )
        if record is None:
            continue

        wrong_types = [key for key in RECORD_KEYS if not isinstance(record[key], str)]
        for key in wrong_types:
            diagnostics.append(
                _diagnostic(
                    manifest_path,
                    "SPEC_TRANSITION_TYPE",
                    f"{context} field '{key}' must be a string.",
                )
            )
        if wrong_types:
            continue

        typed = {key: str(record[key]) for key in RECORD_KEYS}
        empty_fields = [key for key, value in typed.items() if not value.strip()]
        for key in empty_fields:
            diagnostics.append(
                _diagnostic(
                    manifest_path,
                    "SPEC_TRANSITION_VALUE",
                    f"{context} field '{key}' must not be empty.",
                )
            )
        if empty_fields:
            continue

        record_error_count = len(diagnostics)
        if typed["disposition"] not in _ALLOWED_DISPOSITIONS:
            diagnostics.append(
                _diagnostic(
                    manifest_path,
                    "SPEC_TRANSITION_DISPOSITION",
                    f"{context} disposition must be 'superseded' or 'merged'.",
                )
            )
        if _SHA256_RE.fullmatch(typed["fromSourceSha256"]) is None:
            diagnostics.append(
                _diagnostic(
                    manifest_path,
                    "SPEC_TRANSITION_SHA256",
                    f"{context} fromSourceSha256 must be 64 lowercase hexadecimal characters.",
                )
            )

        from_source_path = _parse_path(
            typed["fromSourcePath"],
            "fromSourcePath",
            repo_root,
            spec_root_posix,
            manifest_path,
            diagnostics,
        )
        to_bundle_path = _parse_path(
            typed["toBundlePath"],
            "toBundlePath",
            repo_root,
            spec_root_posix,
            manifest_path,
            diagnostics,
        )
        evidence_path = _parse_path(
            typed["evidencePath"],
            "evidencePath",
            repo_root,
            spec_root_posix,
            manifest_path,
            diagnostics,
        )
        if len(diagnostics) != record_error_count:
            continue

        assert from_source_path is not None
        assert to_bundle_path is not None
        assert evidence_path is not None
        if from_source_path in seen_sources:
            diagnostics.append(
                _diagnostic(
                    manifest_path,
                    "SPEC_TRANSITION_DUPLICATE",
                    f"{context} repeats fromSourcePath '{from_source_path.as_posix()}'.",
                )
            )
        seen_sources.add(from_source_path)
        parsed.append(
            SpecBundleTransition(
                from_source_path=from_source_path,
                from_source_sha256=typed["fromSourceSha256"],
                disposition=typed["disposition"],
                to_bundle_path=to_bundle_path,
                evidence_path=evidence_path,
                reason=typed["reason"],
            )
        )

    target_groups: dict[Path, list[SpecBundleTransition]] = {}
    for transition in parsed:
        target_groups.setdefault(transition.to_bundle_path, []).append(transition)

    for target, group in sorted(target_groups.items()):
        if len(group) == 1 and group[0].disposition == "merged":
            diagnostics.append(
                _diagnostic(
                    manifest_path,
                    "SPEC_TRANSITION_MERGE_GROUP",
                    f"Merged target '{target.as_posix()}' requires at least two records.",
                )
            )
            continue
        if len(group) > 1:
            if any(item.disposition != "merged" for item in group):
                diagnostics.append(
                    _diagnostic(
                        manifest_path,
                        "SPEC_TRANSITION_DUPLICATE",
                        f"Repeated target '{target.as_posix()}' is allowed only for merged records.",
                    )
                )
            elif len({item.evidence_path for item in group}) != 1:
                diagnostics.append(
                    _diagnostic(
                        manifest_path,
                        "SPEC_TRANSITION_MERGE_GROUP",
                        f"Merged target '{target.as_posix()}' must share one evidencePath.",
                    )
                )

    if diagnostics:
        return None, tuple(sorted(diagnostics))
    return TransitionManifest(tuple(parsed)), ()
