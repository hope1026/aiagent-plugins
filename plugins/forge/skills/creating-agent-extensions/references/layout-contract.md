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
