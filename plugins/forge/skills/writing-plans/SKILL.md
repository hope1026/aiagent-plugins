---
name: writing-plans
description: 'Use when an approved spec exists and implementation needs a task-level plan, before touching any code. Triggers: "구현 계획", "계획 작성", "plan", "implementation plan", an approved spec with no plan.'
---

# Writing Plans

**Announce at start:** "Using the forge writing-plans skill to turn the approved spec into an implementation plan."

Respond to the user in the user's language. This skill file stays in English.

## Overview

Turn an approved spec into a plan that an engineer with **zero context** for this codebase could execute: bite-sized tasks, exact file paths, complete code in every step, and explicit traceability back to the spec's requirement and acceptance-criterion IDs. Assume the implementer is skilled but knows nothing about this project's domain, toolset, or past decisions — and may see only their own task. DRY. YAGNI. Test-first. Frequent commits.

## Iron Law

```
NO PLAN WITHOUT AN APPROVED SPEC.
NO STEP WITHOUT ITS COMPLETE CONTENT.
EVERY ACCEPTANCE CRITERION MAPS TO A TASK.
```

## Precondition Gate

Before drafting anything:

1. Locate the spec: `docs/specs/NNN-<slug>/spec.md`.
2. Confirm the status line reads `Status: approved`.
3. Confirm the spec contains zero `[NEEDS CLARIFICATION]` markers.

If any check fails, STOP. Do not sketch "a rough plan in the meantime." Use the forge writing-specs skill to get the spec to approved, then return here.

## When to Use / When NOT

**Use when:**
- An approved spec exists and no plan exists for it yet.
- An approved spec delta (change mode) needs new or revised tasks in an existing plan.

**Do NOT use when:**
- No spec exists, or the spec is still `draft` → the forge writing-specs skill first.
- A plan already exists and needs executing → the forge executing-plans skill.
- The work is on the ceremony floor (typo/comment/formatting-only, no-API dependency bump, CI config not affecting build outputs, pure refactor with no observable behavior change AND existing tests pass) — no spec, no plan. This is a closed list; anything not on it gets a spec and a plan.

**Scope check:** if the spec covers multiple independent subsystems, propose one plan per subsystem. Each plan must produce working, testable software on its own.

## The Process

Create one todo per numbered step below and work through them in order.

1. **Read the spec end to end.** List every R-ID and AC-ID. These are the units the plan must cover.
2. **Map the file structure.** Before defining tasks, decide which files will be created or modified and what each is responsible for. One clear responsibility per file; prefer small focused files; follow the codebase's established patterns rather than restructuring unilaterally.
3. **Draw task boundaries.** A task is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate. Fold setup, configuration, and docs into the task whose deliverable needs them; split only where a reviewer could reject one task while approving its neighbor. Each task ends with an independently testable deliverable.
4. **Write the plan header** (template below), including the AC coverage table.
5. **Write each task** (template below) with bite-sized steps and full traceability.
6. **Self-review** (section below), fixing issues inline.
7. **Save** to `.forge/plans/NNN-<slug>.md` — same `NNN` as the spec — and deliver the Handoff line.

## Traceability Rule

This is the forge addition on top of ordinary planning discipline:

- **Every task header cites the R-IDs and AC-IDs it implements**, e.g. `### Task 3: Login endpoint (R2, R4 · AC2)`.
- **Every AC-ID in the spec appears in at least one task.** An AC no task covers means the plan is incomplete — add the task.
- **The plan starts with a coverage table** so gaps are visible at a glance:

```markdown
## AC Coverage

| AC | Tasks |
|---|---|
| AC1 | 1, 2 |
| AC2 | 3 |
| AC3 | 3, 4 |
```

A task that cites no R-ID needs a stated reason to exist (scaffolding for a cited task is fine — say so).

## Plan Header Template

Every plan MUST start with this header:

