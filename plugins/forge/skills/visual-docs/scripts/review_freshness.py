"""Read-only source freshness checks for Forge Visual Docs."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from types import MappingProxyType
from typing import Mapping


_MANIFEST_RE = re.compile(
    r"<script\b(?=[^>]*\bid=[\"']forge-source-manifest[\"'])"
    r"(?=[^>]*\btype=[\"']application/json[\"'])[^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_REVIEW_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_STATE_RANK = {"current": 0, "stale": 1, "missing": 2, "malformed": 3}
_GROUPS = ("primary", "comparison", "context")
_MEMBER_ROLES = {
    "primary_spec",
    "comparison_spec",
    "related_spec_context",
    "declared_spec",
}
_DOCUMENT_ROLES = {
    "brief_source",
    "primary_plan",
    "plan_progress",
    "plan_task",
    "project_map",
    "repository_evidence",
}


@dataclass(frozen=True)
class CheckResult:
    viewer: str
    sources: tuple[tuple[str, str, str], ...]
    aggregates: Mapping[str, str]
    overall: str
    diagnostics: tuple[str, ...]


def find_repository_root(start: Path) -> Path:
    """Find the nearest ancestor containing a Git directory or worktree file."""

    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        marker = candidate / ".git"
        if marker.is_dir() or marker.is_file():
            return candidate
    raise ValueError(f"repository root not found from: {start}")


def _repo_relative(path: Path, repo_root: Path) -> Path:
    root = repo_root.resolve()
    resolved = path.resolve() if path.is_absolute() else (root / path).resolve()
    try:
        return resolved.relative_to(root)
    except ValueError as error:
        raise ValueError(f"path must remain inside repository: {path}") from error


def _bundle_digest(bundle_path: str, members: list[tuple[str, bytes]]) -> str:
    value = hashlib.sha256()

    def frame(contents: bytes) -> None:
        value.update(len(contents).to_bytes(8, "big"))
        value.update(contents)

    frame(bundle_path.encode("utf-8"))
    prefix = bundle_path + "/"
    for path, contents in sorted(members):
        if not path.startswith(prefix):
            raise ValueError(f"member path is outside bundle: {path}")
        frame(path[len(prefix) :].encode("utf-8"))
        frame(contents)
    return value.hexdigest()


def _aggregate(states: list[str]) -> str:
    if "stale" in states:
        return "stale"
    if states and all(state == "current" for state in states):
        return "current"
    return "unverified"


def _diagnostic_overall(states: list[str]) -> str:
    return max(states, key=_STATE_RANK.__getitem__) if states else "malformed"


def _group_for_role(role: str) -> str | None:
    if role in {
        "primary_spec",
        "brief_source",
        "primary_plan",
        "plan_progress",
        "plan_task",
        "project_map",
    }:
        return "primary"
    if role == "comparison_spec":
        return "comparison"
    if role in {"related_spec_context", "declared_spec", "repository_evidence"}:
        return "context"
    return None


def _malformed(viewer: str, diagnostic: str) -> CheckResult:
    return CheckResult(
        viewer,
        (),
        MappingProxyType({group: "unverified" for group in _GROUPS}),
        "malformed",
        (diagnostic,),
    )


def _valid_counts(value: object) -> bool:
    if not isinstance(value, dict) or set(value) != set(_GROUPS):
        return False

    def valid_node(node: object) -> bool:
        if isinstance(node, dict):
            return all(
                isinstance(key, str) and key and valid_node(item)
                for key, item in node.items()
            )
        return type(node) is int and node >= 0

    return all(isinstance(group, dict) and valid_node(group) for group in value.values())


def _valid_text(row: dict[str, object], fields: tuple[str, ...]) -> bool:
    return all(isinstance(row.get(field), str) and row[field] for field in fields)


def _valid_hash(value: object) -> bool:
    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None


def _manifest_shape_error(manifest: object, path_review_id: str) -> str | None:
    if not isinstance(manifest, dict):
        return "source manifest must be an object"
    required = {
        "view_id", "kind", "output_lifecycle", "locale", "generated_at", "checkpoint", "commit",
        "rebuild_command", "source_base", "offline", "counts", "freshness",
        "bundles", "member_sources", "document_sources",
    }
    missing = sorted(required - set(manifest))
    if missing:
        return f"source manifest is missing required fields: {', '.join(missing)}"
    review_id = manifest["view_id"]
    if not isinstance(review_id, str) or _REVIEW_ID_RE.fullmatch(review_id) is None:
        return "source manifest view_id is invalid"
    if path_review_id and review_id != path_review_id:
        return "source manifest view_id does not match the Visual Docs path"
    if manifest["kind"] not in {"brief", "spec", "plan", "project"}:
        return "source manifest kind must be brief, plan, spec, or project"
    if manifest["output_lifecycle"] not in {"local", "tracked"}:
        return "source manifest output_lifecycle must be local or tracked"
    if manifest["locale"] not in {"en", "ko"}:
        return "source manifest locale must be en or ko"
    for field in ("generated_at", "checkpoint", "rebuild_command"):
        if not isinstance(manifest[field], str) or not manifest[field]:
            return f"source manifest {field} must be a non-empty string"
    if manifest["commit"] is not None and not (
        isinstance(manifest["commit"], str) and manifest["commit"]
    ):
        return "source manifest commit must be null or a non-empty string"
    expected_source_base = "../../" if manifest["output_lifecycle"] == "tracked" else "../../../"
    if manifest["source_base"] != expected_source_base:
        return f"source manifest source_base must be {expected_source_base}"
    if type(manifest["offline"]) is not bool:
        return "source manifest offline must be boolean"
    if not _valid_counts(manifest["counts"]):
        return "source manifest counts must contain primary, comparison, and context count maps"
    if manifest["freshness"] != "unverified":
        return "source manifest freshness must be unverified"
    bundles = manifest["bundles"]
    members = manifest["member_sources"]
    document_sources = manifest["document_sources"]
    if not all(isinstance(value, list) for value in (bundles, members, document_sources)):
        return "source manifest bundles, member_sources, and document_sources must be arrays"
    if not members and not document_sources:
        return "source manifest must contain at least one member or document source"

    bundle_keys: set[tuple[str, str]] = set()
    for index, row in enumerate(bundles):
        if not isinstance(row, dict) or not _valid_text(
            row, ("role", "path", "root_path", "title", "sha256")
        ):
            return f"bundle row {index + 1} has invalid fields"
        if row["role"] not in _MEMBER_ROLES:
            return f"bundle row {index + 1} has invalid role"
        if not _valid_hash(row["sha256"]):
            return f"bundle row {index + 1} has invalid sha256"
        key = (str(row["role"]), str(row["path"]))
        if key in bundle_keys:
            return f"duplicate bundle row: {row['path']}"
        bundle_keys.add(key)

    member_paths: set[str] = set()
    member_keys: dict[tuple[str, str], list[dict[str, object]]] = {}
    for index, row in enumerate(members):
        if not isinstance(row, dict) or not _valid_text(
            row,
            (
                "key", "role", "namespace", "bundle_path", "bundle_title",
                "bundle_sha256", "path", "title", "member_role", "sha256",
            ),
        ):
            return f"member source row {index + 1} has invalid fields"
        if row["role"] not in _MEMBER_ROLES:
            return f"member source row {index + 1} has invalid role"
        if not _valid_hash(row["sha256"]) or not _valid_hash(row["bundle_sha256"]):
            return f"member source row {index + 1} has invalid sha256"
        bundle_key = (str(row["role"]), str(row["bundle_path"]))
        if bundle_key not in bundle_keys:
            return f"member source row {index + 1} has no matching bundle"
        bundle_row = next(
            item for item in bundles
            if (item["role"], item["path"]) == bundle_key
        )
        if row["bundle_sha256"] != bundle_row["sha256"]:
            return f"member source row {index + 1} has inconsistent bundle sha256"
        path = str(row["path"])
        if path in member_paths:
            return f"duplicate member source path: {path}"
        member_paths.add(path)
        member_keys.setdefault(bundle_key, []).append(row)
    for bundle in bundles:
        key = (str(bundle["role"]), str(bundle["path"]))
        rows = member_keys.get(key, [])
        if not rows:
            return f"bundle has no member sources: {bundle['path']}"
        if bundle["root_path"] not in {row["path"] for row in rows}:
            return f"bundle root_path is not a declared member: {bundle['root_path']}"

    document_order = {"primary_plan": 0, "plan_progress": 1, "plan_task": 2}
    document_roles: list[str] = []
    for index, row in enumerate(document_sources):
        if not isinstance(row, dict) or not _valid_text(
            row, ("key", "role", "namespace", "path", "title", "sha256")
        ):
            return f"document source row {index + 1} has invalid fields"
        if row["role"] not in _DOCUMENT_ROLES or not _valid_hash(row["sha256"]):
            return f"document source row {index + 1} has invalid role or sha256"
        document_roles.append(str(row["role"]))

    bundle_roles = [str(row["role"]) for row in bundles]
    if manifest["kind"] == "spec":
        if document_sources or bundle_roles[:1] != ["primary_spec"] or any(
            role != "comparison_spec" for role in bundle_roles[1:]
        ):
            return "spec manifest requires one primary bundle followed by comparison bundles"
    elif manifest["kind"] == "brief":
        if bundle_roles or document_roles != ["brief_source"]:
            return "brief manifest requires exactly one brief source"
    elif manifest["kind"] == "plan":
        if (
            document_roles[:1] != ["primary_plan"]
            or document_roles.count("primary_plan") != 1
            or document_roles.count("plan_progress") > 1
            or any(
                document_order[first] > document_order[second]
                for first, second in zip(document_roles, document_roles[1:])
            )
            or any(role != "related_spec_context" for role in bundle_roles)
        ):
            return "plan manifest has invalid plan source or context bundle order"
    else:
        required_project = {
            "project_map",
            "declared_specs",
            "repository_evidence_sources",
        }
        if not required_project.issubset(manifest):
            return "project manifest is missing Project Map evidence fields"
        if (
            document_roles[:1] != ["project_map"]
            or any(role != "repository_evidence" for role in document_roles[1:])
            or any(role != "declared_spec" for role in bundle_roles)
        ):
            return "project manifest has invalid Project Map, Spec, or evidence sources"
    return None


def check_review(viewer: Path, repo_root: Path) -> CheckResult:
    """Compare an embedded source manifest with repository files without writing."""

    root = repo_root.resolve()
    try:
        viewer_relative = _repo_relative(viewer, root)
    except ValueError as error:
        return _malformed(str(viewer), str(error))
    viewer_label = viewer_relative.as_posix()
    parts = viewer_relative.parts
    local_path = (
        len(parts) != 4
        or parts[:2] != (".forge", "visual-docs")
        or parts[3] != "view.html"
        or _REVIEW_ID_RE.fullmatch(parts[2]) is None
    ) is False
    tracked_path = viewer_relative == Path("docs/project-viewer/index.html")
    if not local_path and not tracked_path:
        return _malformed(
            viewer_label,
            "Visual Docs path must be .forge/visual-docs/<view-id>/view.html or docs/project-viewer/index.html",
        )
    viewer_path = root / viewer_relative
    if not viewer_path.is_file():
        return _malformed(viewer_label, f"viewer file is missing: {viewer_label}")
    try:
        contents = viewer_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return _malformed(viewer_label, f"viewer is not readable UTF-8: {error}")
    matches = _MANIFEST_RE.findall(contents)
    if len(matches) != 1:
        return _malformed(viewer_label, "viewer must contain exactly one forge-source-manifest JSON script")
    try:
        manifest = json.loads(matches[0])
    except json.JSONDecodeError as error:
        return _malformed(viewer_label, f"source manifest is invalid JSON: {error.msg}")
    shape_error = _manifest_shape_error(manifest, parts[2] if local_path else "")
    if shape_error is not None:
        return _malformed(viewer_label, shape_error)
    assert isinstance(manifest, dict)
    if tracked_path and manifest.get("output_lifecycle") != "tracked":
        return _malformed(viewer_label, "Project Handbook must declare tracked output_lifecycle")
    if local_path and manifest.get("output_lifecycle") != "local":
        return _malformed(viewer_label, "local Visual Docs must declare local output_lifecycle")
    rows = [*manifest["member_sources"], *manifest["document_sources"]]

    sources: list[list[str]] = []
    diagnostics: list[str] = []
    grouped: dict[str, list[int]] = {}
    identities: set[str] = set()
    paths: set[str] = set()
    bytes_by_path: dict[str, bytes] = {}
    row_index: dict[str, int] = {}
    for index, row in enumerate(rows):
        identity = str(row["namespace"])
        path_value = str(row["path"])
        expected = str(row["sha256"])
        role = str(row["role"])
        group = _group_for_role(role)
        if group is None:
            return _malformed(viewer_label, f"source row {index + 1} has unknown role: {role}")
        if identity in identities:
            return _malformed(viewer_label, f"duplicate source namespace: {identity}")
        if path_value in paths:
            return _malformed(viewer_label, f"duplicate source path: {path_value}")
        identities.add(identity)
        paths.add(path_value)
        try:
            relative = _repo_relative(Path(path_value), root)
        except ValueError as error:
            return _malformed(viewer_label, str(error))
        if relative.as_posix() != path_value:
            return _malformed(viewer_label, f"source path must be normalized repository-relative POSIX: {path_value}")
        source_path = root / relative
        if not source_path.is_file():
            state = "missing"
            diagnostics.append(f"missing source: {path_value}")
        else:
            source_bytes = source_path.read_bytes()
            bytes_by_path[path_value] = source_bytes
            if hashlib.sha256(source_bytes).hexdigest() != expected:
                state = "stale"
                diagnostics.append(f"stale source: {path_value}")
            else:
                state = "current"
        row_index[path_value] = index
        sources.append([identity, path_value, state])
        grouped.setdefault(group, []).append(index)

    for bundle in manifest["bundles"]:
        bundle_members = [
            row for row in manifest["member_sources"]
            if row["role"] == bundle["role"] and row["bundle_path"] == bundle["path"]
        ]
        if any(str(row["path"]) not in bytes_by_path for row in bundle_members):
            continue
        current_digest = _bundle_digest(
            str(bundle["path"]),
            [(str(row["path"]), bytes_by_path[str(row["path"])]) for row in bundle_members],
        )
        if current_digest == bundle["sha256"]:
            continue
        diagnostics.append(f"stale bundle: {bundle['path']}")
        for row in bundle_members:
            sources[row_index[str(row["path"]) ]][2] = "stale"

    aggregates = {
        group: _aggregate([sources[index][2] for index in grouped.get(group, [])])
        for group in _GROUPS
    }
    states = [state for _, _, state in sources]
    return CheckResult(
        viewer_label,
        tuple(tuple(source) for source in sources),
        MappingProxyType(aggregates),
        _diagnostic_overall(states),
        tuple(diagnostics),
    )
