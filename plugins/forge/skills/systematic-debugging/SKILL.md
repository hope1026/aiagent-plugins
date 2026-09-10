---
name: systematic-debugging
description: 'Use when a defect, recurring test failure, or unexpected behavior needs evidence-based investigation. Triggers: "버그", "디버깅", "에러 원인", "안 돼", "이상해", intermittent failures, uncertain root cause.'
---

# Systematic Debugging

Find enough evidence to explain the defect and verify an appropriate correction. Respond in the user's language. A simple defect can be resolved with one focused observation; it needs no separate phase record.

## Investigate

Read the relevant error, code, inputs, and recent changes. Reproduce the failure when feasible. For intermittent or production-only failures, use logs, traces, environment comparisons, or a controlled experiment; lack of local reproduction does not prohibit a supported proposal or an authorized mitigation.

Form a specific hypothesis and choose evidence that could refute it. Narrow inputs, inspect actual values, trace boundaries, or bisect changes where useful. `references/root-cause-tracing.md` offers an optional tracing technique. No fixed phase count or universal two-way experiment is required.

Resolve repository facts yourself. Ask only if the intended outcome, scope, or authority remains a user-owned decision. If repeated attempts add no evidence, reconsider the hypothesis and method rather than retrying a fixed number of patches.

## Correct and verify

Compare the intended result with the approved contract. Restore it within the existing authorization; use the forge writing-specs skill if durable meaning must change. Preserve unrelated user work and keep the change focused on the cause or explicitly identified mitigation.

Use existing checks and add regression protection where needed. A failing regression before the fix is often the clearest evidence; the forge test-driven-development skill can help when test-first work is appropriate. Test order is not a substitute for a meaningful expectation.

Verify the original symptom when possible, the affected contract, and relevant regression behavior. One check can cover several of these. For a mitigation, state what improved and what remains unresolved; do not report the root cause fixed without evidence. Reuse valid observed evidence and expand checks for concrete uncovered risk.

Keep useful investigation and recovery notes in the existing work record. Disposable probes belong in `.forge/scratch/`; promote a root cause to `docs/debug/` when it will help future work. No fixed report sections are required.
