#!/usr/bin/env python3
"""Create and validate canonical cross-agent extension structures."""

from __future__ import annotations

import argparse
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

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


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


def parse_skill_source(path: Path) -> dict[str, str]:
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
    return {
        "name": metadata["name"],
        "description": metadata["description"],
        "source": str(path.resolve()),
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
        if scope == "repository":
            targets.extend(
                [
                    base_dir / ".codex" / "config.toml",
                    base_dir / ".mcp.json",
                    base_dir / ".agents" / "mcp_config.json",
                ]
            )
        else:
            targets.extend(
                [
                    base_dir / ".codex" / "config.toml",
                    base_dir / ".claude.json",
                    base_dir / ".gemini" / "config" / "mcp_config.json",
                ]
            )
    return targets


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
    if sources["mcp"] is not None:
        canonical_writes.append("mcp/servers.json")
    native_targets = native_targets_for(
        args.scope, base_dir, sources["skills"], sources["mcp"] is not None
    )
    collisions: list[str] = []
    if extension_root.exists():
        collisions.append(str(extension_root))
    collisions.extend(str(path) for path in native_targets if path.exists())
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
    manifest = load_manifest(extension_root)
    paths = [Path("extension.json")]
    paths.extend(Path(item["path"]) for item in manifest["components"]["skills"])
    paths.extend(Path(item["path"]) for item in manifest["components"]["mcpServers"])
    digest = hashlib.sha256()
    for relative in sorted(set(paths), key=str):
        if relative.is_absolute() or ".." in relative.parts:
            fail("E_MANIFEST", f"manifest path escapes extension root: {relative}")
        path = extension_root / relative
        if not path.is_file():
            fail("E_MANIFEST", f"manifest path does not resolve to a file: {relative}")
        digest.update(str(relative).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


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
        else:
            fail("E_NOT_IMPLEMENTED", f"{args.action} is not implemented yet")
    except ManagerError as error:
        print(f"ERROR {error.code}: {error.detail}", file=sys.stderr)
        return 2
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
