# Plan Visual Structure

Use this reference for plans that need a human review view. The plan remains the source of truth; diagrams summarize only relationships explicitly written in the plan or governing spec.

## Recommended order

1. Goal and completion state
2. Implementation Routes or Milestones
3. Task dependency
4. Runtime responsibility
5. Major data flow
6. Place, platform, or subsystem extension points
7. AC Coverage and Task-level R·AC mapping
8. Detailed Tasks and Steps
9. Internal checkpoints, notify checkpoints, and approval boundaries

This order lets a reviewer move from scope to flow to implementation detail to evidence.

## Route table

```markdown
| Route | Tasks | Deliverable | Checkpoint type |
|---|---:|---|---|
| Route 1 — Source | 1–3 | Parser and manifest | notify after count fixture |
| Route 2 — Review | 4–6 | Viewer shell | approval only before release |
```

Use 6–10 Routes for a large plan. Every Task has one primary Route even when it depends on Tasks in another Route. Route names describe outcomes, not team names.

## Task dependency or Route map

Show Route-level order first. Add Task-level edges only where the plan states an explicit dependency. Do not infer an edge from file proximity or execution preference.

## Runtime responsibility or transaction flow

List actors and responsibilities in a table before a wide sequence diagram. Include server authority, validation ownership, transaction boundary, Remote caller and receiver, and failure owner only when the plan states them.

## Extension structure or multi-Place flow

Show the current implementation boundary and the named extension point. Do not draw unreleased Places or platforms as implemented. Keep `available`, feature flags, or rollout states visible when they are part of the source.

## Diagram package

Each diagram has:

- a title framed as the question the reviewer wants answered;
- one sentence stating what to confirm;
- a one-sentence reading guide;
- a source label: `Plan source`, `Spec source`, or `Derived view`;
- a mobile summary table or vertical source-derived flow before any wide diagram.

## Traceability

The combined review path should make these links navigable:

```text
R → AC → Task → Step → verification method → checkpoint evidence
```

Checkboxes record review progress, not product PASS or FAIL. Use Task-scoped Step keys such as `Task4-Step2` because Step numbering restarts inside each Task.

Execution metadata must make routing decidable: exact dependencies, write ownership, stable Interfaces, verification, parallel-safety reason, and any real approval gate. Ordinary local edits, tests, planned commits, tier selection, subagent work, and safe parallel groups use internal or notify checkpoints and do not wait for the user.
