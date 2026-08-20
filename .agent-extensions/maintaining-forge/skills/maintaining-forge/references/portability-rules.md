# Forge Portability Rules

Every distributed Forge skill uses portable Agent Skills instructions that work unmodified on Claude Code, Codex, and Antigravity. The
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
the action: create a checklist item, dispatch a subagent, run in the shell, or edit a
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

## 6. Working-directory and Authority Contract

| Artifact | Path | Committed |
|---|---|---|
| Canonical Spec Bundle — permanent project SOT when approved or implemented | `docs/specs/<semantic-bundle-name>/` with descriptive root and member filenames | yes |
| Optional Change Brief and Spec Delta — work input and approval proposal, never SOT | `.forge/work/<work-id>/brief.md`, `.forge/work/<work-id>/spec-delta.md` | no |
| Execution Plan — high-complexity work source, never project SOT | `docs/plans/PPP-<slug>/plan.md` | yes while retained |
| Optional plan progress and Task detail | `docs/plans/PPP-<slug>/progress.md`, `docs/plans/PPP-<slug>/tasks/*.md` | yes while the plan is retained |
| Brief, Plan, or Spec Visual Doc, when explicitly requested | `.forge/visual-docs/<view-id>/view.html` | no |
| Project Handbook, when explicitly requested | `docs/project-viewer/index.html` | yes, as a reproducible derived document |
| Promoted debug notes | `docs/debug/YYYY-MM-DD-<slug>.md` | yes |
| Promoted research notes | `docs/research/` | yes |
| Local scratch, research, reviews, ledgers, and build intermediates | `.forge/` | no |

Forge routes work on two portable axes: `Canonical Spec impact: yes|no` and `Execution complexity: low|high`. These produce Quick direct, plan-only, spec-backed direct, and full-lifecycle paths on every supported agent. Platform invocation, worker availability, or model mapping changes execution mechanics, never route meaning or artifact authority.

Change Brief readiness is portable too. Every supported agent drafts `Goal`, `Scope`, `Out of Scope`, and observable `Done Checks` in the conversation, inspects repository-discoverable facts, and asks at most one currently blocking user-owned choice before rechecking readiness. A clear request or local reversible default needs no question and no Brief file. Keep Brief clarification (current work outcome), Canonical classification (permanent authority), and Spec clarification (exact durable contract meaning) distinct. Invocation UI and worker availability do not change this boundary.

The ordinary Canonical Spec and Execution Plan lifecycle is Markdown-only. A Spec Bundle is identified by its normalized directory path, and its root `Documents` inventory links every member by descriptive filename and H1. Requirements are mandatory complete statement headings; Acceptance Criteria are optional at bundle level and use complete statement headings when present. Plans and lifecycle verification use Acceptance statements when a bundle has any, otherwise Requirement statements, always through exact `Governing statements:` links rather than short document or statement codes. Visual Docs is a separate request-only presentation layer and never becomes project SOT; only the reproducible Project Handbook is tracked. Promote durable `.forge/research/` findings to `docs/research/`. Retain an applied Spec Delta through verification, then remove it or promote it only as non-authoritative evidence. Before deleting a plan, promote permanent decisions; its `progress.md` and `tasks/*.md` do not remain as independent artifacts.

## 7. Process-skill Structure

Each distributed process skill includes an announce line, Iron Law, Red Flags
table with at least five rows, explicit checklist-item creation, and a
terminal handoff naming the next Forge skill.

## 8. Repository-only Shared Workflows

Repository-only workflows are not distributed Forge skills.

| Layer | Location | Responsibility |
|---|---|---|
| Canonical extension | `.agent-extensions/<extension-name>/` | Complete portable skill, resources, manifest, and ownership state |
| Codex + Antigravity entry | `.agents/skills/<name>/SKILL.md` | Manager-owned thin canonical pointer |
| Claude Code entry | `.claude/skills/<name>/SKILL.md` | Manager-owned thin canonical pointer |

Keep native entries generated and thin. If an adapter differs from its recorded
ownership hash, stop on drift; update the canonical source and render again.
Repository-only paths stay outside `plugins/forge/`, so Marketplace
installation cannot copy them into the user plugin.

## 9. Cross-agent Authoring Structure

The `creating-agent-extensions` distributed skill creates authoring sources, not distribution packages. Repository sources live at `.agent-extensions/<extension-name>/`; user sources live at `~/.agent-extensions/<extension-name>/`. Native entries remain thin or generated and never become an independent source of truth.

| Component | Codex | Claude Code | Antigravity |
|---|---|---|---|
| Repository skill | `.agents/skills/<skill>/SKILL.md` | `.claude/skills/<skill>/SKILL.md` | `.agents/skills/<skill>/SKILL.md` |
| User skill | `~/.agents/skills/<skill>/SKILL.md` | `~/.claude/skills/<skill>/SKILL.md` | `~/.gemini/config/skills/<skill>/SKILL.md` |
| Repository MCP | `.codex/config.toml` | `.mcp.json` | `.agents/mcp_config.json` |
| User MCP | `~/.codex/config.toml` | `~/.claude.json` | `~/.gemini/config/mcp_config.json` |

Native or system authoring helpers may propose detailed skill and MCP content inside a staging boundary. They do not own canonical paths, target adapters, collision decisions, merge ownership, or validation.

## 10. Mechanical Gates

- All JSON manifests parse with `jq .`.
- `bash scripts/validate.sh` checks plugin skills and both repository-local wrapper roots.
- A fresh validation run must print `validate: all checks passed` before commit.

## Claude Code, Codex, and Antigravity Differences

| Aspect | Claude Code | Codex | Antigravity |
|---|---|---|---|
| Distributed skill invocation | `forge:skill-name` or automatic matching | `$skill-name` or implicit matching | automatic matching or native skill invocation |
| Repository-local skill root | `.claude/skills/` | `.agents/skills/` | `.agents/skills/` |
| Hooks | Forge plugin SessionStart hook | No plugin hook support | Agent-specific; never a common dependency |
| Fresh agents | Native agent dispatch | Multi-agent configuration when available; sequential fallback otherwise | Use current agent capability; sequential fallback otherwise |
| Marketplace install in this repository | Managed plugin cache from `.claude-plugin/marketplace.json` | Managed plugin cache from `.agents/plugins/marketplace.json` | No Forge distribution manifest in this repository |
| Local Forge install in this repository | `~/.claude/skills/forge` | Per-skill entries under `~/.agents/skills/<skill-name>` | Consume the Agent Skills source through an explicit Antigravity setup |

Anything agent-only is an enhancement, never a distributed-skill dependency.
