# Maintaining Forge Runbook

Use this runbook when creating, editing, reviewing, or testing Forge skills, or
when changing Forge plugin manifests, hooks, validators, install scripts, or
release documentation in this repository.

Respond to the user in the user's language. Forge plugin skill files and the
repository-local wrapper skills stay in English.

## Overview

Forge skills are process documentation that must hold up under pressure on
Codex, Claude Code, and Antigravity. Editing a distributed skill is releasing software: the
mechanical gate is the validator, the behavioral gate is a pressure test, and
pushing to the repository releases the Marketplace package.

Repository-only workflows use a different packaging boundary. Their detailed
procedure lives under `.agent-runbooks/`, while Claude Code uses a thin
`.claude/skills/` wrapper and Codex plus Antigravity share a thin
`.agents/skills/` wrapper that point to the same runbook.

## Iron Law

```text
VALIDATE BEFORE COMMIT. PRESSURE-TEST BEFORE PUSH. PUSH IS RELEASE.
```

No exception exists for a one-line tweak, a wording-only gate change, or a
promise to test after pushing.

## When to Use

- Adding or editing a user-facing Forge skill under `plugins/forge/skills/`
- Creating or editing a repository-only shared workflow under `.agent-runbooks/`
- Editing Forge skill references, scripts, assets, manifests, or hooks
- Changing the validator, local install script, Marketplace metadata, or release documentation
- Reviewing or pressure-testing Forge skill behavior

Do not use this runbook merely to follow a Forge skill inside another project.
Use the relevant distributed Forge skill there.

## Choose the Correct Skill Boundary

Decide the audience before writing files.

| Workflow type | Detailed source of truth | Agent entry points | Distribution |
|---|---|---|---|
| Marketplace Forge user skill | `plugins/forge/skills/<skill-name>/` | One portable `SKILL.md`; Codex and Claude manifests distribute it, and Antigravity can consume the Agent Skills source | Included in the Forge plugin |
| Repository-only shared workflow | `.agent-runbooks/<name>/` | `.agents/skills/<name>/SKILL.md` for Codex + Antigravity and `.claude/skills/<name>/SKILL.md` for Claude Code | Excluded from the Forge plugin |

For repository-only workflows:

- Put procedures, commands, scripts, references, validation steps, and reporting requirements in `.agent-runbooks/<name>/`.
- Keep agent wrappers limited to frontmatter, trigger conditions, the runbook path, and conflict-resolution rules.
- Keep the shared `.agents/` and Claude Code wrappers identical when tool-specific metadata is unnecessary.
- If a wrapper and runbook disagree, the runbook wins; fix the wrapper.

This shared-runbook/thin-wrapper pattern follows the established structure in
the sibling `weppy-roblox-mcp-private` repository.

## Distributed Forge Skill Anatomy

Distributed Forge `SKILL.md` frontmatter contains exactly `name` and
`description`. The name matches the directory. The description starts with
`Use when`, stays within 1024 characters, uses third person, contains trigger
conditions only, and includes Korean trigger keywords.

A process skill normally contains:

```markdown
# <Title>

Announce at start: "Using the forge <name> skill..."

## Overview
## Iron Law
## When to Use / When NOT
## The Process
## Working Files
## Red Flags
## Handoff
```

Keep `SKILL.md` at or below 500 lines. Move long explanatory material to
`references/`, executables to `scripts/`, and static resources to `assets/`.
Keep the layout one directory level deep.

Bodies name actions rather than harness-specific tools. Cross-reference other
Forge skills by name, as `the forge <name> skill`. Read
`references/portability-rules.md` before writing or reviewing a distributed
Forge skill.

## Editing Loop

1. Read the target skill or runbook completely. For distributed Forge skills,
   also read `references/portability-rules.md`. For a new process skill, read an
   existing process skill as a structural model.
2. Confirm whether the workflow is Marketplace user-facing or repository-only,
   then use the corresponding boundary table above.
3. Write the smallest complete change. Do not copy detailed repository-only
   procedures into the two wrapper skills.
4. Run `bash scripts/validate.sh` from the repository root. It must print
   `validate: all checks passed` before commit.
5. Search changed skill files for banned tokens and re-read every gate under
   deadline pressure. Add explicit counters for any plausible loophole.
6. Pressure-test every new skill and every edit that changes instructions.
   Typos, formatting-only changes, and link fixes may skip the live test, but
   never the adversarial self-read.
7. Use a conventional commit. Do not push until every gate passes and the user
   has authorized release; push publishes the Marketplace state.

## Pre-ship Checklist

Create one todo per applicable item and record evidence for each.

