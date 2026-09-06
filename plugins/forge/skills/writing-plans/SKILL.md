---
name: writing-plans
description: 'Use when execution complexity is high and implementation, migration, operational, or research work needs an explicit task-level Execution Plan. Triggers: "구현 계획", "계획 작성", "복잡한 작업", "plan", "implementation plan", "plan-only".'
---

# Writing Plans

**Announce once when first applied:** "Using the forge writing-plans skill to define the tasks, dependencies, and verification."

Respond in the user's language. Use the governing Canonical Spec's language for plan prose, or the user's language when no Spec governs it. Follow an explicit language request. Keep paths, identifiers, commands, canonical headings, `Task N`, `Step N`, and exact statement links unchanged.

## Overview

An Execution Plan lets work survive interruption and gives an implementer enough context to complete a bounded Task. Specify outcomes, owned files, dependencies, interfaces, verification, and recovery. Include code only when the handoff needs an exact algorithm, example, or interface. Do not write the implementation twice.

The plan owns execution order while retained; Canonical Specs own durable contracts. Keep the plan proportional to execution complexity.

## Iron Law

```text
PLAN HIGH-COMPLEXITY WORK; KEEP LOW-COMPLEXITY WORK DIRECT.
DURABLE CONTRACT CHANGES NEED APPROVED MEANING.
EVERY TASK NEEDS A CLEAR RESULT AND VERIFICATION.
PLAN COVERAGE AND FINAL VERIFICATION USE THE SAME WORK SCOPE.
```

## Preconditions

Use the ready goal and boundaries from the forge using-forge skill. Inspect repository facts yourself. An unresolved user-owned outcome returns to Brief clarification; a bounded technical unknown may become an investigation Task with a question and exit evidence.

1. Name the dependent stages, multiple components, migration or release ordering, rollback risk, parallel ownership, or interruption-recovery need that makes complexity high. Otherwise return to the direct route.
2. Use the router's Canonical Spec impact. When impact is yes, use the approved exact meaning and validate the governing source before implementation. Reuse approval already given for a concrete proposal; do not request the same decision again.
3. Inspect each Related Spec Bundle with `bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . inspect --spec <bundle-directory> --format json`. Require `schema` = `forge/spec@3`, `status` matching the work class, and empty `diagnostics`. New contract work uses `approved`; preservation or restoration may use `approved` or `implemented`.
4. Related Specs are repository-contained, unique normalized bundle paths. Every exact linked Requirement and Acceptance statement must resolve inside a declared bundle.

## When to Use / When NOT

Use for high-complexity implementation, research, migration, or operations, with zero or more Related Specs. If a plan already exists, use the forge executing-plans skill. Do not create a plan just because code changes or because several checks are available.

## The Process

Use one checklist for plan deliverables: scope and context, Task boundaries, coverage, and review. Do not duplicate it inside every specialist skill.

1. Read each governing bundle's inventory, purpose, affected statements, and relevant boundaries. Inspect adjacent contracts needed to assess indirect effects. Record verification scope before defining Tasks.
2. Map owned files and responsibilities. Follow repository patterns and identify stable Interfaces before proposing parallel work.
3. Draw independently reviewable Task boundaries. Fold setup, configuration, and documentation into the deliverable that needs them.
4. Group Tasks by actual phases. Read `references/plan-visual-structure.md` when dependency, runtime, or extension relationships would help review. Large plans may use 6–10 Routes; smaller plans use fewer. Never invent milestones or diagrams to fill a template.
5. Write the compact header and Tasks below. Add precise examples or code only where plain instructions and existing interfaces are insufficient.
6. Review scope, dependencies, interfaces, commands, coverage, and language once. Correct issues and recheck affected parts when the correction changes them.
7. Save to `docs/plans/PPP-<slug>/plan.md`, with the next unused plan number independent of Specs. Continue authorized execution through the forge executing-plans skill; do not stop merely because the plan has been saved.

Markdown is the default. Mention Visual Docs when useful, and create or refresh one only after an explicit user request. One handoff covers source selection, generation, and the requested document's quality verification; see the forge visual-docs skill.

Keep progress in the plan by default. Create `progress.md` only for long history or multiple independent executors. Create `tasks/*.md` only when a large plan, independent ownership, parallel execution, and independent approval are all true. Before deleting a plan, promote permanent decisions to a Canonical Spec, `docs/research/`, an ADR, or another durable source.

## Verification Scope and Traceability

For each Related Spec Bundle, the Canonical verification set is every Acceptance statement when any exist, otherwise every Requirement statement. Select the work scope from that set:

- Full implementation claim for a new or never-implemented baseline: cover the whole set.
- Partial implementation, change, or restoration: cover every directly or indirectly affected statement; name the baseline and regression evidence protecting unchanged behavior. Do not add Tasks for the rest of a never-implemented bundle unless this plan claims to implement the whole bundle.
- No Related Spec: connect every Task to the goal and observable Done Checks.

