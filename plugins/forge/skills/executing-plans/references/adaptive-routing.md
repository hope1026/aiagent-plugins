# Adaptive Execution Routing

Use this reference when coordinating multiple tasks or workers. The plan owns intended outcomes; execution choices do not grant new authority.

## Choose execution that helps

At task start or resumption, identify work that can be delegated. Keep small or tightly coupled work with the agent that owns its context. Use available, permitted subagents for bounded tasks when inputs, outcome, write ownership, and verification are clear and the expected benefit exceeds briefing and integration costs. Independent investigation can run alongside implementation when it does not depend on changing state.

Parallelize only after resolving dependency and write conflicts, including generated files and shared metadata. Inspect actual interfaces and repository state; different task titles alone do not establish independence. If ownership or ordering is unclear, resolve it or work sequentially.

Use available workers and settings within platform permissions and user preferences. Respect concurrency limits; there is no Forge-specific worker cap, mandatory capability tier, score table, or escalation ladder. If workers are unavailable, execute directly without inventing calls.

## Select model and reasoning effort

When supported and permitted, choose each worker's model and effort for its own task. Model choice reflects required capability and context; effort reflects reasoning depth, uncertainty, and the consequences of error. Use the selected model's supported settings and default effort as the starting point. Effort labels are not a universal scale across models.

| Task signals | Model and effort considerations |
|---|---|
| Clear search, extraction, or repetitive edits with easy checks | Favor a fast, lightweight model with its default or a lower supported effort when adequate. |
| Bounded implementation with known interfaces and meaningful tests | Favor a model suited to implementation and balanced reasoning. |
| Ambiguous defects, coupled design decisions, or difficult edge cases | Favor stronger reasoning capability and consider higher supported effort. |
| Security-sensitive behavior, data-loss risk, or weak verification | Prioritize reliable judgment and deeper reasoning; consider independent review where it adds evidence. |

These examples guide judgment, not a required sequence from cheapest to strongest. Respect explicit user settings and higher-priority instructions. Resolve actual model names and supported effort values from the current environment rather than a hardcoded cross-platform list. If overrides are unavailable, inherit current settings; do not change global configuration or assume the running parent model can switch. Record selections only when useful for coordination, recovery, or a requested cost comparison.

## Integrate and recover

Root owns integration, final contract judgment, and completion reporting. Inspect each worker's diff or artifact and actual execution evidence. Reuse evidence that applies to the integrated state; run checks for invalidated or uncovered boundaries.

Use the current plan or app record for completed results, useful evidence, unresolved choices, and the next step. Record ownership or route decisions when another executor or recovery needs them. Do not keep a second ledger merely to mirror app state.

When unexpected dependencies, uncertainty, or verification failures change the task, reassess decomposition, ownership, model, and effort. When attempts stop producing evidence, revisit the hypothesis and approach. Use the forge systematic-debugging skill when useful. A retry count or stronger model does not establish a cause or replace verification. Ask the user only if progress needs a new product, scope, or authority decision.
