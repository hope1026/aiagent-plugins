---
name: writing-plans
description: 'Use when execution complexity is high and implementation, migration, operational, or research work needs an explicit task-level Execution Plan, with Canonical Spec references when durable authority is affected. Triggers: "구현 계획", "계획 작성", "복잡한 작업", "plan", "implementation plan", "plan-only".'
---

# Writing Plans

**Announce at start:** "Using the forge writing-plans skill to create an independently identified implementation plan."

Respond to the user in the user's language. This skill file stays in English. Write the plan in the Related Canonical Spec's language when one governs the work; otherwise use the user's language unless they explicitly request another language.

## Overview

Create a work-scoped Execution Plan that an engineer with **zero context** for this codebase could execute: bite-sized tasks, exact file paths, complete code in every step, and explicit traceability to every Related Canonical Spec. The plan is authoritative for execution order while retained, but it is not the project's SOT. Plans have identifiers and lifetimes independent of Canonical Specs. Assume the implementer is skilled but knows nothing about this project's domain, toolset, or past decisions — and may see only their own task. DRY. YAGNI. Test-first. Frequent commits.

## Plan Language

- Use the governing Canonical Spec's human-readable language when one exists. With no Related Canonical Spec, use the user's language. If the user explicitly requests another plan language, follow that request and keep the plan internally consistent.
- Write all human-readable plan content in that language: the title, goal, architecture, constraints, task names, file responsibilities, interface explanations, step instructions, expected-result explanations, and handoff notes.
- Preserve proper nouns, product and framework names, API and protocol names, code identifiers, type and function signatures, file paths, commands, exact output, and established domain terms in their original form. Follow the project's convention for code, comments, and commit messages.
- Keep only the plan's canonical `##` headings, `Task N` and `Step N` structural tokens, checkbox syntax, exact statement link text, and exact command or output tokens unchanged. Localize ordinary labels such as Spec, Goal, Architecture, Tech Stack, Tasks, Files, Interfaces, Create, Modify, Test, Consumes, Produces, Run, and Expected.
- Do not translate or paraphrase values copied verbatim from a Canonical Spec, including user-facing copy, version constraints, protocol values, and named decisions.

## Iron Law

```
NO EXECUTION PLAN UNLESS EXECUTION COMPLEXITY IS HIGH.
NO DURABLE CONTRACT CHANGE WITHOUT AN APPROVED CANONICAL SPEC OR SPEC DELTA.
NO STEP WITHOUT ITS COMPLETE CONTENT.
EVERY RELATED CANONICAL ACCEPTANCE STATEMENT MAPS TO A TASK.
```

## Precondition Gate

Require a ready work input from the forge using-forge skill before drafting. The conversation or optional Change Brief must provide a one-sentence Goal, non-conflicting Scope and Out of Scope, observable Done Checks, and classifiable routing axes. Inspect repository-discoverable facts yourself. If a user-owned outcome or material scope choice is still blocking, return to Brief clarification; plan authoring must not decide it or hide it as an implementation assumption.

Before drafting anything, prove both routing axes:

1. **Execution complexity:** name the multiple dependencies or components, parallel ownership, migration or release ordering, meaningful rollback risk, zero-context handoff, or interruption-recovery need that makes complexity `high`. If none exists, STOP and return to the forge using-forge skill's selected direct route. Do not create a plan merely because code will change.
2. **Canonical Spec impact:** use the forge using-forge predicate. When impact is `yes`, require an explicitly approved Canonical Spec or Spec Delta before drafting. Run `bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . inspect --spec <bundle-directory> --format json` for every governing bundle. Require `schema` = `forge/spec@3`, `status` = `approved`, and an empty `diagnostics` array.
3. **Preservation and restoration:** when impact is `no` but an existing Canonical Spec supplies context, `approved` or `implemented` is valid. The plan must not claim to change its Requirement or Acceptance statement meaning.
4. **Canonical Related Specs:** require repository-contained bundle paths, unique normalized bundle paths, and every exact linked Requirement and Acceptance statement to resolve inside a declared bundle. With no Related Canonical Spec, use `None — Canonical Spec impact: no; <high-complexity reason>`.

