# Codex Adaptations

Consult this reference only for Forge invocation or capability questions in Codex. Use tools exposed by the current session; do not infer capabilities from an old version table or change global settings to obtain them.

Skills can be invoked explicitly or selected by description. Keep any project instruction pointer short and scoped to project work. Reuse native task planning, conversation state, review, and worktree capabilities where they fit; retain project records needed for human review or cross-session recovery.

Apply the forge using-forge skill's execution-selection policy. In Codex, model and effort overrides can depend on the tool's context mode: a full-history fork may require inheriting both settings. Use a supported limited-context handoff when an override is useful, including the sources and constraints the worker needs; otherwise inherit. Determine worker availability from exposed tools, not a missing model-role label.

Official subagent reference, checked 2026-09-24: https://learn.chatgpt.com/docs/agent-configuration/subagents

Codex supports plugin-bundled lifecycle hooks, subject to the installed version, enabled features, and trust settings. Plugin installation does not by itself trust hooks. Verify actual availability before relying on one. Do not install or enable hooks merely because Forge can use them.

Official reference, checked 2026-09-10: https://learn.chatgpt.com/docs/hooks#plugin-bundled-hooks

App permissions govern tool execution; they do not redefine the approved project contract or authorize unrelated effects.
