---
name: verifying-work
description: 'Use when about to claim work complete, fixed, passing, or done; before commits or progress claims; and when converting an approved Canonical Spec to implemented using evidence matched to Quick, restoration, Spec Delta, or plan-only work. Triggers: "완료", "검증", "다 됐어?", "확인해줘", "verify", "done", finishing any plan or fix.'
---

# Verifying Work

Announce once when first applied: "Using the forge verifying-work skill: matching fresh evidence to this work class before any completion claim."

Respond in the user's language. The discipline below applies in every language.

## Overview

Verification proves the exact completion claim and affected authority. Quick work needs focused evidence. Restoring an existing Canonical contract needs the original reproduction and affected contract observation. A partial implementation verifies its affected statements and reports partial completion. Only a claim that a new or never-implemented bundle is fully implemented walks the full Canonical verification set and changes lifecycle status. An Execution Plan adds recovery and Task evidence but does not by itself raise or lower verification.

## Iron Law

```text
NO COMPLETION CLAIM WITHOUT FRESH EVIDENCE MATCHED TO THE WORK CLASS.
NO CANONICAL SPEC STATUS CHANGE WITHOUT THE REQUIRED CANONICAL VERIFICATION EVIDENCE.
```

## When to Use / When NOT

**Use before:**

- any statement that work is complete, fixed, passing, working, or done;
- committing, reporting progress, accepting worker results, or moving to the next Execution Plan Task;
- setting Canonical Spec lifecycle `status: implemented`.

**NOT needed for:** neutral in-progress narration that claims nothing, answering questions that assert nothing about work state, or a visual-document request whose evidence is handled by the forge visual-docs skill below.

## Work-class Matrix

| Work class | Required fresh evidence | Canonical lifecycle effect |
|---|---|---|
| Quick | focused test, build, lint, type check, real run, or observation that directly proves the claim | none |
| Plan-only | every plan verification command and goal-level Done Check | none |
| Existing-contract restoration | original reproduction now passes, affected Canonical contract observation matches, regression command passes | none |
| Partial implementation of an approved contract | every directly or indirectly affected statement plus relevant regression evidence | none; report the implemented work scope |
| Approved Spec Delta against an implemented baseline | every affected statement in the Canonical verification set passes plus regression command for unchanged behavior | `approved → implemented` after validation |
| Full implementation of a new or never-implemented approved baseline | every statement in the Canonical verification set passes plus the full relevant suite | `approved → implemented` after validation |

Keep an applied Spec Delta through verification so its baseline lifecycle and affected statement links remain available. Remove it after evidence is recorded or promote it only as explicitly non-authoritative evidence.

## The Process

Reuse the existing work checklist. Add one item per required Canonical verification statement when needed; a focused Quick claim can use its command and observation directly without a separate five-stage checklist.

### 1. Identify the claim and work class

State the exact claim. Read route evidence from the forge using-forge classification, optional Change Brief or Spec Delta, Related Canonical Specs, and optional Execution Plan. If the classification is missing, reconstruct both axes from actual scope before verifying.

Treat a ready conversation draft or Change Brief as the claim boundary: its Goal and Done Checks say what must be proven, not that proof already exists. Inspect missing repository facts and run evidence yourself. Evidence gaps are failures or unknowns to resolve; they are not implementation-preference questions for the user.

Plan existence does not determine the class. A plan-only route can have no Canonical Spec, and spec-backed direct work can have no plan.

### 2. Run command-level verification now

1. Choose the command or concrete observation that proves the exact claim.
2. Run it and read the full output and exit code, or use already observed evidence tied to the same unchanged relevant source, implementation, tests, inputs, settings, and environment.
3. Count failures yourself. Remembered or worker-reported success without inspected output is not evidence. Root reviews a worker diff and confirms that inspected execution evidence applies to the integrated state; run affected verification when that evidence is missing, invalidated, or does not cover integration.
4. Compare actual output with the claim. Report disagreement directly.

| Claim | Required evidence | Not sufficient |
|---|---|---|
| Tests pass | Inspected test run on the current relevant state, zero failures, exit 0 | stale run or code review |
| Build succeeds | Fresh build, exit 0 | lint passing |
| Bug fixed | Original reproduction and regression command pass | changed code |
| Plan-only work complete | Every plan command and Done Check passes | Task boxes alone |
| Worker finished | Root diff review and applicable inspected execution evidence | worker report |

### 3. Add Canonical contract evidence when required

For existing-contract restoration, partial implementation, or approved Spec Delta work:

1. Inspect each governing bundle with `bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . inspect --spec <bundle-directory> --format json`. Require `forge/spec@3`, lifecycle `approved|implemented` appropriate to the class, and empty diagnostics.
2. Calculate each bundle's Canonical verification set: use every Acceptance statement when one or more exist; otherwise use every Requirement statement. Then select the required statements from the work class:
   - restoration: the statements whose approved behavior the fix restores;
   - partial implementation or Delta against an implemented baseline: the affected statements linked in the approved scope, plus any statement whose observable outcome the change touches;
   - full implementation claim for a new Canonical Spec or never-implemented approved baseline: every statement in the bundle's Canonical verification set.
