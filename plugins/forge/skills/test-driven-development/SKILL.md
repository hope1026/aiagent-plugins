---
name: test-driven-development
description: 'Use when the user or project requires TDD, or when a test-first experiment is useful for a defined behavior or reproducible regression. Triggers: "TDD", "테스트 먼저", "실패 테스트", test-first development.'
---

# Test-Driven Development

Use test-first development when it helps establish behavior before implementation. Respond in the user's language. Ordinary logic changes may use appropriate existing tests and add missing regression protection without this workflow.

## Apply the method

Define an observable expectation from the request or approved contract. Use the project's runner and real owned code paths. Write a focused test, observe that it fails for the intended behavioral reason, implement the complete requested behavior, then run the affected checks. Refactor when useful and recheck what changed.

A broken import or setup failure is not behavioral evidence. If the test already passes, investigate whether the request is already satisfied; do not break correct behavior to manufacture a failure. Change an expectation only when it is wrong against the intended contract, never to hide a defect.

Preserve existing implementation and user changes. When code predates its test, a previous revision, reversible patch, or controlled fault may establish regression sensitivity. Do not delete and rewrite correct code merely to reenact test-first order, or claim a sequence that did not happen.

Tests should protect outcomes and contract boundaries. Avoid tests that copy constants or implementation details. Prose, styling, generated output, and logic-free configuration may be better checked through rendering, parsing, builds, or their owning generator; do not install a test framework merely to assert static content.

Read `references/testing-anti-patterns.md` when mocks, snapshots, or asynchronous checks pose a concrete testing question. Broaden verification for shared interfaces, dependencies, uncertain impact, or project policy. Reuse evidence still applicable to the current state, retain useful regression tests, and report only what the evidence proves. A cycle needs no separate commit, checklist, or process report.
