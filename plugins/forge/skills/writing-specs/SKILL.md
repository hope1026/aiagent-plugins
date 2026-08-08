---
name: writing-specs
description: 'Use when creating or changing a durable Canonical Spec, proposing a Spec Delta, clarifying a proposed contract, or reconciling code with approved project authority. Triggers: "정본 스펙", "스펙 변경안", "영구 요구사항", "정책 변경", "설계 결정", "spec delta", "canonical spec", durable contract change.'
---

# Writing Canonical Specs

Announce: "Using the forge writing-specs skill — Canonical Spec mode: <new | change | clarify | sync>."

Respond in the user's language. Write human-readable Canonical Spec and Spec Delta content in that language while preserving canonical headings, traceability IDs, lifecycle values, code identifiers, commands, and established technical names.

## Iron Law

```text
ONLY APPROVED OR IMPLEMENTED CANONICAL SPECS ARE PROJECT SOT.
NO CANONICAL CONTRACT MUTATION BEFORE EXPLICIT SPEC DELTA APPROVAL.
NO IMPLEMENTATION HANDOFF UNTIL THE APPROVED CANONICAL SOURCE VALIDATES.
```

## Authority Contract

A Canonical Spec lives at `docs/specs/NNN-<slug>/spec.md` and records durable system intent, contracts, policy, and invariants. Read `references/spec-template.md` before authoring one. It uses restricted `forge/spec@2` frontmatter and reserves `Requirements`, `Acceptance Criteria`, and `Decisions & History` for normative project authority.

A Change Brief describes one work request with `Goal`, `Scope`, `Out of Scope`, and `Done Checks`. A Spec Delta proposes an exact Canonical Spec change before approval. Neither is SOT. Read `references/spec-delta-template.md` before proposing a new Canonical Spec or changing an existing one.

Use EARS as a semantic discipline in the user's language. Each Canonical Spec requirement names its condition and required behavior. Each AC cites explicit R IDs and states its precondition, action, and observable outcome. Keep `Decisions & History` append-only after approval.

## When to Use / When NOT

**Use when Canonical Spec impact is `yes`:** an existing R or AC changes; a durable interface, schema, workflow, state transition, error meaning, policy, cross-component responsibility, release contract, or user-designated permanent decision changes; or approved authority and implementation drift.

**Do NOT use merely because:** code changes, a task starts, a bug is investigated, execution is complex, or a local behavior is fully expressed by code and tests without durable project authority. Those routes are owned by the forge using-forge skill.

## Modes

| Situation | Mode |
|---|---|
| No governing Canonical Spec exists for a new durable contract | `new` |
| An approved or implemented Canonical Spec needs different normative meaning | `change` |
| A proposed candidate or Delta contains unresolved choices | `clarify` |
| Approved authority and implementation disagree | `sync` |

Before starting a mode, create one checklist item per numbered step in that mode and keep it current through approval, application, and validation.

### New

1. Explore current product and repository context.
2. Ask one clarification question per message only for choices that materially change durable authority. Mark unresolved choices in the proposal as `[NEEDS CLARIFICATION: ...]`.
3. Present two or three approaches with trade-offs.
4. Draft a Spec Delta containing the complete proposed Canonical Spec Markdown with lifecycle `status: approved`; keep the proposal in the conversation or `.forge/work/<work-id>/spec-delta.md`. Do not create the authoritative `docs/specs/` source yet.
5. Self-review language, EARS discipline, AC precondition/action/outcome, ambiguity, scope, placeholders, IDs, and source-owned Mermaid.
6. Ask the user to approve the exact proposal. The proposal remains non-authoritative while approval is pending.
7. On explicit approval, create `docs/specs/NNN-<slug>/spec.md` from the approved content, append the approval history entry, and run the writer transaction. Mechanical fixes that preserve approved meaning may proceed; any semantic change returns for approval.

### Change

1. Locate and inspect the governing Canonical Spec. Require `forge/spec@2`, lifecycle `approved|implemented`, and zero diagnostics. Record its ID, path, status, and source SHA-256.
2. Leave the existing Canonical Spec bytes and authority unchanged. Draft a Spec Delta in the conversation or `.forge/work/<work-id>/spec-delta.md` that names the baseline SHA-256, every affected R and AC, exact additions, modifications or tombstones, and the proposed history entry.
3. Self-review the Delta and ask for explicit approval. Do not set the Canonical Spec to `draft` while waiting.
4. Immediately before applying an approved Delta, re-inspect the baseline. If its SHA-256 changed, rebase the Delta and obtain approval for any semantic difference.
5. Apply only the approved meaning. Preserve IDs without renumbering, keep removed IDs as tombstones, set lifecycle `status: approved`, append the dated `[CHANGE]` and approval history, and run the writer transaction.
6. A validation failure blocks implementation handoff. Fix mechanical defects and rerun; return for approval if the correction changes meaning.

### Clarify

Resolve one unresolved durable choice at a time in the proposed Spec Delta or new Canonical Spec candidate. Rewrite the affected proposed contract, record the clarification in the proposal, and require zero `[NEEDS CLARIFICATION]` markers before approval. Do not add clarification markers to an authoritative `approved` or `implemented` source.

