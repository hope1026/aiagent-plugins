---
name: writing-plans
description: 'Use when execution complexity is high and implementation, migration, operational, or research work needs an explicit task-level Execution Plan. Triggers: "구현 계획", "계획 작성", "복잡한 작업", "plan", "implementation plan", "plan-only".'
---

# Writing Plans

Plan to resolve uncertainty, coordinate dependencies, or preserve a recovery point. Use the user's language. Link to the relevant source when the implementer needs to inspect an exact condition or decision.

## Choose useful detail

Start with the requested outcome, relevant constraints, and known dependencies. Inspect repository facts. Resolve only user-owned choices that materially change the result; a technical unknown can become an investigation with a concrete question and exit evidence.

Use an existing session plan, issue, or checklist when it is sufficient. Save a standalone plan when independent review, handoff, or resumption needs one. Several files or steps alone do not require a new document. Do not write the implementation twice.

Define outcomes and how to verify them. Name files, interfaces, ordering, or recovery actions where the implementer needs that precision. Include examples or algorithms only when they remove real ambiguity. Let the implementer choose appropriate tests when the observable result is clear; an unbounded task still needs a result to aim for.

Write so a new worker can tell what to do next and a person can understand what will change. Include the relevant source locations and conditions rather than copying entire Specs. Distinguish confirmed facts, implementation choices and unresolved decisions. The plan's detail should come from dependencies and uncertainty, not from filling every field in an example.

For example, specify that duplicate requests produce one persisted charge, rather than prescribing the test file's internal structure. Diagrams and milestones are optional and should explain actual relationships.

## Preserve contracts and progress

When related Canonical Specs govern the work, read the affected statements and relevant consumers. Confirm authorized meaning through the forge writing-specs skill. A plan does not create authority or expand scope.

Use a bundle's Acceptance statements for Canonical verification when present, otherwise its Requirement statements. Match planned verification to the claim: affected contracts and regression for a partial change, the full required set only for a full bundle implementation claim. An existing test may cover several statements. Use a coverage table when it helps review; do not duplicate traceability already clear in task links and evidence.

Keep progress in the existing record. Add separate progress or task files only when the history or independent ownership needs them. Before deleting a plan, promote permanent decisions to a Canonical Spec, ADR, or `docs/research/`.

## Save a plan when it helps

Use the project's plan location or a descriptive file under `docs/plans/` when a file helps handoff or resumption. Choose headings, checklists and task granularity from the work. Forge requires no numbered directory, `Task N` or `Step N` grammar, mandatory `Related Specs` block, or per-task repetition of full requirement headings. Put useful source links near the decisions they support, with concise readable labels. Check that the linked scope is sufficient and current; reusing a shared source reference is fine when its applicability is clear.

When a requested review needs relationships or diagrams, use the forge visual-docs skill and select the form from the actual plan. Visual Docs generation and refresh require an explicit user request; Markdown or an app plan is sufficient for ordinary review. A requested plan visualization can use that existing source and the current app's capabilities without creating a structured file plan.

Review whether the plan is executable, appropriately bounded, and verifiable. Continue authorized execution through the forge executing-plans skill without another go-ahead just because a plan was saved.
