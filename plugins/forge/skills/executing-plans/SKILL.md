---
name: executing-plans
description: 'Use when a written implementation plan exists in docs/plans/ and tasks need adaptive routing, continuous execution, or durable progress history. Triggers: "계획 실행", "구현 진행", "자동 라우팅", "execute the plan", "다음 태스크", resuming interrupted plan work.'
---

# Executing Plans

**Announce at start:** "Using the forge executing-plans skill to execute this plan task by task."

Respond to the user in the user's language. This skill file stays in English.

## Overview

An Execution Plan in `docs/plans/PPP-<slug>/plan.md` is an independently identified work contract: bite-sized tasks, exact paths, verification per task, and zero or more Related Canonical Specs. It is the work-scoped execution source, not project SOT. This skill routes each Task by `fast`, `balanced`, or `frontier` capability, chooses root, subagent, or parallel execution, and keeps durable progress with the plan. It uses `internal checkpoint`, `notify checkpoint`, and `approval checkpoint` as distinct states so safe work continues without waiting for the user.

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

The startup checklist and every plan task become todos — create one todo per item; never track them only in memory.

### Phase 1: Startup

1. **Read the plan** in `docs/plans/` end to end. For every Related Canonical Spec entry, run `bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . inspect --spec <repo-relative-path> --format json`. Require `schema` = `forge/spec@2`, `status` in `approved|implemented`, and empty `diagnostics`; an approved source governs new contract work and an approved or implemented source may govern preservation or restoration. Review unclear instructions, contradictions, and missing preconditions before execution.
2. **Open progress state.** The default source is Task checkboxes plus `Progress History` in `plan.md`. When `progress.md` exists beside the plan, use it for detailed routing and checkpoint evidence. When `tasks/*.md` exists, confirm each Task ID appears once in the plan index and once in its owned Task file.
3. **Skip completed work.** Tasks the plan-local progress state marks complete are DONE — do not redo them. Resume at the first task not marked complete. After any compaction or resume, trust plan-local progress and commit history over recollection.
4. **Create one todo per remaining task.**
5. **Ignore Review Viewer snapshots during execution.** `.forge/reviews/<review-id>/view.html` is not an execution source. Do not inspect, create, or update it without explicit user intent to create, refresh, or freshness-check a Review Viewer. Resolve source, mode, and review-id from current context during handoff.
6. **Route the remaining Tasks.** Read `references/adaptive-routing.md`. For each Task, use `impact`, `uncertainty`, `context_coupling`, and `verification_clarity` to choose the capability tier and likely execution mode. Use plan dependency, Files, Interfaces, and verification to form only safe `parallel_group` values. Record the final route immediately before the Task starts so repository changes can invalidate an earlier estimate.

### Phase 2: Per-task loop

For each task, in plan order:

1. Mark the task's todo in progress, re-read the full task text including its Interfaces block, confirm its `fast`, `balanced`, or `frontier` route, and record tier, mode, `parallel_group`, and a concise reason in plan-local progress.
2. Execute each step exactly as written. Implementation steps REQUIRE the forge test-driven-development skill: failing test first, watch it fail, minimal code to pass. A plan step is not a license to skip the red-green cycle.
3. Run the task's verification commands NOW and read the actual output. Expected output only counts when you saw it.
4. Commit as the plan directs.
5. Check the Task boxes and append one `Progress History` line: `Task N: complete (commits <a>..<b>)`. When `progress.md` exists, append detailed route evidence there and keep the summary in `plan.md`.
6. If a Review Viewer exists and plan source changed, report possible staleness without assuming freshness. Only explicit create or refresh intent permits one `review-viewer` handoff; resolve its options and stop when the single build succeeds.
7. Mark the todo complete and record an **internal checkpoint**: verification, checkbox, ledger, and planned local commit are the durable recovery point. Start the next safe Task without waiting for the user.
8. Send a non-blocking **notify checkpoint** when a Route or Milestone completes, a `frontier` Task completes, or automatic tier escalation occurs. Summarize completed work, fresh evidence, tier and execution mode, and what continues next. Do not wait for a response before starting the next safe Task.

### Phase 3: Approval boundaries and blockers

Use an **approval checkpoint** only for one of these boundaries. Persist completed work and the exact resume point in the ledger, then state the decision, options, and impact and wait for the user:

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
| Related `docs/specs/NNN-<slug>/spec.md` files | Canonical project SOT, when present | Yes |
| `.forge/reviews/<review-id>/view.html` | Optional requested Review Viewer snapshot | No |

## Red Flags

| Excuse | Reality |
|---|---|
| "This task is obviously wrong, I'll just fix it inline" | If Canonical authority is wrong, that is a Spec Delta with user approval. Silent adaptation makes every later Task inherit a false contract. |
| "Spec Delta is overkill for this" | Durable authority changes through an approved Delta even when the implementation step is small. |
| "This plan has no spec, so scope can expand freely" | Plan-only means Canonical Spec impact remains `no`. Durable contract discovery promotes the route before the next mutation. |
| "I remember finishing that task" | Memory does not survive compaction; plan-local progress and commit history do. Re-executing done work is the single most expensive failure mode. |
| "I'll update Progress History after a few tasks" | A crash between tasks erases everything unwritten. One line per task, immediately after it completes. |
| "This step is too small for the TDD cycle" | Implementation steps require the forge test-driven-development skill. Small steps are exactly where untested regressions hide. |
| "Verification passed earlier, no need to rerun" | The plan's verification runs fresh for THIS task's changes. A remembered pass is not evidence. |
| "Every Task needs a user checkpoint to stay safe." | Safety comes from the internal checkpoint, root verification, and explicit approval boundaries. Per-Task waiting only breaks execution flow. |
| "A notify was sent, so I must wait for feedback." | Notify is informational. Continue with the next safe Task unless an approval boundary exists. |
| "Plan progress changed, so I should refresh the existing Viewer." | The Viewer is stale, but that does not grant update permission. Report it and wait for an explicit user request. |
| "Subagents are available, so every Task gets one." | Dispatch has context and review cost. Use root for tightly coupled work and delegate only Tasks that pass the adaptive routing gate. |
| "I should ask which execution mode the user wants for each Task." | Apply the tier default and report the route. Execution mode is not an approval boundary. |
| "The model role is missing, so parallel work is impossible." | Model mapping and subagent availability are independent. Inherit the current model and keep safe parallelism when workers remain available. |

## Handoff

When every task is complete, verified, and recorded in the ledger:

**All Tasks complete. Continue directly to the forge verifying-work skill against the affected Related Canonical Spec criteria, or against plan Verification Evidence when Canonical Spec impact is `no`.**
