---
name: writing-specs
description: 'Use when creating features, changing behavior, starting a project, resolving spec clarifications, or syncing documented behavior with existing code. Triggers: "스펙", "스펙 작성", "기능 추가", "기능 변경", "요구사항", "설계", "brainstorm", "change request".'
---

# Writing Specs

Announce: "Using the forge writing-specs skill — mode: <new | change | clarify | sync>."

Respond in the user's language. Write human-readable spec content in that language while preserving canonical headings, traceability IDs, lifecycle values, code identifiers, commands, and established technical names.

## Iron Law

```text
NO IMPLEMENTATION OR PLAN FOR PRODUCT BEHAVIOR WITHOUT AN APPROVED STRUCTURED SPEC.
MARKDOWN IS AUTHORITATIVE. SPEC PAGES CHANGE WITH THEIR SOURCE. REVIEW VIEWERS REQUIRE AN EXPLICIT REQUEST.
```

## Contract

Read `references/spec-template.md` before writing. A spec lives at `docs/specs/NNN-<slug>/spec.md`, uses restricted `forge/spec@1` frontmatter, and contains exactly these six `##` sections:

1. `Overview`
2. `Requirements`
3. `Behavior & Flows`
4. `Data & Interfaces`
5. `Acceptance Criteria`
6. `Decisions & History`

Use EARS as a semantic discipline in the user's language. Each requirement names its condition and required behavior. Each AC cites explicit R IDs and states its precondition, action, and observable outcome. The machine validator checks structure and traceability; it does not claim to understand natural-language meaning. Keep `Decisions & History` append-only after approval.

## Modes

| Situation | Mode |
|---|---|
| No governing spec | `new` |
| User requests different behavior | `change` |
| Clarification markers remain | `clarify` |
| Code and spec disagree | `sync` |

The ceremony-floor exemptions are typo/comment/format-only edits, dependency bumps with no API change, CI/tooling config that changes no build output, and behavior-preserving refactors with existing tests. Nothing else is exempt.

### New

1. Explore current product and repository context.
2. Ask one clarifying question per message and mark unresolved decisions `[NEEDS CLARIFICATION: ...]`.
3. Present two or three approaches with trade-offs.
4. Create the structured source with frontmatter `status: draft`.
5. Self-review language, EARS discipline, AC precondition/action/outcome, ambiguity, scope, placeholders, IDs, and source-owned Mermaid.
6. Run the writer transaction below before asking for approval.
7. Ask the user to review Markdown. Mention Review Viewer usefulness only when material; never generate it while waiting.
8. On explicit approval, set frontmatter `status: approved`, append history, and run the writer transaction again before handoff.

### Change

1. Locate the governing structured spec.
2. Return frontmatter `status` to `draft`; mark affected IDs modified or removed and add new IDs without renumbering.
3. Append a dated `[CHANGE]` entry.
4. Self-review and run the writer transaction before approval.
5. After explicit approval, set `status: approved`, append approval history, and run the transaction again.
6. Hand off to `writing-plans` only after the transaction passes.

### Clarify

Resolve every marker one question at a time, rewrite the affected requirement, and append `[CLARIFIED]`. Zero markers is required for `approved`. Run the writer transaction after each source change and again after the approved status change. A failure blocks approval, handoff, and completion reporting.

### Sync

Compare actual behavior with every requirement. Append each mismatch as `[DRIFT]`, let the user choose spec change or code repair, apply the approved result, and run the writer transaction. Code repairs continue through `writing-plans`; spec changes return through the approval gate.

## Current-state supersession

Use this subflow only when an `approved` or `implemented` spec must be replaced by one new identity so active specs contain current facts rather than completed migration history. It does not authorize retirement, merge, a target already present in the baseline, or a same-diff transition chain.

