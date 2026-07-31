---
name: using-forge
description: 'Use when starting any conversation or task - establishes the forge spec-first workflow, how to find and route to forge skills before any response including clarifying questions, and the .forge/ working directory contract. Triggers: any task start, "forge", "포지", "스펙 우선", "작업 시작".'
---

# Using Forge

**Announce at start:** "Using the forge using-forge skill to route this work."

Respond to the user in the user's language. This skill file stays in English.

## Overview

Forge is a spec-first development process: the spec is the source of truth, code follows it, and every kind of work has a skill that says how to do it. This skill is the entry point — it exists to route you to the right forge skill before you do anything else.

**If there is even a 1% chance a forge skill applies to what you are doing, you MUST invoke it. This is not negotiable. You cannot rationalize your way out of it.**

## Iron Law

```
NO PRODUCT-BEHAVIOR IMPLEMENTATION WITHOUT AN APPROVED SPEC.
NO IMPLEMENTATION CODE WITHOUT A PLAN TASK. RELATED SPECS ARE THE SOURCE OF TRUTH.
```

### Ceremony floor (closed exemption list)

Spec-first is exempt ONLY when the change alters no documented or documentable behavior:

- typo / comment / formatting-only changes
- dependency bumps with no API change
- CI/tooling config not affecting build outputs
- pure refactors with no observable behavior change AND existing tests pass

Everything else gets a spec. Ceremony scales down — a small change may be a 10-line spec, but the file exists. This list is closed: if the change is not on it, do not invent a new exemption, and do not stretch a listed item to cover your case.

## When to Use / When NOT

**Use:** at the start of every conversation and every new task — before any response (including clarifying questions) and before any action (including exploring the codebase or reading files).

**Do NOT use** only in one case: you were dispatched as a subagent to execute one specific, fully specified task. Then skip routing and execute that task exactly as instructed, including any forge skills the instructions name. A vague or open-ended dispatch does not qualify — route it.

## The Process

1. **Route before responding.** Match the task against the routing table below BEFORE answering questions, exploring, or touching any file.
2. **Announce** the routed skill: "Using the forge <name> skill to <purpose>."
3. **Follow it exactly.** If the skill has a checklist, create one todo per checklist item — never track checklist items only in memory.
4. **When multiple skills apply,** process skills come first — they set the approach; implementation skills (web-app-design, website-design, writing-tone, test-driven-development) carry it out inside that process. Apply both UI design skills only when one approved Task explicitly changes separately owned application and public website files.
5. **Setting a skill aside** is allowed only after reading it, and only by stating explicitly — in your response — why it does not apply. Silently dropping a skill is skipping, not setting aside.

### Routing

| The task looks like | Route to |
|---|---|
| "Build X" / "add X" / "change X" / new project / unclear requirements | the forge writing-specs skill |
| "Fix this bug" / error / test failure / unexpected behavior | the forge systematic-debugging skill |
| "Is it done?" / about to claim complete, fixed, or passing | the forge verifying-work skill |
| Browser application UI — dashboards, admin, settings, tables, forms, controls, internal tools, SaaS workspaces, PWAs | the forge web-app-design skill |
| Public website — landing pages, homepages, marketing or product sites, editorial, portfolios, public documentation | the forge website-design skill |
| UI request with no evidence of application state/workflow or public content/acquisition | ask one classification question: "Is this a stateful browser application or a public content website?" Then route to exactly one UI skill |
| Native mobile or desktop app while its specialist skill is not available | state that the specialist skill is not available; do not force-route it to a web UI skill |
| Viewer shell, template, style, or interaction tooling changes | the forge web-app-design skill; fixed Viewer generation remains the forge spec-viewer skill alone |
| Writing prose humans will read — docs, PRs, commits, messages | the forge writing-tone skill |
| Cross-agent skill, MCP, or bundle authoring for Codex, Claude Code, and Antigravity | the forge creating-agent-extensions skill |
| "Show me the spec" / render or present a spec for review | the forge spec-viewer skill |
| Approved spec exists, no plan yet | the forge writing-plans skill |
| Operational, research, or ceremony-floor work needs an execution plan | the forge writing-plans skill |
| A plan exists in `docs/plans/` with open tasks | the forge executing-plans skill |
| Writing any implementation code | the forge test-driven-development skill |

## Working Files

Forge keeps its artifacts in fixed locations inside the target project:

| Artifact | Path | Committed |
|---|---|---|
| Specs — permanent source of truth | `docs/specs/NNN-<slug>/spec.md` | yes |
| Spec Viewer — when explicitly generated | `docs/specs/NNN-<slug>/view.html` | yes |
| Work-scoped implementation plans | `docs/plans/PPP-<slug>/plan.md` | yes |
| Plan Viewer — when explicitly generated | `docs/plans/PPP-<slug>/view.html` | yes |
| Promoted debug / root-cause notes | `docs/debug/YYYY-MM-DD-<slug>.md` | yes |
| Promoted research notes | `docs/research/YYYY-MM-DD-<slug>.md` | yes |
| Scratch — local progress and briefs | `.forge/scratch/` | no |
| Viewer build intermediates | `.forge/viewer-build/` | no |

`.forge/scratch/` and `.forge/viewer-build/` contain local, regenerable files and remain uncommitted. Spec directories use independent `NNN-<slug>` identifiers and persist for the project lifetime. Plan directories use independent `PPP-<slug>` identifiers and may be deleted when their work ends after permanent decisions are promoted to a spec, ADR, or another durable document.

## Red Flags

These thoughts mean STOP — you are rationalizing:

| Excuse | Reality |
|---|---|
| "This is just a simple question" | Questions are tasks. Route before answering. |
| "I need more context first" | The skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Route first. |
| "The skill is overkill for this" | Simple things become complex. Ceremony scales down inside the skill, not by skipping it. |
| "This change is too small for a spec" | Check the ceremony floor. If it is not on the closed list, it gets a spec — maybe a 10-line one. |
| "The user told me exactly what to do" | A task description is not permission to skip process. Only an explicit "skip the spec / skip the skill" from the user is. |
| "No forge skill matches this exactly" | Build/change → writing-specs. Broken → systematic-debugging. Done? → verifying-work. If truly nothing applies, state that conclusion out loud before proceeding. |
| "I'm already halfway through" | Route the moment you notice. Work already done does not exempt the work remaining. |
| "I remember what that skill says" | Skills evolve. Read the current version every time. |
| "I'll just do this one thing first" | Route BEFORE doing anything. |
| "The user seems in a hurry" | Skipping process produces rework, which is slower. The disciplined path is the fast path. |

## Platform Adaptation

If running in Codex, read references/codex-tools.md — it maps forge's named actions to Codex tools, explains explicit skill invocation, and gives the sequential fallback rule when subagents are unavailable.

## User Instructions and Language

User instructions — project instruction files (AGENTS.md, CLAUDE.md, and similar) and direct requests — take precedence over skills, which in turn override default behavior. Only skip a skill's workflow when the user has explicitly told you to skip it; a request for an outcome ("just add the button") is not an instruction to skip the process that produces it.

Execution-mode requests may choose only routes that satisfy the routed skill's safety gates: requesting parallel execution does not by itself waive dependency, write-overlap, verification, authority, or release gates. An explicit request to change one of those governing constraints is a spec or scope decision, not an ordinary routing preference.

Skill files are written in English. Always respond to the user in the user's language.

## Handoff

**Routing complete. The routed forge skill owns the process from here — follow its steps and its own Handoff line.** The default lifecycle chain is: the forge writing-specs skill → the forge writing-plans skill → the forge executing-plans skill → the forge verifying-work skill.
