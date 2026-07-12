# Forge Portability Rules

Every distributed Forge skill works unmodified on Claude Code and Codex. The
validator enforces the mechanical subset; the remaining rules require review
and pressure testing.

## 1. Frontmatter

- Use exactly `name` and `description`.
- Match `name` to the skill directory.
- Start descriptions with `Use when`.
- Keep descriptions within 1024 characters, in third person, and limited to trigger conditions.
- Include Korean trigger keywords because description matching is the Codex automatic trigger path.

## 2. Language

Distributed skill bodies stay in English and instruct the agent to respond in
the user's language. Preserve proper names, identifiers, commands, protocols,
and established technical terms in their original form.

## 3. Name Actions, Not Harness Tools

Do not place harness-specific tool names in distributed skill bodies. Describe
the action: create a todo, dispatch a subagent, run in the shell, or edit a
file. The validator rejects the following tokens:

```text
TodoWrite | Task tool | Bash tool | Edit tool | Write tool
```

It also rejects path includes that begin with `@.`, `@/`, or `@skills/`.

## 4. Cross-reference Skills by Name

Use `the forge <name> skill`. Do not use path includes or harness-specific slash
commands. Install paths differ across harnesses and install modes.

## 5. Size and Layout

- Keep `SKILL.md` within 500 lines.
- Move long reference material to `references/`.
- Put executables in `scripts/` and static resources in `assets/`.
- Keep skill support directories one level deep.

## 6. Working-directory Contract

| Artifact | Path | Committed |
|---|---|---|
| Specs | `docs/specs/NNN-<slug>/spec.md` | yes |
| Spec Viewer, when requested | `docs/specs/NNN-<slug>/view.html` | yes |
| Plans | `docs/plans/PPP-<slug>/plan.md` | yes |
| Plan Viewer, when requested | `docs/plans/PPP-<slug>/view.html` | yes |
| Promoted debug notes | `docs/debug/YYYY-MM-DD-<slug>.md` | yes |
| Promoted research notes | `docs/research/` | yes |
| Local scratch and ledgers | `.forge/scratch/` | no |
| Viewer build intermediates | `.forge/viewer-build/` | no |

## 7. Process-skill Structure

Each distributed process skill includes an announce line, Iron Law, Red Flags
table with at least five rows, explicit todo creation for checklists, and a
terminal handoff naming the next Forge skill.

## 8. Repository-only Shared Workflows

Repository-only workflows are not distributed Forge skills.

| Layer | Location | Responsibility |
|---|---|---|
| Shared runbook | `.agent-runbooks/<name>/` | Detailed procedure, scripts, references, validation, and reporting |
| Codex entry | `.agents/skills/<name>/SKILL.md` | Trigger and shared-runbook link |
| Claude Code entry | `.claude/skills/<name>/SKILL.md` | Trigger and shared-runbook link |

Keep both wrappers thin and identical when possible. If a wrapper disagrees
with its runbook, the runbook wins. Repository-only paths stay outside
`plugins/forge/`, so Marketplace installation cannot copy them into the user
plugin.

## 9. Mechanical Gates

- All JSON manifests parse with `jq .`.
- `bash scripts/validate.sh` checks plugin skills and both repository-local wrapper roots.
- A fresh validation run must print `validate: all checks passed` before commit.

## Claude Code and Codex Differences

| Aspect | Claude Code | Codex |
|---|---|---|
| Distributed skill invocation | `forge:skill-name` or automatic matching | `$skill-name` or implicit matching |
| Repository-local skill root | `.claude/skills/` | `.agents/skills/` |
| Hooks | Forge plugin SessionStart hook | No plugin hook support |
| Fresh agents | Native agent dispatch | Multi-agent configuration when available; sequential fallback otherwise |
| Marketplace install | Managed plugin cache from `.claude-plugin/marketplace.json` | Managed plugin cache from `.agents/plugins/marketplace.json` |
| Local Forge install | `~/.claude/skills/forge` | Per-skill entries under `~/.agents/skills/<skill-name>` |

Anything Claude-only is an enhancement, never a distributed-skill dependency.