3. Create one checklist item per required verification statement, labeled with its member path and exact heading.
4. Walk each required statement in order: establish its precondition, perform its action, observe its expected outcome, and record `PASS` or `FAIL` with exact evidence. Code reading alone is not an observation.
5. When an Execution Plan exists, confirm its Related Specs coverage, completed Task verification, route evidence, and goal-level Done Checks agree with the actual implementation.

Unchanged statements retain prior implementation evidence when the approved scope identifies every affected statement and current regression evidence covers unchanged behavior. Any concrete uncertainty expands the affected set. Do not expand merely because more tests or statements exist.

### 4. Handle failures

Name each failure as one of these:

- **Implementation bug:** actual behavior misses Canonical authority or the work claim → use the forge systematic-debugging skill, then restart verification.
- **Canonical Spec bug:** durable authority is wrong or incomplete → use the forge writing-specs skill in change mode, obtain approval, then restart verification.
- **Plan defect:** execution steps or coverage are mechanically wrong while Canonical meaning remains correct → make the smallest plan correction, record it, and rerun affected evidence.

Never change implementation and Canonical meaning silently in the same repair.

### 5. Complete the matching lifecycle

- **Quick, plan-only, restoration, partial implementation:** report the proven scope without changing Canonical Spec status.
- **Full implementation after an approved Spec Delta:** after the full required Canonical verification set and regression evidence pass, set the Canonical Spec lifecycle `status` to `implemented`, update the current decision summary, and run the writer transaction. Git or validated transition evidence retains prior detail. A transaction failure blocks completion reporting.

Stop after the exact claim, affected contracts, and required project gates are proven. A skill handoff, elapsed time, or the availability of a broader suite does not invalidate applicable evidence. New relevant changes, failures, uncovered impact, or environment drift invalidate only the affected evidence.

The report names work class, claim, command evidence, and required Canonical verification statement verdicts:

```markdown
Work class: Existing-contract restoration
Claim: Refresh retries no longer duplicate writes.

| Canonical verification statement | Member | Verdict | Evidence |
|---|---|---|---|
| Given one expired session, refresh returns one usable session | `session-verification.md` | PASS | `pytest tests/test_refresh.py -q` → 7 passed, exit 0 |
```

## Requested Visual Docs

The forge visual-docs skill owns generation and proportional rendered verification for an explicitly requested document. Build success proves file generation; inspect the actual reading path and content before claiming visual quality. Complex sources, new compositions, or diagrams need desktop and narrow-view checks of the relevant navigation, meaning, and readability. Do not rerun the whole tooling suite for every document. A tracked Project Handbook also needs its freshness check and repository validation.

Within the active request, fix source or shared tooling and rebuild as needed; preserve generated-output reproducibility. Report unavailable checks accurately. Tooling changes use normal regression evidence. Neither generation nor visual review alone marks the governing product contract implemented.

## Working Files

- Reads: optional `.forge/work/<work-id>/brief.md` and `spec-delta.md`; Related Canonical Specs; optional Execution Plan, progress, and Task files.
- Writes: Canonical Spec lifecycle `status: implemented` and current decision summary only after the required Canonical verification evidence passes; evidence goes to the user, plan progress, or an explicitly durable evidence path.

## Red Flags

| Excuse | Reality |
|---|---|
| "Quick means no tests." | Quick removes formal artifacts, not fresh proof. |
| "There is no spec, so verification is impossible." | Focused commands and plan Done Checks verify non-SOT work. |
| "The Brief says done, so the evidence can be inferred." | A ready Brief defines the claim. Only fresh commands and observations prove it. |
| "Every Canonical verification statement must run for this one restored branch." | Restoration verifies the affected contract and regression behavior without changing lifecycle status. |
| "This approved bundle is not implemented, so one partial feature requires the full set." | Verify the affected feature and report partial completion. The full set is required only to mark the bundle implemented. |
| "The Delta links one statement, so indirect effects do not count." | Any touched observable outcome joins the required statement set. |
| "The baseline was implemented, so no fresh Canonical evidence is needed." | Changed contract meaning requires fresh affected-statement evidence. |
| "The plan passed, so the Canonical Spec is implemented." | Plan evidence and Canonical verification evidence have different authority. |
| "The worker reported success." | Root review and applicable inspected execution evidence remain mandatory. |
| "Another skill started, so the same unchanged suite must run again." | Reuse valid inspected evidence until a relevant change or uncovered impact invalidates it. |
| "The deadline makes schema work Quick." | Misclassification is a routing failure, not a verification shortcut. |
| "I can say it should work." | Confidence and code reading are not execution evidence. |

## Handoff

**If evidence fails, route the named implementation, Canonical Spec, or plan defect and restart verification. If it passes, report only the claims the evidence proves; change Canonical lifecycle only for an approved Spec Delta with the required Canonical verification set complete.**
