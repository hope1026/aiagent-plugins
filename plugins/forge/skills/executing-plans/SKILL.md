---
name: executing-plans
description: 'Use when a written implementation plan exists in docs/plans/ and tasks need adaptive routing, continuous execution, or durable progress history. Triggers: "계획 실행", "구현 진행", "자동 라우팅", "execute the plan", "다음 태스크", resuming interrupted plan work.'
---

# Executing Plans

**Announce once when first applied:** "Using the forge executing-plans skill to execute this plan task by task."

Respond to the user in the user's language. This skill file stays in English.

## Overview

An Execution Plan in `docs/plans/PPP-<slug>/plan.md` is an independently identified work contract: bite-sized tasks, exact paths, verification per task, and zero or more Related Canonical Spec Bundles. It is the work-scoped execution source, not project SOT. This skill routes each Task by `fast`, `balanced`, or `frontier` capability, chooses root, subagent, or parallel execution, and keeps durable progress with the plan. It uses `internal checkpoint`, `notify checkpoint`, and `approval checkpoint` as distinct states so safe work continues without waiting for the user.

## Iron Law

```
FOLLOW THE EXECUTION PLAN. WHEN REALITY DIVERGES FROM A RELATED CANONICAL SPEC, STOP AND PROPOSE A SPEC DELTA — NEVER SILENTLY ADAPT.
```

When execution reveals a wrong or missing requirement in a Related Canonical Spec: pause the current Task, propose a Spec Delta via the forge writing-specs skill in change mode, get the user's approval, update the plan if the Delta changes execution, then continue. For a plan-only route, continue while scope stays `Canonical Spec impact: no`; durable contract discovery promotes the work before the next mutation.

## When to Use / When NOT

**Use when:**
- A plan exists at `docs/plans/PPP-<slug>/plan.md` and its tasks need executing.
- Resuming interrupted plan work — new session, after compaction, "다음 태스크".

**Do NOT use when:**
- No plan exists → return to the forge using-forge route; only high-complexity work goes to the forge writing-plans skill.
- A bug outside any plan → the forge systematic-debugging skill.
- The request is a question or investigation, not plan execution.

## The Process

Use the plan's Task checklist as the execution checklist. Track startup concerns only when they require separate action; do not duplicate completed routing and verification work.

### Phase 1: Startup

1. **Read the plan** and inspect its Related Spec Bundles with `bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . inspect --spec <bundle-directory> --format json`. Require `forge/spec@3`, lifecycle `approved|implemented` appropriate to new work or preservation, and empty diagnostics. Verify exact `Governing statements:` links against the plan's Verification Scope: the full Canonical verification set only for a full implementation claim, or directly and indirectly affected statements plus regression preservation for partial implementation, change, or restoration. Resolve repository facts yourself. A user-owned outcome gap returns to Brief clarification; a bounded technical question follows its investigation Task.
2. **Open progress state.** The default source is Task checkboxes plus `Progress History` in `plan.md`. When `progress.md` exists beside the plan, use it for detailed routing and checkpoint evidence. When `tasks/*.md` exists, confirm each Task ID appears once in the plan index and once in its owned Task file.
3. **Skip completed work.** Tasks the plan-local progress state marks complete are DONE — do not redo them. Resume at the first task not marked complete. After any compaction or resume, trust plan-local progress and commit history over recollection.
4. **Create one todo per remaining task.**
5. **Ignore Visual Docs during execution.** Neither `.forge/visual-docs/<view-id>/view.html` nor `docs/project-viewer/index.html` is an execution source. Do not inspect, create, or update one without explicit user intent. Resolve source, kind, and view-id from current context during handoff.
6. **Route the remaining Tasks.** Read `references/adaptive-routing.md`. For each Task, use `impact`, `uncertainty`, `context_coupling`, and `verification_clarity` to choose the capability tier and likely execution mode. Use plan dependency, Files, Interfaces, and verification to form only safe `parallel_group` values. Record the final route immediately before the Task starts so repository changes can invalidate an earlier estimate.

### Phase 2: Per-task loop

For each task, in plan order:

1. Mark the task's todo in progress, re-read the full task text including its Interfaces block, confirm its `fast`, `balanced`, or `frontier` route, and record tier, mode, `parallel_group`, and a concise reason in plan-local progress.
2. Execute the Task's outcome and boundaries. Testable logic uses the forge test-driven-development skill; prose, styling, and logic-free configuration use the focused direct check. Correct mechanical plan defects in scope and record them; do not invent unapproved contract meaning.
3. Satisfy the Task's required verification and inspect the actual output. Reuse observed evidence from the same unchanged relevant source, implementation, tests, inputs, settings, and environment. Root reviews worker diffs and confirms that inspected execution evidence applies to the integrated state; run affected checks when evidence is missing, invalidated, or does not cover integration.
4. Commit as the plan directs.
5. Check the Task boxes and append one `Progress History` line: `Task N: complete (commits <a>..<b>)`. When `progress.md` exists, append detailed route evidence there and keep the summary in `plan.md`.
6. If a completed visual document's source changed, report possible staleness without refreshing it. Explicit create or refresh intent permits one `visual-docs` handoff covering the requested document's generation, quality verification, and necessary corrections; an existing View alone grants no refresh authority.
7. Mark the todo complete and record an **internal checkpoint**: verification, checkbox, ledger, and planned local commit are the durable recovery point. Start the next safe Task without waiting for the user.
8. Send a non-blocking **notify checkpoint** when a Route or Milestone completes, a `frontier` Task completes, or automatic tier escalation occurs. Summarize completed work, fresh evidence, tier and execution mode, and what continues next. Do not wait for a response before starting the next safe Task.

