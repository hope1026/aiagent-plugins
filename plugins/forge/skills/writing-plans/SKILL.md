---
name: writing-plans
description: 'Use when an approved spec exists and implementation needs a task-level plan, before touching any code. Triggers: "구현 계획", "계획 작성", "plan", "implementation plan", an approved spec with no plan.'
---

# Writing Plans

**Announce at start:** "Using the forge writing-plans skill to turn the approved spec into an implementation plan."

Respond to the user in the user's language. This skill file stays in English. Write the plan in the governing spec's language unless the user explicitly requests another language.

## Overview

Turn an approved spec into a plan that an engineer with **zero context** for this codebase could execute: bite-sized tasks, exact file paths, complete code in every step, and explicit traceability back to the spec's requirement and acceptance-criterion IDs. Assume the implementer is skilled but knows nothing about this project's domain, toolset, or past decisions — and may see only their own task. DRY. YAGNI. Test-first. Frequent commits.

## Plan Language

- Use the governing spec's human-readable language for the plan. If the user explicitly requests another plan language, follow that request and keep the plan internally consistent.
- Write all human-readable plan content in that language: the title, goal, architecture, constraints, task names, file responsibilities, interface explanations, step instructions, expected-result explanations, and handoff notes.
- Preserve proper nouns, product and framework names, API and protocol names, code identifiers, type and function signatures, file paths, commands, exact output, and established domain terms in their original form. Follow the project's convention for code, comments, and commit messages.
- Keep only the plan's canonical `##` headings, `Task N` and `Step N` structural tokens, R-IDs, AC-IDs, checkbox syntax, and exact command or output tokens unchanged. Localize ordinary labels such as Spec, Goal, Architecture, Tech Stack, Tasks, Files, Interfaces, Create, Modify, Test, Consumes, Produces, Run, and Expected.
- Do not translate or paraphrase values copied verbatim from the spec, including user-facing copy, version constraints, protocol values, and named decisions.

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
4. **Design the implementation Routes and review structure.** Read `references/plan-visual-structure.md`. Group Tasks into 6–10 Routes or Milestones before drawing dependencies; use fewer only when the plan genuinely has fewer independent phases.
5. **Write the plan header** (template below), including the AC coverage table.
6. **Write each task** (template below) with bite-sized steps and full traceability.
7. **Self-review** (section below), fixing issues inline.
8. **Save** to `.forge/plans/NNN-<slug>.md` — same `NNN` as the spec.
9. **Prepare the review view.** For a complex plan, or when the spec already has a Viewer, use the forge spec-viewer skill in `plan` or `combined` mode before execution handoff. Build it in the plan language and confirm its source hash and counts.

## Review Structure for Complex Plans

A complex plan includes these human-review sections before its detailed Tasks:

- goal and completion state;
- 6–10 implementation Routes or Milestones, with each Task assigned to one primary Route;
- Task dependency;
- Runtime responsibility;
- major data flow;
- Place, platform, or subsystem extension points;
- Task-level R and AC mapping;
- checkpoints and user review moments.

Include three diagram perspectives when the source has the relationships needed to draw them:

1. Task dependency or Route map;
2. Runtime responsibility or transaction flow;
3. extension structure or multi-Place flow.

Do not flatten 22 Tasks into one graph. Group them into Routes first, then show Task detail inside each Route. Each diagram includes a question-shaped title, what to confirm, a one-sentence reading guide, and a source-derived mobile summary table. Plan Mermaid belongs to the plan source; Viewer-derived Route and coverage diagrams may only calculate explicit Task numbers, membership, dependencies, and R·AC mappings.

## Traceability Rule

This is the forge addition on top of ordinary planning discipline:

- **Every task header cites the R-IDs and AC-IDs it implements**, e.g. `### Task 3: Login endpoint (R2, R4 · AC2)`.
- **Every AC-ID in the spec appears in at least one task.** An AC no task covers means the plan is incomplete — add the task.
- **The plan starts with a coverage table** so gaps are visible at a glance:

```markdown
## AC Coverage

| AC | <Localized Tasks label> |
|---|---|
| AC1 | 1, 2 |
| AC2 | 3 |
| AC3 | 3, 4 |
```

A task that cites no R-ID needs a stated reason to exist (scaffolding for a cited task is fine — say so).

## Plan Header Template

