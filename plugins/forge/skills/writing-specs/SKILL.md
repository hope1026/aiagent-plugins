---
name: writing-specs
description: 'Use when creating or changing a durable Canonical Spec, proposing a Spec Delta, clarifying a proposed contract, or reconciling code with approved project authority. Triggers: "정본 스펙", "스펙 변경안", "영구 요구사항", "정책 변경", "설계 결정", "spec delta", "canonical spec", durable contract change.'
---

# Writing Canonical Specs

Preserve approved project intent and make durable changes explicit. Respond and write prose in the user's language; preserve schema values, paths, exact statement headings, and code identifiers.

Only `approved` or `implemented` Canonical Spec Bundles are project SOT. A draft, Spec Delta, work brief, or execution plan cannot silently replace them. Local implementation details fully explained by code and tests need no new Canonical Spec.

## Establish the authorized meaning

Read the affected contract and relevant consumers. Inspect a bundle through `scripts/spec-docs.sh --repo-root . inspect --spec <bundle-directory> --format json`; use `forge/spec@3`, the appropriate lifecycle, and empty diagnostics. Reuse inspected context while relevant bytes remain unchanged.

Identify the exact before/after meaning and effects. A concrete user instruction or approval covering the target, meaning, and effects is authorization; do not ask for the same decision again. Ask only about unresolved contract conflicts, added scope, or effects outside that authorization. A vague outcome request does not authorize every possible policy interpretation.

Keep the Spec Delta in the conversation or `.forge/work/<work-id>/spec-delta.md`, with baseline path and hash and affected member/statement links. It can record an already authorized change as well as a pending proposal. Use `references/spec-delta-template.md` when the change needs a standalone review document; no extra form is required for a clear instruction.

When new meaning needs a decision, present the concrete proposal without replacing the current approved source. Group independent clarification questions when useful. Mechanical corrections within authorized meaning can proceed directly.

## Apply and validate

For structured authoring, read `references/bundle-authoring.md` and the applicable existing templates. Keep one independently reviewable durable condition per Requirement heading. Supporting examples, numbers, and exceptions belong in the body. Preserve exact links and unaffected statements.

Before applying a Delta, confirm the baseline is still current. Rebase on changed bytes and ask again only if the resulting meaning or effects exceed the authorization. Apply only approved meaning, set lifecycle to `approved`, update the current decision, and validate. Retain the applied Delta until its scope and evidence are recorded.

A new proposal can be validated in an isolated temporary repository while awaiting a decision. Do not require a separate candidate repository merely to repeat approval for a clear, already authorized local change. Validation must pass before implementation relies on the new source.

For drift, repair implementation to the approved contract unless the user has authorized changing that contract. If intent remains unclear, describe the conflict and ask; do not rewrite source to match an accidental implementation.

For replacement or consolidation of bundle paths, read `references/bundle-transitions.md`. Its isolated worktree, exact baseline, atomic transition, and user-work preservation requirements remain necessary for that fragile operation; ordinary edits do not use that subflow.

## Writer Transaction

Every approved Canonical Spec body, metadata, member layout, or lifecycle change uses this sequence from the repository root:

```bash
bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . validate --root docs/specs --baseline-ref HEAD
```

Any nonzero result blocks implementation handoff and completion claims. The transaction validates Markdown only and creates no HTML. `scripts/validate.sh` repeats repository validation; it never repairs sources or creates Visual Docs.

## Visual Docs Request Boundary

Markdown is the default review path. A Spec Delta is not a Visual Docs source and does not authorize HTML generation. For a requested visualization of Forge sources, use the forge visual-docs skill to preserve meaning and choose an appropriate format. One-time explanations may stay in the conversation or use freely authored visuals; only managed freshness, reproducibility or tracked Handbook requests need the shared renderer. The active request includes proportional verification and necessary corrections.

Source changes, approval, lifecycle status, complexity, Mermaid, tables, or an existing visual document are not generation requests. Report possible staleness without reading or updating it.


Use an appropriate plan when coordination or recovery needs it. Otherwise execute the authorized change directly. The forge verifying-work skill owns evidence-based implementation status; partial work retains its actual lifecycle state.
