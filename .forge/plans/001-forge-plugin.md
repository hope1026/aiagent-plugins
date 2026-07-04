# forge Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `forge` plugin — 11 spec-first process skills usable in both Claude Code and Codex — inside `ai-config-shared`, distributed via GitHub marketplace manifests.

**Architecture:** One shared `skills/` tree under `plugins/forge/` with dual manifests (`.claude-plugin/` + `.codex-plugin/`); repo root doubles as marketplace for both agents; `validate.sh` enforces portability mechanically; a Claude-only SessionStart hook injects the `using-forge` router skill.

**Tech Stack:** Markdown (Agent Skills standard), bash, awk, JSON manifests, Mermaid v11, GitHub Actions.

**Spec:** `docs/specs/2026-07-04-forge-plugin-design.md` (approved). Requirement references below cite its sections (§N).

## Global Constraints

- Skill frontmatter: exactly `name` + `description`; description ≤1024 chars, third person, starts "Use when", **trigger conditions only** (never workflow summaries), includes Korean trigger keywords (§ spec 1, 2.6).
- Skill bodies: English; name **actions, not tools** — banned tokens: `TodoWrite`, `Task tool`, `Bash tool`, `Edit tool`, `Write tool`, `@`-path includes, `/slash-skill` references. Cross-reference skills as "the forge <name> skill" (§2.6).
- SKILL.md ≤500 lines; material >100 lines → `references/`; executables → `scripts/`; one level deep (§2.6).
- Every process skill includes: announce line ("Announce at start: 'Using the forge <name> skill…'"), an Iron Law fenced block, Red Flags rationalization table (`| Excuse | Reality |`), checklist→todo instruction, and a terminal handoff naming the next forge skill (§6).
- Skills instruct: respond to the user in the user's language; skill files stay English.
- Working-directory contract in all skills: specs `docs/specs/NNN-slug/spec.md`; plans `.forge/plans/`; debug `.forge/debug/`; research `.forge/research/`; viewer `.forge/viewer/` (gitignored); scratch `.forge/scratch/` (gitignored) (§4).
- All JSON must parse with `jq .`; `bash scripts/validate.sh` must pass at the end of every task.
- Commit after every task (conventional commits).
- Superpowers 6.1.1 source (MIT, for adaptation — read, adapt, never copy paths/tool names verbatim): `/Users/onestar.lee/.claude/plugins/cache/claude-plugins-official/superpowers/6.1.1/skills/`.

---

### Task 1: Scaffolding, manifests, marketplaces, CI

**Files:**
- Create: `plugins/forge/.claude-plugin/plugin.json`
- Create: `plugins/forge/.codex-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Modify: `.agents/plugins/marketplace.json` (add forge entry)
- Create: `.github/workflows/validate.yml`

**Interfaces:**
- Produces: plugin name `forge` v0.1.0; skill dirs expected under `plugins/forge/skills/` by all later tasks.

- [ ] **Step 1: Claude manifest** — `plugins/forge/.claude-plugin/plugin.json`:

```json
{
  "name": "forge",
  "displayName": "Forge",
  "version": "0.1.0",
  "description": "Spec-first development process skills: spec, plan, execute, verify, debug, design, tone, and spec visualization. For Claude Code and Codex.",
  "author": { "name": "Onestar Lee" },
  "skills": "./skills/",
  "keywords": ["spec-first", "process", "tdd", "debugging", "ui-design", "tone", "korean", "codex", "claude-code"]
}
```

- [ ] **Step 2: Codex manifest** — `plugins/forge/.codex-plugin/plugin.json` (note `"hooks": {}` suppresses hook auto-discovery on Codex, §2.5):

```json
{
  "name": "forge",
  "version": "0.1.0",
  "description": "Spec-first development process skills: spec, plan, execute, verify, debug, design, tone, and spec visualization. For Claude Code and Codex.",
  "author": { "name": "Onestar Lee" },
  "skills": "./skills/",
  "hooks": {},
  "interface": {
    "displayName": "Forge",
    "shortDescription": "Spec-first process skills for real projects.",
    "longDescription": "Forge packages a complete spec-first workflow - brainstorm to spec, spec to plan, plan to verified implementation - plus UI design, writing tone, systematic debugging, TDD, and a spec-to-HTML viewer. The spec is the source of truth; code follows it.",
    "developerName": "Onestar Lee",
    "category": "Productivity",
    "capabilities": ["Skills"],
    "defaultPrompt": [
      "Write a spec for this feature before we code.",
      "Render docs/specs/001 as an HTML viewer."
    ]
  }
}
```

- [ ] **Step 3: Claude marketplace** — `.claude-plugin/marketplace.json` (repo root):

```json
{
  "name": "onestar",
  "owner": { "name": "Onestar Lee" },
  "metadata": {
    "description": "Onestar Lee's shared AI plugins",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "forge",
      "source": "./plugins/forge",
      "description": "Spec-first development process skills for Claude Code and Codex.",
      "category": "productivity"
    },
    {
      "name": "onestar-ai-tools",
      "source": "./plugins/onestar-ai-tools",
      "description": "AI council and collaboration skills.",
      "category": "productivity"
    }
  ]
}
```

- [ ] **Step 4: Codex marketplace** — add forge to `.agents/plugins/marketplace.json` `plugins` array (before the existing entry):

```json
{
  "name": "forge",
  "source": { "source": "local", "path": "./plugins/forge" },
  "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
  "category": "Productivity"
}
```

- [ ] **Step 5: CI** — `.github/workflows/validate.yml`:

```yaml
name: validate
on:
  push:
  pull_request:
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: bash scripts/validate.sh
```

- [ ] **Step 6: Verify** — Run: `jq . plugins/forge/.claude-plugin/plugin.json plugins/forge/.codex-plugin/plugin.json .claude-plugin/marketplace.json .agents/plugins/marketplace.json >/dev/null && echo OK` — Expected: `OK`
- [ ] **Step 7: Commit** — `git add -A && git commit -m "feat(forge): scaffold plugin manifests, marketplaces, CI"`

---

### Task 2: validate.sh — the mechanical test harness

**Files:**
- Modify: `scripts/validate.sh` (full rewrite; keep existing behavior for onestar-ai-tools by validating ALL plugins generically)

**Interfaces:**
- Produces: `bash scripts/validate.sh` — exits non-zero listing violations; used as the gate in every later task.

- [ ] **Step 1: Write failing check** — run `bash scripts/validate.sh` after writing the new version but before skills exist; it must PASS on empty skills dir (no skills yet = nothing invalid) and FAIL when given a fixture violation. Create throwaway fixture `plugins/forge/skills/_fixture/SKILL.md` containing `Use the TodoWrite tool` and frontmatter missing `description`.
- [ ] **Step 2: Implement** — `scripts/validate.sh`:

```bash
#!/usr/bin/env bash
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

