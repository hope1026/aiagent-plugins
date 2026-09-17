---
name: verifying-work
description: 'Use when about to claim work complete, fixed, passing, or done; before commits or progress claims; and when converting an approved Canonical Spec to implemented using evidence matched to Quick, restoration, Spec Delta, or plan-only work. Triggers: "완료", "검증", "다 됐어?", "확인해줘", "verify", "done", finishing any plan or fix.'
---

# Verifying Work

Match evidence to the exact completion claim. Respond in the user's language. Confidence, code changes, a checkbox, or a worker summary alone do not prove a working result.

## Choose evidence

Use the request, affected contracts, and project checks to decide what must be observed. Choose an existing test, focused regression, build, type check, real execution, or rendered observation that actually demonstrates the claim. Add tests where they provide missing correctness or regression protection; do not mirror static content or add a framework only to satisfy a process.

Read the actual result and relevant output. A successful lint run does not prove a build or user interaction. For a defect, check the original symptom where feasible and relevant regression behavior. If reproduction is unavailable, describe the supported mitigation or remaining uncertainty rather than claiming a confirmed fix.

Reuse inspected evidence that applies to the same unchanged relevant source, implementation, tests, inputs, settings, and environment. New changes, failures, uncovered impact, or uncertainty require affected checks. A handoff or elapsed time alone does not require another run.

For worker results, inspect the diff or artifact and execution evidence, then confirm it applies to the integrated state. Run integration checks when that boundary is not covered. Do not simply repeat the worker's summary.

For visual quality, inspect the rendered reading or interaction path and representative affected viewports and states. Compare relevant peer roles and hierarchy. A build or one observed surface cannot prove unobserved UI. Detailed measurements are useful when diagnosing a discrepancy, not mandatory for every claim.

When verifying UI changes, read `references/ui-verification.md` for the affected interaction, state preservation, accessibility, and rendered checks. Apply only relevant cases; ordinary non-UI work does not need this reference.

## Contract and lifecycle claims

Read `references/canonical-verification.md` when evaluating affected Canonical statements or changing a bundle's status. Use the shared parser for structured bundle identity, status, and diagnostics; reuse valid context. Partial implementation, restoration, or plan completion does not by itself make the whole bundle implemented.

A contract conflict goes to the forge writing-specs skill; an uncertain implementation defect may need the forge systematic-debugging skill. Correct mechanical plan errors within the authorized scope. Do not silently change a contract to make the result pass.

## Finish

Stop after the exact claim, affected contracts, and required project gates are proven. Report the result, meaningful evidence, and limitations in the existing work record. Ordinary completion needs no work-class form or statement-by-statement report when the evidence is clear.

For requested Forge visualizations, check source fidelity and the actual delivered surface at the scale of the document. Only managed renderer output needs its build checks; a reproducible tracked Project Handbook also needs freshness and repository validation. Generated views remain derived outputs, and source changes alone do not authorize refresh.
