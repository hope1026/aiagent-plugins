---
name: creating-agent-extensions
description: 'Use when creating or updating a skill, MCP definition, or combined agent extension that must work from one canonical source across Codex, Claude Code, and Antigravity. Triggers: "에이전트 확장 생성", "공통 스킬", "여러 에이전트", "MCP 만들기", "cross-agent skill", "portable MCP".'
---

# Creating Agent Extensions

Announce once when first applied: "Using the forge creating-agent-extensions skill to create one canonical extension with agent-native adapters."

Respond to the user in the user's language. This skill file stays in English.

## Overview

Create or update one agent-neutral source under `.agent-extensions/`, then render the native discovery and MCP configuration required by Codex, Claude Code, and Antigravity. Native authoring capabilities produce content candidates; this skill alone owns scope, canonical paths, adapter formats, collision policy, ownership state, and the final validation verdict.

This is an authoring workflow, not a distribution workflow. It does not create Marketplace entries, release packages, versions, publications, or remote pushes.

## Iron Law

```text
ONE CANONICAL SOURCE; NATIVE ENTRIES ARE ADAPTERS, NEVER COPIES.
NO NATIVE WRITE BEFORE A COMPLETE PREVIEW.
NO PROVIDER MAY OWN PATHS, MERGES, COLLISIONS, OR THE VALIDATION VERDICT.
NO COMPLETION CLAIM BEFORE VALIDATION AND A REALISTIC SCENARIO TEST.
```

## When to Use / When NOT

Use this skill when:

- A repository or user-level skill must work in Codex, Claude Code, and Antigravity.
- One or more MCP server definitions must be rendered into all three agents' native configuration.
- A skill and its MCP servers belong in one `bundle` with shared ownership and drift detection.
- An existing extension created by this workflow needs a drift-free canonical content update.

Do not use this skill when:

- The requested output is a distributable plugin, Marketplace package, installer, or release.
- The feature is intentionally single-agent and has no shared skill or MCP component.
- The request is only for hooks, rules, apps, or another agent-exclusive component. Keep such work in `adapters/<agent>/` or make it a separate scope; do not call it portable.
- The request is automatic migration or adoption of an existing native entry. The first version requires an explicit rename, adopt, or merge decision.

## The Process

Reuse the work checklist for canonical content, preview, rendering, and verification. Read `references/layout-contract.md` for every run and `references/authoring-providers.md` before selecting or invoking a content provider.

### 1. Fix the request contract

Record all of these before creating a canonical file:

- Scope: `repository` or `user`.
- Profile: `skill`, `mcp`, or `bundle`.
- Extension name and description.
- At least one concrete usage example for each skill.
- Skill names, trigger language, and required `references/`, `scripts/`, or `assets/`.
- MCP server names, `stdio` or `http` transport, command or URL, tools it supports, and environment variable names.
- Any requested hooks, rules, or apps as agent-specific extension points, not common components.

If a skill example, trigger, MCP transport, or credential boundary is unknown, stop authoring and resolve that input. Do not hide missing decisions in generated prose.

### 2. Choose the canonical root

Use exactly one root:

| Scope | Canonical root |
|---|---|
| `repository` | `<repo>/.agent-extensions/<extension-name>/` |
| `user` | `~/.agent-extensions/<extension-name>/` |

Normalize names before staging. Names use lowercase letters, digits, and hyphens, begin and end with an alphanumeric character, and stay below 64 characters.

### 3. Discover a native authoring provider

Inventory the official, system, bundled, and installed authoring capabilities visible in the current agent. Select by capability, not by a hard-coded name:

- Skill provider: can turn confirmed examples and triggers into a focused Agent Skill with only necessary support files.
- MCP provider: can define transport, command or URL, environment references, tool usage examples, and an optional server implementation candidate.
- Bundle provider: can explain the relationship between the skill and MCP tools without choosing native paths.

Prefer a suitable native provider. If none is available, use the Bundled fallback in `references/authoring-providers.md`. Provider absence never blocks the common structure.

### 4. Author only inside the staging boundary

Stage candidates under `.forge/scratch/agent-extensions/<extension-name>/` or another disposable directory. The provider may create:

- A complete candidate `SKILL.md` and its `references/`, `scripts/`, and `assets/` siblings.
- A canonical `servers.json` candidate.
- MCP server implementation candidates and shared resources.

The provider must not write `.agent-extensions/`, `.agents/skills/`, `.claude/skills/`, `.gemini/config/skills/`, or any native MCP configuration. Isolate the provider-authored diff, preserve unrelated preexisting content, and remove only the provider's unowned edits outside staging before continuing.

### 5. Normalize provider output

Apply the common contract before canonical creation:

- Keep only `name` and `description` in canonical skill frontmatter.
- Make the frontmatter name match the skill directory and make the description state capability and trigger conditions.
- Remove agent-only invocation metadata, native configuration edits, and copied adapter instructions.
- Replace credential values with `envVars` or `headersFromEnv` environment variable names.
- Reject unfinished markers, invalid paths, unsupported MCP fields, and raw secrets.
- Keep approved MCP implementation candidates staged for the orchestrator to place under `mcp/<server-name>/`; the provider does not choose that destination.

### 6. Preview a new extension with `plan`

Resolve this skill's installed directory and set `MANAGER` to its `scripts/manage_extension.py`. Run `--help` when the interface is unfamiliar. For a concrete bundle:

```bash
python3 "$MANAGER" plan \
  --scope repository \
  --base-dir /path/to/repository \
  --name example-extension \
  --description "Example extension for confirmed workflows." \
  --profile bundle \
  --skill-source /path/to/staging/example-skill/SKILL.md \
  --mcp-source /path/to/staging/servers.json
```

