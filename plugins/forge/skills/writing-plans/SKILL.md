---
name: writing-plans
description: 'Use when execution complexity is high and implementation, migration, operational, or research work needs an explicit task-level Execution Plan. Triggers: "구현 계획", "계획 작성", "복잡한 작업", "plan", "implementation plan", "plan-only".'
---

# Writing Plans

Plan to resolve uncertainty, coordinate dependencies, or preserve a recovery point. Use the user's language. Keep approved contract headings, paths, and tool syntax exact when a structured plan needs them.

## Choose useful detail

Start with the requested outcome, relevant constraints, and known dependencies. Inspect repository facts. Resolve only user-owned choices that materially change the result; a technical unknown can become an investigation with a concrete question and exit evidence.

Use an existing session plan, issue, or checklist when it is sufficient. Save a standalone plan when independent review, handoff, or resumption needs one. Several files or steps alone do not require a new document. Do not write the implementation twice.

Define outcomes and how to verify them. Name files, interfaces, ordering, or recovery actions where the implementer needs that precision. Include examples or algorithms only when they remove real ambiguity. Let the implementer choose appropriate tests when the observable result is clear; an unbounded task still needs a result to aim for.

For example, specify that duplicate requests produce one persisted charge, rather than prescribing the test file's internal structure. Diagrams and milestones are optional and should explain actual relationships.

## Preserve contracts and progress

When related Canonical Specs govern the work, read the affected statements and relevant consumers. Confirm authorized meaning through the forge writing-specs skill. A plan does not create authority or expand scope.

Use a bundle's Acceptance statements for Canonical verification when present, otherwise its Requirement statements. Match planned verification to the claim: affected contracts and regression for a partial change, the full required set only for a full bundle implementation claim. An existing test may cover several statements. Use a coverage table when it helps review; do not duplicate traceability already clear in task links and evidence.

Keep progress in the existing record. Add separate progress or task files only when the history or independent ownership needs them. Before deleting a plan, promote permanent decisions to a Canonical Spec, ADR, or `docs/research/`.

## Structured file plans

For a plan consumed by Forge tooling, use `docs/plans/PPP-<slug>/plan.md` and read `references/structured-plan-format.md`. Preserve repository-contained, unique normalized Related Spec bundle paths and exact heading text in `Governing statements:` links. Inspect an unfamiliar or changed bundle with the writing-specs parser; reuse valid inspected context.

Read `references/plan-visual-structure.md` only when a requested review needs relationships or diagrams. Visual Docs generation and refresh require an explicit user request; Markdown or an app plan is sufficient for ordinary review. A requested one-time plan visualization can use that existing source and the current app's capabilities without creating a structured file plan or invoking the managed renderer.

Review whether the plan is executable, appropriately bounded, and verifiable. Continue authorized execution through the forge executing-plans skill without another go-ahead just because a plan was saved.