Every plan MUST start with this header:

```markdown
# <Feature name and implementation-plan title in the plan language>

> <In the plan language: tell agentic workers to execute with the forge
> executing-plans skill, task by task with checkpoints.>

**<Localized Spec label>:** `docs/specs/NNN-<slug>/spec.md`

**<Localized Goal label>:** [one sentence in the plan language describing what this builds]

**<Localized Architecture label>:** [2-3 sentences in the plan language about the approach]

**<Localized Tech Stack label>:** [key technologies/libraries with versions where they matter; preserve established names]

## Global Constraints

[In the plan language: the spec's project-wide requirements — version floors,
dependency limits, naming and copy rules, platform requirements — one line each, values copied
verbatim from the spec. Every task's requirements implicitly include this
section.]

## AC Coverage

| AC | <Localized Tasks label> |
|---|---|
```

## Task Structure Template

````markdown
### Task N: <Component name in the plan language> (R-IDs · AC-IDs)

**<Localized Files label>:**
- <Localized Create label>: `exact/path/to/file.py`
- <Localized Modify label>: `exact/path/to/existing.py:123-145`
- <Localized Test label>: `tests/exact/path/to/test_file.py`

**<Localized Interfaces label>:**
- <Localized Consumes label>: [in the plan language: what this task uses from earlier tasks — exact signatures]
- <Localized Produces label>: [in the plan language: what later tasks rely on — exact function names, parameter and
  return types. A task's implementer may see only their own task; this block
  is how they learn the names and types neighboring tasks use.]

- [ ] **Step 1: <In the plan language: write the failing test>**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: <In the plan language: run the test and verify that it fails>**

<Localized Run label>: `pytest tests/exact/path/to/test_file.py::test_specific_behavior -v`
<Localized Expected label>: <In the plan language: FAIL with the exact message "function not defined">

- [ ] **Step 3: <In the plan language: write the minimal implementation>**

```python
def function(input):
    return expected
```

- [ ] **Step 4: <In the plan language: run the test and verify that it passes>**

<Localized Run label>: `pytest tests/exact/path/to/test_file.py::test_specific_behavior -v`
<Localized Expected label>: PASS

- [ ] **Step 5: <In the plan language: commit the completed change>**

<Localized Run label>: `git add tests/exact/path/to/test_file.py src/path/file.py && git commit -m "feat: specific behavior"`
````

The surrounding plan prose follows the Plan Language rules. Adapt code, commands, commit messages, and the test runner to the project; keep the red → green → commit cycle.

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
4. **Language consistency:** confirm all human-readable prose uses the governing spec's language, ordinary labels are localized, and original-language terms, code, paths, commands, exact output, and verbatim spec values remain intact.
5. **Review structure:** confirm complex plans include Routes, dependency, Runtime responsibility, data flow, extension points, R·AC mapping, checkpoints, and the three required diagram perspectives when their source relationships exist.
6. **Viewer freshness:** if a plan or combined Viewer is required or already exists, rebuild it and confirm source hash, Task/Step/R/AC/Mermaid counts, and localized labels before handoff.

Fix issues inline and move on — no re-review loop.

## Working Files

| Path | Role |
|---|---|
| `docs/specs/NNN-<slug>/spec.md` | Read: the approved spec (source of truth) |
| `.forge/plans/NNN-<slug>.md` | Write: the plan — same `NNN` as the spec; committed |
| `.forge/viewer/NNN-<slug>-plan.html` | Generated plan review view; uncommitted |
| `.forge/viewer/NNN-<slug>-review.html` | Generated combined review view; uncommitted |

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
| "The user is in a hurry, skip self-review" | Self-review takes minutes; an unexecutable plan wastes hours. Run all four checks. |
| "Implementation plans are technical, so English is clearer." | The plan is also a user review artifact. Write its prose in the spec's language and preserve only the technical terms, identifiers, code, and exact commands that need their original form. |
| "The Task list is already ordered, so Routes are decoration." | Routes make dependency and scope review possible before a reader opens 20 or more detailed Tasks. |
| "The plan is saved, so the handoff is complete." | A complex or previously visualized lifecycle needs a fresh plan or combined Viewer before execution starts. |

## Handoff

After saving the plan and finishing self-review, tell the user:

**Plan complete and saved. Next: the forge executing-plans skill, task by task with checkpoints.**
