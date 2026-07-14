# Agent Extension Layout Contract

The canonical repository root is `<repo>/.agent-extensions/<extension-name>/`. The canonical user root is `~/.agent-extensions/<extension-name>/`.

Each extension has one `extension.json`, canonical skills under `skills/<skill-name>/SKILL.md`, canonical MCP definitions under `mcp/servers.json`, and derived ownership state under `adapters/<agent>/state.json`.

The deterministic manager exposes four actions:

```text
manage_extension.py plan
manage_extension.py init
manage_extension.py render
manage_extension.py validate
```

`plan` never writes. User-scope `init` and `render` require `--confirm-user-write`.

## Canonical Manifest

`extension.json` uses schema version 1 and contains exactly these top-level fields:

```json
{
  "schemaVersion": 1,
  "name": "example-extension",
  "description": "Example extension for confirmed workflows.",
  "scope": "repository",
  "targets": ["codex", "claude-code", "antigravity"],
  "components": {
    "skills": [
      {
        "name": "example-skill",
        "description": "Use when the confirmed example workflow applies.",
        "path": "skills/example-skill/SKILL.md"
      }
    ],
    "mcpServers": []
  }
}
```

All component paths are relative to the extension root and must resolve to files inside that root.

## Skill Targets

| Scope | Codex | Claude Code | Antigravity |
|---|---|---|---|
| repository | `.agents/skills/<skill>/SKILL.md` | `.claude/skills/<skill>/SKILL.md` | `.agents/skills/<skill>/SKILL.md` |
| user | `~/.agents/skills/<skill>/SKILL.md` | `~/.claude/skills/<skill>/SKILL.md` | `~/.gemini/config/skills/<skill>/SKILL.md` |

Repository wrappers use a relative canonical path so a checkout can move. User wrappers use the resolved user canonical path. Wrappers contain frontmatter and an instruction to read the canonical skill; they never copy the canonical body.

## Ownership State

Each agent has `adapters/<agent>/state.json` with schema version, extension owner, canonical SHA-256, native target, and the rendered entry SHA-256. A render may update an owned entry only when its live hash still matches the previous state. A missing, modified, or differently owned entry is drift or collision, never an implicit adoption.

## Canonical MCP Definition

`mcp/servers.json` contains only `mcpServers`. The portable schema supports stdio and streamable HTTP definitions:

```json
{
  "mcpServers": {
    "local-tools": {
      "transport": "stdio",
      "command": "python3",
      "args": ["server.py"],
      "envVars": ["LOCAL_TOOLS_TOKEN"]
    },
    "remote-tools": {
      "transport": "http",
      "url": "https://example.test/mcp",
      "headersFromEnv": {"Authorization": "REMOTE_TOOLS_TOKEN"}
    }
  }
}
```

`envVars` and `headersFromEnv` contain environment variable names, never credential values. Raw `env`, raw `headers`, token, password, secret, and authorization values are rejected.

## MCP Targets

| Scope | Codex | Claude Code | Antigravity |
|---|---|---|---|
| repository | `.codex/config.toml` | `.mcp.json` | `.agents/mcp_config.json` |
| user | `~/.codex/config.toml` | `~/.claude.json` | `~/.gemini/config/mcp_config.json` |

Codex entries live inside `# BEGIN creating-agent-extensions:<extension>` and matching end markers. Bytes outside that block remain unchanged. Claude Code and Antigravity use the native `mcpServers` JSON object; unrelated keys and server values remain semantically unchanged. A same-name server without matching ownership state is a collision.

The user preview lists every canonical source, native target, entry-level create/update/collision action, and required environment variable before `--confirm-user-write` permits a render.
