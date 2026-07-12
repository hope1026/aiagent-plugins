---
name: executing-plans
description: 'Use when a written implementation plan exists in .forge/plans/ and tasks need adaptive routing, continuous execution, or a durable progress ledger. Triggers: "계획 실행", "구현 진행", "자동 라우팅", "execute the plan", "다음 태스크", resuming interrupted plan work.'
---

# Executing Plans

**Announce at start:** "Using the forge executing-plans skill to execute this plan task by task."

Respond to the user in the user's language. This skill file stays in English.

## Overview

A plan in the forge working directory `.forge/plans/` is a contract derived from an approved spec: bite-sized tasks, exact paths, verification per task. This skill routes each Task by `fast`, `balanced`, or `frontier` capability, chooses root, subagent, or parallel execution, and keeps a durable progress ledger. It uses `internal checkpoint`, `notify checkpoint`, and `approval checkpoint` as distinct states so safe work continues without waiting for the user.

## Iron Law

```
FOLLOW THE PLAN. WHEN REALITY DIVERGES FROM THE SPEC, STOP AND PROPOSE A SPEC DELTA — NEVER SILENTLY ADAPT.
```

When execution reveals a wrong or missing requirement: pause the current task, propose a spec delta via the forge writing-specs skill in change mode, get the user's approval, update the plan if the delta requires it, then continue. Discoveries flow back into the spec — the spec stays the source of truth.

## When to Use / When NOT

**Use when:**
- A plan exists at `.forge/plans/NNN-<slug>.md` and its tasks need executing.
- Resuming interrupted plan work — new session, after compaction, "다음 태스크".

**Do NOT use when:**
- No plan exists → the forge writing-plans skill first (which itself requires an approved spec).
- A bug outside any plan → the forge systematic-debugging skill.
- The request is a question or investigation, not plan execution.

## The Process

The startup checklist and every plan task become todos — create one todo per item; never track them only in memory.

### Phase 1: Startup

1. **Read the plan** in `.forge/plans/` end to end. Review it critically: unclear instructions, contradictions, missing preconditions. Raise concerns with the user BEFORE executing — not mid-task.
2. **Open the ledger** `.forge/scratch/progress-NNN.md` (same NNN as the plan). If `.forge/scratch/` does not exist, create it together with a `.forge/scratch/.gitignore` file containing exactly `*`. If the ledger does not exist, create it with a one-line header naming the plan file.
3. **Skip completed work.** Tasks the ledger marks complete are DONE — do not redo them. Resume at the first task not marked complete. After any compaction or resume, trust the ledger and the commit history over your own recollection.
4. **Create one todo per remaining task.**
5. **Check the review view without changing it.** If a plan or combined Viewer exists, compare its source hash to the current spec and plan and report it as stale when they differ. Do not create or update a Viewer without an explicit user request; when the user explicitly requests an update, use the forge spec-viewer skill for the current sources.
6. **Route the remaining Tasks.** Read `references/adaptive-routing.md`. For each Task, use `impact`, `uncertainty`, `context_coupling`, and `verification_clarity` to choose the capability tier and likely execution mode. Use plan dependency, Files, Interfaces, and verification to form only safe `parallel_group` values. Record the final route immediately before the Task starts so repository changes can invalidate an earlier estimate.

### Phase 2: Per-task loop

For each task, in plan order:

1. Mark the task's todo in progress, re-read the full task text including its Interfaces block, confirm its `fast`, `balanced`, or `frontier` route, and record tier, mode, `parallel_group`, and a concise reason in the ledger.
2. Execute each step exactly as written. Implementation steps REQUIRE the forge test-driven-development skill: failing test first, watch it fail, minimal code to pass. A plan step is not a license to skip the red-green cycle.
3. Run the task's verification commands NOW and read the actual output. Expected output only counts when you saw it.
4. Commit as the plan directs.
5. Append one line to the ledger: `Task N: complete (commits <a>..<b>)`.
6. If a lifecycle Viewer exists and the progress ledger changed, report it as stale. Do not rebuild it unless the user made an explicit user request to update the current `combined` Viewer; after such a request, confirm Task, Step, R, AC, Mermaid counts and source hash before reporting.
7. Mark the todo complete and record an **internal checkpoint**: verification, checkbox, ledger, and planned local commit are the durable recovery point. Start the next safe Task without waiting for the user.
8. Send a non-blocking **notify checkpoint** when a Route or Milestone completes, a `frontier` Task completes, or automatic tier escalation occurs. Summarize completed work, fresh evidence, tier and execution mode, and what continues next. Do not wait for a response before starting the next safe Task.

