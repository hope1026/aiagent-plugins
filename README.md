# aiagent-plugins

AI agent plugins managed from one source tree. Forge installs into **Claude Code** and **Codex CLI**, and its cross-agent authoring workflow creates shared skill and MCP structures for those agents plus **Antigravity**.

## What's here

| Plugin | Purpose |
|---|---|
| `forge` | Spec-first development process: structured Markdown spec → plan → execute → verify, plus TDD, debugging, cross-agent authoring, UI design, writing tone overlays, and request-only adaptive Review Viewer snapshots. |

```text
plugins/<name>/
  .claude-plugin/plugin.json   # Claude Code manifest
  .codex-plugin/plugin.json    # Codex manifest
  skills/<skill>/SKILL.md      # shared Agent Skills source
  hooks/                       # Claude-only SessionStart bootstrap (forge)
.agent-extensions/             # canonical repository-only agent extensions
.agents/skills/                # generated Codex + Antigravity repository adapters
.claude/skills/                # generated Claude Code repository adapters
.claude-plugin/marketplace.json    # this repo is a Claude Code marketplace
.agents/plugins/marketplace.json   # ...and a Codex marketplace
docs/specs/                    # specs for this repo (spec-first, dogfooded)
docs/plans/                    # independent, work-scoped implementation plans
docs/research/                 # promoted research worth sharing
docs/debug/                    # promoted root-cause records
.forge/                        # local scratch, research, review snapshots, ledgers, and build files
```

## Install (recommended: GitHub marketplace)

Claude Code:

```text
/plugin marketplace add hope1026/aiagent-plugins
/plugin install forge@hope1026
```

Codex:

```text
codex plugin marketplace add hope1026/aiagent-plugins --ref main --sparse .agents/plugins --sparse plugins/forge
codex plugin add forge@hope1026
```

Marketplace installs copy files into each agent's managed store — no symlinks, works on Windows. Updates: `git push` here, then update the plugin from the agent.

## Install (local dev)

```bash
bash scripts/install.sh                # copy, both agents, forge plugin
bash scripts/install.sh --mode link    # symlink: edit repo -> instantly live (macOS/Linux)
bash scripts/install.sh --agent codex --plugin forge
```

- Codex target: per-skill entries in `~/.agents/skills/` + `~/.agents/plugins/marketplace.json`.
- Claude target: `~/.claude/skills/<plugin>`. Note: the forge SessionStart hook only runs for marketplace-installed plugins.
- Windows: `--mode link` is auto-downgraded to copy (symlinks need admin/Developer Mode); re-run install after edits.
- Marketplace and local dev installs use `plugins/forge/` only. Repository-only canonical extensions and their adapters are not installed for plugin users.

## forge user skill catalog

| Skill | One line |
|---|---|
| `using-forge` | Entry point: routes any task to the right forge skill; spec-first iron law; shared artifact contract |
| `writing-specs` | Idea → approved `forge/spec@2`; validates flexible structured Markdown without generating HTML |
| `writing-plans` | Independent task-level plan with 0..N Related Specs; behavior changes still require approval |
| `executing-plans` | Task-by-task execution with checkpoints and plan-local progress history |
| `test-driven-development` | RED → GREEN → REFACTOR; no implementation without a failing test |
| `systematic-debugging` | Reproduce → isolate → root-cause → fix; no fix without an understood cause |
| `verifying-work` | Evidence before claims; walks acceptance criteria; flips spec to `implemented` |
| `review-viewer` | Builds an adaptive untracked spec or plan snapshot only after explicit intent, using Semantic IR, validated presentation planning, and reusable components |
| `web-app-design` | Browser app hierarchy, control affordance, state geometry, and viewport×state verification |
| `website-design` | Public website visual thesis, content composition, imagery, responsive behavior, and restrained motion |
| `writing-tone` | Base natural prose layer: clear human writing, non-AI-like wording, and Korean engineering communication |
| `marketing-tone` | Marketing and product copy overlay: factual, confident, trust-building claims |
| `operations-tone` | Customer and operations overlay: confirmed status, impact, next action, and restrained cause detail |
| `creating-agent-extensions` | Creates one `.agent-extensions/` source with thin Codex, Claude Code, and Antigravity skill/MCP adapters |

## Repository maintenance

Forge itself is maintained through the repository-only canonical extension at
`.agent-extensions/maintaining-forge/`. Codex and Antigravity share the
manager-owned adapter under `.agents/skills/maintaining-forge/`; Claude Code
uses `.claude/skills/maintaining-forge/`. Both adapters point to the same
canonical skill, whose ownership state detects collisions and drift.

Keep detailed maintainer procedures in `.agent-extensions/` and render native
entries through the `creating-agent-extensions` manager. These files stay
outside `plugins/forge/`, so Marketplace and `scripts/install.sh` distribute
the 14 active user-execution skills listed above.

## Spec-first lifecycle (the short version)

1. Product behavior changes require an approved spec; execution work requires a plan task.
2. Change requests edit the spec first — never patch code and back-fill.
3. Implementation discoveries pause for an approved spec delta.
4. Verification is against the spec's acceptance criteria, with fresh evidence.
5. Spec status `draft → approved` (human) `→ implemented` (verified only).
6. Drift repair (`sync` mode) reconciles brownfield code against its spec.
7. The normal lifecycle creates Markdown only; Review Viewer HTML is request-only, adaptive, and untracked.

Per-project artifacts: permanent specs live in `docs/specs/NNN-<slug>/spec.md`. Work-scoped plans live at `docs/plans/PPP-<slug>/plan.md`; optional `progress.md` and `tasks/*.md` stay only while that plan is retained. Review Viewer snapshots live at `.forge/reviews/<review-id>/view.html`, are created only after an explicit request, and remain untracked. `.forge/research/` is local-only; promote durable findings to `docs/research/` and root-cause records to `docs/debug/`. Promote permanent decisions before deleting a completed plan.

## Validate

```bash
bash scripts/validate.sh
```

Lints plugin skills and repository-local wrappers, validates extensions, and runs strict structured-spec validation with an explicit repository root. CI runs lifecycle, artifact, UI routing, and adaptive renderer contracts on every push.