If Canonical Spec impact is `yes` and no approved source exists, STOP. Use the forge writing-specs skill, then return here. If execution complexity is `low`, STOP. Use the selected direct route instead of authoring an unnecessary plan.

## When to Use / When NOT

**Use when:**
- Execution complexity is `high`, with zero or more Related Canonical Specs.
- An approved Spec Delta needs a multi-stage, multi-component, migration, release, rollback, parallel-ownership, or zero-context implementation route.
- Canonical Spec impact is `no`, but implementation, operational, migration, or research work still needs an explicit recoverable sequence.

**Do NOT use when:**
- Execution complexity is `low` → stay on the Quick or spec-backed direct route.
- Canonical Spec impact is `yes` without an approved governing source → the forge writing-specs skill first.
- An Execution Plan already exists and needs executing → the forge executing-plans skill.

**Scope check:** if a Canonical Spec covers multiple independent subsystems, propose one plan per subsystem. Each plan must produce working, testable software on its own.

## The Process

Create one todo per numbered step below and work through them in order.

1. **Read every Related Canonical Spec Bundle end to end.** Start with the root `Documents` inventory, then read every member and collect the exact statement links needed by each Task. With no related source, record `Canonical Spec impact: no`, the exact high-complexity reason, and the Verification Evidence the plan must produce.
2. **Map the file structure.** Before defining tasks, decide which files will be created or modified and what each is responsible for. One clear responsibility per file; prefer small focused files; follow the codebase's established patterns rather than restructuring unilaterally.
3. **Draw task boundaries.** A task is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate. Fold setup, configuration, and docs into the task whose deliverable needs them; split only where a reviewer could reject one task while approving its neighbor. Each task ends with an independently testable deliverable.
4. **Design the implementation Routes and review structure.** Read `references/plan-visual-structure.md`. Group Tasks into 6–10 Routes or Milestones before drawing dependencies; use fewer only when the plan genuinely has fewer independent phases.
5. **Write the plan header** (template below), including the statement coverage table.
6. **Write each task** (template below) with bite-sized steps and full traceability.
7. **Self-review** (section below), fixing issues inline.
8. **Save** to `docs/plans/PPP-<slug>/plan.md`, where `PPP` is the next unused three-digit plan number independent of every spec number.
9. **Offer the review path.** Markdown is the default. Mention Review Viewer only when useful. Create it solely after an explicit user request to create or refresh a Review Viewer, then resolve source, mode, and review-id from current context and hand off once to `review-viewer`. An existing snapshot or plan edit never authorizes refresh.

Keep the plan source compact by default. Create `progress.md` only for long history or multiple independent executors. Create `tasks/*.md` only when a large plan, independent ownership, parallel execution, and independent approval are all true; if any condition is false, keep Task detail in `plan.md`. Before deleting any completed plan, confirm permanent decisions were promoted to a governing Canonical Spec, `docs/research/`, an ADR, or another durable document.

## Review Structure for Complex Plans

A complex plan includes these human-review sections before its detailed Tasks:

- goal and completion state;
- 6–10 implementation Routes or Milestones, with each Task assigned to one primary Route;
- Task dependency;
- Runtime responsibility;
- major data flow;
- Place, platform, or subsystem extension points;
- Task-level Requirement and Acceptance statement mapping;
- internal checkpoint, notify checkpoint, and real approval gate boundaries.

Include three diagram perspectives when the source has the relationships needed to draw them:

1. Task dependency or Route map;
2. Runtime responsibility or transaction flow;
3. extension structure or multi-Place flow.

Do not flatten 22 Tasks into one graph. Group them into Routes first, then show Task detail inside each Route. Each diagram includes a question-shaped title, what to confirm, a one-sentence reading guide, and a source-derived mobile summary table. Plan Mermaid belongs to the plan source; Viewer-derived Route and coverage diagrams may only calculate explicit Task numbers, membership, dependencies, and full-statement mappings.

## Traceability Rule

This is the forge addition on top of ordinary planning discipline:

- `Related Specs` contains only normalized bundle directory paths. It never copies statement lists into metadata.
- Every governed Task has a `Governing statements:` block with repository-contained Markdown links to the exact Requirement and Acceptance headings it implements or preserves.
- Link text equals the exact heading text. The link target includes the member path and generated heading anchor. A short label or path to the bundle root alone is not traceability.
- Every referenced Acceptance statement appears under at least one Task. An uncovered statement makes the plan incomplete.
- The plan starts with a statement coverage table so gaps remain visible without decoding shorthand.

```markdown
## Statement Coverage

| Statement | Kind | <Localized Tasks label> |
|---|---|---|
| [When a signed-in session expires, renewal preserves one active session](../../specs/session-renewal/session-lifecycle.md#when-a-signed-in-session-expires-renewal-preserves-one-active-session) | Requirement | 1, 2 |
| [Given an expired session, one renewal returns one usable session](../../specs/session-renewal/session-verification.md#given-an-expired-session-one-renewal-returns-one-usable-session) | Acceptance | 3 |
```

A task with no Governing statements needs a stated reason to exist. In a spec-free plan, every task instead cites the plan goal and its exact verification evidence.

## Plan Header Template

Every plan MUST start with this header:

```markdown
# <Feature name and implementation-plan title in the plan language>

> <In the plan language: tell agentic workers to execute with the forge
> executing-plans skill, task by task with checkpoints.>

Status: active

**Related Specs:**
- bundle: docs/specs/<semantic-bundle-name>/

With no related source, use the exact one-line form `**Related Specs:** None — Canonical Spec impact: no; <high-complexity reason>` and omit the list.

**<Localized Goal label>:** [one sentence in the plan language describing what this builds]

**<Localized Architecture label>:** [2-3 sentences in the plan language about the approach]

**<Localized Tech Stack label>:** [key technologies/libraries with versions where they matter; preserve established names]

## Global Constraints

[In the plan language: the Canonical Spec's project-wide requirements — version floors,
dependency limits, naming and copy rules, platform requirements — one line each, values copied
verbatim from the Canonical Spec. Every task's requirements implicitly include this
section.]

## Statement Coverage

| Statement | Kind | <Localized Tasks label> |
|---|---|---|
```

## Task Structure Template

````markdown
### Task N: <Component name in the plan language>

