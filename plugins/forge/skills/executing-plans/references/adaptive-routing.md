# Adaptive Execution Routing

Use this reference for examples when coordinating multiple tasks or workers. The forge using-forge skill owns delegation, model selection, permission, fallback, and evidence-review policy. Reuse that policy; the plan supplies outcomes and dependencies, not new authority.

## Choose execution that helps

Parallelize only after resolving dependency and write conflicts, including generated files and shared metadata. Inspect actual interfaces and repository state; different task titles alone do not establish independence. If ownership or ordering is unclear, resolve it or work sequentially.

## Select model and reasoning effort

| Task signals | Model and effort considerations |
|---|---|
| Clear search, extraction, or repetitive edits with easy checks | Favor a fast, lightweight model with its default or a lower supported effort when adequate. |
| Bounded implementation with known interfaces and meaningful tests | Favor a model suited to implementation and balanced reasoning. |
| Ambiguous defects, coupled design decisions, or difficult edge cases | Favor stronger reasoning capability and consider higher supported effort. |
| Security-sensitive behavior, data-loss risk, or weak verification | Prioritize reliable judgment and deeper reasoning; consider independent review where it adds evidence. |

These examples guide judgment, not a required sequence from cheapest to strongest. Record selections only when useful for coordination, recovery, or a requested cost comparison.

## Integrate and recover

Use the current plan or app record for completed results, useful evidence, unresolved choices, and the next step. Record ownership or route decisions when another executor or recovery needs them. Do not keep a second ledger merely to mirror app state.

When attempts stop producing evidence, revisit the hypothesis and approach through the forge systematic-debugging skill. A retry count or stronger model does not establish a cause or replace verification.
