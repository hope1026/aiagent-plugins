# forge — Spec-First Process Plugin for Claude Code + Codex (Design)

- **Status:** implemented (2026-07-04 — all sections verified; superpowers replacement pending validation period per §8)
- **Date:** 2026-07-04
- **Repo:** `ai-config-shared` → `plugins/forge/`

## 1. Overview

`forge` is a cross-platform plugin (Claude Code + Codex CLI) that packages a complete, spec-first development process: brainstorm → spec → plan → execute → verify, plus UI-design, base writing-tone, marketing/operations tone overlays, and spec-visualization skills. It is the one plugin to install when starting any new project.

Core philosophy: **the spec is the source of truth**. Code follows the spec; feature changes edit the spec first; verification means checking the implementation against the spec's acceptance criteria.

**Decisions already made (user-approved):**

| Decision | Choice |
|---|---|
| Packaging | New plugin `forge` in this repo; `tone-and-manner` moves into it. `onestar-ai-tools` keeps `ai-council`. |
| Project working dir | `.forge/` at target-repo root |
| Spec location | `docs/specs/` (committed, source of truth) |
| Skill language | English body + Korean trigger keywords in descriptions; skills instruct responding to the user in the user's language |
| Approach | Lean spec-first core (13 skills), not a full superpowers mirror |
| superpowers | Keep installed during forge validation; replace (disable) once forge is stable |

**Non-goals:**

- Not a fork of superpowers — a fresh, smaller skill set that adopts its proven discipline patterns.
- No git-worktree / branch-finishing skills (harness-specific, low value in Codex sandbox).
- No runtime dependency on any harness-specific tool name or hook inside skill bodies.

## 2. Verified platform facts (design constraints)

From research on 2026-07-04 (official docs):