### Phase 3: Approval boundaries and blockers

Use an **approval checkpoint** only for one of these boundaries. Persist completed work and the exact resume point in the ledger, then state the decision, options, and impact and wait for the user:

- **Spec divergence:** a requirement is wrong, missing, or cannot work as approved → propose a delta via the forge writing-specs skill in change mode.
- **New authority:** a destructive action, external write, purchase, paid resource, or agreed cost-limit increase is required.
- **Scope or product decision:** execution would materially expand the approved scope or needs a user-owned product or design choice.
- **Release boundary:** push, publish, deploy, or release would expose the result outside the local repository.

A local edit, test, planned local commit, tier selection, subagent dispatch, parallel group, internal checkpoint, or notify checkpoint is not an approval boundary. A mechanical plan defect (typo, stale path, wrong command) receives the smallest spec-consistent correction, a ledger note, and the next notify checkpoint; it does not stop execution. For repeated verification failure, follow `references/adaptive-routing.md`: escalate once, then use the forge systematic-debugging skill. Ask the user only when that investigation reaches an approval boundary.

### Adaptive subagent routing

Use `references/adaptive-routing.md`; do not dispatch one fresh subagent mechanically for every Task. Delegate only bounded work with complete Interfaces, disjoint writes, and independent verification. Parallelize only Tasks that pass every safety gate, respect a maximum of 3 concurrent subagents when the user set no lower cap, and keep root ownership of diff review and fresh verification. If model-role mapping is unavailable, inherit the current model while subagents remain usable. If subagent capability is unavailable, execute sequentially yourself. Never fabricate model selection or subagent calls — platform specifics live in the forge using-forge skill's platform notes.

## Working Files

| Path | Role | Committed? |
|---|---|---|
| `.forge/plans/NNN-<slug>.md` | The plan under execution (read; tick its checkboxes) | Yes |
| `docs/specs/NNN-<slug>/spec.md` | Source of truth, consulted on any divergence | Yes |
| `.forge/scratch/progress-NNN.md` | Progress ledger — route decision, escalation, and completion evidence per Task | No (gitignored) |
| `.forge/scratch/.gitignore` | Contains `*`; create if missing | No |
| `.forge/viewer/NNN-<slug>-review.html` | Combined checkpoint view created or updated only on explicit user request | No |

## Red Flags

| Excuse | Reality |
|---|---|
| "This task is obviously wrong, I'll just fix it inline" | If the spec is wrong, that is a spec delta with user approval. Silent adaptation turns the spec into a lie and every later task inherits the lie. |
| "Spec delta is overkill for this" | A delta can be three lines and one approval. It is always cheaper than code that quietly disagrees with the document everyone trusts. |
| "I remember finishing that task" | Memory does not survive compaction; the ledger and commit history do. Re-executing done work is the single most expensive failure mode. |
| "I'll update the ledger after a few tasks" | A crash between tasks erases everything unwritten. One line per task, immediately after it completes. |
| "This step is too small for the TDD cycle" | Implementation steps require the forge test-driven-development skill. Small steps are exactly where untested regressions hide. |
| "Verification passed earlier, no need to rerun" | The plan's verification runs fresh for THIS task's changes. A remembered pass is not evidence. |
| "Every Task needs a user checkpoint to stay safe." | Safety comes from the internal checkpoint, root verification, and explicit approval boundaries. Per-Task waiting only breaks execution flow. |
| "A notify was sent, so I must wait for feedback." | Notify is informational. Continue with the next safe Task unless an approval boundary exists. |
| "The ledger changed, so I should refresh the existing Viewer." | The Viewer is stale, but that does not grant update permission. Report it as stale and wait for an explicit user request. |
| "Subagents are available, so every Task gets one." | Dispatch has context and review cost. Use root for tightly coupled work and delegate only Tasks that pass the adaptive routing gate. |
| "The model role is missing, so parallel work is impossible." | Model mapping and subagent availability are independent. Inherit the current model and keep safe parallelism when workers remain available. |

## Handoff

When every task is complete, verified, and recorded in the ledger:

**All tasks complete. Continue directly to the forge verifying-work skill against the spec's acceptance criteria.**