err() { echo "FAIL: $1"; FAIL=1; }

# 1. JSON manifests parse
for f in "$ROOT_DIR"/plugins/*/.claude-plugin/plugin.json \
         "$ROOT_DIR"/plugins/*/.codex-plugin/plugin.json \
         "$ROOT_DIR"/.claude-plugin/marketplace.json \
         "$ROOT_DIR"/.agents/plugins/marketplace.json; do
  [[ -f "$f" ]] || continue
  jq . "$f" >/dev/null 2>&1 || err "invalid JSON: $f"
done

# 2. Marketplace sources resolve to existing dirs
for f in "$ROOT_DIR"/.agents/plugins/marketplace.json; do
  [[ -f "$f" ]] || continue
  while IFS= read -r p; do
    [[ -d "$ROOT_DIR/$p" ]] || err "marketplace path missing: $p (in $f)"
  done < <(jq -r '.plugins[].source.path // empty' "$f")
done
if [[ -f "$ROOT_DIR/.claude-plugin/marketplace.json" ]]; then
  while IFS= read -r p; do
    [[ -d "$ROOT_DIR/$p" ]] || err "marketplace path missing: $p (.claude-plugin)"
  done < <(jq -r '.plugins[].source | if type == "object" then .source // empty else . end' "$ROOT_DIR/.claude-plugin/marketplace.json" | grep '^\./' || true)
fi

# 3. Skill checks
while IFS= read -r skill; do
  dir="$(dirname "$skill")"
  name="$(basename "$dir")"
  [[ "$name" == _* ]] && continue

  # frontmatter block exists
  head -1 "$skill" | grep -q '^---$' || { err "$name: missing frontmatter"; continue; }
  fm="$(awk '/^---$/{n++; next} n==1{print} n>=2{exit}' "$skill")"

  echo "$fm" | grep -q '^name:' || err "$name: frontmatter missing 'name'"
  echo "$fm" | grep -q '^description:' || err "$name: frontmatter missing 'description'"

  fmname="$(echo "$fm" | sed -n 's/^name:[[:space:]]*//p')"
  [[ "$fmname" == "$name" ]] || err "$name: frontmatter name '$fmname' != dir name"

  desc="$(echo "$fm" | sed -n 's/^description:[[:space:]]*//p')"
  [[ "${#desc}" -le 1024 ]] || err "$name: description ${#desc} chars (>1024)"
  echo "$desc" | grep -qi 'use when' || err "$name: description must contain 'Use when'"

  # body line cap
  lines="$(wc -l < "$skill")"
  [[ "$lines" -le 500 ]] || err "$name: SKILL.md $lines lines (>500)"

  # portability: banned tokens in body (skill files under this plugin only)
  banned='TodoWrite|Task tool|Bash tool|Edit tool|Write tool'
  if grep -nE "$banned" "$skill" >/dev/null; then
    err "$name: banned harness-specific token: $(grep -nE "$banned" "$skill" | head -3 | tr '\n' ' ')"
  fi
  if grep -nE '@(\.|/|skills/)' "$skill" >/dev/null; then
    err "$name: banned @-path include: $(grep -nE '@(\.|/|skills/)' "$skill" | head -3 | tr '\n' ' ')"
  fi
done < <(find "$ROOT_DIR/plugins" -name SKILL.md -not -path '*/node_modules/*')

