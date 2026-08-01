"""Read-only source freshness checks for Forge Review Viewers."""

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
_REQUIREMENT_RE = re.compile(r"^R[0-9]+$")
_ACCEPTANCE_RE = re.compile(r"^AC[0-9]+$")
_STATE_RANK = {"current": 0, "stale": 1, "missing": 2, "malformed": 3}
_GROUPS = ("primary", "comparison", "context")


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


def _digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            value.update(chunk)
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
    if role in {"primary_spec", "primary_plan", "plan_progress", "plan_task"}:
        return "primary"
    if role == "comparison_spec":
        return "comparison"
    if role == "related_spec_context":
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
    if not isinstance(value, dict) or set(value) != {
        "primary",
        "comparison",
        "context",
    }:
        return False

    def valid_node(node: object) -> bool:
        if isinstance(node, dict):
            return all(
                isinstance(key, str) and key and valid_node(item)
                for key, item in node.items()
            )
        return type(node) is int and node >= 0

    return all(isinstance(group, dict) and valid_node(group) for group in value.values())


def _valid_selected_items(value: object, pattern: re.Pattern[str]) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, str) and pattern.fullmatch(item) for item in value)
        and len(value) == len(set(value))
    )


def _manifest_shape_error(
    manifest: object, path_review_id: str
) -> str | None:
    if not isinstance(manifest, dict):
        return "source manifest must be an object"
    required = {
        "review_id",
        "mode",
        "locale",
        "generated_at",
        "checkpoint",
        "commit",
        "rebuild_command",
        "source_base",
        "offline",
        "counts",
        "freshness",
        "sources",
    }
    missing = sorted(required - set(manifest))
    if missing:
        return f"source manifest is missing required fields: {', '.join(missing)}"
    review_id = manifest["review_id"]
    if not isinstance(review_id, str) or _REVIEW_ID_RE.fullmatch(review_id) is None:
        return "source manifest review_id is invalid"
    if review_id != path_review_id:
        return "source manifest review_id does not match the viewer path"
    if not isinstance(manifest["mode"], str) or manifest["mode"] not in {
        "spec",
        "plan",
    }:
        return "source manifest mode must be spec or plan"
    if not isinstance(manifest["locale"], str) or manifest["locale"] not in {
        "en",
        "ko",
    }:
        return "source manifest locale must be en or ko"
    for field in ("generated_at", "checkpoint", "rebuild_command"):
        if not isinstance(manifest[field], str) or not manifest[field]:
            return f"source manifest {field} must be a non-empty string"
    if manifest["commit"] is not None and (
        not isinstance(manifest["commit"], str) or not manifest["commit"]
    ):
        return "source manifest commit must be null or a non-empty string"
    if manifest["source_base"] != "../../../":
        return "source manifest source_base must be ../../../"
    if type(manifest["offline"]) is not bool:
        return "source manifest offline must be boolean"
    if not _valid_counts(manifest["counts"]):
        return "source manifest counts must contain primary, comparison, and context count maps"
    if manifest["freshness"] != "unverified":
        return "source manifest freshness must be unverified"
    sources = manifest["sources"]
    if not isinstance(sources, list) or not sources:
        return "source manifest must contain at least one source"
    for index, row in enumerate(sources):
        if not isinstance(row, dict):
            return f"source row {index + 1} must be an object"
        missing_row = sorted(
            {"role", "namespace", "path", "sha256", "requirements", "acceptance"}
            - set(row)
        )
        if missing_row:
            return f"source row {index + 1} is missing fields: {', '.join(missing_row)}"
        if not all(
            isinstance(row[field], str) and row[field]
            for field in ("role", "namespace", "path")
        ):
            return f"source row {index + 1} has invalid role, namespace, or path"
        if (
            not isinstance(row["sha256"], str)
            or _SHA256_RE.fullmatch(row["sha256"]) is None
        ):
            return f"source row {index + 1} has invalid sha256"
        if not _valid_selected_items(row["requirements"], _REQUIREMENT_RE):
            return f"source row {index + 1} has invalid requirements"
        if not _valid_selected_items(row["acceptance"], _ACCEPTANCE_RE):
            return f"source row {index + 1} has invalid acceptance"
        if "status" in row and not isinstance(row["status"], str):
            return f"source row {index + 1} has invalid status"

    roles = [row["role"] for row in sources]
    if manifest["mode"] == "spec":
        if roles[:1] != ["primary_spec"] or any(
            role != "comparison_spec" for role in roles[1:]
        ):
            return "spec manifest requires one primary_spec followed by comparison_spec sources"
    else:
        allowed = {
            "primary_plan": 0,
            "plan_progress": 1,
            "plan_task": 2,
            "related_spec_context": 3,
        }
        if (
            roles[:1] != ["primary_plan"]
            or roles.count("primary_plan") != 1
            or roles.count("plan_progress") > 1
            or any(role not in allowed for role in roles)
            or any(
                allowed[first] > allowed[second]
                for first, second in zip(roles, roles[1:])
            )
        ):
            return "plan manifest has invalid source role cardinality or order"
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
    if (
        len(parts) != 4
        or parts[:2] != (".forge", "reviews")
        or parts[3] != "view.html"
        or _REVIEW_ID_RE.fullmatch(parts[2]) is None
    ):
        return _malformed(
            viewer_label,
            "viewer path must be .forge/reviews/<review-id>/view.html",
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
        return _malformed(
            viewer_label,
            "viewer must contain exactly one forge-source-manifest JSON script",
        )
    try:
        manifest = json.loads(matches[0])
    except json.JSONDecodeError as error:
        return _malformed(viewer_label, f"source manifest is invalid JSON: {error.msg}")
    shape_error = _manifest_shape_error(manifest, parts[2])
    if shape_error is not None:
        return _malformed(viewer_label, shape_error)
    assert isinstance(manifest, dict)
    assert isinstance(manifest["sources"], list)

    sources: list[tuple[str, str, str]] = []
    diagnostics: list[str] = []
    grouped: dict[str, list[str]] = {}
    namespaces: set[str] = set()
    paths: set[str] = set()
    for index, row in enumerate(manifest["sources"]):
        if not isinstance(row, dict):
            return _malformed(viewer_label, f"source row {index + 1} must be an object")
        namespace = row.get("namespace")
        path_value = row.get("path")
        expected = row.get("sha256")
        role = row.get("role")
        if not all(isinstance(value, str) and value for value in (namespace, path_value, role)):
            return _malformed(
                viewer_label,
                f"source row {index + 1} has invalid namespace, path, or role",
            )
        if not isinstance(expected, str) or _SHA256_RE.fullmatch(expected) is None:
            return _malformed(viewer_label, f"source row {index + 1} has invalid sha256")
        group = _group_for_role(role)
        if group is None:
            return _malformed(viewer_label, f"source row {index + 1} has unknown role: {role}")
        if namespace in namespaces:
            return _malformed(viewer_label, f"duplicate source namespace: {namespace}")
        if path_value in paths:
            return _malformed(viewer_label, f"duplicate source path: {path_value}")
        namespaces.add(namespace)
        paths.add(path_value)
        try:
            relative = _repo_relative(Path(path_value), root)
        except ValueError as error:
            return _malformed(viewer_label, str(error))
        if relative.as_posix() != path_value:
            return _malformed(
                viewer_label,
                f"source path must be normalized repository-relative POSIX: {path_value}",
            )
        source_path = root / relative
        if not source_path.is_file():
            state = "missing"
            diagnostics.append(f"missing source: {path_value}")
        elif _digest(source_path) != expected:
            state = "stale"
            diagnostics.append(f"stale source: {path_value}")
        else:
            state = "current"
        sources.append((namespace, path_value, state))
        grouped.setdefault(group, []).append(state)

    aggregates = {
        group: _aggregate(grouped.get(group, []))
        for group in _GROUPS
    }
    overall = _diagnostic_overall([state for _, _, state in sources])
    return CheckResult(
        viewer_label,
        tuple(sources),
        MappingProxyType(aggregates),
        overall,
        tuple(diagnostics),
    )
