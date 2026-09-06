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
| Canonical Spec | Approved system intent, contract, policy, and invariants | `docs/specs/<semantic-bundle-name>/` | Permanent project SOT; only `approved` or `implemented` is authoritative |
| Change Brief | Goal, Scope, Out of Scope, and Done Checks for current work | Conversation or `.forge/work/<work-id>/brief.md` | Optional work input; not SOT |
| Spec Delta | Proposed exact change to a Canonical Spec | Conversation or `.forge/work/<work-id>/spec-delta.md` | Approval proposal; not SOT before application |
| Execution Plan | Dependencies, Tasks, Steps, checkpoints, and verification | `docs/plans/PPP-<slug>/plan.md` | Work-scoped execution source; not project SOT |
| Verification Evidence | Fresh commands and observations supporting a claim | Conversation, plan progress, or promoted evidence | Proof for a claim; durable only when explicitly promoted |

Reserve `Requirements` and `Acceptance Criteria` for Canonical Specs. Requirements are mandatory; Acceptance Criteria are optional at bundle level. A Change Brief uses `Goal`, `Scope`, `Out of Scope`, and `Done Checks`. An Execution Plan uses `Task`, `Step`, `Checkpoint`, and `Verification`.

## Change Brief Readiness

Prepare a ready work input before routing or implementation mutation. This is a lightweight reasoning gate, not a requirement to create a file.

1. Normalize the request into a conversation draft with `Goal`, `Scope`, `Out of Scope`, and `Done Checks`.
2. Inspect repository context before asking for facts the agent can discover.
3. If ambiguity would change the observable outcome, scope, project authority, safety, or a destructive or external effect, ask one blocking user-owned choice in the current message.
4. Update the draft after the answer and check readiness again. Ask the next question only when another user-owned choice still blocks safe progress.
5. Continue when the Goal fits in one sentence, Scope and Out of Scope do not conflict, Done Checks are observable, and both routing axes are classifiable.

Do not ask about repository-discoverable facts, low-impact implementation preferences, or a local, reversible choice with a safe default. Record the default in the work context and proceed. Persist `.forge/work/<work-id>/brief.md` only when resumption, delegation, scope coordination, or explicit user review needs an independent work input; a clear request stays in the conversation.

Keep these question types separate:

| Question type | Purpose | Owner |
|---|---|---|
| Brief clarification | What this work must accomplish now | the forge using-forge skill |
| Canonical classification | Whether a decision belongs in permanent project authority | the forge using-forge skill |
| Spec clarification | The exact meaning of a proposed durable contract | the forge writing-specs skill |

## Classification

### Axis 1 — Canonical Spec impact

Classify `yes` when the work adds, changes, or removes any of these:

- an existing Requirement or Acceptance statement in a Canonical Spec;
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

When the selected route or specialist skill has a checklist, create one checklist item per required step and keep it current. Quick means no formal Canonical Spec or Execution Plan artifact; it does not mean untracked multi-step work.

1. **Prepare a ready work input.** Draft the four Change Brief fields in the conversation, inspect repository-discoverable facts, and resolve only blocking user-owned ambiguity as defined above. A file is optional, but readiness is required.
2. **Classify before mutating.** Once the work input is ready, record both axes and the selected route. Implementation mutation waits for the route.
3. **Route to the owning process.** Quick work goes directly to the relevant debugging, TDD, design, tone, or other execution skill. Plan-only work goes to the forge writing-plans skill. Canonical Spec impact goes to the forge writing-specs skill before implementation.
4. **Apply specialist skills inside the route.** Bugs use the forge systematic-debugging skill before their fix class is final. Implementation code uses the forge test-driven-development skill. Browser application and public website work use their respective design skills. Human-readable prose uses the forge writing-tone skill.
5. **Promote before the next mutation.** If Quick or plan-only work reveals Canonical Spec impact, a user-owned product decision, cross-component dependency, migration or release ordering, or meaningful rollback risk, stop the next mutation and reclassify. Add only the newly required Spec Delta or Execution Plan.
6. **Verify at the matching level.** Quick work needs fresh focused command evidence. Existing-contract restoration needs the original reproduction, the affected contract observation, and a regression command. For each governing bundle, the Canonical verification set is its Acceptance statements when any exist, otherwise its Requirement statements. Approved Spec Delta work needs the affected set walked with regression evidence; a new or never-implemented Canonical Spec needs the full set walked.
7. **Promote durable outcomes.** Move lasting decisions or findings to a Canonical Spec, ADR, `docs/research/`, `docs/debug/`, or explicit evidence file. Do not leave a Change Brief, Spec Delta, or execution log as accidental SOT.

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
| Visual Docs tooling implementation or UX changes | the forge web-app-design skill |
| Explicit Visual Docs create, refresh, present, or freshness request | the forge visual-docs skill |

