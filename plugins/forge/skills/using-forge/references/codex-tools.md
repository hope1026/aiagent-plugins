# Codex Adaptations

How forge runs on the Codex CLI. Read this once per session when running in Codex, then apply the mappings whenever a forge skill names an action.

## Skill invocation

Codex has no session-start hook, so this router skill arrives by description matching, not injection.

- **Explicit:** invoke any forge skill by typing `$<skill-name>` (for example `$writing-specs`, `$systematic-debugging`).
- **Implicit:** Codex matches skill descriptions against the task; the routing table in the forge using-forge skill still decides which one is correct.
- **Recommended:** add one pointer line to the project's `AGENTS.md` so the workflow loads at session start, for example: "Before responding to any task, follow the forge using-forge skill (spec-first workflow)."

## Action-to-tool mapping

Forge skills name actions, never harness tools. On Codex, perform them as:

| When a forge skill says | On Codex, use |
|---|---|
| create a todo / track a checklist | `update_plan` |
| run in the shell | `shell` |
| edit files / write files | `apply_patch` |
| dispatch a subagent | `spawn_agent` (see multi-agent support below) |

## Subagent dispatch requires multi-agent support

Add to your Codex config (`~/.codex/config.toml`):

```toml
[features]
multi_agent = true
```

These operations let the forge executing-plans skill dispatch bounded Tasks that pass adaptive routing. Do not dispatch a fresh subagent mechanically for every Task. Use only the multi-agent lifecycle operations exposed by the current Codex session.

## Sequential fallback rule

If no subagent capability is available, execute sequentially; never fabricate tool calls. Do the tasks yourself, one at a time, in plan order, applying the same per-task gates (the forge test-driven-development skill, per-task verification, ledger updates) the dispatching skill requires. A missing feature changes who does the work — never whether the process is followed.

## Capability-tier agent roles

Forge uses `fast`, `balanced`, and `frontier` as portable capability tiers, not fixed model slugs. Codex custom agent roles may map `forge_fast`, `forge_balanced`, and `forge_frontier` through `agents.<name>.config_file`; the user's role config owns the actual model and reasoning settings.

When a configured tier role is unavailable, inherit the current model. Model fallback does not disable collaboration: subagents remain available whenever Codex exposes multi-agent capability, so independent Tasks may still run in parallel with the inherited model. Use sequential fallback only when subagent capability itself is unavailable. Never claim a role or model switch that the current session cannot perform.
