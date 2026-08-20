---
name: writing-specs
description: 'Use when creating or changing a durable Canonical Spec, proposing a Spec Delta, clarifying a proposed contract, or reconciling code with approved project authority. Triggers: "정본 스펙", "스펙 변경안", "영구 요구사항", "정책 변경", "설계 결정", "spec delta", "canonical spec", durable contract change.'
---

# Writing Canonical Specs

Announce: "Using the forge writing-specs skill — Canonical Spec mode: <new | change | clarify | sync>."

Respond in the user's language. Write human-readable Canonical Spec and Spec Delta content in that language while preserving canonical headings, lifecycle values, code identifiers, commands, paths, and established technical names.

## Iron Law

```text
ONLY APPROVED OR IMPLEMENTED CANONICAL SPEC BUNDLES ARE PROJECT SOT.
NO CANONICAL CONTRACT MUTATION BEFORE EXPLICIT SPEC DELTA APPROVAL.
NO IMPLEMENTATION HANDOFF UNTIL THE APPROVED CANONICAL SOURCE VALIDATES.
```

## Authority Contract

A Canonical Spec is a Spec Bundle at `docs/specs/<semantic-bundle-name>/`. The normalized repository-relative bundle path is its human-facing identity. Do not assign a separate document identifier. Read `references/spec-template.md` before authoring a bundle.

Each bundle has exactly one `forge/spec@3` root document and one or more Markdown members. The root owns lifecycle metadata and a complete `Documents` inventory. Root and member filenames describe their contents; generic names and numeric filename or directory prefixes are invalid. Keep one file when it remains readable. Split it only when several independently reviewable concerns need distinct members, and keep every member in the same bundle directory.

`Requirements`, `Acceptance Criteria`, and `Decisions & History` carry normative project authority. A Requirement or Acceptance statement is a complete `###` heading, not a short code. Acceptance statements include `Verifies:` or `검증하는 요구사항:` followed by Markdown links whose member path, anchor, and link text exactly identify the Requirement headings they verify. A Change Brief and a Spec Delta remain non-authoritative work inputs. Read `references/spec-delta-template.md` before proposing a new or changed bundle.

Use EARS as a semantic discipline in the user's language. Each Requirement heading states the condition and required behavior. Each Acceptance heading states a precondition, action, and observable outcome. Keep `Decisions & History` focused on the current adopted decision; Git and validated transition evidence retain superseded detail.

## When to Use / When NOT

**Use when Canonical Spec impact is `yes`:** a Requirement or Acceptance statement changes; a durable interface, schema, workflow, state transition, error meaning, policy, cross-component responsibility, release contract, or user-designated permanent decision changes; or approved authority and implementation drift.

**Do NOT use merely because:** code changes, a task starts, a bug is investigated, execution is complex, or a local behavior is fully expressed by code and tests without durable project authority. Those routes belong to the forge using-forge skill.

## Modes

| Situation | Mode |
|---|---|
| No governing Canonical Spec exists for a new durable contract | `new` |
| An approved or implemented Spec Bundle needs different normative meaning | `change` |
| A proposed bundle or Delta contains unresolved choices | `clarify` |
| Approved authority and implementation disagree | `sync` |

Before starting a mode, create one checklist item per numbered step and keep it current through approval, application, and validation.

### New

1. Explore current product and repository context.
2. Ask one clarification question per message only for choices that materially change durable authority. Mark unresolved choices in the proposal as `[NEEDS CLARIFICATION: ...]`.
3. Present two or three approaches with trade-offs.
4. Choose a semantic bundle directory and descriptive root and member filenames. Draft a Spec Delta containing the complete proposed Spec Bundle with lifecycle `status: approved`; keep it in the conversation or `.forge/work/<work-id>/spec-delta.md`. Do not create authoritative files under `docs/specs/` yet.
5. Self-review language, EARS discipline, member boundaries, `Documents` completeness, full Requirement and Acceptance statement wording, exact statement links, ambiguity, and source-owned Mermaid.
6. Validate the proposal in an isolated temporary repository, then ask the user to approve the exact proposal. The proposal remains non-authoritative while approval is pending.
7. On explicit approval, create the approved bundle, record the current adopted decision, and run the writer transaction. Remove completed migration detail and superseded contract text from the active bundle; retain audit detail in Git or validated transition evidence. Mechanical fixes that preserve approved meaning may proceed; any semantic change returns for approval.

