#!/usr/bin/env python3
"""Create and validate canonical cross-agent extension structures."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
TARGETS = ["codex", "claude-code", "antigravity"]
NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
ENV_RE = re.compile(r"^[A-Z_][A-Z0-9_]*$")
PLACEHOLDER_RE = re.compile(r"\b(?:TBD|TODO)\b|\[TODO\s*:", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(
    r"(?:\bBearer\s+\S+|\bsk-[A-Za-z0-9_-]{8,}|\bghp_[A-Za-z0-9]{8,})",
    re.IGNORECASE,
)
SECRET_KEYS = {
    "apikey",
    "api_key",
    "authorization",
    "env",
    "headers",
    "password",
    "secret",
    "token",
}


class ManagerError(Exception):
    """Expected contract failure with a stable error code."""

    def __init__(self, code: str, detail: str, payload: dict[str, Any] | None = None) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.payload = payload


def fail(code: str, detail: str) -> None:
    raise ManagerError(code, detail)


def validate_name(value: str, label: str) -> str:
    if not NAME_RE.fullmatch(value):
        fail(
            "E_NAME",
            f"{label} '{value}' must use lowercase letters, digits, and hyphens and be shorter than 64 characters",
        )
    return value


def reject_placeholders(text: str, label: str) -> None:
    if PLACEHOLDER_RE.search(text):
        fail("E_PLACEHOLDER", f"{label} contains an unfinished placeholder")


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_skill_source(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail("E_SOURCE", f"skill source does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    reject_placeholders(text, f"skill source {path}")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        fail("E_SKILL_SCHEMA", f"skill source lacks frontmatter: {path}")
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail("E_SKILL_SCHEMA", f"skill frontmatter is not closed: {path}")

    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or ":" not in line:
            fail("E_SKILL_SCHEMA", f"invalid skill frontmatter line in {path}: {line}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if key in metadata:
            fail("E_SKILL_SCHEMA", f"duplicate skill frontmatter key '{key}' in {path}")
        metadata[key] = unquote(raw_value.strip())
    if set(metadata) != {"name", "description"}:
        fail("E_SKILL_SCHEMA", f"skill frontmatter must contain only name and description: {path}")
    validate_name(metadata["name"], "skill name")
    if not metadata["description"].lower().startswith("use when"):
        fail("E_SKILL_SCHEMA", f"skill description must start with 'Use when': {path}")
    if not "\n".join(lines[end + 1 :]).strip():
        fail("E_SKILL_SCHEMA", f"skill body is empty: {path}")
    resources: list[dict[str, str]] = []
    for resource_name in ("references", "scripts", "assets"):
        resource_root = path.parent / resource_name
        if not resource_root.exists():
            continue
        if not resource_root.is_dir() or resource_root.is_symlink():
            fail("E_RESOURCE", f"skill resource must be a real directory: {resource_root}")
        for resource in sorted(resource_root.rglob("*")):
            if resource.is_symlink():
                fail("E_RESOURCE", f"skill resources may not contain symlinks: {resource}")
            if not resource.is_file():
                continue
            relative = resource.relative_to(path.parent)
            if "__pycache__" in relative.parts or resource.suffix in {".pyc", ".pyo"}:
                continue
            try:
                resource_text = resource.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                resource_text = ""
            if resource_text:
                reject_placeholders(resource_text, f"skill resource {resource}")
            resources.append(
                {"source": str(resource.resolve()), "relative": relative.as_posix()}
            )
    return {
        "name": metadata["name"],
        "description": metadata["description"],
        "source": str(path.resolve()),
        "resources": resources,
    }


def reject_secret_values(value: Any, location: str = "mcpServers") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_is_environment_reference = location.endswith(".headersFromEnv")
            if key.lower() in SECRET_KEYS and not key_is_environment_reference:
                fail("E_SECRET", f"raw credential field '{location}.{key}' is not allowed")
            reject_secret_values(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_secret_values(child, f"{location}[{index}]")
    elif isinstance(value, str) and SECRET_VALUE_RE.search(value):
        fail("E_SECRET", f"raw credential value at '{location}' is not allowed")


def validate_relative_path(value: str, label: str) -> None:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        fail("E_MCP_SCHEMA", f"{label} must be relative and remain inside the extension root")


def validate_server(name: str, server: dict[str, Any]) -> None:
    validate_name(name, "MCP server name")
    if not isinstance(server, dict):
        fail("E_MCP_SCHEMA", f"MCP server '{name}' must be an object")
    reject_secret_values(server, f"mcpServers.{name}")
    reject_placeholders(json.dumps(server, sort_keys=True), f"MCP server {name}")
    transport = server.get("transport")
    if transport == "stdio":
        allowed = {"transport", "command", "args", "envVars", "cwd"}
        unknown = set(server) - allowed
        if unknown:
            fail("E_MCP_SCHEMA", f"MCP server '{name}' has unsupported fields: {sorted(unknown)}")
        if not isinstance(server.get("command"), str) or not server["command"].strip():
            fail("E_MCP_SCHEMA", f"MCP server '{name}' requires a non-empty command")
        args = server.get("args", [])
        if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
            fail("E_MCP_SCHEMA", f"MCP server '{name}' args must be a string array")
        env_vars = server.get("envVars", [])
        if not isinstance(env_vars, list) or not all(
            isinstance(item, str) and ENV_RE.fullmatch(item) for item in env_vars
        ):
            fail("E_MCP_SCHEMA", f"MCP server '{name}' envVars must contain environment variable names")
        if "cwd" in server:
            if not isinstance(server["cwd"], str):
                fail("E_MCP_SCHEMA", f"MCP server '{name}' cwd must be a string")
            validate_relative_path(server["cwd"], f"MCP server '{name}' cwd")
    elif transport == "http":
        allowed = {"transport", "url", "headersFromEnv"}
        unknown = set(server) - allowed
        if unknown:
            fail("E_MCP_SCHEMA", f"MCP server '{name}' has unsupported fields: {sorted(unknown)}")
        url = server.get("url")
        if not isinstance(url, str) or not re.match(r"^https?://", url):
            fail("E_MCP_SCHEMA", f"MCP server '{name}' requires an http or https URL")
        headers = server.get("headersFromEnv", {})
        if not isinstance(headers, dict) or not all(
            isinstance(header, str)
            and header.strip()
            and isinstance(env_name, str)
            and ENV_RE.fullmatch(env_name)
            for header, env_name in headers.items()
        ):
            fail("E_MCP_SCHEMA", f"MCP server '{name}' headersFromEnv must map headers to environment names")
    else:
        fail("E_MCP_SCHEMA", f"MCP server '{name}' has unsupported transport '{transport}'")


def parse_mcp_source(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail("E_SOURCE", f"MCP source does not exist: {path}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        fail("E_MCP_SCHEMA", f"invalid MCP JSON at {path}: {error}")
    if not isinstance(document, dict) or set(document) != {"mcpServers"}:
        fail("E_MCP_SCHEMA", "canonical MCP source must contain only mcpServers")
    servers = document["mcpServers"]
    if not isinstance(servers, dict) or not servers:
        fail("E_MCP_SCHEMA", "canonical MCP source requires at least one server")
    for name, server in servers.items():
        validate_server(name, server)
    return {
        "source": str(path.resolve()),
        "servers": servers,
    }


def collect_sources(args: argparse.Namespace) -> dict[str, Any]:
    skills = [parse_skill_source(Path(value).expanduser()) for value in args.skill_source]
    skill_names = [skill["name"] for skill in skills]
    if len(skill_names) != len(set(skill_names)):
        fail("E_PROFILE_INPUT", "skill source names must be unique")
    mcp = parse_mcp_source(Path(args.mcp_source).expanduser()) if args.mcp_source else None
    if args.profile == "skill" and (not skills or mcp is not None):
        fail("E_PROFILE_INPUT", "skill profile requires skill sources and no MCP source")
    if args.profile == "mcp" and (skills or mcp is None):
        fail("E_PROFILE_INPUT", "mcp profile requires one MCP source and no skill sources")
    if args.profile == "bundle" and (not skills or mcp is None):
        fail("E_PROFILE_INPUT", "bundle profile requires skill and MCP sources")
    return {"skills": skills, "mcp": mcp}


def extension_root_for(scope: str, base_dir: Path, name: str) -> Path:
    del scope
    return base_dir / ".agent-extensions" / name


def native_targets_for(
    scope: str,
    base_dir: Path,
    skills: list[dict[str, str]],
    has_mcp: bool,
) -> list[Path]:
    targets: list[Path] = []
    for skill in skills:
        name = skill["name"]
        if scope == "repository":
            targets.extend(
                [
                    base_dir / ".agents" / "skills" / name / "SKILL.md",
                    base_dir / ".claude" / "skills" / name / "SKILL.md",
                ]
            )
        else:
            targets.extend(
                [
                    base_dir / ".agents" / "skills" / name / "SKILL.md",
                    base_dir / ".claude" / "skills" / name / "SKILL.md",
                    base_dir / ".gemini" / "config" / "skills" / name / "SKILL.md",
                ]
            )
    if has_mcp:
        targets.extend(path for _, path, _ in mcp_target_mappings(scope, base_dir))
    return targets


def mcp_target_mappings(scope: str, base_dir: Path) -> list[tuple[str, Path, str]]:
    if scope == "repository":
        return [
            ("codex", base_dir / ".codex" / "config.toml", "toml"),
            ("claude-code", base_dir / ".mcp.json", "json"),
            ("antigravity", base_dir / ".agents" / "mcp_config.json", "json"),
        ]
    return [
        ("codex", base_dir / ".codex" / "config.toml", "toml"),
        ("claude-code", base_dir / ".claude.json", "json"),
        (
            "antigravity",
            base_dir / ".gemini" / "config" / "mcp_config.json",
            "json",
        ),
    ]


def toml_server_names(text: str) -> set[str]:
    pattern = re.compile(
        r'^\s*\[mcp_servers\.(?:"([^"]+)"|([A-Za-z0-9_-]+))\]\s*$',
        re.MULTILINE,
    )
    return {quoted or bare for quoted, bare in pattern.findall(text)}


def existing_mcp_names(path: Path, native_format: str) -> set[str]:
    if not path.exists():
        return set()
    if native_format == "toml":
        return toml_server_names(path.read_text(encoding="utf-8"))
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        fail("E_NATIVE_CONFIG", f"cannot parse native JSON config {path}: {error}")
    if not isinstance(document, dict):
        fail("E_NATIVE_CONFIG", f"native JSON config must be an object: {path}")
    servers = document.get("mcpServers", {})
    if not isinstance(servers, dict):
        fail("E_NATIVE_CONFIG", f"mcpServers must be an object in {path}")
    return set(servers)


def plan_collisions(
    scope: str,
    base_dir: Path,
    extension_root: Path,
    sources: dict[str, Any],
) -> list[str]:
    collisions: list[str] = []
    if extension_root.exists():
        collisions.append(str(extension_root))
    skill_targets_only = native_targets_for(scope, base_dir, sources["skills"], False)
    collisions.extend(str(path) for path in skill_targets_only if path.exists())
    if sources["mcp"] is not None:
        canonical_names = set(sources["mcp"]["servers"])
        for _, path, native_format in mcp_target_mappings(scope, base_dir):
            for name in sorted(canonical_names & existing_mcp_names(path, native_format)):
                collisions.append(f"{path}#{name}")
    return collisions


def source_credential_requirements(sources: dict[str, Any]) -> list[str]:
    names: set[str] = set()
    if sources["mcp"] is not None:
        for server in sources["mcp"]["servers"].values():
            names.update(server.get("envVars", []))
            names.update(server.get("headersFromEnv", {}).values())
    return sorted(names)


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    validate_name(args.name, "extension name")
    reject_placeholders(args.description, "extension description")
    base_dir = Path(args.base_dir).expanduser().resolve()
    if not base_dir.is_dir():
        fail("E_BASE_DIR", f"base directory does not exist: {base_dir}")
    sources = collect_sources(args)
    extension_root = extension_root_for(args.scope, base_dir, args.name)
    canonical_writes = ["extension.json"]
    canonical_writes.extend(
        f"skills/{skill['name']}/SKILL.md" for skill in sources["skills"]
    )
    for skill in sources["skills"]:
        canonical_writes.extend(
            f"skills/{skill['name']}/{resource['relative']}"
            for resource in skill["resources"]
        )
    if sources["mcp"] is not None:
        canonical_writes.append("mcp/servers.json")
    native_targets = native_targets_for(
        args.scope, base_dir, sources["skills"], sources["mcp"] is not None
    )
    collisions = plan_collisions(args.scope, base_dir, extension_root, sources)
    return {
        "action": "plan",
        "scope": args.scope,
        "profile": args.profile,
        "name": args.name,
        "description": args.description,
        "baseDir": str(base_dir),
        "extensionRoot": str(extension_root),
        "canonicalWrites": canonical_writes,
        "nativeTargets": [str(path) for path in native_targets],
        "collisions": collisions,
        "credentialRequirements": source_credential_requirements(sources),
        "requiresConfirmation": args.scope == "user",
        "sources": {
            "skills": sources["skills"],
            "mcp": (
                {
                    "source": sources["mcp"]["source"],
                    "serverNames": list(sources["mcp"]["servers"]),
                }
                if sources["mcp"] is not None
                else None
            ),
        },
    }


def manifest_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    skills = [
        {
            "name": skill["name"],
            "description": skill["description"],
            "path": f"skills/{skill['name']}/SKILL.md",
        }
        for skill in plan["sources"]["skills"]
    ]
    mcp_source = plan["sources"]["mcp"]
    mcp_servers = (
        [
            {"name": name, "path": "mcp/servers.json"}
            for name in mcp_source["serverNames"]
        ]
        if mcp_source is not None
        else []
    )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "name": plan["name"],
        "description": plan["description"],
        "scope": plan["scope"],
        "targets": TARGETS,
        "components": {"skills": skills, "mcpServers": mcp_servers},
    }


def initialize(plan: dict[str, Any], confirmed: bool) -> Path:
    if plan["scope"] == "user" and not confirmed:
        fail("E_CONFIRMATION", "user-scope init requires --confirm-user-write after preview")
    if plan["collisions"]:
        fail("E_COLLISION", f"init target already exists: {plan['collisions'][0]}")
    extension_root = Path(plan["extensionRoot"])
    parent = extension_root.parent
    parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{plan['name']}-", dir=parent))
    try:
        manifest = manifest_from_plan(plan)
        (temporary / "extension.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        for skill in plan["sources"]["skills"]:
            destination = temporary / "skills" / skill["name"] / "SKILL.md"
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(skill["source"], destination)
            for resource in skill["resources"]:
                resource_destination = destination.parent / resource["relative"]
                resource_destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(resource["source"], resource_destination)
        mcp_source = plan["sources"]["mcp"]
        if mcp_source is not None:
            destination = temporary / "mcp" / "servers.json"
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(mcp_source["source"], destination)
        os.replace(temporary, extension_root)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return extension_root


def load_manifest(extension_root: Path) -> dict[str, Any]:
    manifest_path = extension_root / "extension.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        fail("E_MANIFEST", f"cannot read {manifest_path}: {error}")
    if not isinstance(manifest, dict) or manifest.get("schemaVersion") != SCHEMA_VERSION:
        fail("E_MANIFEST", f"unsupported manifest schema in {manifest_path}")
    return manifest


def canonical_digest(extension_root: Path) -> str:
    load_manifest(extension_root)
    root = extension_root.resolve()
    paths: list[Path] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == "adapters":
            continue
        if path.is_symlink():
            fail("E_MANIFEST", f"canonical source may not contain symlinks: {relative}")
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = ""
        if text:
            reject_placeholders(text, f"canonical source {relative}")
        paths.append(relative)
    digest = hashlib.sha256()
    for relative in sorted(paths, key=str):
        if relative.is_absolute() or ".." in relative.parts:
            fail("E_MANIFEST", f"manifest path escapes extension root: {relative}")
        path = root / relative
        if not path.is_file():
            fail("E_MANIFEST", f"manifest path does not resolve to a file: {relative}")
        digest.update(str(relative).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extension_context(extension_root: Path) -> tuple[Path, Path, dict[str, Any]]:
    root = extension_root.expanduser().resolve()
    manifest = load_manifest(root)
    required = {
        "schemaVersion",
        "name",
        "description",
        "scope",
        "targets",
        "components",
    }
    if set(manifest) != required:
        fail("E_MANIFEST", f"manifest keys do not match schema at {root / 'extension.json'}")
    validate_name(manifest["name"], "extension name")
    if root.name != manifest["name"] or root.parent.name != ".agent-extensions":
        fail("E_MANIFEST", f"extension root does not match manifest name: {root}")
    if manifest["scope"] not in {"repository", "user"}:
        fail("E_MANIFEST", f"unsupported manifest scope '{manifest['scope']}'")
    if manifest["targets"] != TARGETS:
        fail("E_MANIFEST", "manifest targets must be codex, claude-code, and antigravity")
    components = manifest["components"]
    if not isinstance(components, dict) or set(components) != {"skills", "mcpServers"}:
        fail("E_MANIFEST", "manifest components must contain skills and mcpServers")
    if not isinstance(components["skills"], list) or not isinstance(
        components["mcpServers"], list
    ):
        fail("E_MANIFEST", "manifest component declarations must be arrays")
    base_dir = root.parent.parent
    return root, base_dir, manifest


def state_target(path: Path, base_dir: Path, scope: str) -> str:
    if scope == "repository":
        try:
            return path.relative_to(base_dir).as_posix()
        except ValueError:
            fail("E_MANIFEST", f"repository native target escapes base directory: {path}")
    return str(path)


def skill_targets(
    manifest: dict[str, Any], extension_root: Path, base_dir: Path
) -> list[dict[str, Any]]:
    scope = manifest["scope"]
    descriptors: list[dict[str, Any]] = []
    for skill in manifest["components"]["skills"]:
        if not isinstance(skill, dict) or set(skill) != {"name", "description", "path"}:
            fail("E_MANIFEST", "each skill declaration requires name, description, and path")
        validate_name(skill["name"], "skill name")
        expected_relative = f"skills/{skill['name']}/SKILL.md"
        if skill["path"] != expected_relative:
            fail("E_MANIFEST", f"skill path must be {expected_relative}")
        canonical = extension_root / skill["path"]
        parsed = parse_skill_source(canonical)
        if parsed["name"] != skill["name"] or parsed["description"] != skill["description"]:
            fail("E_MANIFEST", f"skill declaration does not match canonical source: {skill['name']}")
        if scope == "repository":
            mappings = [
                ("codex", base_dir / ".agents" / "skills" / skill["name"] / "SKILL.md"),
                (
                    "claude-code",
                    base_dir / ".claude" / "skills" / skill["name"] / "SKILL.md",
                ),
                (
                    "antigravity",
                    base_dir / ".agents" / "skills" / skill["name"] / "SKILL.md",
                ),
            ]
        else:
            mappings = [
                ("codex", base_dir / ".agents" / "skills" / skill["name"] / "SKILL.md"),
                (
                    "claude-code",
                    base_dir / ".claude" / "skills" / skill["name"] / "SKILL.md",
                ),
                (
                    "antigravity",
                    base_dir
                    / ".gemini"
                    / "config"
                    / "skills"
                    / skill["name"]
                    / "SKILL.md",
                ),
            ]
        for agent, target in mappings:
            descriptors.append(
                {
                    "agent": agent,
                    "kind": "skill",
                    "name": skill["name"],
                    "description": skill["description"],
                    "canonical": canonical,
                    "target": target,
                    "stateTarget": state_target(target, base_dir, scope),
                }
            )
    return descriptors


def canonical_mcp_servers(
    manifest: dict[str, Any], extension_root: Path
) -> dict[str, dict[str, Any]]:
    declarations = manifest["components"]["mcpServers"]
    if not declarations:
        return {}
    declared_names: list[str] = []
    for declaration in declarations:
        if not isinstance(declaration, dict) or set(declaration) != {"name", "path"}:
            fail("E_MANIFEST", "each MCP declaration requires name and path")
        validate_name(declaration["name"], "MCP server name")
        if declaration["path"] != "mcp/servers.json":
            fail("E_MANIFEST", "MCP declaration path must be mcp/servers.json")
        declared_names.append(declaration["name"])
    parsed = parse_mcp_source(extension_root / "mcp" / "servers.json")
    servers = parsed["servers"]
    if declared_names != list(servers):
        fail("E_MANIFEST", "MCP declarations must match canonical mcpServers order and names")
    return servers


def to_json_native(server: dict[str, Any], extension_root: Path) -> dict[str, Any]:
    if server["transport"] == "stdio":
        native: dict[str, Any] = {
            "type": "stdio",
            "command": server["command"],
            "args": list(server.get("args", [])),
        }
        if server.get("envVars"):
            native["env"] = {
                name: f"${{{name}}}" for name in server["envVars"]
            }
        if "cwd" in server:
            native["cwd"] = str((extension_root / server["cwd"]).resolve())
        return native
    native = {"type": "http", "url": server["url"]}
    if server.get("headersFromEnv"):
        native["headers"] = {
            header: f"${{{env_name}}}"
            for header, env_name in server["headersFromEnv"].items()
        }
    return native


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_array(values: list[str]) -> str:
    return "[" + ", ".join(toml_string(value) for value in values) + "]"


def toml_inline_map(values: dict[str, str]) -> str:
    pairs = ", ".join(
        f"{toml_string(key)} = {toml_string(value)}" for key, value in values.items()
    )
    return "{ " + pairs + " }"


def to_codex_toml(
    name: str, server: dict[str, Any], extension_root: Path
) -> str:
    lines = [f"[mcp_servers.{toml_string(name)}]"]
    if server["transport"] == "stdio":
        lines.append(f"command = {toml_string(server['command'])}")
        if server.get("args"):
            lines.append(f"args = {toml_array(server['args'])}")
        if server.get("envVars"):
            lines.append(f"env_vars = {toml_array(server['envVars'])}")
        if "cwd" in server:
            lines.append(f"cwd = {toml_string(str((extension_root / server['cwd']).resolve()))}")
    else:
        lines.append(f"url = {toml_string(server['url'])}")
        if server.get("headersFromEnv"):
            lines.append(
                "env_http_headers = "
                + toml_inline_map(server["headersFromEnv"])
            )
    return "\n".join(lines) + "\n"


def codex_managed_block(
    extension_name: str,
    servers: dict[str, dict[str, Any]],
    extension_root: Path,
) -> str:
    lines = [f"# BEGIN creating-agent-extensions:{extension_name}"]
    for name, server in servers.items():
        lines.append(to_codex_toml(name, server, extension_root).rstrip("\n"))
        lines.append("")
    if lines[-1] == "":
        lines.pop()
    lines.append(f"# END creating-agent-extensions:{extension_name}")
    return "\n".join(lines) + "\n"


def mcp_targets(
    manifest: dict[str, Any], extension_root: Path, base_dir: Path
) -> list[dict[str, Any]]:
    servers = canonical_mcp_servers(manifest, extension_root)
    descriptors: list[dict[str, Any]] = []
    for agent, target, native_format in mcp_target_mappings(
        manifest["scope"], base_dir
    ):
        for name, server in servers.items():
            descriptors.append(
                {
                    "agent": agent,
                    "kind": "mcp",
                    "name": name,
                    "target": target,
                    "stateTarget": state_target(
                        target, base_dir, manifest["scope"]
                    ),
                    "format": native_format,
                    "native": (
                        to_json_native(server, extension_root)
                        if native_format == "json"
                        else server
                    ),
                }
            )
    return descriptors


def render_skill_wrapper(descriptor: dict[str, Any], scope: str) -> str:
    canonical = descriptor["canonical"]
    if scope == "repository":
        canonical_reference = os.path.relpath(canonical, descriptor["target"].parent).replace(
            os.sep, "/"
        )
    else:
        canonical_reference = str(canonical)
    title = " ".join(part.capitalize() for part in descriptor["name"].split("-"))
    return "\n".join(
        [
            "---",
            f"name: {descriptor['name']}",
            "description: " + json.dumps(descriptor["description"], ensure_ascii=False),
            "---",
            "",
            f"# {title} Adapter",
            "",
            f"Read `{canonical_reference}` completely, then follow it as the source of truth.",
            "If this adapter conflicts with the canonical skill, the canonical skill wins.",
            "",
        ]
    )


def state_path(extension_root: Path, agent: str) -> Path:
    return extension_root / "adapters" / agent / "state.json"


def load_state(extension_root: Path, agent: str) -> dict[str, Any] | None:
    path = state_path(extension_root, agent)
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        fail("E_STATE", f"cannot read ownership state {path}: {error}")
    if (
        not isinstance(state, dict)
        or state.get("schemaVersion") != SCHEMA_VERSION
        or not isinstance(state.get("entries"), list)
    ):
        fail("E_STATE", f"invalid ownership state: {path}")
    return state


def previous_entry(
    state: dict[str, Any] | None, descriptor: dict[str, Any]
) -> dict[str, Any] | None:
    if state is None:
        return None
    for entry in state["entries"]:
        if (
            entry.get("kind") == descriptor["kind"]
            and entry.get("name") == descriptor["name"]
            and entry.get("target") == descriptor["stateTarget"]
        ):
            return entry
    return None


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def stable_json_hash(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_native_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        fail("E_NATIVE_CONFIG", f"cannot parse native JSON config {path}: {error}")
    if not isinstance(document, dict):
        fail("E_NATIVE_CONFIG", f"native JSON config must be an object: {path}")
    servers = document.get("mcpServers", {})
    if not isinstance(servers, dict):
        fail("E_NATIVE_CONFIG", f"mcpServers must be an object in {path}")
    return document


def split_managed_block(
    text: str, extension_name: str
) -> tuple[str, str | None, str]:
    begin = f"# BEGIN creating-agent-extensions:{extension_name}"
    end = f"# END creating-agent-extensions:{extension_name}"
    start = text.find(begin)
    finish_marker = text.find(end)
    if start == -1 and finish_marker == -1:
        return text, None, ""
    if start == -1 or finish_marker == -1 or finish_marker < start:
        fail("E_NATIVE_CONFIG", f"malformed managed TOML block for '{extension_name}'")
    if text.find(begin, start + len(begin)) != -1 or text.find(
        end, finish_marker + len(end)
    ) != -1:
        fail("E_NATIVE_CONFIG", f"duplicate managed TOML block for '{extension_name}'")
    block_end = finish_marker + len(end)
    if block_end < len(text) and text[block_end] == "\n":
        block_end += 1
    return text[:start], text[start:block_end], text[block_end:]


def append_managed_block(text: str, block: str) -> str:
    if not text:
        return block
    separator = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
    return text + separator + block


def prepare_json_mcp_output(
    target: Path,
    descriptors: list[dict[str, Any]],
    state: dict[str, Any] | None,
    extension_name: str,
) -> str:
    document = load_native_json(target)
    existing_servers = document.get("mcpServers", {})
    for descriptor in descriptors:
        prior = previous_entry(state, descriptor)
        existing = existing_servers.get(descriptor["name"])
        if existing is not None:
            if prior is None:
                fail(
                    "E_COLLISION",
                    f"MCP server '{descriptor['name']}' in '{target}' is not owned by extension '{extension_name}'",
                )
            if prior.get("owner") != extension_name or stable_json_hash(
                existing
            ) != prior.get("renderedHash"):
                fail(
                    "E_DRIFT",
                    f"MCP entry '{descriptor['name']}' drifted at '{target}' for expected owner '{extension_name}'",
                )
        elif prior is not None:
            fail(
                "E_DRIFT",
                f"owned MCP entry '{descriptor['name']}' is missing at '{target}'",
            )

    merged = copy.deepcopy(document)
    merged_servers = merged.setdefault("mcpServers", {})
    for descriptor in descriptors:
        merged_servers[descriptor["name"]] = descriptor["native"]
        descriptor["renderedHash"] = stable_json_hash(descriptor["native"])
    return json.dumps(merged, indent=2, ensure_ascii=False) + "\n"


def prepare_codex_mcp_output(
    target: Path,
    descriptors: list[dict[str, Any]],
    state: dict[str, Any] | None,
    extension_name: str,
    extension_root: Path,
) -> str:
    text = target.read_text(encoding="utf-8") if target.exists() else ""
    before, existing_block, after = split_managed_block(text, extension_name)
    external_names = toml_server_names(before + after)
    requested_names = {descriptor["name"] for descriptor in descriptors}
    collisions = sorted(external_names & requested_names)
    if collisions:
        fail(
            "E_COLLISION",
            f"MCP server '{collisions[0]}' in '{target}' is not owned by extension '{extension_name}'",
        )
    if existing_block is not None:
        actual_hash = sha256_text(existing_block)
        for descriptor in descriptors:
            prior = previous_entry(state, descriptor)
            if (
                prior is None
                or prior.get("owner") != extension_name
                or prior.get("renderedHash") != actual_hash
            ):
                fail(
                    "E_DRIFT",
                    f"managed MCP block drifted at '{target}' for expected owner '{extension_name}'",
                )
    else:
        for descriptor in descriptors:
            if previous_entry(state, descriptor) is not None:
                fail("E_DRIFT", f"owned managed MCP block is missing at '{target}'")

    servers = canonical_mcp_servers(load_manifest(extension_root), extension_root)
    block = codex_managed_block(extension_name, servers, extension_root)
    block_hash = sha256_text(block)
    for descriptor in descriptors:
        descriptor["renderedHash"] = block_hash
    if existing_block is None:
        return append_managed_block(text, block)
    return before + block + after


def preview_changes(
    descriptors: list[dict[str, Any]],
    extension_root: Path,
    manifest: dict[str, Any],
) -> list[dict[str, str]]:
    states = {agent: load_state(extension_root, agent) for agent in TARGETS}
    changes: list[dict[str, str]] = []
    codex_cache: dict[Path, tuple[str, str | None, str]] = {}
    json_cache: dict[Path, dict[str, Any]] = {}
    for descriptor in descriptors:
        target = descriptor["target"]
        prior = previous_entry(states[descriptor["agent"]], descriptor)
        action = "create"
        if descriptor["kind"] == "skill":
            if target.exists():
                if prior is None:
                    action = "collision"
                elif (
                    prior.get("owner") != manifest["name"]
                    or hashlib.sha256(target.read_bytes()).hexdigest()
                    != prior.get("renderedHash")
                ):
                    action = "drift"
                else:
                    action = "update"
            elif prior is not None:
                action = "drift"
        elif descriptor["format"] == "json":
            document = json_cache.setdefault(target, load_native_json(target))
            existing = document.get("mcpServers", {}).get(descriptor["name"])
            if existing is not None:
                if prior is None:
                    action = "collision"
                elif (
                    prior.get("owner") != manifest["name"]
                    or stable_json_hash(existing) != prior.get("renderedHash")
                ):
                    action = "drift"
                else:
                    action = "update"
            elif prior is not None:
                action = "drift"
        else:
            if target not in codex_cache:
                text = target.read_text(encoding="utf-8") if target.exists() else ""
                codex_cache[target] = split_managed_block(text, manifest["name"])
            before, block, after = codex_cache[target]
            if descriptor["name"] in toml_server_names(before + after):
                action = "collision"
            elif block is not None:
                if (
                    prior is None
                    or prior.get("owner") != manifest["name"]
                    or sha256_text(block) != prior.get("renderedHash")
                ):
                    action = "drift"
                else:
                    action = "update"
            elif prior is not None:
                action = "drift"
        changes.append(
            {
                "agent": descriptor["agent"],
                "kind": descriptor["kind"],
                "name": descriptor["name"],
                "target": str(target),
                "action": action,
            }
        )
    return changes


def credential_requirements(
    manifest: dict[str, Any], extension_root: Path
) -> list[str]:
    names: set[str] = set()
    for server in canonical_mcp_servers(manifest, extension_root).values():
        names.update(server.get("envVars", []))
        names.update(server.get("headersFromEnv", {}).values())
    return sorted(names)


def render_preview(extension_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    root, base_dir, manifest = extension_context(extension_root)
    descriptors = skill_targets(manifest, root, base_dir) + mcp_targets(
        manifest, root, base_dir
    )
    changes = preview_changes(descriptors, root, manifest)
    canonical_sources = [
        str(root / item["path"]) for item in manifest["components"]["skills"]
    ]
    if manifest["components"]["mcpServers"]:
        canonical_sources.append(str(root / "mcp" / "servers.json"))
    preview = {
        "action": "render",
        "scope": manifest["scope"],
        "extensionRoot": str(root),
        "canonicalSources": canonical_sources,
        "nativeTargets": sorted({str(item["target"]) for item in descriptors}),
        "changes": changes,
        "credentialRequirements": credential_requirements(manifest, root),
        "collisions": [
            f"{item['target']}#{item['name']}"
            for item in changes
            if item["action"] == "collision"
        ],
        "requiresConfirmation": manifest["scope"] == "user",
    }
    return preview, descriptors


def render_extension(extension_root: Path, confirmed: bool) -> dict[str, Any]:
    preview, descriptors = render_preview(extension_root)
    if preview["scope"] == "user" and not confirmed:
        raise ManagerError(
            "E_CONFIRMATION",
            "user-scope render requires --confirm-user-write after preview",
            preview,
        )
    root, _, manifest = extension_context(extension_root)
    digest = canonical_digest(root)
    states = {agent: load_state(root, agent) for agent in TARGETS}
    rendered: dict[Path, str] = {}

    skill_descriptors = [item for item in descriptors if item["kind"] == "skill"]
    mcp_descriptors = [item for item in descriptors if item["kind"] == "mcp"]

    for descriptor in skill_descriptors:
        text = render_skill_wrapper(descriptor, manifest["scope"])
        target = descriptor["target"]
        if target in rendered and rendered[target] != text:
            fail("E_STATE", f"shared target has conflicting rendered content: {target}")
        rendered[target] = text
        state = states[descriptor["agent"]]
        prior = previous_entry(state, descriptor)
        if target.exists():
            if prior is None:
                fail(
                    "E_COLLISION",
                    f"target '{target}' is not owned by extension '{manifest['name']}'",
                )
            actual_hash = hashlib.sha256(target.read_bytes()).hexdigest()
            if prior.get("owner") != manifest["name"] or actual_hash != prior.get(
                "renderedHash"
            ):
                fail(
                    "E_DRIFT",
                    f"target '{target}' drifted from expected owner '{manifest['name']}'",
                )
        elif prior is not None:
            fail(
                "E_DRIFT",
                f"owned target '{target}' is missing for expected owner '{manifest['name']}'",
            )
        descriptor["renderedHash"] = sha256_text(text)

    mcp_groups: dict[Path, list[dict[str, Any]]] = {}
    for descriptor in mcp_descriptors:
        mcp_groups.setdefault(descriptor["target"], []).append(descriptor)
    for target, group in mcp_groups.items():
        agent = group[0]["agent"]
        if group[0]["format"] == "json":
            rendered[target] = prepare_json_mcp_output(
                target,
                group,
                states[agent],
                manifest["name"],
            )
        else:
            rendered[target] = prepare_codex_mcp_output(
                target,
                group,
                states[agent],
                manifest["name"],
                root,
            )

    new_states: dict[str, dict[str, Any]] = {}
    for agent in TARGETS:
        entries = []
        for descriptor in descriptors:
            if descriptor["agent"] != agent:
                continue
            entries.append(
                {
                    "kind": descriptor["kind"],
                    "name": descriptor["name"],
                    "target": descriptor["stateTarget"],
                    "owner": manifest["name"],
                    "renderedHash": descriptor["renderedHash"],
                }
            )
        new_states[agent] = {
            "schemaVersion": SCHEMA_VERSION,
            "extension": manifest["name"],
            "canonicalHash": digest,
            "entries": entries,
        }

    for path, text in rendered.items():
        atomic_write_text(path, text)
    for agent, state in new_states.items():
        atomic_write_text(
            state_path(root, agent),
            json.dumps(state, indent=2, ensure_ascii=False) + "\n",
        )
    return {**preview, "canonicalHash": digest, "requiresConfirmation": False}


def validate_extension(extension_root: Path) -> list[str]:
    root, base_dir, manifest = extension_context(extension_root)
    digest = canonical_digest(root)
    skill_descriptors = skill_targets(manifest, root, base_dir)
    mcp_descriptors = mcp_targets(manifest, root, base_dir)
    descriptors = skill_descriptors + mcp_descriptors
    issues: list[str] = []
    states = {agent: load_state(root, agent) for agent in TARGETS}
    for agent, state in states.items():
        if state is None:
            issues.append(
                f"ownership state missing for expected owner '{manifest['name']}' and agent '{agent}'"
            )
            continue
        if state.get("extension") != manifest["name"]:
            issues.append(f"state owner mismatch for agent '{agent}'")
        if state.get("canonicalHash") != digest:
            issues.append(
                f"canonical hash drift for expected owner '{manifest['name']}' and agent '{agent}'"
            )
    for descriptor in skill_descriptors:
        state = states[descriptor["agent"]]
        prior = previous_entry(state, descriptor)
        target = descriptor["target"]
        if prior is None:
            issues.append(
                f"ownership entry missing for expected owner '{manifest['name']}' at '{target}'"
            )
            continue
        if prior.get("owner") != manifest["name"]:
            issues.append(f"owner drift at '{target}', expected '{manifest['name']}'")
        if not target.is_file():
            issues.append(
                f"owned target missing at '{target}', expected owner '{manifest['name']}'"
            )
            continue
        actual_hash = hashlib.sha256(target.read_bytes()).hexdigest()
        expected_text = render_skill_wrapper(descriptor, manifest["scope"])
        expected_hash = sha256_text(expected_text)
        if actual_hash != prior.get("renderedHash") or actual_hash != expected_hash:
            issues.append(
                f"adapter drift at '{target}', expected owner '{manifest['name']}'"
            )

    mcp_groups: dict[Path, list[dict[str, Any]]] = {}
    for descriptor in mcp_descriptors:
        mcp_groups.setdefault(descriptor["target"], []).append(descriptor)
    for target, group in mcp_groups.items():
        agent = group[0]["agent"]
        state = states[agent]
        if group[0]["format"] == "json":
            document = load_native_json(target)
            native_servers = document.get("mcpServers", {})
            for descriptor in group:
                prior = previous_entry(state, descriptor)
                native = native_servers.get(descriptor["name"])
                if prior is None:
                    issues.append(
                        f"ownership entry missing for MCP '{descriptor['name']}' at '{target}'"
                    )
                    continue
                if prior.get("owner") != manifest["name"]:
                    issues.append(
                        f"owner drift for MCP '{descriptor['name']}' at '{target}'"
                    )
                if native is None:
                    issues.append(
                        f"owned MCP entry '{descriptor['name']}' missing at '{target}'"
                    )
                    continue
                actual_hash = stable_json_hash(native)
                expected_hash = stable_json_hash(descriptor["native"])
                if actual_hash != prior.get("renderedHash") or actual_hash != expected_hash:
                    issues.append(
                        f"MCP adapter drift for '{descriptor['name']}' at '{target}', expected owner '{manifest['name']}'"
                    )
        else:
            text = target.read_text(encoding="utf-8") if target.exists() else ""
            before, block, after = split_managed_block(text, manifest["name"])
            external_names = toml_server_names(before + after)
            requested_names = {descriptor["name"] for descriptor in group}
            if external_names & requested_names:
                issues.append(
                    f"MCP collision outside managed block at '{target}' for expected owner '{manifest['name']}'"
                )
            expected_block = codex_managed_block(
                manifest["name"],
                canonical_mcp_servers(manifest, root),
                root,
            )
            actual_hash = sha256_text(block) if block is not None else None
            expected_hash = sha256_text(expected_block)
            for descriptor in group:
                prior = previous_entry(state, descriptor)
                if prior is None:
                    issues.append(
                        f"ownership entry missing for MCP '{descriptor['name']}' at '{target}'"
                    )
                    continue
                if prior.get("owner") != manifest["name"]:
                    issues.append(
                        f"owner drift for MCP '{descriptor['name']}' at '{target}'"
                    )
                if block is None:
                    issues.append(f"owned managed MCP block missing at '{target}'")
                elif actual_hash != prior.get("renderedHash") or actual_hash != expected_hash:
                    issues.append(
                        f"MCP adapter drift for '{descriptor['name']}' at '{target}', expected owner '{manifest['name']}'"
                    )
    return issues


def add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--scope", choices=("repository", "user"), required=True)
    parser.add_argument("--base-dir", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--profile", choices=("skill", "mcp", "bundle"), required=True)
    parser.add_argument("--skill-source", action="append", default=[])
    parser.add_argument("--mcp-source")
    parser.add_argument("--confirm-user-write", action="store_true")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage one canonical skill and MCP source across Codex, Claude Code, and Antigravity."
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    for action in ("plan", "init"):
        add_source_arguments(subparsers.add_parser(action))
    for action in ("render", "validate"):
        action_parser = subparsers.add_parser(action)
        action_parser.add_argument("--extension", required=True)
        if action == "render":
            action_parser.add_argument("--confirm-user-write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    try:
        if args.action in {"plan", "init"}:
            plan = build_plan(args)
            if args.action == "plan":
                output = plan
            else:
                extension_root = initialize(plan, args.confirm_user_write)
                output = {
                    "action": "init",
                    "extensionRoot": str(extension_root),
                    "manifest": str(extension_root / "extension.json"),
                }
        elif args.action == "render":
            output = render_extension(
                Path(args.extension),
                args.confirm_user_write,
            )
        else:
            extension_root = Path(args.extension)
            issues = validate_extension(extension_root)
            if issues:
                fail("E_DRIFT", "; ".join(issues))
            output = {
                "action": "validate",
                "status": "PASS",
                "extensionRoot": str(extension_root.expanduser().resolve()),
                "canonicalHash": canonical_digest(extension_root.expanduser().resolve()),
            }
    except ManagerError as error:
        if error.payload is not None:
            print(json.dumps(error.payload, indent=2, ensure_ascii=False))
        print(f"ERROR {error.code}: {error.detail}", file=sys.stderr)
        return 2
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
