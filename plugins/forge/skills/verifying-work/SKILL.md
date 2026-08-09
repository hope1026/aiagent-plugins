---
name: verifying-work
description: 'Use when about to claim work complete, fixed, passing, or done; before commits or progress claims; and when converting an approved Canonical Spec to implemented using evidence matched to Quick, restoration, Spec Delta, or plan-only work. Triggers: "완료", "검증", "다 됐어?", "확인해줘", "verify", "done", finishing any plan or fix.'
---

# Verifying Work

Announce at start: "Using the forge verifying-work skill: matching fresh evidence to this work class before any completion claim."

Respond in the user's language. The discipline below applies in every language.

## Overview

Verification depth follows project authority, not artifact count. Quick work still needs fresh focused evidence. Restoring an existing Canonical contract needs the original reproduction and affected contract observation. Implementing an approved Spec Delta needs the affected AC walk, and a new Canonical Spec needs every AC walked. An Execution Plan adds recovery and Task evidence but does not by itself raise or lower Canonical verification.

## Iron Law

```text
NO COMPLETION CLAIM WITHOUT FRESH EVIDENCE MATCHED TO THE WORK CLASS.
NO CANONICAL SPEC STATUS CHANGE WITHOUT THE REQUIRED AC EVIDENCE.
```

## When to Use / When NOT

**Use before:**

- any statement that work is complete, fixed, passing, working, or done;
- committing, reporting progress, accepting worker results, or moving to the next Execution Plan Task;
- setting Canonical Spec lifecycle `status: implemented`.

**NOT needed for:** neutral in-progress narration that claims nothing, answering questions that assert nothing about work state, or one fixed Review Viewer build handled by the exception below.

## Work-class Matrix

| Work class | Required fresh evidence | Canonical lifecycle effect |
|---|---|---|
| Quick | focused test, build, lint, type check, real run, or observation that directly proves the claim | none |
| Plan-only | every plan verification command and goal-level Done Check | none |
| Existing-contract restoration | original reproduction now passes, affected Canonical contract observation matches, regression command passes | none |
| Approved Spec Delta against an implemented baseline | every affected AC passes plus regression command for unchanged behavior | `approved → implemented` after validation |
| New Canonical Spec or Delta against a never-implemented approved baseline | every AC passes plus the full relevant suite | `approved → implemented` after validation |

Keep an applied Spec Delta through verification so its baseline lifecycle and affected R and AC IDs remain available. Remove it after evidence is recorded or promote it only as explicitly non-authoritative evidence.

## The Process

Create one checklist item per applicable numbered stage below, plus one item per required Canonical AC. Do not collapse several ACs into one memory-only judgment.

### 1. Identify the claim and work class

State the exact claim. Read route evidence from the forge using-forge classification, optional Change Brief or Spec Delta, Related Canonical Specs, and optional Execution Plan. If the classification is missing, reconstruct both axes from actual scope before verifying.

Treat a ready conversation draft or Change Brief as the claim boundary: its Goal and Done Checks say what must be proven, not that proof already exists. Inspect missing repository facts and run evidence yourself. Evidence gaps are failures or unknowns to resolve; they are not implementation-preference questions for the user.

Plan existence does not determine the class. A plan-only route can have no Canonical Spec, and spec-backed direct work can have no plan.

### 2. Run command-level verification now

1. Choose the command or concrete observation that proves the exact claim.
2. Run it now and read the full output and exit code.
3. Count failures yourself. Cached, remembered, and worker-reported results count as no evidence.
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

1. Inspect each governing source with `bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . inspect --spec <path> --format json`. Require `forge/spec@2`, lifecycle `approved|implemented` appropriate to the class, and empty diagnostics.
2. Determine the AC set from the work class:
   - restoration: the ACs whose approved behavior the fix restores;
   - Delta against an implemented baseline: the affected ACs named in the approved Delta, plus any AC whose observable outcome the change touches;
   - new Canonical Spec or never-implemented approved baseline: every AC.
3. Create one checklist item per required AC.
4. Walk each required AC in order: establish its precondition, perform its action, observe its expected outcome, and record `PASS` or `FAIL` with exact evidence. Code reading alone is not an observation.
5. When an Execution Plan exists, confirm its Related Specs coverage, completed Task verification, route evidence, and goal-level Done Checks agree with the actual implementation.

Unchanged ACs from an implemented baseline retain their prior implementation evidence only when the approved Delta names every affected R and AC and a fresh regression command covers unchanged behavior. Any uncertainty expands the fresh AC set; it never shrinks it.

### 4. Handle failures

Name each failure as one of these:

- **Implementation bug:** actual behavior misses Canonical authority or the work claim → use the forge systematic-debugging skill, then restart verification.
- **Canonical Spec bug:** durable authority is wrong or incomplete → use the forge writing-specs skill in change mode, obtain approval, then restart verification.
- **Plan defect:** execution steps or coverage are mechanically wrong while Canonical meaning remains correct → make the smallest plan correction, record it, and rerun affected evidence.

Never change implementation and Canonical meaning silently in the same repair.

### 5. Complete the matching lifecycle

- **Quick, plan-only, restoration:** report evidence without changing Canonical Spec status.
- **Approved Spec Delta:** after the required AC set and regression evidence pass, set the Canonical Spec to `implemented`, append the verification history entry, and run the writer transaction. A transaction failure blocks completion reporting.

The report names work class, claim, command evidence, and required AC verdicts:

```markdown
Work class: Existing-contract restoration
Claim: Refresh retries no longer duplicate writes.

| AC | Verdict | Evidence |
|---|---|---|
| AC3 | PASS | `pytest tests/test_refresh.py -q` → 7 passed, exit 0 |
```

## Fixed Review Viewer Exception

After explicit user intent, one successful build of `.forge/reviews/<review-id>/view.html` from unchanged review-viewer tooling proves generation only. Do not add a second checker, browser, screenshot, layout, interaction, Mermaid, or freshness run. Review Viewer tooling changes use normal command and Canonical evidence.

## Working Files

- Reads: optional `.forge/work/<work-id>/brief.md` and `spec-delta.md`; Related Canonical Specs; optional Execution Plan, progress, and Task files.
- Writes: Canonical Spec lifecycle `status: implemented` and history only after the required AC evidence passes; evidence goes to the user, plan progress, or an explicitly durable evidence path.

## Red Flags

| Excuse | Reality |
|---|---|
| "Quick means no tests." | Quick removes formal artifacts, not fresh proof. |
| "There is no spec, so verification is impossible." | Focused commands and plan Done Checks verify non-SOT work. |
| "The Brief says done, so the evidence can be inferred." | A ready Brief defines the claim. Only fresh commands and observations prove it. |
| "Every spec AC must run for this one restored branch." | Restoration verifies the affected contract and regression behavior without changing lifecycle status. |
| "The Delta names one AC, so indirect effects do not count." | Any touched observable outcome joins the required AC set. |
| "The baseline was implemented, so no fresh AC is needed." | Changed contract meaning requires fresh affected-AC evidence. |
| "The plan passed, so the Canonical Spec is implemented." | Plan evidence and Canonical AC evidence have different authority. |
| "The worker reported success." | Root review and fresh root evidence remain mandatory. |
| "The deadline makes schema work Quick." | Misclassification is a routing failure, not a verification shortcut. |
| "I can say it should work." | Confidence and code reading are not execution evidence. |

## Handoff

**If evidence fails, route the named implementation, Canonical Spec, or plan defect and restart verification. If it passes, report only the claims the evidence proves; change Canonical lifecycle only for an approved Spec Delta with the required AC set complete.**
