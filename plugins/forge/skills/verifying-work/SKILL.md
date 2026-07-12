---
name: verifying-work
description: 'Use when about to claim work is complete, fixed, passing, or done - before committing, creating PRs, reporting progress, or setting a spec to implemented. Triggers: "완료", "검증", "다 됐어?", "확인해줘", "verify", "done", finishing any plan or fix.'
---

# Verifying Work

Announce at start: "Using the forge verifying-work skill: gathering fresh evidence before any completion claim."

Respond to the user in the user's language. The discipline below applies in every language.

## Overview

Claiming work is complete without verification is dishonesty, not efficiency. Every "done", "fixed", or "passing" — in any wording, including paraphrases and implied satisfaction — must be backed by evidence produced in the current moment, and spec-driven work must be walked against the spec's acceptance criteria one by one.

## Iron Law

```
NO COMPLETION CLAIM WITHOUT FRESH VERIFICATION EVIDENCE. EVIDENCE BEFORE ASSERTIONS, ALWAYS.
```

Violating the letter of this law is violating its spirit. Rewording a claim ("should be good now", "looks complete") does not exempt it.

## When to Use / When NOT

**Use before:**

- Any statement that work is complete, fixed, passing, working, or done — exact words, synonyms, or implication.
- Committing, creating a PR, reporting progress, or moving to the next plan task.
- Setting a spec's `Status:` to `implemented` (this skill is the ONLY thing permitted to set that value).
- Accepting a subagent's success report.

**NOT needed for:** neutral in-progress narration that claims nothing ("running the tests now"), or answering questions that assert nothing about work state.

## The Process

Verification has two levels. Level 1 always applies. Level 2 additionally applies whenever the work traces to a spec.

### Level 1 — command-level verification (always)

1. **Identify** the command that proves the claim: build, test suite, lint, type check, or a real run of the changed behavior.
2. **Run it NOW in the shell** — the full command, fresh. Cached results, remembered output, and runs from earlier in the session count as nothing.
3. **Read the full output.** Check the exit code. Count the failures yourself instead of skimming for a green word.
4. **Compare output to claim.** If they disagree, state the actual status with the evidence — never soften or defer the bad news.
5. **Only then** make the claim, and include the evidence with it.

| Claim | Requires | Not sufficient |
|---|---|---|
| Tests pass | Fresh test run: 0 failures, exit 0 | An earlier run, "should pass" |
| Build succeeds | Fresh build: exit 0 | Lint passing, logs looking fine |
| Bug fixed | Original reproduction now passes | Code changed, fix assumed |
| Subagent finished | You inspected the diff and re-ran checks | The subagent's own report |
| Requirements met | Level 2 walk below | Tests passing alone |

#### Viewer-only Level 1 scope

A Viewer-only change alters a read-only review artifact or its presentation without changing product behavior. Verify it separately from product implementation:

1. Exactly six fragment panels exist in the required order.
2. Task, Step, AC, and Mermaid counts equal their sources; include R count when the mode displays requirements.
3. Every source Mermaid block is byte-for-byte identical to its governing source.
4. Unresolved placeholders are 0 and fragment shell markup is 0.
5. At 1440px and 390px, tabs, Task/R/AC deep links, table and diagram scroll, and print layout behave correctly.
6. Mermaid errors are 0 for valid fixtures; an invalid fixture shows its error location and original source.
7. AC and Step checkbox states persist independently after reload.
8. Offline output makes no external Mermaid request and renders the same diagrams.

Record these as Level 1 evidence. Viewer-only PASS never changes the governing product spec to `Status: implemented`, because the Viewer does not implement product behavior. When the Viewer implementation itself has a governing spec, that implementation still requires the full Level 2 walk against its own ACs.

### Level 2 — spec-level verification (when a spec exists)