if [[ "$FAIL" -eq 0 ]]; then
  echo "validate: all checks passed"
else
  exit 1
fi
```

- [ ] **Step 3: Verify fail** — Run with fixture present: `bash scripts/validate.sh` — Expected: `FAIL: _fixture...` lines? No — `_`-prefixed dirs are skipped; rename fixture to `zfixture` temporarily to see failures, confirm both violations reported, then delete the fixture dir.
- [ ] **Step 4: Verify pass** — Run: `bash scripts/validate.sh` — Expected: `validate: all checks passed`
- [ ] **Step 5: Commit** — `git commit -am "feat(forge): portability-linting validate.sh"`

---

### Task 3: Claude SessionStart hook

**Files:**
- Create: `plugins/forge/hooks/hooks.json`
- Create: `plugins/forge/hooks/run-hook.cmd` (adapt verbatim structure from superpowers `hooks/run-hook.cmd` — battle-tested polyglot batch/bash wrapper, MIT)
- Create: `plugins/forge/hooks/session-start` (extensionless bash, §3)

**Interfaces:**
- Consumes: `plugins/forge/skills/using-forge/SKILL.md` (Task 4; hook must tolerate its absence until then).
- Produces: SessionStart context injection on Claude Code.

- [ ] **Step 1: hooks.json**:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start" }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: run-hook.cmd** — read `/Users/onestar.lee/.claude/plugins/cache/claude-plugins-official/superpowers/6.1.1/hooks/run-hook.cmd`, adapt (same polyglot mechanism, forge paths).
- [ ] **Step 3: session-start**:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL="$ROOT/skills/using-forge/SKILL.md"
[[ -f "$SKILL" ]] || exit 0
content="$(cat "$SKILL")"
wrapped="<FORGE_BOOTSTRAP>
You have forge: a spec-first development process.

**Below is the full content of the 'forge:using-forge' skill. For all other forge skills, use the skill mechanism:**

${content}
</FORGE_BOOTSTRAP>"
if command -v jq >/dev/null 2>&1; then
  jq -n --arg ctx "$wrapped" '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$ctx}}'
else
  python3 - "$wrapped" <<'PY'
import json, sys
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": sys.argv[1]}}))
PY
fi
```

- [ ] **Step 4: Verify** — Run: `chmod +x plugins/forge/hooks/session-start plugins/forge/hooks/run-hook.cmd && plugins/forge/hooks/session-start | jq -e '.hookSpecificOutput.hookEventName' ` — Expected: exits 0 with no output before Task 4 (skill absent), then re-verify after Task 4: prints `"SessionStart"`.
- [ ] **Step 5: Commit** — `git commit -am "feat(forge): claude session-start bootstrap hook"`

---

## Skill authoring conventions (Tasks 4–14)

Every skill task follows the same steps — written once here, cited per task:

- [ ] **Step A: Author** the SKILL.md (+ listed reference/asset files) per the task's content spec below, following Global Constraints. Adapt from named sources; do not copy harness-specific text.
- [ ] **Step B: Validate** — Run: `bash scripts/validate.sh` — Expected: `validate: all checks passed`
- [ ] **Step C: Self-check** — grep your own skill for the banned tokens AND read it asking: "could an agent rationalize around the gates?" Tighten if yes.
- [ ] **Step D: Commit** — `git add plugins/forge/skills/<name> && git commit -m "feat(forge): <name> skill"`

Section skeleton for **process** skills (4,5,6,7,8,9,10):

```markdown
---
name: <name>
description: <from task below>
---

# <Title>

<Announce at start line>
## Overview            — core principle, 2-3 sentences
## Iron Law            — fenced block, verbatim from task below
## When to Use / When NOT
## The Process         — numbered phases/steps; checklist items become todos
## Working Files       — exact .forge/ or docs/specs/ paths this skill reads/writes
## Red Flags           — | Excuse | Reality | table, ≥5 rows
## Handoff             — verbatim from task below
```

---

### Task 4: using-forge (router)

**Files:**
- Create: `plugins/forge/skills/using-forge/SKILL.md`
- Create: `plugins/forge/skills/using-forge/references/codex-tools.md`

**Frontmatter description (verbatim):**
`Use when starting any conversation or task - establishes the forge spec-first workflow, how to find and route to forge skills before any response including clarifying questions, and the .forge/ working directory contract. Triggers: any task start, "forge", "포지", "스펙 우선", "작업 시작".`

