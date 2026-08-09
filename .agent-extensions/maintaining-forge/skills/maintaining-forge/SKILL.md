---
name: maintaining-forge
description: 'Use when creating, editing, reviewing, or testing Forge skills or changing Forge plugin manifests, hooks, validators, install scripts, or release documentation in this repository. Triggers: "스킬 수정", "스킬 추가", "forge 수정", "플러그인 수정", editing files under plugins/forge/.'
---

# Maintaining Forge

Use this runbook when creating, editing, reviewing, or testing Forge skills, or
when changing Forge plugin manifests, hooks, validators, install scripts, or
release documentation in this repository.

Respond to the user in the user's language. Forge plugin skill files and the
repository-local adapter skills stay in English.

## Overview

Forge skills are process documentation that must hold up under pressure on
Codex, Claude Code, and Antigravity. Editing a distributed skill is releasing software: the
mechanical gate is the validator, the behavioral gate is a pressure test, and
pushing to the repository releases the Marketplace package.

Repository-only workflows use a different packaging boundary. Their canonical
source lives under `.agent-extensions/<extension-name>/`; generated native
entries under `.agents/skills/` and `.claude/skills/` only point back to it.

## Iron Law

```text
VALIDATE BEFORE COMMIT. PRESSURE-TEST BEFORE PUSH. PUSH IS RELEASE.
DISTRIBUTED SKILL CHANGES REQUIRE A VERSION BUMP BEFORE PUSH.
```

No exception exists for a one-line tweak, a wording-only gate change, or a
promise to test after pushing.

## When to Use

- Adding or editing a user-facing Forge skill under `plugins/forge/skills/`
- Creating or editing a repository-only shared workflow under `.agent-extensions/`
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
| Repository-only shared workflow | `.agent-extensions/<extension-name>/skills/<skill-name>/` | Manager-owned thin wrappers under `.agents/skills/` and `.claude/skills/` | Excluded from the Forge plugin |

For repository-only workflows:

- Put the complete portable skill and its resources in one owned `.agent-extensions/<extension-name>/` canonical root.
- Create and update native wrappers only through the creating-agent-extensions manager.
- Stop on unowned same-name entries or changed owned wrappers; rename, adopt, or merge only after an explicit user decision.
- Treat the canonical skill as the source of truth and repair adapters by rendering again, never by hand-editing wrappers.

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
3. Write the smallest complete change. For repository-only workflows, edit only
   the owned canonical skill and render its native adapters through the manager.
4. Keep the normal spec and plan lifecycle Markdown-only. Visual Docs tooling may create HTML only through an explicit user request; maintainer tests use isolated temporary fixtures and never create a repository Visual Docs as a side effect.
5. Run `bash scripts/validate.sh` from the repository root. It must print
   `validate: all checks passed` before commit.
6. Search changed skill files for banned tokens and re-read every gate under
   deadline pressure. Add explicit counters for any plausible loophole.
7. Pressure-test every new skill and every edit that changes instructions.
   Typos, formatting-only changes, and link fixes may skip the live test, but
   never the adversarial self-read.
8. Before push, inspect the commits that are ahead of the configured upstream.
   If the push target includes `plugins/forge/skills/`, run the Version Gate
   Before Push below. A version bump is part of the same release, not a later
   follow-up.
9. Use a conventional commit. Do not push until every gate passes and the user
   has authorized release; push publishes the Marketplace state.

## Pre-ship Checklist

Create one checklist item per applicable item and record evidence for each.

- [ ] The workflow audience is classified as Marketplace user-facing or repository-only.
- [ ] Distributed skill frontmatter contains exactly `name` and `description` and the name matches its directory.
- [ ] Descriptions start with `Use when`, contain triggers only, include Korean keywords, and stay within 1024 characters.
- [ ] Distributed skill bodies name actions, not harness-specific tools.
- [ ] Process skill structure includes its announce line, Iron Law, Red Flags, and terminal handoff.
- [ ] `SKILL.md` stays within 500 lines and support files use `references/`, `scripts/`, or `assets/`.
- [ ] Repository-only detail lives in one owned `.agent-extensions/` source; native wrappers are manager-rendered adapters.
- [ ] `bash scripts/validate.sh` printed `validate: all checks passed` in a fresh run.
- [ ] When the push target includes `plugins/forge/skills/`, both plugin
      manifests satisfy the Version Gate Before Push.
