# Agent Extension Layout Contract

The canonical repository root is `<repo>/.agent-extensions/<extension-name>/`. The canonical user root is `~/.agent-extensions/<extension-name>/`.

Each extension has one `extension.json`, canonical skills under `skills/<skill-name>/SKILL.md`, canonical MCP definitions under `mcp/servers.json`, and derived ownership state under `adapters/<agent>/state.json`.

The deterministic manager exposes four actions:

```text
manage_extension.py plan
manage_extension.py init
manage_extension.py render
manage_extension.py validate
```

`plan` never writes. User-scope `init` and `render` require `--confirm-user-write`.
