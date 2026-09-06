# aiagent-plugins

AI agent plugins managed from one source tree. Forge installs into **Claude Code** and **Codex CLI**, and its cross-agent authoring workflow creates shared skill and MCP structures for those agents plus **Antigravity**.

## What's here

| Plugin | Purpose |
|---|---|
| `forge` | Fast, clear agent work with proportional verification: bounded work runs directly, complex work uses focused Execution Plans, and durable contract changes preserve approved meaning. Includes TDD, debugging, cross-agent authoring, UI design, tone overlays, and request-only Visual Docs. |

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
| `writing-plans` | Plans high-complexity work through bounded Tasks, stable interfaces, and scope-matched full-statement links |
| `executing-plans` | Executes plan Tasks with checkpoints while keeping the plan a work source rather than project SOT |
| `test-driven-development` | Focused RED → GREEN → REFACTOR for logic; direct checks for prose, styling, and logic-free configuration |
| `systematic-debugging` | Reproduce → isolate → root-cause → fix; no fix without an understood cause |
| `verifying-work` | Matches fresh evidence to Quick, plan-only, restoration, or approved-Delta work; changes Canonical lifecycle only when required |
| `visual-docs` | Builds and verifies requested Brief, Plan, Spec, and Project views, preserving source meaning through shared components |
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

`spec` is reserved for permanent Canonical Specs. A Change Brief captures one work request; a Spec Delta is an approval proposal; an Execution Plan controls implementation order but is not project SOT; Verification Evidence proves a concrete claim. Quality and accurate authority come first. Within that boundary, Forge uses the smallest verification that proves the requested result and affected contract, reuses inspected evidence while the relevant state is unchanged, and stops when the claim and required project gates are proven. Partial implementation does not require or permit marking the whole bundle implemented. New logic and behavioral defects use focused TDD; prose, styling, and logic-free configuration use appropriate direct checks.

Before acting, Forge establishes the goal, boundaries, and observable Done Checks and inspects repository-discoverable facts. A clear local request uses internal classification and a short goal-and-verification update; it needs no four-field form. It asks one user-owned blocking choice only when ambiguity changes the outcome, scope, authority, safety, or destructive or external effects. Clear requests and safe reversible defaults proceed without a question or Brief file. Brief clarification defines the current work, Canonical classification decides whether a choice belongs in permanent authority, and Spec clarification resolves the exact meaning of that durable contract.

Per-project artifacts: authoritative Canonical Specs live as `forge/spec@3` bundles under `docs/specs/<semantic-bundle-name>/` with lifecycle `approved → implemented`. The bundle path is the human-facing identity. Its root and member filenames describe their content, and one durable contract may use several members listed by the root `Documents` section. Requirement and Acceptance statements are complete headings linked by exact member path and anchor. Optional work input lives at `.forge/work/<work-id>/brief.md` and `spec-delta.md` and stays untracked. High-complexity Execution Plans live at `docs/plans/PPP-<slug>/plan.md`; their `Related Specs` list bundle paths and each governed Task uses `Governing statements:` links. Optional `progress.md` and `tasks/*.md` stay only while the plan is retained. Requested Brief, Plan, and Spec views live at `.forge/visual-docs/<view-id>/view.html` and remain untracked. A requested Project Handbook is regenerated from `docs/project/project-map.md` and declared Specs at tracked `docs/project-viewer/index.html`. Promote lasting decisions, research, and root-cause findings before removing work artifacts.

## Validate

```bash
bash scripts/validate.sh
```

Lints plugin skills and repository-local wrappers, validates extensions, and runs strict structured-spec validation with an explicit repository root. CI runs all Spec and Visual Docs Python suites, extension-manager tests, lifecycle and install checks, and browser regression scenarios.

## Proportional planning and visual verification

Plans specify outcomes, ownership, dependencies, interfaces, verification, and recovery. They include complete code only where an exact example or shared interface is needed. New or never-implemented contracts use full statement coverage; partial changes to an implemented baseline name affected statements and regression preservation.

An explicit Visual Docs request includes the rendered checks and source or shared-tooling corrections needed to complete the requested document. Rebuild as needed within that request. Completed documents are not refreshed merely because their sources changed. Generated HTML stays reproducible and is never edited by hand.
