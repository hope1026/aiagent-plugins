---
name: verifying-work
description: 'Use when about to claim work complete, fixed, passing, or done; before commits or progress claims; and when converting an approved Canonical Spec to implemented using evidence matched to Quick, restoration, Spec Delta, or plan-only work. Triggers: "완료", "검증", "다 됐어?", "확인해줘", "verify", "done", finishing any plan or fix.'
---

# Verifying Work

Announce once when first applied: "Using the forge verifying-work skill: matching fresh evidence to this work class before any completion claim."

Respond in the user's language. The discipline below applies in every language.

## Overview

Verification depth follows project authority, not artifact count. Quick work still needs fresh focused evidence. Restoring an existing Canonical contract needs the original reproduction and affected contract observation. For each bundle, its Canonical verification set is its Acceptance statements when any exist, otherwise its Requirement statements. Implementing an approved Spec Delta needs the affected set walked, and a new or never-implemented Canonical Spec needs the full set walked. An Execution Plan adds recovery and Task evidence but does not by itself raise or lower Canonical verification.

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
| Approved Spec Delta against an implemented baseline | every affected statement in the Canonical verification set passes plus regression command for unchanged behavior | `approved → implemented` after validation |
| New Canonical Spec or Delta against a never-implemented approved baseline | every statement in the Canonical verification set passes plus the full relevant suite | `approved → implemented` after validation |

Keep an applied Spec Delta through verification so its baseline lifecycle and affected statement links remain available. Remove it after evidence is recorded or promote it only as explicitly non-authoritative evidence.

## The Process

Reuse the existing work checklist. Add one item per required Canonical verification statement when needed; a focused Quick claim can use its command and observation directly without a separate five-stage checklist.

### 1. Identify the claim and work class

State the exact claim. Read route evidence from the forge using-forge classification, optional Change Brief or Spec Delta, Related Canonical Specs, and optional Execution Plan. If the classification is missing, reconstruct both axes from actual scope before verifying.

Treat a ready conversation draft or Change Brief as the claim boundary: its Goal and Done Checks say what must be proven, not that proof already exists. Inspect missing repository facts and run evidence yourself. Evidence gaps are failures or unknowns to resolve; they are not implementation-preference questions for the user.

Plan existence does not determine the class. A plan-only route can have no Canonical Spec, and spec-backed direct work can have no plan.

### 2. Run command-level verification now

1. Choose the command or concrete observation that proves the exact claim.
2. Run it and read the full output and exit code, or use already observed evidence tied to the same unchanged implementation, tests, inputs, and environment.
3. Count failures yourself. Remembered or worker-reported success without inspected output is not evidence. Root must review the worker diff and run fresh affected verification; an unchanged root-verified result need not be run again at handoff.
4. Compare actual output with the claim. Report disagreement directly.

| Claim | Required evidence | Not sufficient |
|---|---|---|
| Tests pass | Fresh test run, zero failures, exit 0 | earlier run or code review |
| Build succeeds | Fresh build, exit 0 | lint passing |
| Bug fixed | Original reproduction and regression command pass | changed code |
| Plan-only work complete | Every plan command and Done Check passes | Task boxes alone |
| Worker finished | Root diff review and fresh root verification | worker report |

### 3. Add Canonical contract evidence when required

For existing-contract restoration or approved Spec Delta work:

1. Inspect each governing bundle with `bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . inspect --spec <bundle-directory> --format json`. Require `forge/spec@3`, lifecycle `approved|implemented` appropriate to the class, and empty diagnostics.
2. Calculate each bundle's Canonical verification set: use every Acceptance statement when one or more exist; otherwise use every Requirement statement. Then select the required statements from the work class:
   - restoration: the statements whose approved behavior the fix restores;
   - Delta against an implemented baseline: the affected statements linked in the approved Delta, plus any statement whose observable outcome the change touches;
   - new Canonical Spec or never-implemented approved baseline: every statement in the bundle's Canonical verification set.
3. Create one checklist item per required verification statement, labeled with its member path and exact heading.
4. Walk each required statement in order: establish its precondition, perform its action, observe its expected outcome, and record `PASS` or `FAIL` with exact evidence. Code reading alone is not an observation.
5. When an Execution Plan exists, confirm its Related Specs coverage, completed Task verification, route evidence, and goal-level Done Checks agree with the actual implementation.

Unchanged statements from an implemented baseline retain their prior implementation evidence only when the approved Delta links every affected Requirement and Acceptance statement and a fresh regression command covers unchanged behavior. Any uncertainty expands the fresh statement set; it never shrinks it.

### 4. Handle failures

Name each failure as one of these:

- **Implementation bug:** actual behavior misses Canonical authority or the work claim → use the forge systematic-debugging skill, then restart verification.
- **Canonical Spec bug:** durable authority is wrong or incomplete → use the forge writing-specs skill in change mode, obtain approval, then restart verification.
- **Plan defect:** execution steps or coverage are mechanically wrong while Canonical meaning remains correct → make the smallest plan correction, record it, and rerun affected evidence.

Never change implementation and Canonical meaning silently in the same repair.

### 5. Complete the matching lifecycle

- **Quick, plan-only, restoration:** report evidence without changing Canonical Spec status.
- **Approved Spec Delta:** after the required Canonical verification set and regression evidence pass, set the Canonical Spec lifecycle `status` to `implemented`, update the current decision summary, and run the writer transaction. Git or validated transition evidence retains prior detail. A transaction failure blocks completion reporting.

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
| "The Delta links one statement, so indirect effects do not count." | Any touched observable outcome joins the required statement set. |
| "The baseline was implemented, so no fresh Canonical evidence is needed." | Changed contract meaning requires fresh affected-statement evidence. |
| "The plan passed, so the Canonical Spec is implemented." | Plan evidence and Canonical verification evidence have different authority. |
| "The worker reported success." | Root review and fresh root evidence remain mandatory. |
| "The deadline makes schema work Quick." | Misclassification is a routing failure, not a verification shortcut. |
| "I can say it should work." | Confidence and code reading are not execution evidence. |

## Handoff

**If evidence fails, route the named implementation, Canonical Spec, or plan defect and restart verification. If it passes, report only the claims the evidence proves; change Canonical lifecycle only for an approved Spec Delta with the required Canonical verification set complete.**