1. **Both harnesses implement the Agent Skills open standard** (agentskills.io): a folder with `SKILL.md`; frontmatter `name` + `description` required; body lazy-loaded.
2. **Codex skill discovery:** `.agents/skills` (CWD → repo root), `~/.agents/skills`, `/etc/codex/skills`. **Symlinks are followed.** Legacy `~/.codex/skills` is uncertain → treat `~/.agents/skills` as canonical, optionally link legacy too.
3. **Codex plugins are official:** `.codex-plugin/plugin.json` + `~/.agents/plugins/marketplace.json` (this repo's existing dual-manifest layout is correct). Invocation: `$skill-name` or implicit description matching.
4. **Claude Code plugins:** `.claude-plugin/plugin.json`; skills invoked as `forge:skill-name` or auto-invoked; hooks auto-discovered from `hooks/hooks.json`.
5. **No SessionStart hook on Codex** → the bootstrap skill must work via description matching alone on Codex; the hook is a Claude-only enhancement. `.codex-plugin/plugin.json` ships `"hooks": {}` to suppress hook auto-discovery (superpowers pattern).
6. **Portability rules** (adopted from superpowers' porting guide, enforced by lint):
   - Skill bodies name **actions, not tools**: "create a todo", "dispatch a subagent", "run in the shell" — never `TodoWrite`, `Task`, `Bash`, `Edit`.
   - Cross-reference skills **by name only** ("use the forge writing-specs skill") — never `@path` includes or `/slash` syntax.
   - Descriptions: third person, "Use when…", triggering conditions ONLY (never summarize the workflow), ≤1024 chars.
   - `SKILL.md` ≤500 lines; material >100 lines goes to `references/`; executables to `scripts/`; one level deep.

## 3. Repo layout

```text
plugins/forge/
  .claude-plugin/plugin.json        # Claude manifest (skills + hooks auto-discovered)
  .codex-plugin/plugin.json         # Codex manifest ("skills": "./skills/", "hooks": {})
  hooks/                            # Claude Code only
    hooks.json                      # SessionStart (startup|clear|compact)
    run-hook.cmd                    # polyglot batch/bash wrapper (superpowers pattern)
    session-start                   # injects skills/using-forge/SKILL.md as context
  skills/
    using-forge/                    # entry point / router
      SKILL.md
      references/codex-tools.md     # Codex tool mapping + env detection
    writing-specs/
      SKILL.md
      references/spec-template.md   # the canonical spec.md template
    writing-plans/SKILL.md
    executing-plans/SKILL.md
    test-driven-development/
      SKILL.md
      references/testing-anti-patterns.md
    systematic-debugging/
      SKILL.md
      references/root-cause-tracing.md
    verifying-work/SKILL.md
    spec-viewer/
      SKILL.md
      assets/viewer-template.html   # fixed HTML shell with content slots
      scripts/build-viewer.sh       # assembles HTML; --offline inlines mermaid
    ui-design/SKILL.md
    writing-tone/
      SKILL.md
      references/style-rules.md     # base natural prose + Strunk core + Korean comms shapes
    marketing-tone/SKILL.md         # marketing/product copy overlay on writing-tone
    operations-tone/SKILL.md        # customer/operations reply overlay on writing-tone
    maintaining-forge/
      SKILL.md
      references/portability-rules.md
plugins/onestar-ai-tools/           # keeps ai-council; tone-and-manner removed
scripts/
  install.sh                        # dev-mode install (see §8)
  validate.sh                       # extended: frontmatter + portability lint (see §8)
.claude-plugin/marketplace.json     # Claude Code marketplace manifest (repo root)
.agents/plugins/marketplace.json    # Codex marketplace manifest (+ forge entry)
.github/workflows/validate.yml      # CI: validate.sh on every push
docs/specs/                         # this repo's own specs (dogfooding)
```

## 4. Per-project working contract

What forge creates inside any target project:

```text
docs/specs/
  001-user-auth/spec.md        # SOURCE OF TRUTH — committed
.forge/
  plans/001-user-auth.md       # implementation plans — committed
  debug/2026-07-04-login-race.md    # root-cause notes — committed
  research/2026-07-03-push-options.md  # investigation notes — committed
  viewer/001-user-auth.html    # generated spec viewer — NOT committed
  scratch/                     # NOT committed
    progress-001.md            # execution ledger (survives compaction)
    task-3-brief.md …          # subagent handoff files
```

- `viewer/` and `scratch/` each contain a self-ignoring `.gitignore` (`*`) so no target-repo `.gitignore` edits are needed (superpowers' sdd-workspace trick; lives in the working tree because agents cannot write into `.git/`).
- Spec dirs are numbered (`NNN-slug`) with fixed artifact names — agents navigate this reliably (spec-kit/Kiro convention).
- Skills refer to "the forge working directory `.forge/`" so a future rename is one find-replace.

## 5. Spec format and spec-first lifecycle

### 5.1 spec.md template (simplified spec-kit × Kiro EARS)

```markdown
# <Feature name>
Status: draft | approved | implemented

## Overview            — 2–4 sentences what & why; Non-goals bullet list
## Requirements        — stable IDs, EARS-style, testable
   R1. WHEN <condition> THE SYSTEM SHALL <behavior>
   R2. …               (ambiguity flagged inline: [NEEDS CLARIFICATION: …])
## Behavior & Flows    — Mermaid flowchart/sequence/state fences (feeds spec-viewer)
## Data & Interfaces   — entity/field tables; API & event contracts as tables
## Acceptance Criteria — AC1..ACn, Given/When/Then, each maps to R-IDs
## Decisions & History — dated log: clarifications, change deltas, rejected options
```

The two load-bearing elements are **stable R-IDs** and **testable EARS/GWT phrasing** — plans and verification both cite them. Diagram sources live in spec.md fences (single source; the HTML viewer lifts them verbatim).

### 5.2 Lifecycle iron laws

1. **No plan without an approved spec. No code without a plan task.** Ceremony scales down — a small change may be a 10-line spec, but the file exists.
2. **Change requests edit the spec first.** New/`MODIFIED`/`REMOVED` requirements recorded in Decisions & History → user approves → plan → code. Never patch code and back-fill the spec.
3. **Implementation discoveries flow back.** If execution reveals a wrong/missing requirement: pause, propose a spec delta, get approval, update spec, continue.
4. **Verification is against the spec.** Walk AC1..ACn with fresh command output as evidence. A mismatch is either a code bug or a spec bug — one of them must change, explicitly.
5. **Status is the gate token:** `draft → approved` (human only) `→ implemented` (set only by verifying-work after all ACs pass). Zero `[NEEDS CLARIFICATION]` markers required to reach approved.
6. **Drift repair is a named operation:** writing-specs has a `sync` mode that reconciles an existing codebase against its spec (brownfield onboarding, spec-kit `/converge` analog).

### 5.3 Ceremony floor (explicit exemption predicate)

Spec-first is exempt ONLY when the change alters no documented or documentable behavior:

- typo / comment / formatting-only changes
- dependency bumps with no API change
- CI/tooling config not affecting build outputs
- pure refactors with no observable behavior change AND existing tests pass

Everything else gets a spec. (Research finding: unmatched ceremony is the #1 spec-driven-development failure mode, but a vague carve-out gets rationalized — hence a closed list.)

## 6. Skill catalog (13 skills)

Every process skill bakes in the superpowers discipline patterns: an **Iron Law** fenced block, **Red Flags** list + rationalization table (`| Excuse | Reality |`), "announce at start" line, checklist→one-todo-per-item, and an explicit **terminal handoff** naming the next skill. Process-flow `dot` graphs only where a decision is non-obvious.

| # | Skill | Purpose | Adapts (verified sources) |
|---|---|---|---|
| 1 | `using-forge` | Entry point: skill-check-before-any-response rule, skill priority, spec-first iron law, `.forge/` layout, platform adaptation table → `references/codex-tools.md`. Claude: injected by SessionStart hook. Codex: implicit matching + recommended AGENTS.md pointer line. | superpowers `using-superpowers` |
| 2 | `writing-specs` | Four modes: **new** (brainstorm→spec via one-question-at-a-time), **change** (spec delta for change requests), **clarify** (resolve `[NEEDS CLARIFICATION]`), **sync** (brownfield drift repair). HARD-GATE: no implementation before approved spec. Terminal handoff → writing-plans. | superpowers `brainstorming` + spec-kit `/specify`,`/clarify` + Kiro approval gates |
| 3 | `writing-plans` | Approved spec → `.forge/plans/NNN-slug.md`. Bite-sized tasks with exact paths, written for "an engineer with zero context"; every task cites R-IDs/AC-IDs (traceability). Handoff → executing-plans. | superpowers `writing-plans` + spec-kit tasks.md |
| 4 | `executing-plans` | Task-by-task execution with review checkpoints; progress ledger `.forge/scratch/progress-NNN.md` (survives compaction); per-task TDD (invokes skill 5); **spec-delta pause rule** (law 3). Subagent dispatch optional — sequential-first so Codex works without `multi_agent`. Handoff → verifying-work. | superpowers `executing-plans`/`subagent-driven-development` |
| 5 | `test-driven-development` | RED-GREEN-REFACTOR iron law; write the failing test first; anti-pattern reference. Usable standalone (bugfixes outside plans). | superpowers `test-driven-development` |
| 6 | `systematic-debugging` | Four phases: reproduce → isolate → root-cause → fix+verify. No fix without an understood, reproduced cause. Findings logged to `.forge/debug/`. | superpowers `systematic-debugging` |
| 7 | `verifying-work` | Before any "done/fixed/passing" claim: run verification commands, read output, then walk AC1..ACn line-by-line with evidence. Flips spec status to `implemented`. Evidence before assertions, always. | superpowers `verification-before-completion` + spec-kit `/analyze` |
| 8 | `spec-viewer` | Renders a spec.md into ONE self-contained tabbed HTML at `.forge/viewer/NNN-slug.html`: Overview / Requirements / Flows (Mermaid) / Data & Interfaces / Acceptance checklist (localStorage) / History. Print-friendly. Regenerable view — never the truth. | New (open niche; stack per §7) |
| 9 | `ui-design` | Declare the visual system before code (type scale, palette, spacing, depth — each with a WHY); concrete numeric floors; named anti-slop ban-list; self-tests (swap/squint/signature); effort calibration (utilitarian vs editorial). | Anthropic `frontend-design` + `artifact-design` + community `interface-design` |
| 10 | `writing-tone` | Base natural prose layer for anything humans read (docs, PRs, commits, UI text, Slack): non-AI-like wording, Strunk core, and Korean engineering-comms voice. Heavy rules in `references/`, read only when writing. | obra `writing-clearly-and-concisely` + existing `tone-and-manner` |
| 11 | `marketing-tone` | Purpose overlay on `writing-tone` for marketing, product, launch, social, and campaign copy: fact-based confidence, trust-building claims, and hype restraint. | New |
| 12 | `operations-tone` | Purpose overlay on `writing-tone` for customer support and operations replies: confirmed status, user impact, action plan, customer action, next update, and restrained root-cause detail. | New |
| 13 | `maintaining-forge` | How to add/edit forge skills: portability rules (§2.6), description-writing rules, template anatomy, validate.sh usage, testing skills with subagents. | superpowers `writing-skills` (lean) |

**Skill routing (encoded in using-forge):** process skills fire before implementation skills. "Build X" → writing-specs. "Fix this bug" → systematic-debugging (+ TDD for the fix). "Is it done?" → verifying-work. UI work inside a task → ui-design. Human-readable prose → writing-tone. Marketing copy → writing-tone plus marketing-tone. Customer or operations replies → writing-tone plus operations-tone.

**Excluded** (and why): code-review skills (harness built-ins cover it; revisit later), git-worktrees / finishing-a-branch (harness-specific), separate brainstorming skill (merged into writing-specs).

## 7. spec-viewer technical design

- **Engine: Mermaid v11 only** — covers flowchart, sequence, state, ER, requirement diagrams; highest LLM syntax reliability; UMD build verified self-contained (no dynamic imports).
- **Assembly, not generation:** the skill ships `assets/viewer-template.html` (fixed shell: tab bar, CSS tokens, print rules, render bootstrap) and `scripts/build-viewer.sh` which splices spec content into slots. The model fills content; it never freestyles the fragile shell and **never emits the mermaid bundle**.
- **Offline strategy:** default `<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js">` (small file); `--offline` flag makes the script `curl` the ~3.4 MB bundle (or ~2.4 MB `@mermaid-js/tiny`) and inline it.
- **Robust rendering:** `mermaid.initialize({startOnLoad:false, securityLevel:'strict'})`; per-block `mermaid.parse(src,{suppressErrors:true})` → valid blocks render via `mermaid.run()`, invalid blocks fall back to the fenced source. One bad diagram never blanks the page.
- **Sections mirror spec.md 1:1**; diagram sources lifted verbatim from spec.md fences, so the HTML cannot structurally diverge from the markdown truth. AC checkboxes persist to localStorage. `@media print` flattens tabs to sequential sections with `page-break-inside: avoid`.
- Styling follows the forge `ui-design` token discipline (dogfooding).

## 8. Distribution, install, validation, migration

### Primary channel: GitHub marketplace (both agents, Windows-safe)

The repo (`github.com/hope1026/aiagent-plugins`) doubles as a plugin **marketplace** for both agents — one skill source, two marketplace manifests at repo root:

| Agent | Marketplace manifest | Install (end user) | Mechanism |
|---|---|---|---|
| Claude Code | `.claude-plugin/marketplace.json` | `/plugin marketplace add hope1026/aiagent-plugins` → `/plugin install forge@hope1026` | Clones/copies into Claude's managed plugin cache; SessionStart hook active |
| Codex | `.agents/plugins/marketplace.json` (exists; add `forge` entry) | `codex plugin marketplace add hope1026/aiagent-plugins --ref main --sparse .agents/plugins --sparse plugins/forge` → `codex plugin add forge@hope1026` | Copies into Codex's managed plugin cache |

- Marketplace installs **copy** files into each agent's managed store — **no symlinks anywhere in the end-user path**, so Windows works out of the box.
- Updates flow through each agent's native update mechanism (marketplace refresh / plugin update) — `git push` to the repo is the release action.
- Hook scripts stay Windows-compatible via the extensionless polyglot `run-hook.cmd` wrapper (§3).
- CI: a GitHub Actions workflow runs `validate.sh` on every push, so a broken skill never reaches the marketplace.

### Dev/iteration channel: install.sh (local checkout)

For editing skills without the marketplace round-trip:

| Platform | Mode | Behavior |
|---|---|---|
| macOS/Linux | `--mode link` (default for dev) | Symlinks: Codex `~/.agents/skills/*` per-skill links (officially followed), Claude `~/.claude/skills/forge`. Edit → instantly live. Hook inactive in Claude link mode (acceptable during iteration). |
| Windows | `--mode copy` (auto-selected) | Deterministic copy; re-run one command after edits. Note: in Git Bash/MSYS, `ln -s` silently degrades to copy anyway, so copy is the honest default. Optional: directory junctions (`mklink /J`, no admin required) as a live-link analog for those who want it. |

Symlinks are an iteration convenience on Unix, never a correctness requirement — the marketplace path is the load-bearing install for all platforms.

### validate.sh (extended) — portability by construction

- frontmatter: `name` + `description` present; description ≤1024 chars, third-person "Use when…" shape
- **banned-token lint** in skill bodies: `TodoWrite`, `Task tool`, `Bash tool`, `@`-path includes, `/skill-name` references
- SKILL.md ≤500 lines; manifests parse as JSON; marketplace entries resolve to existing dirs

### Migration & rollout

1. Build forge; move `tone-and-manner` content into `writing-tone`; remove it from `onestar-ai-tools`; bump both plugin versions; update README.
2. Validation period: superpowers stays installed alongside forge.
3. Once forge is proven: disable/uninstall superpowers in Claude Code (documented step, user-triggered).
4. Note for later dedup: the global `natural-korean-communication` skill overlaps `writing-tone`.

### Tone overlay change

- 2026-07-04 [CHANGE] Added `marketing-tone` and `operations-tone` as purpose-specific overlays on top of `writing-tone`; kept `writing-tone` as the single base natural prose skill instead of adding `natural-writing-tone`.

## 9. Testing the plugin itself

- `validate.sh` green on every commit.
- Smoke test per harness: fresh session in a scratch project → "build a tiny feature X" must trigger writing-specs (not direct coding); "fix this bug" must trigger systematic-debugging; spec-viewer output opens and renders all diagram types offline and via CDN; on Codex, `$writing-specs` explicit invocation works and skills appear in `/skills`.
- Subagent-based skill pressure-testing (per maintaining-forge): give a subagent a task + the skill, check it follows the gates instead of rationalizing around them.