Keep exact heading text as link text and use the member path plus its generated anchor. Every governed Task has `Governing statements:` links. A task with no such link states its goal contribution instead. A partial plan does not need artificial Tasks for unaffected statements, but uncertain impact must expand the checked scope.

Put a statement coverage table near the beginning. Its selected set must match the Task links and final verification scope. Record unchanged-contract preservation by a concrete regression command or observation, not by writing "everything else unchanged" without evidence.

## Header Template

```markdown
# <Plan title>

> Execute with the forge executing-plans skill.

Status: active

**Related Specs:**
- bundle: docs/specs/<semantic-bundle-name>/

**Goal:** <one concrete completion result>
**Approach:** <key responsibilities and sequence>

## Global Constraints

<Only constraints that actually govern this work.>

## Verification Scope

<Work class, baseline, affected or full set, and regression boundary.>

## Statement Coverage

| Statement | Task | Verification |
|---|---|---|
| [<exact heading>](../../specs/<bundle>/<member>.md#<anchor>) | 1 | <observable check> |
```

With no Related Spec, use the exact one-line form `**Related Specs:** None — Canonical Spec impact: no; <high-complexity reason>` and omit the list. Localize ordinary Goal, Approach, Files, Interfaces, and verification prose according to the plan language.

## Task Template

```markdown
### Task N: <Outcome>

Governing statements:

- [<exact heading>](../../specs/<bundle>/<member>.md#<anchor>)

**Files:** <exact owned files and their responsibilities>
**Interfaces:** <inputs, outputs, names/types or links to stable definitions>
**Dependencies:** <Task IDs or none>
**Verification:** <command or procedure and observable expected result>
**Recovery:** <checkpoint and how to resume or undo if needed>
**Approval gate:** <new authority or user-owned decision, otherwise none>

- [ ] **Step 1: Establish the expected behavior or investigation evidence.**
- [ ] **Step 2: Make the bounded change using the appropriate implementation skill.**
- [ ] **Step 3: Verify the outcome and record the checkpoint.**
```

Adapt Steps to the deliverable. Testable logic follows the forge test-driven-development skill. Research names a concrete question, sources or experiments, and the finding needed by the next Task. Operations names ordering, a dry run when applicable, recovery, and the success signal. Pure prose or styling uses direct checks.

## Enough Detail

An implementer must know what to change and how to prove it. Include exact shared signatures, error behavior, data boundaries, and tricky examples where needed. Refer to stable existing definitions rather than copying code into every Task.

Reject unbounded instructions such as "handle edge cases", "do the research", "write appropriate tests", or unresolved user outcomes. A technical question with a bounded experiment and exit evidence is executable work, not a placeholder. Do not claim an unknown API or implementation already exists.

## Review and Checkpoints

Confirm:

- Task outcomes and verification cover the selected work scope.
- Dependencies, Files, Interfaces, and write ownership make execution order and parallel safety decidable.
- Commands use actual repository paths and runners; expected failures represent behavior, not missing imports or typo errors.
- Diagrams answer a review question and only show source-backed relationships.
- Internal checkpoints preserve verification and progress; notify checkpoints inform without waiting; approval gates cover only a genuine new boundary.
- Plan and Spec language, exact links, and artifact lifetime remain correct.

Local edits, tests, planned local commits, tier selection, subagents, and parallel groups are not approval gates. Use existing authorization for the concrete work already approved.

## Working Files

| Path | Role |
|---|---|
| `docs/specs/<semantic-bundle-name>/` | Durable authority when approved or implemented |
| `docs/plans/PPP-<slug>/plan.md` | Execution and progress source |
| `progress.md`, `tasks/*.md` beside the plan | Optional detail under the creation rules above |
| `.forge/work/<work-id>/` | Optional brief and applied Delta retained through verification |
| `.forge/visual-docs/<view-id>/view.html` | Requested local reading view |
| `docs/project-viewer/index.html` | Requested tracked Project Handbook |

## Red Flags

| Pressure | Response |
|---|---|
| "Every change deserves a plan." | Plan only when safe execution needs it. |
| "Zero context means duplicate all implementation code." | Give complete outcomes, boundaries, interfaces, and evidence; include code where it resolves a real handoff risk. |
| "A partial fix must map every unrelated statement." | Declare affected scope and regression preservation; expand only for actual or uncertain impact. |
| "The implementation is unknown, so invent it now." | Define a bounded investigation Task and its exit evidence. |
| "A technical plan must contain three diagrams." | Include only relationships that exist and help review. |
| "The plan can decide the missing product outcome." | Return that user-owned choice to Brief clarification. |
| "The plan is saved, so execution needs another go-ahead." | Continue when the user already authorized this concrete work. |
| "A Viewer is required for approval." | Markdown remains valid; Visual Docs needs explicit intent. |

## Handoff

Execute authorized Tasks with the forge executing-plans skill. Preserve progress, report meaningful milestones, and finish with the forge verifying-work skill against the selected work scope.