**Content spec (adapt superpowers `using-superpowers`; §6 skill 1):**
- The Rule: invoke relevant forge skills BEFORE any response or action; 1% doubt → invoke.
- Routing table: "build/change X" → forge writing-specs · "fix bug" → forge systematic-debugging · "is it done?" → forge verifying-work · UI work → forge ui-design · human-readable prose → forge writing-tone · "show me the spec" → forge spec-viewer.
- Spec-first Iron Law (verbatim): ```NO PLAN WITHOUT AN APPROVED SPEC. NO CODE WITHOUT A PLAN TASK. THE SPEC IS THE SOURCE OF TRUTH.```
- Ceremony floor: closed exemption list from spec §5.3, verbatim.
- Working directory contract table (spec §4 paths).
- Red flags table (≥6 rows, adapt superpowers' rationalization patterns: "just a simple question", "I'll explore first", "skill is overkill"…).
- Platform Adaptation section: "If running in Codex, read references/codex-tools.md."
- User instructions precedence note; respond in the user's language.
- `references/codex-tools.md`: adapt superpowers' codex-tools.md — multi_agent config for subagents, `$skill` invocation, sequential fallback rule ("if no subagent capability, execute sequentially; never fabricate tool calls"), plus mapping table: create a todo → `update_plan`, run in shell → `shell`, edit files → `apply_patch`.

Steps: A–D above.

---

### Task 5: writing-specs

**Files:**
- Create: `plugins/forge/skills/writing-specs/SKILL.md`
- Create: `plugins/forge/skills/writing-specs/references/spec-template.md`

**Frontmatter description (verbatim):**
`Use when creating features, changing any behavior, starting a project, or when requirements are unclear - BEFORE any plan or implementation. Also use for spec change requests, resolving [NEEDS CLARIFICATION] markers, or syncing a spec with existing code (drift repair). Triggers: "스펙", "스펙 작성", "기능 추가", "기능 변경", "요구사항", "설계", "brainstorm", "new feature", "change request".`

**Content spec (adapt superpowers `brainstorming` + spec-kit specify/clarify + Kiro gates; spec §5, §6 skill 2):**
- HARD-GATE fenced block: no implementation skill, no code, no scaffolding until spec approved by the user.
- Four modes with a mode-selection table: **new** / **change** / **clarify** / **sync**.
  - new: explore context → one question at a time (multiple choice preferred) → 2-3 approaches with recommendation → write spec from references/spec-template.md → self-review (placeholders, contradictions, ambiguity, scope) → user approval gate → status: approved.
  - change: locate spec → draft delta (MODIFIED/REMOVED/ADDED R-IDs) → record in Decisions & History → user approval → hand to writing-plans. Never patch code first.
  - clarify: enumerate `[NEEDS CLARIFICATION]`, resolve each via one question, remove markers; approved requires zero markers.
  - sync: read code, diff behavior vs spec, append deltas to spec with `[DRIFT]` tag in History, propose reconciliation (spec change vs code fix) per item.
- Spec numbering: next `NNN` in `docs/specs/`; dir `docs/specs/NNN-<slug>/spec.md`.
- Scale rule: small change = small spec, but the file exists.
- Red flags: "the change is too small for a spec" / "I'll spec it after coding" / "user seems in a hurry" rows.
- Handoff (verbatim): "**Spec approved. The next step is the forge writing-plans skill — do not start coding directly.**"
- `references/spec-template.md`: the full template from spec §5.1 with EARS examples (2 filled example requirements, 1 filled GWT acceptance criterion, 1 example mermaid flowchart fence + 1 sequence fence, example Data & Interfaces table, History entry format `- 2026-07-04 [CHANGE] R3 MODIFIED: ...`), plus Status line semantics (draft/approved/implemented, who may set each — spec §5.2 law 5).

Steps: A–D.

---

### Task 6: writing-plans

**Files:**
- Create: `plugins/forge/skills/writing-plans/SKILL.md`

**Frontmatter description (verbatim):**
`Use when an approved spec exists and implementation needs a task-level plan, before touching any code. Triggers: "구현 계획", "계획 작성", "plan", "implementation plan", an approved spec with no plan.`

**Content spec (adapt superpowers `writing-plans` + spec-kit tasks; §6 skill 3):**
- Precondition gate: spec exists with `Status: approved` — otherwise stop and use the forge writing-specs skill.
- Plan location: `.forge/plans/NNN-<slug>.md` (same NNN as spec).
- Zero-context engineer framing; bite-sized steps (one action each); exact paths; complete code in steps; no placeholders list (TBD/TODO/"similar to Task N"/"add error handling").
- **Traceability rule (the forge addition): every task header cites the R-IDs and AC-IDs it implements; every AC-ID must appear in ≥1 task — include a coverage table at the plan top: | AC | Tasks |.**
- Header template (goal/architecture/stack/global constraints) + task structure template (Files/Interfaces Consumes-Produces/steps with test-first cycle).
- Self-review: spec coverage, placeholder scan, type consistency.
- Handoff (verbatim): "**Plan complete and saved. Next: the forge executing-plans skill, task by task with checkpoints.**"

Steps: A–D.

---

### Task 7: executing-plans

**Files:**
- Create: `plugins/forge/skills/executing-plans/SKILL.md`

**Frontmatter description (verbatim):**
`Use when a written implementation plan exists in .forge/plans/ and tasks need to be executed with review checkpoints and a durable progress ledger. Triggers: "계획 실행", "구현 진행", "execute the plan", "다음 태스크", resuming interrupted plan work.`

**Content spec (adapt superpowers `executing-plans`; §6 skill 4):**
- Startup: read plan; read/create ledger `.forge/scratch/progress-NNN.md` (create `.forge/scratch/.gitignore` containing `*` if missing); skip tasks already marked complete.
- Per task loop: read task → per-step execution; implementation steps REQUIRE the forge test-driven-development skill → run task verification → append ledger line `Task N: complete (commits <a>..<b>)` → checkpoint report to user every task (or batch of parallel-safe tasks).
- Iron Law (verbatim): ```FOLLOW THE PLAN. WHEN REALITY DIVERGES FROM THE SPEC, STOP AND PROPOSE A SPEC DELTA — NEVER SILENTLY ADAPT.``` (spec §5.2 law 3: pause → delta via the forge writing-specs skill change mode → approval → continue.)
- Subagent option: "If subagent capability is available, dispatch one fresh subagent per task with the task text + Interfaces block; review between tasks. If not available, execute sequentially yourself. Never fabricate subagent calls." (Codex `multi_agent` note lives in using-forge's codex-tools.md.)
- Red flags: "this task is obviously wrong, I'll just fix it inline" / "spec delta is overkill for this".
- Handoff (verbatim): "**All tasks complete. Next: the forge verifying-work skill against the spec's acceptance criteria.**"

Steps: A–D.

---

### Task 8: test-driven-development

**Files:**
- Create: `plugins/forge/skills/test-driven-development/SKILL.md`
- Create: `plugins/forge/skills/test-driven-development/references/testing-anti-patterns.md`

**Frontmatter description (verbatim):**
`Use when implementing any feature or bugfix, before writing implementation code. Triggers: "TDD", "테스트 먼저", "테스트 작성", writing new functions, fixing bugs, "구현해줘" for testable code.`

**Content spec (adapt superpowers `test-driven-development`; §6 skill 5):**
- Iron Law (verbatim): ```NO IMPLEMENTATION CODE WITHOUT A FAILING TEST. RED → GREEN → REFACTOR.```
- Cycle: write ONE failing test → run it, SEE it fail with the expected error → minimal code to pass → run, see pass → refactor → run again → commit.
- "Seeing it fail is the point" — a test that passes immediately tests nothing.
- When NOT: throwaway scripts, pure config, generated code; spike-then-test rule (delete the spike, keep the tests).
- Red flags: "I'll write tests after" / "too simple to test" / "the test would just duplicate the code".
- `references/testing-anti-patterns.md`: adapt superpowers' file — testing implementation details, mocking what you own, assertion-free tests, snapshot overuse, test interdependence, sleeping instead of waiting on conditions.

Steps: A–D.

---

### Task 9: systematic-debugging

**Files:**
- Create: `plugins/forge/skills/systematic-debugging/SKILL.md`
- Create: `plugins/forge/skills/systematic-debugging/references/root-cause-tracing.md`

**Frontmatter description (verbatim):**
`Use when encountering any bug, test failure, error, or unexpected behavior, before proposing or applying any fix. Triggers: "버그", "디버깅", "에러", "원인", "안 돼", "이상해", test failures, crashes, wrong output.`

**Content spec (adapt superpowers `systematic-debugging`; §6 skill 6):**
- Iron Law (verbatim): ```NO FIX WITHOUT A REPRODUCED, UNDERSTOOD ROOT CAUSE.```
- Four phases: 1 Reproduce (minimal, deterministic) → 2 Isolate (bisect layers/inputs/time; instrument, read actual values) → 3 Root-cause (trace backward from symptom to first wrong state; "why" ×5; verify the hypothesis makes the symptom appear AND disappear) → 4 Fix + verify (fix the cause not the symptom; add the regression test via the forge test-driven-development skill; confirm original repro passes).
- Debug note: on non-trivial bugs write `.forge/debug/YYYY-MM-DD-<slug>.md` — symptom, repro, root cause, fix, regression test path.
- Red flags: "I see the problem, quick fix" / "it's probably X, let me try" / "adding a null check should do it" / "can't reproduce but the fix looks right".
- `references/root-cause-tracing.md`: adapt superpowers' — backward tracing technique, first-wrong-state discipline, instrumentation patterns.

Steps: A–D.

---

### Task 10: verifying-work

**Files:**
- Create: `plugins/forge/skills/verifying-work/SKILL.md`

**Frontmatter description (verbatim):**
`Use when about to claim work is complete, fixed, passing, or done - before committing, creating PRs, reporting progress, or setting a spec to implemented. Triggers: "완료", "검증", "다 됐어?", "확인해줘", "verify", "done", finishing any plan or fix.`

**Content spec (adapt superpowers `verification-before-completion` + spec-kit analyze; §6 skill 7):**
- Iron Law (verbatim): ```NO COMPLETION CLAIM WITHOUT FRESH VERIFICATION EVIDENCE. EVIDENCE BEFORE ASSERTIONS, ALWAYS.```
- Two levels: (1) command-level — run the actual build/test/lint commands NOW, read full output, no cached/remembered results; (2) spec-level — open the spec, walk AC1..ACn, for each record verdict PASS/FAIL + the exact command output or observation as evidence.
- Verdict handling: any AC FAIL → either code bug (fix via the forge systematic-debugging skill) or spec bug (delta via the forge writing-specs skill change mode) — one must change, explicitly; never both silently.
- Only after all ACs PASS: set spec `Status: implemented` and report the AC table to the user.
- Report format template: | AC | Verdict | Evidence |.
- Red flags: "tests passed earlier" / "the diff looks right" / "I'm confident it works" / "user is waiting, skip the rerun".

Steps: A–D.

---

### Task 11: spec-viewer

**Files:**
- Create: `plugins/forge/skills/spec-viewer/SKILL.md`
- Create: `plugins/forge/skills/spec-viewer/assets/viewer-template.html`
- Create: `plugins/forge/skills/spec-viewer/scripts/build-viewer.sh`

**Interfaces:**
- Consumes: spec.md structure from Task 5's template (section names must match exactly).
- Produces: `.forge/viewer/NNN-<slug>.html` self-contained viewer.

**Frontmatter description (verbatim):**
`Use when a spec needs to be rendered for human review as a self-contained HTML document with diagrams, tables, and an acceptance checklist, or when the user asks to visualize or present a spec. Triggers: "스펙 시각화", "스펙 보여줘", "spec html", "스펙 뷰어", "다이어그램으로", reviewing a spec with a human.`

- [ ] **Step 1: viewer-template.html** — single-file shell with slots `{{TITLE}}`, `{{STATUS}}`, `{{GENERATED}}`, `{{MERMAID}}`, `{{CONTENT}}`:
  - CSS custom-property tokens (background/surface/text/accent/border, dark-mode via `prefers-color-scheme`), system font stack, 65ch measure for prose, real type scale (1.25 ratio).
  - Tab bar (`<nav>` buttons) + `<section class="tab-panel" id="...">` panels; vanilla JS toggling `hidden`; hash-based deep links (`#flows`).
  - Fixed tab set matching spec.md sections: Overview · Requirements · Flows · Data & Interfaces · Acceptance · History.
  - Mermaid bootstrap: `mermaid.initialize({startOnLoad:false, securityLevel:'strict', theme:'neutral'})`; for each `pre.mermaid`, `await mermaid.parse(src,{suppressErrors:true})` → valid: render via `mermaid.run({nodes:[el]})`; invalid: replace with `<pre class="mermaid-error">` showing source. Render on first tab activation (and on load for the active tab).
  - Acceptance panel: `<label><input type="checkbox" data-ac="AC1">…` persisted to `localStorage` keyed by document title.
  - `@media print`: hide nav, show all panels sequentially with their titles as h2, `page-break-inside: avoid` on `table, pre, svg`.
- [ ] **Step 2: build-viewer.sh**:

```bash
#!/usr/bin/env bash
set -euo pipefail
usage() { echo "usage: build-viewer.sh -c content.html -t 'Title' -s 'status' -o out.html [--offline]"; exit 2; }
CONTENT="" TITLE="" STATUS="" OUT="" OFFLINE=0
while [[ $# -gt 0 ]]; do case "$1" in
  -c) CONTENT="$2"; shift 2;; -t) TITLE="$2"; shift 2;; -s) STATUS="$2"; shift 2;;
  -o) OUT="$2"; shift 2;; --offline) OFFLINE=1; shift;; *) usage;;
esac; done
[[ -f "$CONTENT" && -n "$TITLE" && -n "$OUT" ]] || usage
TPL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/assets/viewer-template.html"
MERMAID_TMP="$(mktemp)"
trap 'rm -f "$MERMAID_TMP"' EXIT
if [[ "$OFFLINE" -eq 1 ]]; then
  echo "<script>" > "$MERMAID_TMP"
  curl -fsSL "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js" >> "$MERMAID_TMP"
  echo "</script>" >> "$MERMAID_TMP"
else
  echo '<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>' > "$MERMAID_TMP"
fi
mkdir -p "$(dirname "$OUT")"
awk -v title="$TITLE" -v status="$STATUS" -v generated="$(date +%Y-%m-%d)" \
    -v content_file="$CONTENT" -v mermaid_file="$MERMAID_TMP" '
  /\{\{CONTENT\}\}/ { while ((getline line < content_file) > 0) print line; close(content_file); next }
  /\{\{MERMAID\}\}/ { while ((getline line < mermaid_file) > 0) print line; close(mermaid_file); next }
  { gsub(/\{\{TITLE\}\}/, title); gsub(/\{\{STATUS\}\}/, status); gsub(/\{\{GENERATED\}\}/, generated); print }
' "$TPL" > "$OUT"
echo "built: $OUT"
```

- [ ] **Step 3: SKILL.md** — process: read spec.md → author `content.html` fragment in `.forge/scratch/` (panels in fixed tab order; lift mermaid fences verbatim into `<pre class="mermaid">`; markdown tables → HTML tables; requirements as a table with R-ID anchor ids; ACs as checkboxes with GWT text) → run build-viewer.sh → output `.forge/viewer/NNN-<slug>.html` (ensure `.forge/viewer/.gitignore` with `*`) → tell the user the path and offer `--offline`. Rules: NEVER hand-write the HTML shell or emit the mermaid bundle; the HTML is a VIEW — if it looks wrong, fix spec.md or the fragment, the spec stays the truth. Escape raw `<` in spec text.
- [ ] **Step 4: Test end-to-end** — create `.forge/scratch/test-spec-content.html` with one panel containing a valid flowchart fence, one with an INVALID mermaid block, one table, two AC checkboxes; run `bash plugins/forge/skills/spec-viewer/scripts/build-viewer.sh -c .forge/scratch/test-spec-content.html -t "Test Spec" -s draft -o .forge/scratch/test-viewer.html`; Expected: `built:` line; `grep -c 'cdn.jsdelivr' .forge/scratch/test-viewer.html` = 1; open in browser (or headless) → tabs switch, valid diagram renders as SVG, invalid block shows source not a blank page. Repeat with `--offline`: `grep -c 'cdn.jsdelivr' ` = 0 and file >2MB.
- [ ] **Step 5: Validate + commit** — Steps B–D.

---

### Task 12: ui-design

**Files:**
- Create: `plugins/forge/skills/ui-design/SKILL.md`

**Frontmatter description (verbatim):**
`Use when designing or implementing any user interface - web pages, components, dashboards, HTML artifacts, slides - or reviewing UI work. Triggers: "UI", "디자인", "화면", "예쁘게", "프론트", "landing page", "component", CSS/styling work.`

**Content spec (adapt Anthropic frontend-design + artifact-design + community interface-design; §6 skill 9):**
- Step 0 — effort calibration: utilitarian (docs, admin, internal tools) vs editorial (landing, marketing, showcase); same craft, different treatment.
- MANDATORY pre-code checkpoint — declare the visual system in a visible block before any UI code: Intent (one sentence, evocative not generic), Type scale (ratio 1.2–1.333; weight/color do hierarchy work before size), Palette (60/30/10 neutral/secondary/accent; greys carry a hue bias toward the accent), Spacing (one density decision in px), Depth (pick ONE strategy: borders OR shadows OR layering — commit), Signature (one element another AI would not produce). "If you can't explain why, stop — you're defaulting."
- Hard floors: hit targets ≥44px; body ≥16px web / ≥24px slides; motion <300ms, `transform`/`opacity` only, never `transition: all`; tabular numbers for changing values; layout via flexbox/grid `gap`, not per-element margins.
- Anti-slop ban list (named, verbatim-ish): default Inter/Roboto without a reason, purple-gradient-on-white, cream+terracotta "AI palette", `rounded-lg` on everything, emoji as section markers, rounded-card-with-left-border, centered-everything, CSS silhouettes faking product shots.
- Self-tests before presenting: swap test (would this work for any product? then it's not designed), squint test (hierarchy visible when blurred?), signature test (point to the distinctive element), token test (read the CSS variable names aloud — do they evoke this product?).
- "Spend your boldness in one place" rule; verify in a real browser when possible.

Steps: A–D.

---

### Task 13: writing-tone (absorbs tone-and-manner)

**Files:**
- Create: `plugins/forge/skills/writing-tone/SKILL.md`
- Create: `plugins/forge/skills/writing-tone/references/style-rules.md`
- Delete: `plugins/onestar-ai-tools/skills/tone-and-manner/` (entire dir)
- Modify: `plugins/onestar-ai-tools/.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` (version → 0.2.0, description/keywords drop tone)

**Frontmatter description (verbatim):**
`Use when writing or editing anything humans will read - documentation, README, PR descriptions, commit messages, error messages, UI copy, Slack messages, emails, reports - in any language, especially Korean technical communication. Triggers: "톤앤매너", "말투", "자연스럽게", "문서", "메시지 작성", "리드미", drafting or reviewing prose.`

**Content spec (obra writing-clearly-and-concisely structure + existing tone-and-manner content; §6 skill 10):**
- SKILL.md is a small index (<80 lines): the four core rules bolded — **use active voice; put statements in positive form; use definite, specific, concrete language; omit needless words** — plus "lead with the point", and the rule "read references/style-rules.md before writing any substantial prose; for short messages apply the core rules directly".
- `references/style-rules.md` two parts: (1) English prose mechanics — condensed Strunk principles (the 11 composition principles, one line + example each); (2) Korean engineering communication — port the ENTIRE current `plugins/onestar-ai-tools/skills/tone-and-manner/SKILL.md` body (voice rules, editing rules, message shapes for status/review/Slack/PR) verbatim-adapted.
- Limited-context strategy (from obra): if the reference won't fit, draft with judgment, then dispatch a subagent with the draft + reference to copyedit (if subagents unavailable, re-read only part 2 for Korean output).

Steps: A–D (Step D also commits the tone-and-manner deletion + manifest bumps: `git commit -m "feat(forge): writing-tone skill; retire onestar-ai-tools tone-and-manner"`).

---

### Task 14: maintaining-forge

**Files:**
- Create: `plugins/forge/skills/maintaining-forge/SKILL.md`
- Create: `plugins/forge/skills/maintaining-forge/references/portability-rules.md`

**Frontmatter description (verbatim):**
`Use when creating, editing, reviewing, or testing forge skills themselves, or changing the forge plugin structure, manifests, hooks, or install scripts. Triggers: "스킬 수정", "스킬 추가", "forge 수정", "플러그인 수정", editing files under plugins/forge/.`

**Content spec (lean superpowers `writing-skills`; §6 skill 11):**
- Skill anatomy (frontmatter rules incl. description=triggers-only rationale: "an agent may follow a workflow summary in the description instead of reading the body"); section skeleton (this plan's conventions section); when to add references/ (>100 lines) and scripts/.
- Editing loop: edit → `bash scripts/validate.sh` → pressure-test by giving a fresh subagent a realistic task + the skill, checking it follows gates instead of rationalizing (adapt superpowers' testing-skills-with-subagents idea, one paragraph) → commit → push (push = release; marketplace users pull updates).
- The 11-skill map (one line each) so maintainers see the whole system.
- `references/portability-rules.md`: full portability ruleset from Global Constraints + WHY for each rule + the banned-token list mirroring validate.sh + Codex/Claude difference table (invocation, hooks, subagents, install paths).

Steps: A–D.

---

### Task 15: install.sh (dev mode) + README

**Files:**
- Modify: `scripts/install.sh` (generalize to both plugins; Windows-safe)
- Modify: `README.md` (structure, marketplace install commands for both agents, dev-mode instructions, forge overview + skill table)

**Interfaces:**
- Consumes: plugin dirs from Tasks 1–14.

- [ ] **Step 1: install.sh** — extend the existing script:
  - `--plugin forge|onestar-ai-tools|all` (default all), keep `--agent`, `--mode copy|link`.
  - Codex target: per-skill entries under `~/.agents/skills/<skill-name>` (link mode: `ln -s`; copy mode: `cp -R`) + marketplace copy to `~/.agents/plugins/marketplace.json` as today.
  - Claude target: `~/.claude/skills/<plugin>` whole-tree (as today).
  - Windows guard at top: `case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) [[ "$MODE" == "link" ]] && { echo "note: symlinks unreliable on Windows; forcing --mode copy"; MODE=copy; };; esac`
  - Print per-agent "installed" lines + a final hint: "marketplace install (recommended): see README".
- [ ] **Step 2: Test** — `HOME=$(mktemp -d) bash scripts/install.sh --mode link && ls -la $HOME/.agents/skills/ | head` — Expected: symlinks for all 11 forge skills + ai-council; re-run with `--mode copy` → real dirs. (Set HOME inline for the test only.)
- [ ] **Step 3: README** — sections: What's here (plugin table) · Install via GitHub marketplace (Claude: `/plugin marketplace add OnestarLee/ai-config-shared` → `/plugin install forge@onestar`; Codex: `codex marketplace add https://github.com/OnestarLee/ai-config-shared` → `/plugins`) · Local dev install (install.sh flags, Windows note) · forge skill catalog table (11 rows) · spec-first lifecycle summary (6 laws, one line each) · Validate/CI.
- [ ] **Step 4: Validate + commit** — `bash scripts/validate.sh && git commit -am "feat(forge): dev install script + README"`

---

### Task 16: Final verification & release

**Files:** none new.

- [ ] **Step 1: Full validation** — Run: `bash scripts/validate.sh` — Expected: `validate: all checks passed`.
- [ ] **Step 2: AC walkthrough** — use the forge process manually (dogfood verifying-work): check each spec §6 skill row exists with matching description; hook emits valid JSON containing "using-forge" content; viewer test artifacts render (Task 11 Step 4 outputs); banned-token grep over all skills returns nothing; `wc -l` all SKILL.md ≤500.
- [ ] **Step 3: Claude smoke test** — `claude plugin marketplace add "$(pwd)"` (or `/plugin marketplace add` in a session) + install forge; new session in a scratch dir: "간단한 기능 만들어줘" must route to writing-specs, not direct coding. Record result.
- [ ] **Step 4: Codex smoke test** (if codex CLI available) — `codex marketplace add "$(pwd)"` or dev symlinks; `/skills` lists forge skills; `$writing-specs` invokes. Record result; if codex unavailable locally, note as deferred.
- [ ] **Step 5: Push** — `git push origin main` (push = marketplace release).
- [ ] **Step 6: Report** — AC table + smoke results to the user; superpowers stays installed during validation period (spec §8 migration step 2).

---

## AC coverage

| Spec element | Tasks |
|---|---|
| §3 layout, manifests, CI | 1 |
| §8 validate/portability lint | 2 |
| §2.5/§3 hook | 3 |
| §6 skills 1–11 | 4,5,6,7,8,9,10,11,12,13,14 |
| §4 working contract encoded in skills | 4,5,6,7,9,10,11 |
| §5 lifecycle laws encoded | 4 (law 1), 5 (laws 1,2,6), 7 (law 3), 10 (laws 4,5) |
| §7 viewer stack | 11 |
| §8 distribution/install/README | 1, 15 |
| §8 migration (tone move) | 13 |
| §9 testing | 2, 11, 16 |
