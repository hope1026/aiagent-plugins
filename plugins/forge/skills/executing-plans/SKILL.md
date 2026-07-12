---
name: executing-plans
description: 'Use when a written implementation plan exists in .forge/plans/ and tasks need to be executed with review checkpoints and a durable progress ledger. Triggers: "계획 실행", "구현 진행", "execute the plan", "다음 태스크", resuming interrupted plan work.'
---

# Executing Plans

**Announce at start:** "Using the forge executing-plans skill to execute this plan task by task."

Respond to the user in the user's language. This skill file stays in English.

## Overview

A plan in the forge working directory `.forge/plans/` is a contract derived from an approved spec: bite-sized tasks, exact paths, verification per task. This skill executes that contract task by task with a durable progress ledger (survives compaction and session restarts), a checkpoint report after every task, and one hard rule for what happens when reality contradicts the spec.

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

### Phase 2: Per-task loop

For each task, in plan order:

1. Mark the task's todo in progress and re-read the full task text, including its Interfaces block.
2. Execute each step exactly as written. Implementation steps REQUIRE the forge test-driven-development skill: failing test first, watch it fail, minimal code to pass. A plan step is not a license to skip the red-green cycle.
3. Run the task's verification commands NOW and read the actual output. Expected output only counts when you saw it.
4. Commit as the plan directs.
5. Append one line to the ledger: `Task N: complete (commits <a>..<b>)`.
6. If a lifecycle Viewer exists and the progress ledger changed, report it as stale. Do not rebuild it unless the user made an explicit user request to update the current `combined` Viewer; after such a request, confirm Task, Step, R, AC, Mermaid counts and source hash before reporting.
7. Mark the todo complete and **checkpoint**: report to the user after every task (or after a batch of parallel-safe tasks) — what was done, the verification evidence, what comes next, and a Viewer path only when the user explicitly requested that build. The checkpoint is the user's review gate; do not blow past it. Batching is allowed only when the plan itself marks those tasks as independent — never decide unilaterally that tasks are parallel-safe.

### Phase 3: Divergence and blockers

- **Spec is wrong or incomplete** (a requirement can't work as specified, a case the spec never covered): iron-law procedure — pause, propose a delta via the forge writing-specs skill in change mode, get approval, continue.
- **Plan has a mechanical defect but the spec is fine** (typo, stale path, wrong command): apply the smallest correction that keeps the plan true to the spec, note it in the ledger, and mention it at the checkpoint. If you are unsure which case you are in, it is a spec divergence — stop and follow the iron-law procedure.
- **Blocked** (missing dependency, verification fails repeatedly, instruction you don't understand): stop and ask the user. Never guess your way through a blocker, and never force a task to "pass" by weakening its verification.

### Subagent option

If subagent capability is available, dispatch one fresh subagent per task with the task text + Interfaces block; review its work between tasks, then update the ledger yourself. If not available, execute sequentially yourself. Never fabricate subagent calls — platform specifics live in the forge using-forge skill's platform notes.

## Working Files

| Path | Role | Committed? |
|---|---|---|
| `.forge/plans/NNN-<slug>.md` | The plan under execution (read; tick its checkboxes) | Yes |
| `docs/specs/NNN-<slug>/spec.md` | Source of truth, consulted on any divergence | Yes |
| `.forge/scratch/progress-NNN.md` | Progress ledger — one line per completed task | No (gitignored) |
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
| "The user is waiting, skip the checkpoint" | Checkpoints are the user's review gate. Skipping them hides divergence until it is expensive to unwind. |
| "These tasks feel independent, I'll checkpoint once at the end" | Only the plan can mark tasks parallel-safe. Self-declared batching is checkpoint-skipping with extra steps. |
| "The ledger changed, so I should refresh the existing Viewer." | The Viewer is stale, but that does not grant update permission. Report it as stale and wait for an explicit user request. |

## Handoff

When every task is complete, verified, and recorded in the ledger:

**All tasks complete. Next: the forge verifying-work skill against the spec's acceptance criteria.**