Repeat `--skill-source` for multiple skills. For `skill`, omit `--mcp-source`; for `mcp`, omit skill sources. Review `canonicalWrites`, `nativeTargets`, `collisions`, `credentialRequirements`, and `requiresConfirmation`. A non-empty collision list stops creation until the user chooses rename, adopt, or merge; this workflow does not make that choice.

### 7. Confirm user-scope canonical writes

For `user` scope, show the complete `plan` JSON plus any staged MCP implementation and shared-resource destination that the manager cannot infer. Ask for confirmation before passing `--confirm-user-write` to `init` or copying any candidate into the user canonical root.

Repository scope uses the repository change authorization already given for the task. Do not interpret it as release or push authority.

### 8. Create the canonical source with `init`

Run `init` with the same source arguments used for the reviewed plan. Add `--confirm-user-write` only after the user confirmed a user-scope preview.

The manager copies each staged skill plus its `references/`, `scripts/`, and `assets/`, writes canonical MCP JSON, and creates `extension.json`. After `init`, the orchestrator may copy approved MCP implementation candidates into `mcp/<server-name>/` and shared files into `shared/`. Keep every such write inside the previewed root.

For an existing owned extension, do not run `init` again. Run `validate` before editing, preview the canonical diff, obtain user-scope confirmation, apply only canonical content/resource changes, then continue to adapter rendering. Component removal, rename, or ownership adoption requires an explicit user decision.

### 9. Preview and render native adapters

For repository scope:

```bash
python3 "$MANAGER" render --extension /path/to/repository/.agent-extensions/example-extension
```

For user scope, first run `render` without confirmation. Its expected `E_CONFIRMATION` response includes `canonicalSources`, entry-level `changes`, `nativeTargets`, `credentialRequirements`, and `collisions` without writing. Compare that preview with the concrete scope already approved. Reuse the approval when targets, content, credentials, and effects match; ask only for a new or changed decision. Once covered by approval, run:

```bash
python3 "$MANAGER" render \
  --extension /home/user/.agent-extensions/example-extension \
  --confirm-user-write
```

Never bypass `E_COLLISION` or `E_DRIFT`. A same-name native entry without matching ownership state belongs to someone else. An owned entry whose live hash changed requires the user to choose how to reconcile it.

### 10. Validate canonical and native parity

```bash
python3 "$MANAGER" validate --extension /path/to/.agent-extensions/example-extension
```

Validation must return `status: PASS`. It checks manifest shape, canonical paths and resources, unfinished markers, raw credential fields, ownership state, canonical hash, native entry hashes, and adapter parity. Do not edit state to make a failure disappear; repair the canonical or live owner mismatch and render again.

### 11. Run realistic scenario tests

Test the actual request, not only file existence:

- Ask each target agent to discover the skill from its native entry and follow one concrete usage example.
- Exercise at least one MCP tool path for every declared transport that is available in the environment.
- Test provider-present and provider-absent authoring paths when the workflow itself changed.
- Inject one safe collision or drift case and confirm the manager refuses it without changing unrelated configuration.

If an external service or target agent is unavailable, report that scenario as pending rather than claiming full completion. Structural validation is not a substitute for a behavior test.

## Working Files

| Purpose | Path |
|---|---|
| Repository canonical source | `<repo>/.agent-extensions/<extension-name>/` |
| User canonical source | `~/.agent-extensions/<extension-name>/` |
| Disposable provider staging | `.forge/scratch/agent-extensions/<extension-name>/` |
| Deterministic manager | `scripts/manage_extension.py` in this skill |
| Layout and native target contract | `references/layout-contract.md` in this skill |
| Provider and fallback contract | `references/authoring-providers.md` in this skill |

## Error Contract

| Code | Meaning | Required response |
|---|---|---|
| `E_CONFIRMATION` | user-scope write lacks reviewed confirmation | show payload, obtain confirmation, rerun only if approved |
| `E_COLLISION` | same native name is not owned by this extension | stop for rename, adopt, or merge decision |
| `E_DRIFT` | canonical, state, or live native entry no longer matches | identify owner and target; reconcile before rendering |
| `E_PROFILE_INPUT` | profile and staged sources disagree | fix the request contract and rerun `plan` |
| `E_MCP_SCHEMA` | canonical MCP fields or transport are invalid | normalize the staged definition |
| `E_SECRET` | a raw credential field or value was found | remove it and use an environment variable name |

## Red Flags

| Pressure | Required response |
|---|---|
| "Copy the finished skill into all three directories; it is faster." | Full copies create three sources. Keep one canonical skill and thin wrappers. |
| "The provider already edited the native files, so keep them." | Provider writes outside staging have no ownership proof. Preserve unrelated content, remove only those unowned edits, and render through the manager. |
| "User scope always needs a second approval at render." | Inspect the current preview. A complete approval covering the same targets and changes remains valid; changed content, effects, or collisions require a new decision. |
| "The same name probably belongs to this extension." | Ownership is state plus matching hashes, not a guess. Stop on collision. |
| "Put the token in the config temporarily." | Temporary credentials leak and persist. Use environment variable names only. |
| "Claude-only or Antigravity-only metadata is close enough to portable." | Keep agent-only behavior under that agent's adapter extension point; do not claim parity. |
| "Validation passed, so the scenario test is unnecessary." | Validation proves structure and drift state, not discovery or tool behavior. Run a realistic scenario. |
| "This common folder should also become a plugin package." | Authoring structure and distribution are different lifecycles. Use a separate explicitly approved distribution workflow. |

## Handoff

After manager validation and realistic scenario tests pass, use the forge verifying-work skill against the required verification set for the current work class. Use affected statements and regression evidence for a partial change to an implemented baseline; do not invent a Spec for spec-free work. Release and push remain separate actions requiring explicit authority.