1. Write and present the current-state replacement as `draft` before touching the old source or page. Keep this approval copy outside the final `toPath`, such as under `.forge/scratch/spec-supersession/`, so it cannot become a baseline-existing target. Preserve completed execution details in a plan, ADR, or evidence file.
2. Obtain explicit approval of the replacement Markdown. Then use `writing-plans` to record the exact source and target identities, the SHA-256 of the old source bytes from the expected Git baseline, the evidence path, all reference updates, and the release boundary.
3. Commit the approved plan and durable evidence first. Record the expected clean HEAD and a fingerprint of its HEAD, index, tracked, and untracked bytes. A dirty root blocks candidate creation; do not clean, stash, or overwrite user work.
4. Create a registered isolated Git worktree detached at the expected HEAD. Perform all supersession mutations there, never in the production root.
5. In that worktree, append exactly one one-to-one `superseded` record to `docs/specs/.transitions.json`; promote the approved replacement at its new `docs/specs/NNN-<slug>/spec.md` identity; remove the old source and generated page; update active relations and Markdown links; and preserve evidence. Use the old SHA-256 from Git object bytes, not current filesystem bytes.
6. Run baseline validation against the expected HEAD, then run a full Spec Pages build without `--changed`, repository check, and exact expected-byte checks. Create one candidate commit only after every gate passes.
7. On any validation, build, check, expected-byte, or commit failure, discard the candidate worktree and prove that the production fingerprint is unchanged. When the user did not explicitly request a Review Viewer, the Review Viewer output count stays exactly zero.
8. Immediately before promotion, require the production root to remain at the expected clean HEAD with the exact recorded fingerprint. Apply only the verified candidate commit with a fast-forward operation. Any HEAD or byte drift refuses promotion without modifying the root.

The transition manifest is durable audit data, but the replacement spec remains the active source of truth. Existing transition records stay in canonical order as an exact prefix; a prior record never authorizes another deletion.

## Writer transaction

Every body, metadata, or frontmatter status change uses the same sequence from the repository root. Existing sources include the explicit Git baseline:

```bash
bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . validate --root docs/specs --baseline-ref HEAD
bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . build --root docs/specs --changed docs/specs/NNN-<slug>/spec.md --offline
bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . check --root docs/specs
```

For a new source not present in `HEAD`, validation still uses the repository baseline so approved/implemented peers retain append-only protection. Any nonzero result blocks approval requests, lifecycle handoff, and completion claims.

When generator, template, runtime, or asset bytes change, omit `--changed` and rebuild the full catalog before checking:

```bash
bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . build --root docs/specs --offline
bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . check --root docs/specs
```

Spec Pages at `docs/specs/NNN-<slug>/index.html` and `docs/specs/index.html` are tracked, deterministic, read-only outputs. They always change in the same transaction as source or lifecycle status. `scripts/validate.sh` checks expected bytes; it never repairs them.

## Review Viewer request boundary

Markdown is the default review path. Review Viewer is a separate untracked snapshot at `.forge/reviews/<review-id>/view.html`.

- Source edits, frontmatter status changes, complexity, checkpoints, or an existing Review Viewer are not an explicit generation request.
- Never assume an existing Review Viewer is current. Report possible staleness without reading, creating, or refreshing it.
- Explicit Review Viewer intent is sufficient—for example, “현재 스펙 Review Viewer 만들어줘.” The agent resolves the current source, `spec` or `plan` mode, and a valid review-id from context during handoff; ask only when context is genuinely ambiguous.
- Only an explicit create or refresh request permits exactly one handoff to `review-viewer`. The successful build ends generation.
- The negative pressure “기존 Viewer는 알아서 최신일 것이라 가정하고 status만 변경” still requires the source/status and Spec Pages in the same transaction and permits zero Review Viewer builds.

## Working files

| Artifact | Path | Git policy |
|---|---|---|
| Structured spec | `docs/specs/NNN-<slug>/spec.md` | tracked source |
| Per-spec Spec Page | `docs/specs/NNN-<slug>/index.html` | tracked generated |
| Spec catalog | `docs/specs/index.html` | tracked generated |
| Review Viewer | `.forge/reviews/<review-id>/view.html` | untracked, explicit request only |
| Supersession approval draft | `.forge/scratch/spec-supersession/<id>/spec.md` | local only until approved candidate |
| Investigation notes | `.forge/research/` | local only; promote durable findings to `docs/research/` |

## Red Flags

| Excuse | Reality |
|---|---|
| "The request is clear, so approval is implied." | Only the user can approve the reviewed Markdown. |
| "The validator passed, so the prose is good." | Self-review owns EARS and observable AC meaning. |
| "Status is only metadata." | Frontmatter status changes source bytes and require page build/check. |
| "The old Viewer is probably fresh." | Its existence proves nothing and grants no build permission. |
| "The deadline makes HTML regeneration safer." | The durable transaction updates Spec Pages; Review Viewer still requires explicit create or refresh intent. |
| "One failed check can be fixed after handoff." | Any failure blocks the approval, handoff, and completion claim. |

## Handoff

After explicit approval and a passing writer transaction, use `writing-plans`. On an explicit Review Viewer create or refresh request, resolve handoff options and hand off once to `review-viewer`, then return to the owning lifecycle.
