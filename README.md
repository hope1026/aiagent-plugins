# aiagent-plugins

AI agent plugins managed from one source tree. Forge installs into **Claude Code** and **Codex CLI**, and its cross-agent authoring workflow creates shared skill and MCP structures for those agents plus **Antigravity**.

## What's here

| Plugin | Purpose |
|---|---|
| `forge` | Canonical Spec and complexity-aware execution process: durable contract changes use approved Spec Deltas, bounded work can run directly with fresh evidence, and complex work uses optional Execution Plans. Includes TDD, debugging, cross-agent authoring, UI design, tone overlays, and request-only Review Viewer snapshots. |

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
docs/specs/                    # permanent semantic Canonical Spec Bundles for this repo
docs/plans/                    # optional, work-scoped Execution Plans
docs/research/                 # promoted research worth sharing
docs/debug/                    # promoted root-cause records
.forge/                        # local briefs, Spec Deltas, scratch, reviews, ledgers, and build files
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
| `using-forge` | Classifies Canonical Spec impact and execution complexity, then selects Quick, plan-only, spec-backed direct, or full lifecycle |
| `writing-specs` | Proposes approved Spec Deltas and maintains permanent `forge/spec@3` Canonical Spec Bundles without generating HTML |
| `writing-plans` | Creates an optional Execution Plan for high-complexity work with 0..N Related Spec Bundle paths and Task-level full-statement links |
| `executing-plans` | Executes plan Tasks with checkpoints while keeping the plan a work source rather than project SOT |
| `test-driven-development` | RED → GREEN → REFACTOR; no implementation without a failing test |
| `systematic-debugging` | Reproduce → isolate → root-cause → fix; no fix without an understood cause |
| `verifying-work` | Matches fresh evidence to Quick, plan-only, restoration, or approved-Delta work; changes Canonical lifecycle only when required |
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

## Canonical Spec and task routing

Forge decides two things independently:

1. **Canonical Spec impact:** does the request change durable project authority such as an interface, schema, workflow, policy, cross-component responsibility, or user-designated permanent decision?
2. **Execution complexity:** does safe work need dependent stages, several components, migration or release ordering, rollback, parallel ownership, or a zero-context handoff?

| Canonical Spec impact | Execution complexity | Route |
|---|---|---|
| no | low | Quick direct execution with fresh focused evidence |
| no | high | Optional Change Brief + Execution Plan |
| yes | low | Approved Spec Delta + direct execution |
| yes | high | Approved Spec Delta + Execution Plan |

`spec` is reserved for permanent Canonical Specs. A Change Brief captures one work request; a Spec Delta is an approval proposal; an Execution Plan controls implementation order but is not project SOT; Verification Evidence proves a concrete claim. Quick removes formal artifacts, never TDD, debugging, or fresh verification.

Before routing, Forge drafts `Goal`, `Scope`, `Out of Scope`, and observable `Done Checks` in the conversation and inspects repository-discoverable facts. It asks one user-owned blocking choice only when ambiguity changes the outcome, scope, authority, safety, or destructive or external effects. Clear requests and safe reversible defaults proceed without a question or Brief file. Brief clarification defines the current work, Canonical classification decides whether a choice belongs in permanent authority, and Spec clarification resolves the exact meaning of that durable contract.

Per-project artifacts: authoritative Canonical Specs live as `forge/spec@3` bundles under `docs/specs/<semantic-bundle-name>/` with lifecycle `approved → implemented`. The bundle path is the human-facing identity. Its root and member filenames describe their content, and one durable contract may use several members listed by the root `Documents` section. Requirement and Acceptance statements are complete headings linked by exact member path and anchor. Optional work input lives at `.forge/work/<work-id>/brief.md` and `spec-delta.md` and stays untracked. High-complexity Execution Plans live at `docs/plans/PPP-<slug>/plan.md`; their `Related Specs` list bundle paths and each governed Task uses `Governing statements:` links. Optional `progress.md` and `tasks/*.md` stay only while the plan is retained. Review Viewer snapshots live at `.forge/reviews/<review-id>/view.html`, require an explicit request, and remain untracked. Promote lasting decisions, research, and root-cause findings before removing work artifacts.

## Validate

```bash
bash scripts/validate.sh
```

Lints plugin skills and repository-local wrappers, validates extensions, and runs strict structured-spec validation with an explicit repository root. CI runs lifecycle, artifact, UI routing, and adaptive renderer contracts on every push.
