---
name: using-forge
description: 'Use when starting any conversation or task - establishes Canonical Spec and task routing, work-artifact authority, direct and planned execution paths, and the .forge/ contract. Triggers: any task start, "forge", "포지", "정본 스펙", "작업 시작", "바로 진행".'
---

# Using Forge

**Announce at start:** "Using the forge using-forge skill to classify Canonical Spec impact and execution complexity."

Respond to the user in the user's language. This skill file stays in English.

## Overview

Forge separates durable project truth from the artifacts used to complete one piece of work. A Canonical Spec records approved intent, contracts, policy, and invariants that future work must preserve. A Change Brief, Spec Delta, Execution Plan, or Verification Evidence has narrower authority and a shorter lifetime.

Route every execution request on two independent axes:

1. **Canonical Spec impact:** does the request change durable project authority?
2. **Execution complexity:** does safe execution need an explicit multi-step plan?

Small work can change a durable contract, and complex work can leave the project contract untouched. Do not infer one axis from the other.

## Iron Law

```text
NO DURABLE CONTRACT CHANGE WITHOUT AN APPROVED CANONICAL SPEC OR SPEC DELTA.
NO HIGH-COMPLEXITY EXECUTION WITHOUT AN EXECUTION PLAN.
NO COMPLETION CLAIM WITHOUT FRESH VERIFICATION EVIDENCE.
```

## Terminology and Authority

| Artifact | Purpose | Default location | Authority and lifetime |
|---|---|---|---|
| Canonical Spec | Approved system intent, contract, policy, and invariants | `docs/specs/NNN-<slug>/spec.md` | Permanent project SOT; only `approved` or `implemented` is authoritative |
| Change Brief | Goal, Scope, Out of Scope, and Done Checks for current work | Conversation or `.forge/work/<work-id>/brief.md` | Optional work input; not SOT |
| Spec Delta | Proposed exact change to a Canonical Spec | Conversation or `.forge/work/<work-id>/spec-delta.md` | Approval proposal; not SOT before application |
| Execution Plan | Dependencies, Tasks, Steps, checkpoints, and verification | `docs/plans/PPP-<slug>/plan.md` | Work-scoped execution source; not project SOT |
| Verification Evidence | Fresh commands and observations supporting a claim | Conversation, plan progress, or promoted evidence | Proof for a claim; durable only when explicitly promoted |

Reserve `Requirements` and `Acceptance Criteria` for Canonical Specs. A Change Brief uses `Goal`, `Scope`, `Out of Scope`, and `Done Checks`. An Execution Plan uses `Task`, `Step`, `Checkpoint`, and `Verification`.

## Classification

### Axis 1 — Canonical Spec impact

Classify `yes` when the work adds, changes, or removes any of these:

- an existing Canonical Spec R or AC;
- an external interface, persisted data or schema, user workflow or state transition, or error meaning;
- security, authorization, privacy, billing, compliance, or another durable policy;
- a cross-component responsibility or integration contract;
- a release or operational contract that future work must preserve;
- a decision the user explicitly designates for permanent project authority.

Classify `no` when the work restores implementation to an existing approved contract, or changes a local implementation or presentation detail whose complete intent is carried by code and tests and does not need durable project authority. Investigation alone does not create Canonical Spec impact.

If durable value is genuinely unclear, ask one classification question before the first mutation. Do not turn ordinary implementation preferences into project policy by assumption.

### Axis 2 — Execution complexity

Classify `high` when safe execution needs any of these:

- multiple dependent stages or components;
- parallel write ownership or a zero-context handoff;
- migration or release ordering;
- meaningful rollback or data-safety risk;
- a work sequence whose recovery point must survive interruption.

Classify `low` when the work is bounded, local, reversible, independently understandable, and provable with a focused command or observation.

### Route matrix

| Canonical Spec impact | Execution complexity | Route |
|---|---|---|
| `no` | `low` | **Quick direct:** no Canonical Spec, Spec Delta, or Execution Plan; apply the relevant execution skill and gather fresh focused evidence |
| `no` | `high` | **Plan-only:** create a Change Brief only when needed and use the forge writing-plans skill without inventing a Canonical Spec |
| `yes` | `low` | **Spec-backed direct:** use the forge writing-specs skill for an approved Spec Delta, then execute directly without an Execution Plan |
| `yes` | `high` | **Full lifecycle:** approved Spec Delta or Canonical Spec, then the forge writing-plans and executing-plans skills |

## The Process