1. Open `docs/specs/NNN-<slug>/spec.md` and read the Acceptance Criteria section.
2. Create one todo per acceptance criterion (AC1..ACn) so none can be silently skipped.
3. **Check route evidence** in the plan's `Progress History` and optional `progress.md`: every executed Task records tier, execution mode, parallel group or `none`, verification, and commit scope. For subagent work, confirm the root agent inspected the result and produced fresh verification; a worker report alone is not acceptance evidence.
4. Walk each AC in order: reproduce its precondition, perform its action, and observe its expected outcome against the real implementation. Record a verdict — **PASS** or **FAIL** — with the exact command output or concrete observation as evidence. No AC may be judged from memory or from reading the code.
5. Cross-check consistency: each AC still maps to current R-IDs, and each related plan under `docs/plans/` has a coverage table matching what was built. A dangling AC or uncovered requirement is a FAIL to resolve, not a footnote.

### Verdict handling

Any AC FAIL means exactly one of two things, and you must name which:

- **Code bug** — the implementation does not meet the spec → fix it via the forge systematic-debugging skill, then redo the walk from Level 1.
- **Spec bug** — the requirement itself is wrong or outdated → propose a delta via the forge writing-specs skill in change mode and get the user's approval, then re-verify.

One of the two must change, explicitly. Never adjust both silently, and never re-interpret an AC until it passes.

### Completion

Only after **every** AC records PASS with evidence for the actual implementation governed by that spec:

1. Set the spec's `Status:` line to `implemented`. This value is set only by this skill, only at this point.
2. Report the AC table to the user.

If no spec exists, first confirm the change is genuinely on the ceremony-floor exemption list (typo/comment/formatting, no-API dependency bump, non-output CI config, behavior-preserving refactor with passing tests). Only then does Level 1 alone gate the claim — and say explicitly that verification was command-level only. If the work altered behavior and has no spec, that is a process gap: route to the forge writing-specs skill before any completion claim, never around it.

### Report format

```
| AC | Verdict | Evidence |
|----|---------|----------|
| AC1 | PASS | `npm test` → 42/42 passed, exit 0 |
| AC2 | FAIL | POST /login returned 500, expected 201 (output attached) |
```

## Working Files

- Reads: every related `docs/specs/NNN-<slug>/spec.md` and the current `docs/plans/PPP-<slug>/plan.md`, plus optional `progress.md` and `tasks/*.md`.
- Writes: the `Status: implemented` line in `docs/specs/NNN-<slug>/spec.md` — only after all ACs PASS. The AC report goes to the user in chat, not to a file.

## Red Flags

| Excuse | Reality |
|---|---|
| "Tests passed earlier" | Earlier is not now — the code has changed since. Run them again. |
| "The diff looks right" | Reading code is not running it. Correct-looking code fails constantly. |
| "I'm confident it works" | Confidence is not evidence. Run the command. |
| "User is waiting, skip the rerun" | A false "done" costs far more of their time than one rerun. |
| "The subagent reported success" | A report is a claim, not evidence. Inspect the diff and re-run the checks yourself. |
| "The Task passed, so route evidence is optional." | Adaptive execution must remain auditable. Record tier, mode, group, verification, and root review before using the Task as AC evidence. |
| "Lint is clean, so it builds" | A linter is neither a compiler nor a test suite. |
| "I'll set implemented now, verify after" | Status is the gate token. It flips only after the evidence exists. |
| "That AC obviously passes" | The "obvious" AC is where regressions hide. Walk it like every other one. |
| "No spec exists, so Level 1 is enough" | Only if the change is on the ceremony-floor exemption list. A missing spec for behavior-changing work is a gap to close via the forge writing-specs skill, not a shortcut. |
| "The Viewer checklist passed, so the product spec is implemented." | Viewer-only evidence proves the review artifact, not product behavior. Leave the product status unchanged. |
| "Desktop is enough for a read-only document." | Wide diagrams and tables fail differently at 390px. Viewer verification always includes both widths. |

## Handoff

**If any AC failed: the next step is the forge systematic-debugging skill (code bug) or the forge writing-specs skill in change mode (spec bug) — then return here and re-verify from Level 1. If all ACs passed: set the spec `Status: implemented`, report the AC table to the user — the lifecycle is complete.**
