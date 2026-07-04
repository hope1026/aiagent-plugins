# ai-config-shared

Shared AI agent plugins managed from one source tree, usable in both **Claude Code** and **Codex CLI**. Skill files are written once (Agent Skills open standard) and installed into each agent's own structure.

## What's here

| Plugin | Purpose |
|---|---|
| `forge` | Spec-first development process: spec → plan → execute → verify, plus TDD, debugging, UI design, writing tone, and a spec-to-HTML viewer. Install this when starting any project. |

```text
plugins/<name>/
  .claude-plugin/plugin.json   # Claude Code manifest
  .codex-plugin/plugin.json    # Codex manifest
  skills/<skill>/SKILL.md      # shared skill source (one file, both agents)
  hooks/                       # Claude-only SessionStart bootstrap (forge)
.claude-plugin/marketplace.json    # this repo is a Claude Code marketplace
.agents/plugins/marketplace.json   # ...and a Codex marketplace
docs/specs/                    # specs for this repo (spec-first, dogfooded)
.forge/plans/                  # implementation plans for this repo
```

## Install (recommended: GitHub marketplace)

Claude Code:

```text
/plugin marketplace add OnestarLee/ai-config-shared
/plugin install forge@onestar
```

Codex:

```text
codex marketplace add https://github.com/OnestarLee/ai-config-shared
# then install forge from /plugins
```

Marketplace installs copy files into each agent's managed store — no symlinks, works on Windows. Updates: `git push` here, then update the plugin from the agent.

## Install (local dev)

```bash
bash scripts/install.sh                # copy, both agents, all plugins
bash scripts/install.sh --mode link    # symlink: edit repo -> instantly live (macOS/Linux)
bash scripts/install.sh --agent codex --plugin forge
```

- Codex target: per-skill entries in `~/.agents/skills/` + `~/.agents/plugins/marketplace.json`.
- Claude target: `~/.claude/skills/<plugin>`. Note: the forge SessionStart hook only runs for marketplace-installed plugins.
- Windows: `--mode link` is auto-downgraded to copy (symlinks need admin/Developer Mode); re-run install after edits.

## forge skill catalog

| Skill | One line |
|---|---|
| `using-forge` | Entry point: routes any task to the right forge skill; spec-first iron law; `.forge/` contract |
| `writing-specs` | Idea → approved spec (new/change/clarify/sync modes); the spec is the source of truth |
| `writing-plans` | Approved spec → task-level plan; every task cites requirement/acceptance IDs |
| `executing-plans` | Task-by-task execution with checkpoints and a durable progress ledger |
| `test-driven-development` | RED → GREEN → REFACTOR; no implementation without a failing test |
| `systematic-debugging` | Reproduce → isolate → root-cause → fix; no fix without an understood cause |
| `verifying-work` | Evidence before claims; walks acceptance criteria; flips spec to `implemented` |
| `spec-viewer` | Renders a spec as one self-contained tabbed HTML (Mermaid diagrams, AC checklist) |
| `ui-design` | Declared visual system before UI code; numeric floors; anti-slop ban list; self-tests |
| `writing-tone` | Clear prose for humans (Strunk core) + Korean engineering communication |
| `maintaining-forge` | How to add/edit forge skills without breaking cross-agent portability |

## Spec-first lifecycle (the short version)

1. No plan without an approved spec; no code without a plan task.
2. Change requests edit the spec first — never patch code and back-fill.
3. Implementation discoveries pause for an approved spec delta.
4. Verification is against the spec's acceptance criteria, with fresh evidence.
5. Spec status `draft → approved` (human) `→ implemented` (verified only).
6. Drift repair (`sync` mode) reconciles brownfield code against its spec.

Per-project artifacts: specs in `docs/specs/NNN-<slug>/spec.md` (committed); plans/debug/research under `.forge/` (committed); `.forge/scratch/` and `.forge/viewer/` (self-gitignored).

## Validate

```bash
bash scripts/validate.sh
```

Lints every skill: frontmatter shape, description rules (trigger-only, ≤1024 chars, YAML quoting), 500-line cap, and banned harness-specific tokens (portability). CI runs this on every push.