**Governing statements:**
- [<exact Requirement heading text>](../../specs/<semantic-bundle-name>/<descriptive-member-name>.md#<exact-heading-anchor>)
- [<exact Acceptance heading text>](../../specs/<semantic-bundle-name>/<descriptive-acceptance-name>.md#<exact-heading-anchor>)

**<Localized Files label>:**
- <Localized Create label>: `exact/path/to/file.py`
- <Localized Modify label>: `exact/path/to/existing.py:123-145`
- <Localized Test label>: `tests/exact/path/to/test_file.py`

**<Localized Interfaces label>:**
- <Localized Consumes label>: [in the plan language: what this task uses from earlier tasks — exact signatures]
- <Localized Produces label>: [in the plan language: what later tasks rely on — exact function names, parameter and
  return types. A task's implementer may see only their own task; this block
  is how they learn the names and types neighboring tasks use.]

**<Localized Execution metadata label>:**
- <Localized Dependencies label>: [exact Task IDs or `none`]
- <Localized Write ownership label>: [exact files or directories this Task may modify]
- <Localized Parallel safety label>: [safe group and reason, or sequential reason]
- <Localized Approval gate label>: [exact spec divergence, authority, scope decision, or release boundary; otherwise `none`]

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

After writing the complete plan, reread every Related Canonical Spec with fresh eyes and check the plan against it. Create one todo per check:

1. **Canonical coverage:** walk every linked Requirement and Acceptance statement; point to the Task that implements or preserves it. Verify the coverage table matches each `Governing statements:` block. With no Related Canonical Spec, verify every Task maps to the plan goal and evidence. List and fix any gap.
2. **Placeholder scan:** search the plan for every pattern in "No Placeholders" above. Fix them.
3. **Type consistency:** do names, signatures, and types used in later tasks match what earlier tasks defined? `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.
4. **Language consistency:** confirm all human-readable prose uses the governing Canonical Spec's language, ordinary labels are localized, and original-language terms, code, paths, commands, exact output, and verbatim Canonical Spec values remain intact.
5. **Review structure:** confirm complex plans include Routes, dependency, Runtime responsibility, data flow, extension points, full-statement mapping, internal and notify checkpoints, real approval gates, and the three required diagram perspectives when their source relationships exist. Local edits, tests, planned local commits, tier selection, subagents, and parallel groups are not approval gates.
6. **Review Viewer request boundary:** confirm no snapshot was created or updated without explicit create or refresh intent. Resolve source, mode, and review-id at handoff. If requested, hand off once to `review-viewer`; fixed generation receives no extra browser or layout QA.
7. **Plan artifact lifetime:** confirm `progress.md` and `tasks/*.md` meet their closed creation gates. Before deleting a plan, verify every permanent decision is promoted to a spec, research record, ADR, or another durable source.
8. **Canonical Related Specs:** re-run inspect for each bundle entry and confirm repository containment, unique normalized bundle paths, allowed lifecycle for the selected impact class, and exact resolution of every linked Requirement and Acceptance statement before handoff. Review Viewer presence is irrelevant to this gate.

Fix issues inline and move on — no re-review loop.

## Working Files

| Path | Role |
|---|---|
| `docs/specs/<semantic-bundle-name>/` | Read: each Related Canonical Spec Bundle whose inspect JSON satisfies the impact-class lifecycle gate |
| `docs/plans/PPP-<slug>/plan.md` | Write: independently identified Execution Plan; committed while retained |
| `docs/plans/PPP-<slug>/progress.md` | Optional long or multi-writer progress history; committed |
| `docs/plans/PPP-<slug>/tasks/*.md` | Optional independently owned Task details; committed |
| `.forge/reviews/<review-id>/view.html` | Optional requested Review Viewer snapshot; untracked |

## Red Flags

| Excuse | Reality |
|---|---|
| "The Spec Delta is basically approved, I'll start planning" | Canonical Spec impact requires explicit approval and diagnostic-free inspect output. |
| "The durable requirements are all in this conversation — effectively SOT" | A conversation or Spec Delta is a proposal. Promote approved meaning to the validated Canonical Spec first. |
| "I'll fill in this step's code during execution" | The executor may be a fresh context with zero knowledge. A step without content is a placeholder, and placeholders are plan failures. |
| "Similar to Task 2 — no need to repeat" | Implementers read tasks in isolation. Repeat the code. |
| "This coverage table is just bookkeeping" | The table makes uncovered Acceptance statements visible. Skipping it is how requirements silently drop. |
| "Every implementation deserves a plan" | Low-complexity work follows a direct route. Plans exist for execution complexity, not ceremony. |
| "The migration is not product behavior, so it needs no route" | Canonical Spec impact may be `no` while complexity is `high`; use a plan-only route. |
| "This plan is the source of truth" | It is the execution source. Durable project authority remains in Canonical Specs and other promoted records. |
| "Add error handling here — the engineer will know what" | They won't. Name the errors, the handling, and the test that proves it. |
| "The user is in a hurry, skip self-review" | Self-review takes minutes; an unexecutable plan wastes hours. Run all four checks. |
| "Implementation plans are technical, so English is clearer." | The plan is also a user review artifact. Write its prose in the Canonical Spec's language and preserve only the technical terms, identifiers, code, and exact commands that need their original form. |
| "The Task list is already ordered, so Routes are decoration." | Routes make dependency and scope review possible before a reader opens 20 or more detailed Tasks. |
| "The plan is complex, so handoff requires a Viewer." | Complexity justifies telling the user why a Viewer may help. Markdown remains valid, and HTML requires an explicit user request. |
| "A user checkpoint after every Task is safer." | Put verification and recovery in the internal checkpoint. Reserve approval gates for spec divergence, new authority, scope decisions, and release. |
| "The plan can define the missing product outcome." | A plan sequences ready work. Return a user-owned outcome or material scope gap to Brief clarification before drafting. |

## Handoff

After saving the plan and finishing self-review, tell the user:

**Execution Plan complete and saved. Next: the forge executing-plans skill with adaptive routing, continuous internal checkpoints, non-blocking Route notifications, and approval only at explicit authority boundaries.**