### Phase 3: Approval boundaries and blockers

Use an **approval checkpoint** only when one of these boundaries is not already covered by the user's concrete authorization. Preserve existing approvals. Persist completed work and the exact resume point, then state the new decision, options, and impact:

- **Canonical Spec divergence:** a requirement in a Related Canonical Spec is wrong, missing, or cannot work as approved → propose a Spec Delta via the forge writing-specs skill in change mode.
- **New authority:** a destructive action, external write, purchase, paid resource, or agreed cost-limit increase is required.
- **Scope or product decision:** execution would materially expand the approved scope or needs a user-owned product or design choice.
- **Release boundary:** push, publish, deploy, or release would expose the result outside the local repository.

A local edit, test, planned local commit, tier selection, subagent dispatch, parallel group, internal checkpoint, or notify checkpoint is not an approval boundary. A mechanical plan defect (typo, stale path, wrong command) receives the smallest spec-consistent correction, a ledger note, and the next notify checkpoint; it does not stop execution. For repeated verification failure, follow `references/adaptive-routing.md`: escalate once, then use the forge systematic-debugging skill. Ask the user only when that investigation reaches an approval boundary.

### Adaptive subagent routing

Use `references/adaptive-routing.md`; apply its deterministic defaults: `fast` uses root, an eligible `balanced` Task uses a subagent, and `frontier` uses root. Do not ask the user to choose an execution mode for an ordinary Task. Honor explicit `root-only`, disabled-subagent, and lower-concurrency preferences, then record the route and report delegation at notify or final reporting.

Do not dispatch one fresh subagent mechanically for every Task. Delegate only bounded work with complete Interfaces, disjoint writes, and independent verification. Parallelize only Tasks that pass every safety gate, respect a maximum of 3 concurrent subagents when the user set no lower cap, and keep root ownership of diff review and fresh verification. If model-role mapping is unavailable, inherit the current model while subagents remain usable. If subagent capability is unavailable, execute sequentially yourself. Never fabricate model selection or subagent calls — platform specifics live in the forge using-forge skill's platform notes.

## Working Files

| Path | Role | Committed? |
|---|---|---|
| `docs/plans/PPP-<slug>/plan.md` | Plan index, Task checkboxes, and Progress History | Yes |
| `docs/plans/PPP-<slug>/progress.md` | Optional detailed route and checkpoint evidence | Yes |
| `docs/plans/PPP-<slug>/tasks/*.md` | Optional independently owned Task details | Yes |
| Related `docs/specs/<semantic-bundle-name>/` directories | Canonical project SOT, when present | Yes |
| `.forge/visual-docs/<view-id>/view.html` | Optional requested Brief, Plan, or Spec view | No |
| `docs/project-viewer/index.html` | Optional requested Project Handbook | No; tracked derived output only |

## Red Flags

| Excuse | Reality |
|---|---|
| "This task is obviously wrong, I'll just fix it inline" | If Canonical authority is wrong, that is a Spec Delta with user approval. Silent adaptation makes every later Task inherit a false contract. |
| "Spec Delta is overkill for this" | Durable authority changes through an approved Delta even when the implementation step is small. |
| "This plan has no spec, so scope can expand freely" | Plan-only means Canonical Spec impact remains `no`. Durable contract discovery promotes the route before the next mutation. |
| "I remember finishing that task" | Memory does not survive compaction; plan-local progress and commit history do. Re-executing done work is the single most expensive failure mode. |
| "I'll update Progress History after a few tasks" | A crash between tasks erases everything unwritten. One line per task, immediately after it completes. |
| "This logic is too small for the TDD cycle" | Testable behavior needs its focused test; labels and styling use direct checks. |
| "Any earlier pass proves the changed code" | Evidence must match the current code and test state. Rerun affected checks after changes. |
| "Every Task needs a user checkpoint to stay safe." | Safety comes from the internal checkpoint, root verification, and explicit approval boundaries. Per-Task waiting only breaks execution flow. |
| "A notify was sent, so I must wait for feedback." | Notify is informational. Continue with the next safe Task unless an approval boundary exists. |
| "Plan progress changed, so I should refresh the existing Viewer." | The Viewer is stale, but that does not grant update permission. Report it and wait for an explicit user request. |
| "Subagents are available, so every Task gets one." | Dispatch has context and review cost. Use root for tightly coupled work and delegate only Tasks that pass the adaptive routing gate. |
| "I should ask which execution mode the user wants for each Task." | Apply the tier default and report the route. Execution mode is not an approval boundary. |
| "The model role is missing, so parallel work is impossible." | Model mapping and subagent availability are independent. Inherit the current model and keep safe parallelism when workers remain available. |
| "The plan exists, so its missing outcome is an implementation detail." | Plan existence does not prove work-input readiness. A user-owned outcome or material scope gap returns to Brief clarification before mutation. |

## Handoff

When every task is complete, verified, and recorded in the ledger:

**All Tasks complete. Continue directly to the forge verifying-work skill against the affected Canonical verification set, or against plan Verification Evidence when Canonical Spec impact is `no`.**
