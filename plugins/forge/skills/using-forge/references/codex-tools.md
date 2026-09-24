# Codex Adaptations

Consult this reference only for Forge invocation or capability questions in Codex. Use tools exposed by the current session; do not infer capabilities from an old version table or change global settings to obtain them.

Skills can be invoked explicitly or selected by description. Keep any project instruction pointer short and scoped to project work. Reuse native task planning, conversation state, review, and worktree capabilities where they fit; retain project records needed for human review or cross-session recovery.

The forge using-forge skill requests delegation of suitable independent work when subagents are available and permitted. At task start, assess that work and select each subagent's model and reasoning effort using the exposed capabilities, task needs, and user settings. Inspect worker artifacts and evidence against the integrated result. A missing model role does not imply workers are unavailable; missing workers means direct execution.

Use per-subagent model and effort overrides only when the current tool and context mode support them. A full-history fork may require inheriting both settings; use a supported limited-context handoff when an override is useful, and include the sources and constraints the worker needs. Otherwise inherit current settings. Do not infer an ability to change the running parent model or edit global configuration to force selection. Honor explicit user settings and higher-priority restrictions.

Official subagent reference, checked 2026-09-24: https://learn.chatgpt.com/docs/agent-configuration/subagents

Codex supports plugin-bundled lifecycle hooks, subject to the installed version, enabled features, and trust settings. Plugin installation does not by itself trust hooks. Verify actual availability before relying on one. Do not install or enable hooks merely because Forge can use them.

Official reference, checked 2026-09-10: https://learn.chatgpt.com/docs/hooks#plugin-bundled-hooks

App permissions govern tool execution; they do not redefine the approved project contract or authorize unrelated effects.
