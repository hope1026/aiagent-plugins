# Authoring Providers

Native authoring capabilities improve the detailed skill or MCP content. They are providers, not owners of the cross-agent layout. The common workflow remains usable when no provider is installed.

## Capability discovery

Inspect the current agent's available system skills, bundled skills, official guidance, and installed extensions before authoring content. Match capabilities rather than requiring a fixed name.

| Current agent | Preferred source when available | Fallback source |
|---|---|---|
| Codex | The system `skill-creator` for skill content; current official OpenAI MCP guidance for MCP definitions | The bundled checklists below |
| Claude Code | A discovered skill-authoring helper or the current official Claude Code skill and MCP guidance | The bundled checklists below |
| Antigravity | A discovered customization/skill-authoring helper or the current official Antigravity Agent Skills and MCP guidance | The bundled checklists below |

Provider names and installation state can change. Do not fail because one example name is absent, do not install an adjacent capability without the user's request, and do not let a provider select final paths.

Current official format references:

- Claude Code: [Extend Claude with skills](https://code.claude.com/docs/en/slash-commands) and [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)
- Antigravity: [Agent Skills](https://antigravity.google/docs/skills) and [MCP](https://antigravity.google/docs/mcp)
- Codex: use the current official OpenAI Agent Skills and MCP documentation available to the running Codex environment.

## Staging boundary

Give a provider a disposable directory and an explicit output contract. The provider may write only inside that directory.

```text
.forge/scratch/agent-extensions/<extension-name>/
├── skills/<skill-name>/SKILL.md
├── skills/<skill-name>/references/
├── skills/<skill-name>/scripts/
├── skills/<skill-name>/assets/
├── mcp/servers.json
├── mcp/<server-name>/
└── shared/
```

The provider must return:

- The files it created and the concrete usage example each file supports.
- Skill triggers and any progressive-disclosure resources.
- MCP transport, command or URL, environment variable names, and tool usage examples.
- A list of platform-only suggestions it intentionally left out of the canonical candidate.
- Its own content review findings.

The provider must not create or edit canonical roots, native skill roots, native MCP configuration, ownership state, Marketplace metadata, plugin manifests, or release files.

## Skill authoring contract

Provide the authoring capability with confirmed examples, trigger phrases, output expectations, failure behavior, and resource needs. Require a candidate that:

- Has one focused responsibility.
- Uses a lowercase hyphenated name that matches its target directory.
- Uses only `name` and `description` in common frontmatter.
- Puts capability and trigger conditions in the description.
- Keeps the main workflow concise and moves conditional detail into `references/`.
- Uses scripts only for deterministic repeated work and assets only when the output consumes them.
- Contains no unfinished markers or copied native adapter instructions.

The manager copies staged `references/`, `scripts/`, and `assets/` siblings with the skill. Their bytes participate in the canonical hash, so later resource changes require another render.

## MCP authoring contract

Provide server purpose, expected tools, transport, launch or endpoint details, and credential boundaries. Require one of these canonical shapes:

```json
{
  "transport": "stdio",
  "command": "python3",
  "args": ["server.py"],
  "envVars": ["SERVICE_TOKEN"]
}
```

```json
{
  "transport": "http",
  "url": "https://example.test/mcp",
  "headersFromEnv": {"Authorization": "SERVICE_TOKEN"}
}
```

The provider may propose an implementation under its staging `mcp/<server-name>/` directory. The orchestrating workflow decides whether to copy that candidate into the canonical root. Forge does not claim to implement or operate the full MCP server unless the user separately requests that work.

## Normalization boundary

| Provider output | Orchestrator response |
|---|---|
| Platform-only frontmatter | Remove it from canonical skill frontmatter; preserve only under a named agent extension point when required. |
| Direct native skill or MCP edits | Discard or reverse them; render through the deterministic manager. |
| Raw credential or authorization value | Reject it and request an environment variable name. |
| Absolute or parent-traversing canonical path | Reject it. Canonical component paths remain relative to the extension root. |
| Unfinished marker or empty instruction | Reject it before `init`. |
| Hook, rule, or app presented as common | Reclassify it as an agent-specific adapter extension or future scope. |
| Collision resolution or validation verdict | Ignore the provider's decision; the manager and user-owned decision boundary control it. |

## Bundled fallback

When no suitable provider exists, author the candidate directly from the confirmed request using these minimum checks.

For a skill:

1. Write one sentence describing the concrete job and one sentence describing when it triggers.
2. Turn the concrete usage example into an observable workflow with inputs, actions, failures, and output.
3. Keep `SKILL.md` focused; create only resources that the workflow actually reads or executes.
4. Re-read the candidate under deadline pressure and close any path that permits copying, secret insertion, collision overwrite, or skipped validation.

For MCP:

1. Choose exactly `stdio` or `http` from the confirmed runtime.
2. Record command and args or URL, plus environment variable names only.
3. Add one concrete tool-use example to the related skill or reference.
4. Keep server implementation work staged and explicitly separate from configuration rendering.

The fallback produces the same canonical inputs as a native provider. It does not weaken preview, ownership, collision, drift, validation, or scenario-test gates.