1. **Classify before mutating.** Record both axes and the selected route. Reading context needed to classify is allowed; implementation mutation waits for the route.
2. **Route to the owning process.** Quick work goes directly to the relevant debugging, TDD, design, tone, or other execution skill. Plan-only work goes to the forge writing-plans skill. Canonical Spec impact goes to the forge writing-specs skill before implementation.
3. **Apply specialist skills inside the route.** Bugs use the forge systematic-debugging skill before their fix class is final. Implementation code uses the forge test-driven-development skill. Browser application and public website work use their respective design skills. Human-readable prose uses the forge writing-tone skill.
4. **Promote before the next mutation.** If Quick or plan-only work reveals Canonical Spec impact, a user-owned product decision, cross-component dependency, migration or release ordering, or meaningful rollback risk, stop the next mutation and reclassify. Add only the newly required Spec Delta or Execution Plan.
5. **Verify at the matching level.** Quick work needs fresh focused command evidence. Existing-contract restoration needs the original reproduction, the affected contract observation, and a regression command. Approved Spec Delta work needs the affected AC walk and regression evidence; a new Canonical Spec needs every AC walked.
6. **Promote durable outcomes.** Move lasting decisions or findings to a Canonical Spec, ADR, `docs/research/`, `docs/debug/`, or explicit evidence file. Do not leave a Change Brief, Spec Delta, or execution log as accidental SOT.

### Specialist routing

| The task looks like | Route inside the selected path |
|---|---|
| Bug, error, test failure, or unexpected behavior | the forge systematic-debugging skill; classify the fix after root cause |
| Canonical Spec proposal, durable behavior or policy change, clarification, or drift | the forge writing-specs skill |
| High-complexity execution with or without Related Specs | the forge writing-plans skill |
| Existing Execution Plan with open Tasks | the forge executing-plans skill |
| Writing implementation code | the forge test-driven-development skill |
| About to claim complete, fixed, or passing | the forge verifying-work skill |
| Browser application UI | the forge web-app-design skill |
| Public website | the forge website-design skill |
| Human-readable prose | the forge writing-tone skill |
| Cross-agent skill or MCP authoring | the forge creating-agent-extensions skill |
| Explicit Review Viewer create, refresh, present, or freshness request | the forge review-viewer skill |

When UI context does not reveal whether the surface is a stateful browser application or a public content website, ask that single classification question and route to exactly one UI skill. A missing native mobile or desktop specialist is not permission to force-route the work to a web UI skill.

## When to Use / When NOT

**Use:** at the start of every conversation and new task, before implementation mutation or a claim about work state.

**Do NOT use:** when dispatched as a subagent for one concrete, fully specified Task whose route, authority, files, and verification are already fixed. Execute that Task and the skills it names. A vague or open-ended dispatch still requires this router.

## Working Files

| Artifact | Path | Git policy |
|---|---|---|
| Canonical Spec | `docs/specs/NNN-<slug>/spec.md` | Tracked, permanent |
| Execution Plan | `docs/plans/PPP-<slug>/plan.md` | Tracked while retained |
| Optional plan progress and Task detail | `docs/plans/PPP-<slug>/progress.md`, `docs/plans/PPP-<slug>/tasks/*.md` | Tracked while the plan is retained |
| Optional Change Brief and Spec Delta | `.forge/work/<work-id>/brief.md`, `.forge/work/<work-id>/spec-delta.md` | Local only until durable meaning is promoted |
| Requested Review Viewer | `.forge/reviews/<review-id>/view.html` | Local only, explicit request required |
| Shared research and root-cause records | `docs/research/`, `docs/debug/` | Tracked when promoted |

## Red Flags

| Excuse | Reality |
|---|---|
| "It is simple, so it is Quick." | Simplicity describes execution, not durable authority. Classify both axes. |
| "It changes behavior, so it needs a new spec." | Only behavior that belongs in durable project authority needs a Canonical Spec or Delta. |
| "No spec exists, so the change cannot affect the SOT." | A new durable contract is exactly when a Canonical Spec may be needed. |
| "The plan captures the truth." | A plan owns execution order, not the project contract. |
| "Quick means skip tests and verification." | Quick removes formal artifacts, never fresh evidence. |
| "The bug fix is obviously a restoration." | Establish root cause and compare it with the approved contract before classifying the fix. |
| "I already started, so reclassification would waste work." | Scope discovery changes the route before the next mutation; sunk cost grants no exemption. |
| "The deadline makes schema work local." | Schema, security, interface, and cross-component contracts remain Canonical Spec impact under pressure. |
| "The user said proceed, so every authority gate is approved." | Proceed authorizes in-scope execution. A Spec Delta, destructive action, external write, cost, or release still needs its own explicit boundary when required. |

## Platform Adaptation

If running in Codex, read `references/codex-tools.md`. It maps portable actions to current capabilities. Platform differences change how work runs, never which artifact has authority or which route applies.

## User Instructions and Language

Direct user and project instructions take precedence over skills. An explicit instruction to skip a workflow gate may override it; a request for an outcome does not silently redefine artifact authority. Respond in the user's language. Distributed skill files stay in English.

## Handoff

**Routing complete. Follow the selected Quick, plan-only, spec-backed direct, or full-lifecycle path. Reclassify before the next mutation when its assumptions stop being true, and finish through the forge verifying-work skill.**