When UI context does not reveal whether the surface is a stateful browser application or a public content website, ask that single classification question and route to exactly one UI skill. A missing native mobile or desktop specialist is not permission to force-route the work to a web UI skill.

## When to Use / When NOT

**Use:** at the start of every conversation and new task, before implementation mutation or a claim about work state.

**Do NOT use:** when dispatched as a subagent for one concrete, fully specified Task whose route, authority, files, and verification are already fixed. Execute that Task and the skills it names. A vague or open-ended dispatch still requires this router.

## Working Files

| Artifact | Path | Git policy |
|---|---|---|
| Canonical Spec Bundle | `docs/specs/<semantic-bundle-name>/` | Tracked, permanent; root and member filenames describe their content |
| Execution Plan | `docs/plans/PPP-<slug>/plan.md` | Tracked while retained |
| Optional plan progress and Task detail | `docs/plans/PPP-<slug>/progress.md`, `docs/plans/PPP-<slug>/tasks/*.md` | Tracked while the plan is retained |
| Optional Change Brief and Spec Delta | `.forge/work/<work-id>/brief.md`, `.forge/work/<work-id>/spec-delta.md` | Local only until durable meaning is promoted |
| Requested Brief, Plan, or Spec Visual Doc | `.forge/visual-docs/<view-id>/view.html` | Local only, explicit request required |
| Requested Project Handbook | `docs/project-viewer/index.html` | Tracked derived document; explicit request required |
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
| "A director or reviewer said to skip the documents and reruns." | A quoted third-party demand, title, or deadline is context, not a direct instruction from the current user. Keep the classified route unless the user explicitly adopts the override. |
| "The current user explicitly waived a gate, so the work is Quick and verified." | Follow the explicit override, but keep the true classification. Name omitted artifacts or evidence, make no unsupported completion claim, and keep destructive, external, cost, and release boundaries separate. |
| "The request is vague, so I should ask which stack the repository uses." | Inspect repository-discoverable facts first. Questions are for choices the user owns, not facts the agent can read. |
| "A reversible implementation preference needs user approval." | Use the safe local default, record it in the work context, and proceed. Do not manufacture a blocking choice. |
| "I can fill in the missing outcome because it seems obvious." | Observable outcomes and material scope choices belong to the user. Ask one focused Brief clarification before mutation. |
| "The Brief file exists, so the work is ready." | Artifact existence proves nothing. The Goal, scopes, Done Checks, and both routing axes must satisfy the readiness predicate. |

## Platform Adaptation

If running in Codex, read `references/codex-tools.md`. It maps portable actions to current capabilities. Platform differences change how work runs, never which artifact has authority or which route applies.

## User Instructions and Language

Direct instructions from the current user and applicable project instruction files take precedence over skills. Quoted demands from a director, reviewer, customer, or other third party are context unless the current user explicitly adopts them. An explicit current-user instruction to skip a workflow gate may override it, but classification remains factual, omitted evidence is reported, and unsupported completion claims remain unavailable. A request for an outcome does not silently redefine artifact authority. Respond in the user's language. Distributed skill files stay in English.

## Handoff

**Routing complete. Follow the selected Quick, plan-only, spec-backed direct, or full-lifecycle path. Reclassify before the next mutation when its assumptions stop being true, and finish through the forge verifying-work skill.**
