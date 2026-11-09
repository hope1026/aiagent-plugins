# Test Policy

Use when selecting checks across repeated changes and deployments, or when designing or cleaning up a test suite. Follow the project's existing runner, CI, and required checks. A project can start with its existing commands and configuration.

Preserve necessary protection while reducing duplicate tests and release delays from unjustified execution. Select checks for the affected behavior and current phase, reuse acceptable passing evidence, and execute only the missing or invalidated scope. Forge supplies decision criteria; automated selection and reuse require support in the project's runner or CI. No new registry, framework, or per-test form is required.

## Define what a suite protects

Group tests by the feature or module they protect and distinguish scope (unit, integration, end-to-end), failure impact (for example, critical behavior or appearance only), the environment they need, and when passing evidence is required. Keep defaults at suite level and record exceptions where needed. Use runner-native locations, packages, or tags for membership. Keep changed inputs that trigger a suite separate from its test membership. Include dependencies such as shared code, fixtures, configuration, and the suite's own tests.

| Scope | Protection and selection |
|---|---|
| Unit | Isolated logic; select when that logic or its relevant dependencies change. |
| Integration | Connections between components, actual storage, or provider contracts; select for affected interfaces, schemas, wiring, or configuration. |
| End-to-end | A complete user or operator journey; select for affected journeys and project-required acceptance or release gates. |

Smoke describes a purpose, not a separate scope: a short integration or end-to-end check may establish basic deployed health. A unit pass does not replace required integration or end-to-end evidence. Similar assertions at distinct boundaries are not automatically duplicates. Test type alone determines neither cost nor required frequency; use observed cost and project policy.

Put fast checks for critical behavior, such as preventing duplicate charges, in the required PR set when project policy calls for it. Require deeper checks when the affected boundary changes or before a release where they are needed. Schedule appearance-only comparisons and broad regression runs separately where the project permits deferred feedback. A layout that hides a required control or gives a wrong total affects function and belongs in the corresponding functional checks.

## Add and maintain protection

Before adding a test, identify the observable failure it must catch and inspect existing coverage for the same conditions, path, boundary, and outcome. If an existing test already detects it, fix the defect and verify with that test. Extend a suitable case for missing inputs; add a separate test only for a missing behavior or boundary. Choose the narrowest reliable scope that can expose the failure. Adding a test does not automatically make it required on every release; assign its change triggers and required phases using the suite defaults.

A failure alone is not a reason to add permanent regression coverage. Distinguish a product defect from a wrong expectation or fixture, installation or environment failure, and a transient external failure. Correct expectations only against the approved behavior. Resolve setup failures and recheck the affected stage; add protection only if investigation reveals a missing supported behavior, such as required timeout recovery. Keep diagnostic probes temporary unless they provide distinct lasting protection. Do not rerun flaky checks until green and discard the failed evidence; investigate whether the cause still undermines the result.

Review related tests when touching a feature or explicitly cleaning up its suite; do not audit the entire repository on every task. Consolidate tests that protect the same failure under equivalent conditions, and remove or replace assertions that merely mirror implementation without protecting a meaningful outcome. Remove obsolete tests and their unused fixtures only after confirming that the behavior and support obligation have ended. Preserve old-version compatibility, migration, recovery, and distinct provider or deployed-configuration coverage while those obligations remain. Age, slowness, or a current failure alone is not grounds for deletion.

When consolidating or removing coverage, use a known regression or controlled fault where feasible to confirm that retained checks still catch the relevant failure. Inspect preserved boundaries and run affected checks; a green suite after deletion alone does not establish preserved protection.

## Select and run checks

- During local work, run focused affected checks that the environment supports. Surface required checks still waiting on CI or another environment.
- For the current phase, select the project's required checks, added or changed tests, and suites affected directly or through dependencies. An execution needs a concrete reason: affected inputs, failed or invalid evidence, a required outcome without acceptable evidence, or impact that cannot be bounded. Investigate uncertain dependencies before broadening; run the full applicable set when impact cannot be bounded or project policy requires it. Preserve authorized phase ordering and execution restrictions; report a coverage gap rather than running in a prohibited environment. A release, handoff, new commit, or general desire for reassurance alone does not justify a full rerun. Change an unnecessarily broad project gate through its authorized policy process, never by silently bypassing it.
- Merge the selected tests before execution. Run the same test case and parameters once per equivalent runner, configuration, and environment, and share its outcome across the rules that selected it. Use the runner's discovery and filtering when available. For commands with opaque membership, deduplicate identical registered invocations and keep their test groups disjoint where practical. A test run against two required environments provides separate evidence.
- In reports, distinguish passing results, reused evidence, policy exclusions, and unavailable or failed required checks. Required checks without acceptable passing evidence cannot satisfy a merge or release gate.

## Reuse evidence across phases

PR and release gates use evidence trusted by the project. Local success helps development and only satisfies a CI gate if the gate can verify the result and its inputs. Reuse results only when the relevant source and dependencies, tests, inputs, configuration, runtime and tools, environment, artifact, and freshness policy still match. Retain enough provenance in existing execution records to establish that match. Equal commit IDs alone do not prove unchanged inputs; different IDs alone do not invalidate unrelated evidence. Preserve project requirements that pin evidence to an exact revision. Recheck only the invalidated scope.

Dependency caches, build artifacts, and passing test evidence are separate. Key dependency caches to relevant runtime, platform, lockfiles, and install options; a cache hit proves no test passed. Reuse artifacts only with trusted provenance and verified content identity, including the bytes actually deployed. Changes confined to deployment tooling still need affected tooling checks even when runtime evidence remains reusable.

If validation passed and only deployment failed, reuse valid evidence and artifacts and retry only the failed deployment stage where supported. For an uncertain external effect, inspect actual state and recover the original operation under the project's retry and idempotency rules before repeating writes. Recheck current authorization, leases, versions, and other mutable preconditions when required. Run required deployed-instance checks for an actual rollout, including redeployment of the same artifact; completing an existing operation's recovery or records is not automatically a new rollout. Confirm missing or invalidated postconditions without restarting unrelated validation. A missing or failed required smoke check blocks rollout expansion.

Keep temporary exceptions scoped to their approved targets, deadline, and final acceptance conditions. Preserve the meanings of full, targeted, skipped, and reused evidence; never relabel a focused pass as a full pass.

## Measure and improve selection

Before optimizing a slow path, separate queueing, dependency installation, fixture setup and teardown, test execution, type checks, build, artifact transfer, deployment, and health checks as relevant. Track release wall time separately from aggregate runner usage, along with duplicate executions, reuse, and regressions or required checks missed by selection. A combined job duration is not the duration of its tests, and a synthetic improvement does not prove a faster release.

Validate new selection rules against a comparable full result for the same revision and environment before reducing required CI coverage; reuse a suitable existing result. This evaluates selection accuracy, not every later edit or deployment. Agree on periodic or on-demand broad audits where useful and allowed, without moving currently required checks out of the release path. Reduce measured setup and repeated build costs before removing needed protection. Share immutable fixtures or safely isolated setup where appropriate; preserve test independence, cleanup, and required concurrency constraints.
