# aiagent-plugins

AI agent plugins managed from one source tree. Forge installs into **Claude Code** and **Codex CLI**, and its cross-agent authoring workflow creates shared skill and MCP structures for those agents plus **Antigravity**.

## What's here

| Plugin | Purpose |
|---|---|
| `forge` | Fast, clear agent work with proportional verification: bounded work runs directly, complex work uses focused Execution Plans, and durable contract changes preserve approved meaning. Includes TDD, debugging, cross-agent authoring, UI verification, tone overlays, and request-only Visual Docs. |

```text
plugins/<name>/
  .claude-plugin/plugin.json   # Claude Code manifest
  .codex-plugin/plugin.json    # Codex manifest
  skills/<skill>/SKILL.md      # shared Agent Skills source
  hooks/                       # Optional trusted SessionStart bootstrap (forge)
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
| `writing-plans` | Plans complex work through clear outcomes, dependencies, completion checks and useful source links |
| `executing-plans` | Executes plan Tasks with checkpoints while keeping the plan a work source rather than project SOT |
| `test-driven-development` | Test-first method when requested, required, or useful; ordinary changes use appropriate outcome checks |
| `systematic-debugging` | Evidence-based investigation, regression protection, and honest distinction between mitigation and confirmed fix |
| `verifying-work` | Matches fresh evidence to the work and affected contracts, with an optional UI reference for state, recovery, accessibility, and rendered checks |
| `visual-docs` | Preserves meaning and sources in Forge visualizations; chooses the format and layout for the reader without bundled visual templates |
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
the 12 active user-execution skills listed above.

Forge does not bundle general web app or website design skills. UI work follows
the existing product and any useful design guidance the user has selected;
installing another design skill is optional. `verifying-work` loads its UI
reference only when needed, and `visual-docs` retains Forge source visualization.

When upgrading an older local dev install, Codex's per-skill copy mode may leave
previous `web-app-design` and `website-design` entries under `~/.agents/skills/`.
Confirm their origin and move obsolete Forge copies outside skill discovery paths
if desired. The installer does not delete same-named user-owned skills. Marketplace
packages and fresh isolated exports contain only the current catalog.

## Canonical Spec and task routing

Forge decides two things independently:

1. **Canonical Spec impact:** does the request change durable project authority such as an interface, schema, workflow, policy, cross-component responsibility, or user-designated permanent decision?
2. **Execution complexity:** would planning help resolve uncertainty, coordinate dependencies, or preserve a useful recovery point? Reuse session planning or an existing work record; create a file when independent review, handoff, or resumption needs one.

| Canonical Spec impact | Execution complexity | Route |
|---|---|---|
| no | low | Quick direct execution with fresh focused evidence |
| no | high | Optional Change Brief + Execution Plan |
| yes | low | Authorized contract change + direct execution |
| yes | high | Authorized contract change + proportionate plan |

`spec` is reserved for permanent Canonical Specs. A Change Brief captures one work request; a Spec Delta records exact pending or already authorized contract changes; an Execution Plan controls implementation order but is not project SOT; Verification Evidence proves a concrete claim. Quality and accurate authority come first. Within that boundary, Forge uses the smallest verification that proves the requested result and affected contract, reuses inspected evidence while the relevant state is unchanged, and stops when the claim and required project gates are proven. Partial implementation does not require or permit marking the whole bundle implemented. Use existing tests and add tests where correctness or regression protection needs them. TDD is optional unless the user or project requires it; prose, styling, and logic-free configuration may use appropriate direct checks.

Forge inspects repository facts and asks only about ambiguity that materially changes the outcome, scope, or authority. Independent questions may be grouped. Clear requests and safe reversible details need no question or Brief file. Concrete user instructions authorize their specified contract meaning; ask again only for unresolved conflicts or added effects. Plans, detailed records, and specialist methods are chosen for the work, not imposed as a ceremony. Delegation follows actual independence, coordination cost, platform capabilities, and user settings without fixed model tiers or a Forge worker cap.

Per-project artifacts: authoritative Canonical Specs live as `forge/spec@3` bundles under `docs/specs/<semantic-bundle-name>/` with lifecycle `approved → implemented`. The bundle path is the human-facing identity. Its root and member filenames describe their content, and one durable contract may use several members listed by the root `Documents` section. Requirement and Acceptance statements are complete headings linked by exact member path and anchor. Optional work input lives at `.forge/work/<work-id>/brief.md` and `spec-delta.md` and stays untracked. When a saved plan is useful, it follows project conventions, usually under `docs/plans/`. Headings, checklists and source-link labels follow the work; there is no fixed Plan parser grammar or repeated full-statement block. Auxiliary progress and task records stay only while useful. Requested local HTML defaults to `.forge/visual-docs/<view-id>/view.html` and remains untracked. Shared handbooks follow the user's location or project convention and remain derived explanations. Promote lasting decisions, research, and root-cause findings before removing work artifacts.

## Validate

```bash
bash scripts/validate.sh
```

Lints plugin skills and repository-local wrappers, validates extensions, and runs strict structured-spec validation with an explicit repository root. CI runs Spec Python suites, Mermaid validation, extension-manager tests, lifecycle checks and isolated install checks.

## Context for work and explanations for people

Forge uses the same project sources to support correct agent work and clear human understanding. Select the contracts, conditions, exceptions, code and tests needed for the task; expand the selection when dependencies or uncertainty require it. Keep source locations with summaries and distinguish approved intent, observed implementation and verified outcomes. Documents explain their subject before accommodating parser metadata; a parser pass alone does not prove their content is sufficient.

The optional `using-forge/scripts/source_context.py` captures selected plain UTF-8 files and checks their later byte changes without a visual template or required source headings. It can also record an explanation artifact's hash. It does not discover dependencies, approve content, certify meaning, or rewrite files. Ordinary work needs no snapshot. See [the source tracking guide](docs/guides/source-context.md) for examples and limitations.

Human explanations answer the reader's questions about purpose, behavior, changes and decisions. Task handoffs emphasize relevant conditions, progress and verification. Both retain access to their underlying sources. Representative workflow evaluations check an agent's actual task outcome and a separate reader's answers, rather than treating source coverage or component presence as comprehension.

## Proportional planning and visual verification

Plans specify outcomes, ownership, dependencies, interfaces, verification, and recovery. They include complete code only where an exact example or shared interface is needed. New or never-implemented contracts use full statement coverage; partial changes to an implemented baseline name affected statements and regression preservation.

Requested Forge visualizations preserve source meaning, conditions and approval states while using the format that fits the reader: in-conversation tables or diagrams, available visualization tools, or directly authored HTML. Visual explanations need no Brief file, Project Map, composition JSON or shared renderer. General visualization requests use current app capabilities without a Forge-specific workflow. Freely authored artifacts can be edited directly; default local HTML lives under `.forge/visual-docs/` and stays untracked.

Forge no longer ships the visual HTML template, managed builder, composition schema or freshness runtime. Existing documents remain usable; requested updates follow a project-owned generator when available or edit the authored document directly. Remove obsolete generator or freshness claims when updating a former managed artifact. If reproducibility or source freshness is requested, verify it with an appropriate project method such as source revision/hash comparison or a retained build command. Check meaning and the actual reading surface; completed documents do not refresh merely because their sources changed.

Behavior changes are evaluated with realistic requests for both correctness and unnecessary process. Mechanical gates check executable interfaces, links, ownership, and side effects; they do not require a particular announcement, test order, or ledger phrase. See [the principle-first audit](docs/research/2026-09-10-forge-principle-first-audit.md) for the rationale.
