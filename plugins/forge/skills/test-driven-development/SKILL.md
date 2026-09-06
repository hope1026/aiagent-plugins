---
name: test-driven-development
description: 'Use when implementing testable logic, behavior changes, or behavioral bugfixes before writing their implementation. Triggers: "TDD", "테스트 먼저", "테스트 작성", "로직 구현", "동작 버그", new functions, behavioral regression.'
---

# Test-Driven Development

**Announce once when first applied:** "Using the forge test-driven-development skill to prove the behavior before changing it."

Respond in the user's language. This skill file stays in English.

## Overview

For testable behavior, write a focused test, observe its expected failure, implement the smallest fix, then verify and refactor. Tests protect observable results and contract boundaries. They do not exist to reproduce implementation details or satisfy a quota.

## Iron Law

```text
NEW LOGIC AND BEHAVIORAL FIXES NEED AN OBSERVED FAILING TEST BEFORE IMPLEMENTATION.
VERIFICATION MUST PROVE THE CHANGED BEHAVIOR.
```

## When to Use / When NOT

Use for new logic, behavioral bugs, behavior changes, and refactoring that needs missing regression protection, through direct or planned routes.

Use a smaller direct check for:

- prose, labels, and presentation-only styling: inspect the actual changed output;
- logic-free configuration: parse, validate, build, or exercise the affected setting;
- generated output: test its source or generator when those change;
- disposable exploration: record what was learned and verify any code promoted into implementation.

Do not install a test framework just to assert a label, CSS value, or static file content. If a UI change adds interaction or state logic, test that behavior. Choose from the actual change; ordinary verification choices do not need user approval.

## The Process

Reuse the work's checklist. Track each independently testable behavior, not another six-item checklist for every cycle.

### 1. RED — capture the expected outcome

Use the project's existing runner and real code paths. One focused test should expose the missing behavior or defect.

```python
def test_retry_stops_at_three_failed_attempts():
    attempts = []
    def operation():
        attempts.append(1)
        raise TemporaryError()
    with pytest.raises(TemporaryError):
        retry(operation, max_attempts=3)
    assert len(attempts) == 3
```

Run it and read the failure. A typo, missing dependency, or broken test setup is not behavioral evidence. Establish the callable boundary first if needed, then make the assertion fail for the intended reason. If the test already passes, investigate whether existing behavior satisfies the request; do not change correct code to manufacture RED.

### 2. GREEN — implement the behavior

Write the smallest complete change. Keep unrelated cleanup out of the fix. Run the focused test and the relevant existing regression tests. Change a test only when its expectation is wrong against the approved contract, not to make a defect disappear.

### 3. Refactor and verify the affected scope

Clean up only after GREEN. Rerun tests affected by the refactor. Expand to the relevant integration or full suite when shared interfaces, dependency changes, broad impact, uncertain coverage, or repository policy requires it.

Evidence from the current unchanged relevant source, implementation, tests, inputs, settings, and environment can support the final claim; do not rerun an identical suite merely because another skill is handing off. New relevant changes, failures, uncovered impact, or environment drift require affected evidence. Stop after the changed behavior, affected regression boundary, and required project gates pass.

### 4. Record the result

Keep the regression test with the implementation. Record the command and outcome in the existing work evidence. Commit at the work or plan's checkpoint when authorized; a RED/GREEN cycle does not require its own commit.

### Existing or prematurely written implementation

Preserve user work. If implementation was written before the regression test, isolate that change and demonstrate that the test fails against the previous behavior and passes against the fix. A temporary worktree, reversible patch, or controlled fault can establish this. Do not delete and rewrite correct code solely to reenact the sequence, and do not claim test-first evidence that was not observed.

### Bugfixes

Use the forge systematic-debugging skill to establish the root cause, then encode the reproduction. The regression must fail under the original fault and pass after the fix. A presentation-only defect may be proven by focused rendered comparison without installing a new runner.

## Working Files

Tests belong in the project's test tree. Direct work needs no Execution Plan. Planned work uses its existing Task and progress record. Keep disposable reproduction tools in `.forge/scratch/`; promote useful root-cause evidence to `docs/debug/`.

Read `references/testing-anti-patterns.md` when using mocks, snapshots, or asynchronous tests. Mock boundaries you do not own, assert outcomes, and wait on real conditions.

## Red Flags

| Pressure | Response |
|---|---|
| "This logic is too small to test." | Small logic still needs a focused behavioral test. |
| "The deadline permits skipping regression evidence." | Preserve the reproduction and prove the fix in the smallest relevant scope. |
| "The CSS value needs a new testing framework." | Observe the rendered result; tests should add protection, not mirror a constant. |
| "The test already passes, so it proves nothing." | It may prove existing behavior. Investigate before changing implementation. |
| "Delete the existing code to call this TDD." | Preserve work and demonstrate the regression against the previous behavior. |
| "Every cycle must rerun the whole repository." | Broaden verification when risk or dependency reach requires it. |
| "The mocks were called, so the feature works." | Exercise the owned behavior and inspect its observable result. |

## Handoff

Return to the current direct route or the forge executing-plans skill. Use the forge verifying-work skill before claiming completion, reusing valid evidence from the same unchanged state.