- [ ] Instruction changes passed a live pressure test; every change passed an adversarial self-read.
- [ ] The commit uses a conventional message.
- [ ] Push occurs only with release authorization.

## Version Gate Before Push

Before pushing, resolve the configured upstream and inspect the commits that
would be published. If that range changes any path under
`plugins/forge/skills/`:

1. Read the upstream release versions from
   `plugins/forge/.claude-plugin/plugin.json` and
   `plugins/forge/.codex-plugin/plugin.json`.
2. Increase the Claude plugin base version above the upstream release version.
3. Set the Codex plugin to the same base version and append a fresh UTC
   `+codex.YYYYMMDDHHMMSS` suffix.
4. Re-run validation after changing the manifests. Stop before push if either
   manifest is unchanged, the base versions differ, or the Codex suffix is not
   fresh.

This gate applies to the complete outgoing commit range, not only the latest
commit or the current working tree. Multiple skill commits may share one
release version bump when they are pushed together.

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
| `writing-specs` | Create, approve, inspect, and validate semantic Spec Bundles with full-statement links |
| `writing-plans` | Create independently identified plans with optional Related Spec Bundle paths and Task-level governing statement links |
| `executing-plans` | Execute tasks with plan-local progress and checkpoints |
| `test-driven-development` | Enforce red, green, refactor |
| `systematic-debugging` | Reproduce, isolate, and establish root cause |
| `verifying-work` | Gather fresh acceptance evidence |
| `visual-docs` | Build request-only Brief, Plan, and Spec views plus the tracked source-backed Project Handbook |
| `web-app-design` | Design browser application hierarchy, state geometry, and interaction |
| `website-design` | Design public website content composition, imagery, and responsive behavior |
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
| Repository-only canonical extensions | `.agent-extensions/<extension-name>/` |
| Codex + Antigravity repository adapters | `.agents/skills/<name>/SKILL.md` |
| Claude Code repository adapters | `.claude/skills/<name>/SKILL.md` |
| Plugin manifests | `plugins/forge/.claude-plugin/plugin.json`, `plugins/forge/.codex-plugin/plugin.json` |
| Marketplace manifests | `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json` |
| Claude-only hooks | `plugins/forge/hooks/` |
| Validator | `scripts/validate.sh` |
| Dev install script | `scripts/install.sh` |
| Pressure-test notes | `.forge/scratch/` |
| Repository Spec Bundles | `docs/specs/<semantic-bundle-name>/` with descriptive root and member filenames |
| Repository plans | `docs/plans/PPP-<slug>/plan.md` |
| Requested Brief, Plan, or Spec view | `.forge/visual-docs/<view-id>/view.html` |
| Requested Project Handbook | `docs/project-viewer/index.html` |
| Shared research and debug records | `docs/research/`, `docs/debug/` |

The validator checks distributed plugin skills, canonical extension skills,
and repository adapters, then validates each extension's ownership and parity.

## Red Flags

| Excuse | Reality |
|---|---|
| "It is only a wording change." | One line can open a loophole; validate and re-read the gates. |
| "The skill is obviously clear." | A fresh agent under pressure is the behavioral test. |
| "Validation passed, so it can ship." | Mechanical validation does not prove behavior; pressure-test instruction changes. |
| "I will test after pushing." | Push is release; Marketplace users can receive the defect first. |
| "Put the repository workflow in the plugin for convenience." | That exposes maintainer-only behavior to installation users and breaks the packaging boundary. |
| "Copy the procedure into both wrappers." | Duplicate procedures drift; the canonical extension is the only detailed source. |
| "Edit the wrapper because it is only a small change." | Owned adapters are generated artifacts; edit canonical content and render again. |
| "Repository-only means validation can be lighter." | Local agent workflows can still release the plugin; the same mechanical and behavioral gates apply. |
| "No fresh agent is available, so skip the test." | Perform and record the adversarial self-read; do not silently omit the gate. |
| "The skill change is already committed; bump the version next time." | The outgoing commits are the release unit. Bump both manifests before this push or stop. |

## Handoff

After local implementation, validation, and pressure testing, use the Forge
verifying-work skill against the approved repository spec. Report release as a
separate action: do not push without explicit authorization.