### Change

1. Locate and inspect the governing bundle directory. Require `forge/spec@3`, lifecycle `approved|implemented`, and zero diagnostics. Record its bundle path, root path, status, and bundle SHA-256.
2. Leave the existing bundle bytes and authority unchanged. Draft a Spec Delta that names the baseline bundle SHA-256 and links every affected Requirement and Acceptance statement by member path and exact heading. State exact additions, modifications, removals, member moves, and the proposed current decision summary.
3. Self-review the Delta and ask for explicit approval. Do not set the authoritative bundle to `draft` while waiting.
4. Immediately before applying an approved Delta, re-inspect the baseline. If its bundle SHA-256 changed, rebase the Delta and obtain approval for any semantic difference.
5. Apply only the approved meaning. Preserve unaffected statement headings, remove superseded contract text, set lifecycle `status: approved`, replace the current decision summary, and run the writer transaction. Git or validated transition evidence retains the prior detail.
6. A validation failure blocks implementation handoff. Fix mechanical defects and rerun; return for approval if the correction changes meaning.

### Clarify

Resolve one unresolved durable choice at a time in the proposed Delta or bundle candidate. Rewrite the affected proposed contract, record the clarification, and require zero `[NEEDS CLARIFICATION]` markers before approval. Do not add clarification markers to an authoritative `approved` or `implemented` bundle.

### Sync

Compare actual behavior with the authoritative Spec Bundle. Record each mismatch in a Change Brief or Spec Delta, not by mutating approved source first. Let the user choose one route:

- **Code repair:** retain the bundle and route the implementation through the forge systematic-debugging or test-driven-development skill.
- **Contract change:** enter `change` mode, approve the Delta, update the bundle, then execute through the selected direct or planned route.

## Current-state Replacement and Consolidation

Use this subflow only when one or more `approved` or `implemented` sources must move to one new semantic bundle path so active sources contain current facts rather than completed migration history. It authorizes one-to-one replacement or a coordinated many-to-one `merged` consolidation. It does not authorize retirement without a target, split, incremental merge into a target already present in the baseline, partial source removal, or a same-diff transition chain.

1. Write and present the complete replacement as a Spec Delta before touching the current source. Keep it outside the final bundle path. Preserve completed execution details in a plan, ADR, or evidence file.
2. Obtain explicit approval. Then use the forge writing-plans skill to record every exact source path and baseline bundle SHA-256, the one new target bundle path, evidence path, reference updates, and release boundary.
3. Commit the approved Execution Plan and durable evidence first. Record the expected clean HEAD and a fingerprint of its HEAD, index, tracked, and untracked bytes. A dirty root blocks candidate creation; do not clean, stash, or overwrite user work.
4. Create a registered isolated Git worktree detached at the expected HEAD. Perform all supersession mutations there, never in the production root.
5. In that worktree, append to `docs/specs/.bundle-transitions.json`, choose exactly one transition shape, and apply it atomically:
   - One baseline to one new target: append one `superseded` record.
   - Two or more baselines to one new target: append one coordinated `merged` record per baseline in the same candidate diff. Every record uses the exact baseline hash, one shared `toBundlePath`, and one shared `evidencePath`.
   Promote the replacement, remove every authorized source, update active relations and Markdown links, and preserve evidence. The transition uses `fromSourcePath`, `fromSourceSha256`, `disposition`, `toBundlePath`, `evidencePath`, and `reason`, never a document identifier.