```markdown
# <Feature Name> Implementation Plan

> **For agentic workers:** execute with the forge executing-plans skill,
> task by task with checkpoints. Steps use checkbox (`- [ ]`) syntax for tracking.

**Spec:** `docs/specs/NNN-<slug>/spec.md`

**Goal:** [one sentence describing what this builds]

**Architecture:** [2-3 sentences about the approach]

**Tech Stack:** [key technologies/libraries with versions where they matter]

## Global Constraints

[The spec's project-wide requirements — version floors, dependency limits,
naming and copy rules, platform requirements — one line each, values copied
verbatim from the spec. Every task's requirements implicitly include this
section.]

## AC Coverage

| AC | Tasks |
|---|---|
```

## Task Structure Template

````markdown
### Task N: <Component Name> (R-IDs · AC-IDs)

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test_file.py`

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter and
  return types. A task's implementer may see only their own task; this block
  is how they learn the names and types neighboring tasks use.]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/exact/path/to/test_file.py::test_specific_behavior -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write the minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/exact/path/to/test_file.py::test_specific_behavior -v`
Expected: PASS

- [ ] **Step 5: Commit**

Run: `git add tests/exact/path/to/test_file.py src/path/file.py && git commit -m "feat: specific behavior"`
````

Adapt the language and test runner to the project; keep the red → green → commit cycle.

## Bite-Sized Steps

Each step is ONE action (2-5 minutes):

- "Write the failing test" — step
- "Run it and confirm it fails" — step
- "Implement the minimal code to pass" — step
- "Run the tests and confirm they pass" — step
- "Commit" — step

## No Placeholders

Every step must contain the actual content the implementer needs. These are **plan failures** — never write them:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without the actual test code)
- "Similar to Task N" (repeat the code — the implementer may read tasks out of order, or see only one)
- Steps that describe what to do without showing how (code steps require code blocks)
- References to types, functions, or methods not defined in any task

## Self-Review

After writing the complete plan, reread the spec with fresh eyes and check the plan against it. Create one todo per check:

1. **Spec coverage:** walk every R-ID and AC-ID; point to the task that implements each. Verify the coverage table matches the task headers. List and fix any gap.
2. **Placeholder scan:** search the plan for every pattern in "No Placeholders" above. Fix them.
3. **Type consistency:** do names, signatures, and types used in later tasks match what earlier tasks defined? `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

Fix issues inline and move on — no re-review loop.

## Working Files

| Path | Role |
|---|---|
| `docs/specs/NNN-<slug>/spec.md` | Read: the approved spec (source of truth) |
| `.forge/plans/NNN-<slug>.md` | Write: the plan — same `NNN` as the spec; committed |

## Red Flags

| Excuse | Reality |
|---|---|
| "The spec is basically approved, I'll start planning" | "Basically approved" is draft. The gate is the literal `Status: approved` line — get it via the forge writing-specs skill. |
| "The requirements are all in this conversation — effectively a spec" | Chat scrollback is not a source of truth; it has no status line, no R-IDs, and it evaporates. Capture it in `docs/specs/` via the forge writing-specs skill first. |
| "I'll fill in this step's code during execution" | The executor may be a fresh context with zero knowledge. A step without content is a placeholder, and placeholders are plan failures. |
| "Similar to Task 2 — no need to repeat" | Implementers read tasks in isolation. Repeat the code. |
| "This coverage table is just bookkeeping" | The table is how uncovered ACs become visible. Skipping it is how requirements silently drop. |
| "The change is small, I'll just code it directly" | Small change = small plan, but the plan exists. No code without a plan task. |
| "Add error handling here — the engineer will know what" | They won't. Name the errors, the handling, and the test that proves it. |
| "The user is in a hurry, skip self-review" | Self-review takes minutes; an unexecutable plan wastes hours. Run all three checks. |

## Handoff

After saving the plan and finishing self-review, tell the user:

**Plan complete and saved. Next: the forge executing-plans skill, task by task with checkpoints.**
