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
- Setting structured spec frontmatter `status` to `implemented` (this skill is the ONLY workflow permitted to set that value).
- Accepting a subagent's success report.

**NOT needed for:** neutral in-progress narration that claims nothing, answering questions that assert nothing about work state, or a fixed Review Viewer snapshot whose one requested build already succeeded. Review Viewer tooling changes still require full verification.

## The Process

Verification has two levels. Level 1 applies to implementation work. Level 2 additionally applies whenever that work traces to a spec. A fixed requested Review Viewer snapshot is handled by the exception below.

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

#### Fixed Review Viewer generation exception

Generating `.forge/reviews/<review-id>/view.html` from unchanged `review-viewer` tooling after explicit user intent to create or refresh a Review Viewer is read-only assembly. The agent resolves source, mode, and review-id from current context. The successful single build is sufficient evidence; do not add a second checker, browser, screenshot, layout, interaction, Mermaid, or freshness run.

This exception is artifact-specific. Review Viewer tooling changes use `web-app-design` plus normal Level 1 and every governing Level 2 AC. A snapshot never changes structured spec frontmatter status.

### Level 2 — spec-level verification (when a spec exists)

1. Run `bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . inspect --spec docs/specs/NNN-<slug>/spec.md --format json`. Require `schema` = `forge/spec@2`, lifecycle `status` in `approved|implemented`, and empty `diagnostics`, then read the typed acceptance array.
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

1. Set the spec frontmatter `status` to `implemented`. This value is set only by this skill at this point.
2. Run the same Markdown-only source transaction used by the writer. A failure blocks handoff and completion reporting:
   `spec-docs.sh --repo-root . validate --root docs/specs --baseline-ref HEAD`.
3. Report the AC table to the user only after validation passes.

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
- Writes: structured spec frontmatter `status: implemented`, only after all ACs pass. The AC report goes to the user in chat.

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
| "I'll set implemented now, verify after" | Frontmatter status changes only after evidence and is incomplete until Markdown validation passes. |
| "That AC obviously passes" | The "obvious" AC is where regressions hide. Walk it like every other one. |
| "No spec exists, so Level 1 is enough" | Only if the change is on the ceremony-floor exemption list. A missing spec for behavior-changing work is a gap to close via the forge writing-specs skill, not a shortcut. |
| "The generated View needs the full completion checklist." | Successful assembly is enough for this convenience artifact. Full verification belongs to Viewer tooling changes, not each generated file. |
| "I can say the generated layout is verified because the build passed." | Build success proves generation only. Report the artifact without an independent layout claim. |

## Handoff

**If any AC failed: use the forge systematic-debugging skill for a code bug or the forge writing-specs skill in change mode for a spec bug, then re-verify from Level 1. If all ACs passed: set frontmatter `status: implemented`, complete the Markdown validation transaction, and only then report the AC table.**