6. Run baseline validation against the expected HEAD and exact expected-byte checks. Create one candidate commit only after every gate passes.
7. On any validation, expected-byte, or commit failure, discard the candidate worktree and prove that the production fingerprint is unchanged. When the user did not explicitly request a Visual Docs, the Visual Docs output count stays exactly zero.
8. Immediately before promotion, require the production root to remain at the expected clean HEAD with the exact recorded fingerprint. Apply only the verified candidate commit with a fast-forward operation. Any HEAD or byte drift refuses promotion without modifying the root.

The transition manifest is durable audit data, but the replacement bundle remains the active source of truth. Existing transition records stay in canonical order as an exact prefix; a prior record never authorizes another deletion. A `merged` group must contain at least two exact active baseline sources and cannot be extended after the target becomes part of a baseline.

## Writer Transaction

Every approved Canonical Spec body, metadata, member layout, or lifecycle change uses this sequence from the repository root:

```bash
bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . validate --root docs/specs --baseline-ref HEAD
```

Any nonzero result blocks implementation handoff and completion claims. The transaction validates Markdown only and creates no HTML. `scripts/validate.sh` repeats repository validation; it never repairs sources or creates Visual Docs.

## Visual Docs Request Boundary

Markdown is the default review path. A Spec Delta is not a Visual Docs source and does not authorize HTML generation. Only an explicit user request to create, refresh, present, or freshness-check a Brief, Canonical Spec, Execution Plan, or Project Handbook permits one handoff to the forge visual-docs skill.

Source changes, approval, lifecycle status, complexity, Mermaid, tables, or an existing visual document are not generation requests. Report possible staleness without reading or updating it.

## Working Files

| Artifact | Path | Git policy |
|---|---|---|
| Canonical Spec Bundle | `docs/specs/<semantic-bundle-name>/` | Tracked, permanent SOT when approved or implemented |
| Bundle root | `docs/specs/<semantic-bundle-name>/<descriptive-root-name>.md` | Tracked; owns metadata and `Documents` |
| Bundle members | `docs/specs/<semantic-bundle-name>/<descriptive-content-name>.md` | Tracked; grouped by one durable contract |
| Optional Change Brief | `.forge/work/<work-id>/brief.md` | Local work input |
| Optional Spec Delta | `.forge/work/<work-id>/spec-delta.md` | Local approval proposal; retain through verification, then remove or promote only as non-authoritative evidence |
| Supersession evidence | `docs/plans/`, `docs/adr/`, or `docs/evidence/` | Tracked when the transition requires it |
| Investigation notes | `.forge/research/` | Local only; promote durable findings to `docs/research/` |

## Red Flags

| Excuse | Reality |
|---|---|
| "The task changes code, so it needs a spec." | Code change and Canonical Spec impact are independent axes. |
| "A short code is easier to trace." | Readers must open another index to understand it. Use the exact statement heading and member path. |
| "One generic filename is conventional." | Filenames are part of human navigation. Name each file for the content it owns. |
| "Returning the current source to draft is harmless." | It removes the authority token from the current SOT before the proposal is approved. Keep the Delta separate. |
| "The request is clear, so approval is implied." | Only explicit approval promotes proposed contract meaning. |
| "The Delta is effectively the SOT now." | A proposal has no project authority until applied to validated Canonical source. |
| "The validator passed, so the prose is good." | Self-review owns EARS meaning, scope, and observable Acceptance statements. |
| "The baseline changed only a little." | Re-inspect and rebase before applying; silent merge can change approved meaning. |
| "I can remove two sources now and append the last merged record later." | Consolidation is atomic. All exact sources, the new target, shared evidence, relation updates, and removals belong to one isolated candidate diff. |
| "A Viewer would make approval safer." | Markdown is sufficient; HTML still requires explicit Viewer intent. |

## Handoff

**After approval and a passing writer transaction, return to the forge using-forge route: low-complexity work executes directly with the relevant implementation skill; high-complexity work continues through the forge writing-plans skill.**
