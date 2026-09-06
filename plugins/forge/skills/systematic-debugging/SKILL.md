---
name: systematic-debugging
description: 'Use when encountering any bug, test failure, error, or unexpected behavior, before proposing or applying any fix. Triggers: "버그", "디버깅", "에러", "원인", "안 돼", "이상해", test failures, crashes, wrong output.'
---

# Systematic Debugging

**Announce once when first applied:** "Using the forge systematic-debugging skill to find the root cause before fixing."

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
- structured spec validation failures and Visual Docs tooling failures; first reproduce whether source, parser, planner, asset, or runtime state diverged

**Use ESPECIALLY when:**

- You are under time pressure — guessing feels fast and is slow
- The fix "seems obvious"
- A previous fix did not work
- You have already tried two or more fixes

**Do NOT use for:**

- New feature work with no misbehavior — return to the forge using-forge route; only durable contract changes use the forge writing-specs skill
- A test you just wrote failing as expected — that is the RED step of the forge test-driven-development skill working correctly

## The Process

Reuse the work checklist and keep reproduction, isolation, root cause, and verification evidence. For a bounded defect, the same focused observation can satisfy several phases; do not expand one-line findings into separate forms. Complex investigations need explicit recovery notes.

### Phase 1: Reproduce

Goal: a minimal, deterministic reproduction.

1. Read the complete error message and stack trace — every line, not the first line. Note file paths, line numbers, error codes. The answer is often already printed.
2. Trigger the failure yourself. Record the exact steps or command.
3. Shrink the reproduction: remove inputs, steps, and setup until removing anything more makes the bug disappear.
4. Make it deterministic. If it only fails sometimes, find what varies (timing, ordering, environment, data) until it fails every run — or capture enough logging to make each failure informative.

**Exit criterion:** one command or short procedure that reliably shows the bug. If you cannot reproduce it, gather more evidence — logs, inputs, environment diffs, recent changes. Never fix what you cannot reproduce.

Use the reproduction and repository inspection to resolve technical facts before asking the user. If the desired fixed outcome or material scope remains a user-owned choice, stop before fix mutation and return to Brief clarification through the forge using-forge skill. A missing framework, path, version, or current behavior that the repository can reveal is not a user question.

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

1. **Classify the fix before mutation.** Compare the root cause and intended outcome with every relevant approved or implemented Canonical Spec. Restoring approved behavior, or fixing a local implementation detail whose complete intent stays in code and tests, has `Canonical Spec impact: no`. Changing durable contract meaning has impact `yes` and requires an approved Spec Delta through the forge writing-specs skill.
2. **Classify execution complexity.** A bounded, reversible fix with strong focused verification proceeds directly. Multiple dependent components, migration or release ordering, meaningful rollback risk, or interruption recovery requires the forge writing-plans skill. Record both axes.
3. Fix the cause, not the symptom. If the wrong value originates three calls up, fix it there — do not pad the crash site with guards.
4. Write the regression test first, using the forge test-driven-development skill: the test encodes the reproduction, fails before the fix, passes after.
5. Apply ONE change. No bundled refactoring, no "while I'm here" improvements.
6. Confirm the original reproduction now passes, the affected Canonical contract matches when present, and relevant regression behavior is protected. One focused execution may prove all three when it exercises the contract boundary. Broaden the suite for shared interfaces, concrete uncertain impact, or repository policy, then stop when the fix claim and affected scope are proven.
7. If the fix does not work: STOP. Count your attempts. Fewer than three → return to Phase 1 with the new information. Three or more failed fixes → stop automatic patching and re-examine the architecture and evidence. Ask the user only if that investigation reaches a product, scope, or new-authority decision.

**Exit criterion:** fix class recorded; original reproduction passes; affected Canonical contract matches when present; regression evidence recorded; relevant suite green.

## Working Files

- Keep active investigation notes, reproduction scripts, and instrumentation experiments in `.forge/scratch/` (gitignored).
- A clear investigation does not need a Change Brief file. Use `.forge/work/<work-id>/brief.md` only when resumption, delegation, scope coordination, or explicit user review needs independent work input.
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
| "One more fix attempt" (after 2+ failures) | Repeated failures mean the mental model is wrong. Three or more → re-examine the architecture; ask only for a user-owned decision. |
| "The bug changes behavior, so it always needs a new spec" | Restoration changes implementation behavior without changing Canonical authority. Compare the intended contract first. |
| "It is only a bugfix, so it can never change the spec" | A root cause may expose a wrong durable contract. That result requires a Spec Delta before the fix changes authority. |
| "I cannot reproduce yet, so I should ask which framework this uses." | Read the repository and runtime evidence first. Ask only when the desired outcome or material scope is a user-owned blocking choice. |

## Handoff

**Root cause fixed and regression test in place. Next: the forge verifying-work skill — confirm with fresh evidence before claiming the bug is fixed.**
