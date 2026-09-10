# Structured Plan Format

Use this format only when saving a plan for Forge parsers or Visual Docs. The exact `Related Specs`, `Governing statements:`, `Task N`, and `Step N` syntax is a tool interface, not a requirement for session plans. Omit optional fields that add no useful context.

## Select governing verification statements

When a related bundle has Acceptance statements, use them as its Canonical verification set; otherwise use its Requirement statements. Select affected statements and regression evidence for partial work, or the full set only for a full implementation claim. The Task links, optional coverage table, and final verification must agree on this scope. Use the forge verifying-work skill's Canonical verification guidance when lifecycle classification is uncertain.

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

Adapt Steps to the deliverable. Choose tests that establish the requested outcome; TDD is optional unless required. Research names a concrete question, sources or experiments, and the finding needed by the next Task. Operations names ordering, a dry run when applicable, recovery, and the success signal. Pure prose or styling uses direct checks.