- [ ] The workflow audience is classified as Marketplace user-facing or repository-only.
- [ ] Distributed skill frontmatter contains exactly `name` and `description` and the name matches its directory.
- [ ] Descriptions start with `Use when`, contain triggers only, include Korean keywords, and stay within 1024 characters.
- [ ] Distributed skill bodies name actions, not harness-specific tools.
- [ ] Process skill structure includes its announce line, Iron Law, Red Flags, and terminal handoff.
- [ ] `SKILL.md` stays within 500 lines and support files use `references/`, `scripts/`, or `assets/`.
- [ ] Repository-only detail lives in `.agent-runbooks/`; both wrappers point to it and do not duplicate it.
- [ ] `bash scripts/validate.sh` printed `validate: all checks passed` in a fresh run.
- [ ] Instruction changes passed a live pressure test; every change passed an adversarial self-read.
- [ ] The commit uses a conventional message.
- [ ] Push occurs only with release authorization.

## Pressure-testing Skills

Write a realistic scenario that combines at least two pressures, such as a
deadline, sunk cost, or authority asking for a one-time exception. Give a fresh
agent the scenario, the entry skill, the runbook or distributed skill body, and
the required references without announcing that it is a test.

Compliance means the agent follows the gates and chooses the correct packaging
boundary. If it rationalizes around a gate, quote the rationalization, add a
specific counter to the governing Red Flags section, and repeat the test. If no
fresh-agent capability exists, perform the adversarial self-read and record that
the live pressure test remains pending.

## Forge System Map

The distributed Forge plugin contains user-execution skills only:

| Skill | Responsibility |
|---|---|
| `using-forge` | Route user project work into the spec-first lifecycle |
| `writing-specs` | Create and approve the source-of-truth spec |
| `writing-plans` | Create independently identified plans with optional Related Specs |
| `executing-plans` | Execute tasks with plan-local progress and checkpoints |
| `test-driven-development` | Enforce red, green, refactor |
| `systematic-debugging` | Reproduce, isolate, and establish root cause |
| `verifying-work` | Gather fresh acceptance evidence |
| `spec-viewer` | Render lifecycle review Views from source documents |
| `ui-design` | Declare and verify visual systems |
| `writing-tone` | Shape natural human-readable prose |
| `marketing-tone` | Apply factual marketing and product tone |
| `operations-tone` | Apply clear support and operations tone |
| `creating-agent-extensions` | Author one `.agent-extensions/` source and render owned skill/MCP adapters for Codex, Claude Code, and Antigravity |

This `maintaining-forge` runbook is repository-only and is not part of that
distributed catalog.

## Working Files

| Purpose | Path |
|---|---|
| Marketplace Forge skills | `plugins/forge/skills/<skill-name>/` |
| Repository-only runbooks | `.agent-runbooks/<name>/` |
| Codex + Antigravity repository wrappers | `.agents/skills/<name>/SKILL.md` |
| Claude Code repository wrappers | `.claude/skills/<name>/SKILL.md` |
| Plugin manifests | `plugins/forge/.claude-plugin/plugin.json`, `plugins/forge/.codex-plugin/plugin.json` |
| Marketplace manifests | `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json` |
| Claude-only hooks | `plugins/forge/hooks/` |
| Validator | `scripts/validate.sh` |
| Dev install script | `scripts/install.sh` |
| Pressure-test notes | `.forge/scratch/` |
| Repository specs | `docs/specs/NNN-<slug>/spec.md` |
| Repository plans | `docs/plans/PPP-<slug>/plan.md` |
| Shared research and debug records | `docs/research/`, `docs/debug/` |

The validator checks distributed plugin skills plus repository-local wrapper
skills under `.agents/skills/` and `.claude/skills/`.

## Red Flags

| Excuse | Reality |
|---|---|
| "It is only a wording change." | One line can open a loophole; validate and re-read the gates. |
| "The skill is obviously clear." | A fresh agent under pressure is the behavioral test. |
| "Validation passed, so it can ship." | Mechanical validation does not prove behavior; pressure-test instruction changes. |
| "I will test after pushing." | Push is release; Marketplace users can receive the defect first. |
| "Put the repository workflow in the plugin for convenience." | That exposes maintainer-only behavior to installation users and breaks the packaging boundary. |
| "Copy the procedure into both wrappers." | Duplicate procedures drift; the shared runbook is the only detailed source. |
| "The wrappers differ only a little." | Keep them identical unless a real harness-specific requirement exists and is documented. |
| "Repository-only means validation can be lighter." | Local agent workflows can still release the plugin; the same mechanical and behavioral gates apply. |
| "No fresh agent is available, so skip the test." | Perform and record the adversarial self-read; do not silently omit the gate. |

## Handoff

After local implementation, validation, and pressure testing, use the Forge
verifying-work skill against the approved repository spec. Report release as a
separate action: do not push without explicit authorization.
