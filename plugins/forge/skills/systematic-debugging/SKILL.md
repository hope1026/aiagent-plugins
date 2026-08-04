---
name: systematic-debugging
description: 'Use when encountering any bug, test failure, error, or unexpected behavior, before proposing or applying any fix. Triggers: "버그", "디버깅", "에러", "원인", "안 돼", "이상해", test failures, crashes, wrong output.'
---

# Systematic Debugging

**Announce at start:** "Using the forge systematic-debugging skill to find the root cause before fixing."

Respond to the user in the user's language. This skill file stays in English.

## Overview

Random fixes waste time and create new bugs. A patch that makes a symptom disappear without an understood cause is a failure, not a fix — the bug returns wearing a different symptom. This skill enforces four phases — Reproduce, Isolate, Root-cause, Fix + verify — and forbids writing any fix until the first three are complete.

## Iron Law

```
NO FIX WITHOUT A REPRODUCED, UNDERSTOOD ROOT CAUSE.
```

If you cannot state the root cause in one sentence AND show a reproduction that confirms it, you may not propose or apply a fix. No exceptions for "obvious" bugs, emergencies, or one-line patches.

## When to Use / When NOT

**Use for ANY technical misbehavior:**

- Test failures, crashes, wrong output
- Unexpected behavior, flaky runs, performance cliffs
- Build failures, integration failures
- structured spec validation failures and Review Viewer tooling failures; first reproduce whether source, parser, planner, asset, or runtime state diverged

**Use ESPECIALLY when:**

- You are under time pressure — guessing feels fast and is slow
- The fix "seems obvious"
- A previous fix did not work
- You have already tried two or more fixes

**Do NOT use for:**

- New features or behavior changes — that is the forge writing-specs skill
- A test you just wrote failing as expected — that is the RED step of the forge test-driven-development skill working correctly

## The Process

Before starting, create one todo per phase below and complete them strictly in order. A phase is done only when its exit criterion is met — never skip ahead to the fix.

### Phase 1: Reproduce

Goal: a minimal, deterministic reproduction.

1. Read the complete error message and stack trace — every line, not the first line. Note file paths, line numbers, error codes. The answer is often already printed.
2. Trigger the failure yourself. Record the exact steps or command.
3. Shrink the reproduction: remove inputs, steps, and setup until removing anything more makes the bug disappear.
4. Make it deterministic. If it only fails sometimes, find what varies (timing, ordering, environment, data) until it fails every run — or capture enough logging to make each failure informative.

**Exit criterion:** one command or short procedure that reliably shows the bug. If you cannot reproduce it, gather more evidence — logs, inputs, environment diffs, recent changes. Never fix what you cannot reproduce.

### Phase 2: Isolate

Goal: shrink the search space until the fault has nowhere left to hide.

1. **Bisect layers:** in a multi-component path (UI → API → service → storage; CI → build → deploy), log what enters and exits each boundary. Run the reproduction once and find the first boundary where data goes wrong.
2. **Bisect inputs:** halve the failing input until you have the smallest input that still fails.
3. **Bisect time:** check recent changes — diffs, commits, dependency and config updates. Version-control bisection finds the breaking change mechanically.
4. **Instrument and read ACTUAL values.** Print the real runtime values at suspect points. Do not reason from what a value "should" be — look at what it is.

**Exit criterion:** the failure is localized to one component, one change, or one code path.

### Phase 3: Root-cause

Goal: the first wrong state and why it happened.

1. Trace backward from the symptom to the first wrong state — the earliest point where data or control flow diverged from correct. Read `references/root-cause-tracing.md` in this skill directory for the full technique.
2. Ask "why" repeatedly (five times is the classic depth) until the answer is a decision, assumption, or defect — not another symptom.
3. State one specific hypothesis: "X is the root cause because Y."
4. Verify it both ways: the hypothesis must make the symptom **appear** (trigger the condition → bug shows) AND **disappear** (neutralize only that condition → bug gone). One direction is coincidence; both is causation.
5. If the hypothesis fails, form a new one from what you learned. Do not stack a second guess on top of the first.

**Exit criterion:** a one-sentence root cause, confirmed in both directions.

### Phase 4: Fix + verify

Goal: the cause is fixed, proven, and guarded against regression.

1. Fix the cause, not the symptom. If the wrong value originates three calls up, fix it there — do not pad the crash site with guards.
2. Write the regression test first, using the forge test-driven-development skill: the test encodes the reproduction, fails before the fix, passes after.
3. Apply ONE change. No bundled refactoring, no "while I'm here" improvements.
4. Confirm the original reproduction from Phase 1 now passes, and the rest of the test suite still passes.
5. If the fix does not work: STOP. Count your attempts. Fewer than three → return to Phase 1 with the new information. Three or more failed fixes → the problem is likely architectural; stop fixing and discuss the design with the user before any further attempt.

**Exit criterion:** original reproduction passes, regression test committed, suite green.

## Working Files

- Keep active investigation notes, reproduction scripts, and instrumentation experiments in `.forge/scratch/` (gitignored).
- When a non-trivial root cause is worth sharing or preserving, promote it to `docs/debug/YYYY-MM-DD-<slug>.md` with exactly these sections: **Symptom**, **Reproduction**, **Root cause**, **Fix**, **Regression test path**.

## Red Flags

If you catch yourself thinking any of these, STOP and return to Phase 1.

| Excuse | Reality |
|--------|---------|
| "I see the problem, quick fix" | Seeing a symptom is not understanding a cause. Quick fixes on guesses create second bugs. |
| "It's probably X, let me try" | "Probably" means unverified. Test the hypothesis both ways before touching code. |
| "Adding a null check should do it" | A guard at the crash site hides where the bad value came from. Trace to the source. |
| "Can't reproduce, but the fix looks right" | An unreproduced fix is unverifiable — you cannot know it worked. Reproduce first. |
| "This is urgent, no time for process" | Systematic debugging is faster than guess-and-check thrashing. Emergencies are when guessing costs most. |
| "The issue is too simple for all this" | Simple bugs have root causes too, and the process is fast on simple bugs. |
| "One more fix attempt" (after 2+ failures) | Repeated failures mean the mental model is wrong. Three or more → question the architecture with the user. |

## Handoff

**Root cause fixed and regression test in place. Next: the forge verifying-work skill — confirm with fresh evidence before claiming the bug is fixed.**
