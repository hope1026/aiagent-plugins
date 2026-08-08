# Adaptive Execution Routing

Use this reference to choose the capability tier, execution mode, parallel group, and escalation path for each plan Task. The plan remains the execution source; routing changes who performs the work, never what the Task means or which artifact owns project authority.

## Routing Signals

Record four signals before dispatch:

| Field | Values | Question |
|---|---|---|
| `impact` | `low`, `medium`, `high` | How costly is an incorrect change or conclusion? |
| `uncertainty` | `low`, `medium`, `high` | How unclear are the requirement, root cause, or solution? |
| `context_coupling` | `low`, `medium`, `high` | How many files, subsystems, decisions, or actors must stay consistent? |
| `verification_clarity` | `strong`, `partial`, `weak` | How decisively can fresh evidence prove completion? |

Use the current Task text, its Files and Interfaces blocks, dependency diagram, governing R and AC IDs, and repository state. Do not guess missing independence or file ownership.

## Capability Tiers

| Tier | Selection rule | Typical work |
|---|---|---|
| `fast` | All of `impact`, `uncertainty`, and `context_coupling` are `low`; `verification_clarity` is `strong`; no Canonical Spec or other durable authority decision | inventory, focused search, mechanical fixture or formatting work |
| `balanced` | Default when every `fast` condition is not met and no `frontier` signal exists | isolated implementation, tests, documentation with stable interfaces |
| `frontier` | Any signal is `high`, verification is `weak`, or the Task owns Canonical Spec, architecture, security, data safety, root cause, or final cross-system judgment | durable authority decisions, risky migration, ambiguous debugging, final synthesis |

The tier is a capability requirement, not a permanent model slug. Platform configuration maps it to an available role, model, and reasoning setting.

## Execution Mode

Choose one:

- `root`: the root agent executes work that owns Canonical Spec or other durable authority decisions, spans tightly coupled context, or would cost more to brief and review than to perform directly.
- `subagent`: one bounded worker receives the complete Task plus its Interfaces, files, constraints, verification, and allowed authority.
- `parallel`: multiple independent Tasks run concurrently as one `parallel_group`.

Subagent availability alone is not a reason to delegate. Use one only when the handoff is complete and root review remains cheaper than direct execution.

## Default Execution Modes

Apply these defaults after selecting the capability tier and before forming a parallel group:

- `fast` defaults to `root`. Use `parallel` only for multiple mechanical Tasks that pass every parallel safety condition and save more wall-clock time than dispatch and review cost.
- `balanced` defaults to `subagent` only when `context_coupling=low`, `verification_clarity=strong`, the handoff is complete, write ownership is disjoint, and root review is cheaper than direct execution. Otherwise use `root`. When two or more eligible Tasks also pass the parallel safety gate, prefer `parallel` within the concurrency cap.
- `frontier` defaults to `root`. Delegate only bounded evidence collection that is separable from durable authority judgment; Canonical Spec, architecture, security, data safety, root cause, integration, and final judgment remain root-owned.

User execution preferences override these defaults when they are more restrictive: honor `root-only`, disabled subagents, and a lower concurrency cap. A preference never waives dependency, write-overlap, verification, or root-ownership gates. Do not ask the user to choose a mode for an ordinary Task; record the automatic choice in the ledger and summarize delegation in a notify or final report.

## Parallel Safety Gate

Parallelize only when every condition holds:

1. No Task depends on another Task in the proposed group.
2. Write paths do not overlap, including generated or shared metadata files.
3. Interfaces are already stable and named in the plan.
4. Each Task has independent verification and a bounded result.
5. Failure in one Task does not invalidate work already underway in another.
6. Expected wall-clock savings exceed dispatch, context, and review cost.

Missing evidence means sequential execution. Never infer independence from adjacent Task numbers or different headings.

Respect the platform limit and any user-configured cap. Without a user cap, use a **maximum of 3 concurrent subagents**. Queue additional safe Tasks until a slot is available.

## Root Ownership and Review

The root agent always owns:

- Canonical Spec changes and Execution Plan source changes;
- routing and `parallel_group` decisions;
- approval requests and authority boundaries;
- integration across worker results;
- reading every worker diff or artifact;
- fresh Task verification after worker completion;
- progress ledger and final acceptance judgment.

A worker completion message is not evidence by itself. Do not mark a Task complete until root review and fresh verification pass.

## Platform Fallback

Treat model mapping and subagent availability independently:

| Model mapping | Subagents | Behavior |
|---|---|---|
| available | available | Use the mapped tier role and safe root, subagent, or parallel mode. |
| unavailable | available | Inherit the current model for every tier; safe subagent and parallel modes remain available. |
| available | unavailable | Use the mapped tier in root sequential mode. |
| unavailable | unavailable | Inherit the current model and execute sequentially in root. |

Never claim to select a model, role, or worker capability the platform does not expose.

## Ledger Contract

Record route and completion separately:

```text
Task N: routed (impact=medium, uncertainty=low, context_coupling=low, verification_clarity=strong, tier=balanced, mode=subagent, parallel_group=route-2, reason="isolated implementation with deterministic tests")
Task N: complete (commits a1b2c3d..d4e5f6a; verification="target suite passed")
```

Use `parallel_group=none` when the Task is not in a group. At milestone notify and final reporting, summarize tier and mode without exposing hidden reasoning or claiming an unavailable model slug.

## Escalation and Stop Rule

When the same verification failure occurs twice or the route assumptions become false:

1. Record the failed evidence and why the current route is invalid.
2. Escalate one tier: `fast → balanced → frontier`.
3. Re-evaluate execution mode and parallel safety; do not preserve a stale group automatically.
4. Retry once under the new route.

If the same failure recurs at `frontier`, or after the one escalation retry, stop automatic retries and use the forge systematic-debugging skill. Continue without user approval when root-cause work stays inside the approved scope. Use an approval checkpoint only when the root cause requires a spec delta, new authority, destructive or external action, cost escalation, scope expansion, or release.

## Red Flags

| Pressure | Required response |
|---|---|
| "The user demanded parallel execution." | User preference and deadline pressure do not establish independence; overlapping writes remain sequential. |
| "The deadline makes a fourth worker harmless." | The concurrency cap still applies. Queue the extra Task until a slot opens. |
| "No tier role is configured, so workers are unavailable." | Model mapping and worker availability are separate. Inherit the current model and retain safe subagent execution. |
| "The worker says it passed, so root verification is redundant." | A worker report is a claim. Root review and fresh verification remain mandatory. |
| "Balanced means I should always dispatch a worker." | The subagent default applies only when coupling is low, verification is strong, handoff is complete, ownership is disjoint, and review is cheaper than direct execution. Otherwise use root. |
| "I should ask the user which mode they prefer for this Task." | Apply the deterministic default and report it. Ask only when a user-owned authority, scope, cost, or product decision is actually required. |