### Sync

Compare actual behavior with the authoritative Canonical Spec. Record each mismatch in a Change Brief or Spec Delta, not by mutating the approved source first. Let the user choose one of two routes:

- **Code repair:** retain the Canonical Spec and route the affected implementation through the forge systematic-debugging or test-driven-development skill.
- **Contract change:** enter `change` mode, approve the Spec Delta, update the Canonical Spec, then execute through the selected direct or planned route.

## Current-state Supersession

Use this subflow only when an `approved` or `implemented` Canonical Spec must be replaced by one new identity so active specs contain current facts rather than completed migration history. It does not authorize retirement, merge, a target already present in the baseline, or a same-diff transition chain.

1. Write and present the complete replacement as a Spec Delta before touching the old source. Keep it outside the final `toPath`, such as `.forge/work/<work-id>/spec-delta.md`. Preserve completed execution details in a plan, ADR, or evidence file.
2. Obtain explicit approval. Then use the forge writing-plans skill to record the exact source and target identities, the SHA-256 of the old source bytes from the expected Git baseline, the evidence path, all reference updates, and the release boundary.
3. Commit the approved Execution Plan and durable evidence first. Record the expected clean HEAD and a fingerprint of its HEAD, index, tracked, and untracked bytes. A dirty root blocks candidate creation; do not clean, stash, or overwrite user work.
4. Create a registered isolated Git worktree detached at the expected HEAD. Perform all supersession mutations there, never in the production root.
5. In that worktree, append exactly one one-to-one `superseded` record to `docs/specs/.transitions.json`; promote the approved replacement at its new `docs/specs/NNN-<slug>/spec.md` identity; remove the old source; update active relations and Markdown links; and preserve evidence. Use the old SHA-256 from Git object bytes, not current filesystem bytes.
6. Run baseline validation against the expected HEAD and exact expected-byte checks. Create one candidate commit only after every gate passes.
7. On any validation, expected-byte, or commit failure, discard the candidate worktree and prove that the production fingerprint is unchanged. When the user did not explicitly request a Review Viewer, the Review Viewer output count stays exactly zero.
8. Immediately before promotion, require the production root to remain at the expected clean HEAD with the exact recorded fingerprint. Apply only the verified candidate commit with a fast-forward operation. Any HEAD or byte drift refuses promotion without modifying the root.

The transition manifest is durable audit data, but the replacement Canonical Spec remains the active source of truth. Existing transition records stay in canonical order as an exact prefix; a prior record never authorizes another deletion.

## Writer Transaction

Every approved Canonical Spec body, metadata, or lifecycle change uses this sequence from the repository root:

```bash
bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . validate --root docs/specs --baseline-ref HEAD
```

Any nonzero result blocks implementation handoff and completion claims. The transaction validates Markdown only and creates no HTML. `scripts/validate.sh` repeats repository validation; it never repairs sources or creates Review Viewers.

## Review Viewer Request Boundary

Markdown is the default review path. A Spec Delta is not a Review Viewer source and does not authorize HTML generation. Only an explicit user request to create, refresh, present, or freshness-check a Canonical Spec or Execution Plan Review Viewer permits one handoff to the forge review-viewer skill.

Source changes, approval, lifecycle status, complexity, Mermaid, tables, or an existing Viewer are not generation requests. Report possible staleness without reading or updating the Viewer.

## Working Files

| Artifact | Path | Git policy |
|---|---|---|
| Canonical Spec | `docs/specs/NNN-<slug>/spec.md` | Tracked, permanent SOT when approved or implemented |
| Optional Change Brief | `.forge/work/<work-id>/brief.md` | Local work input |
| Optional Spec Delta | `.forge/work/<work-id>/spec-delta.md` | Local approval proposal; retain through verification, then remove or promote only as non-authoritative evidence |
| Supersession evidence | `docs/plans/`, `docs/adr/`, or `docs/evidence/` | Tracked when the transition requires it |
| Investigation notes | `.forge/research/` | Local only; promote durable findings to `docs/research/` |

## Red Flags

| Excuse | Reality |
|---|---|
| "The task changes code, so it needs a spec." | Code change and Canonical Spec impact are independent axes. |
| "Returning the current source to draft is harmless." | It removes the authority token from the current SOT before the proposal is approved. Keep the Delta separate. |
| "The request is clear, so approval is implied." | Only explicit approval promotes proposed contract meaning. |
| "The Delta is effectively the SOT now." | A proposal has no project authority until applied to validated Canonical source. |
| "The validator passed, so the prose is good." | Self-review owns EARS meaning, scope, and observable ACs. |
| "The baseline changed only a little." | Re-inspect and rebase before applying; silent merge can change approved meaning. |
| "The bug proves the spec is wrong." | First establish whether implementation drift or contract change owns the mismatch. |
| "A Viewer would make approval safer." | Markdown is sufficient; HTML still requires explicit Viewer intent. |

## Handoff

**After approval and a passing writer transaction, return to the forge using-forge route: low-complexity work executes directly with the relevant implementation skill; high-complexity work continues through the forge writing-plans skill.**
