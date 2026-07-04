---
name: maintaining-forge
description: 'Use when creating, editing, reviewing, or testing forge skills themselves, or changing the forge plugin structure, manifests, hooks, or install scripts. Triggers: "스킬 수정", "스킬 추가", "forge 수정", "플러그인 수정", editing files under plugins/forge/.'
---

# Maintaining Forge

Announce at start: "Using the forge maintaining-forge skill to change forge itself."

Respond to the user in the user's language. Forge skill files themselves stay in English.

## Overview

Forge skills are process documentation that must hold up under pressure on two harnesses (Claude Code and Codex). Editing a skill is releasing software: the mechanical gate is the validator, the behavioral gate is a pressure test, and pushing to the repository IS the release — marketplace users pull whatever is on the main branch.

## Iron Law

```
VALIDATE BEFORE COMMIT. PRESSURE-TEST BEFORE PUSH. PUSH IS RELEASE.
```

No exceptions for "one-line tweaks", "just a typo fix in a gate", or "I'll test it after pushing". A change that skips these gates ships a defect to every installed copy.

## When to Use / When NOT

**Use when:**
- Adding a new skill under `plugins/forge/skills/`
- Editing any SKILL.md, `references/`, `scripts/`, or `assets/` file of a forge skill
- Changing plugin manifests, marketplace entries, hooks, the validator, or install scripts
- Reviewing or pressure-testing a forge skill

**Do NOT use for:**
- Following a forge skill inside a target project — just use that skill
- Writing project specs or prose — use the forge writing-specs skill or the forge writing-tone skill
- Skills that live outside the forge plugin — their conventions may differ

## Skill Anatomy

**Frontmatter** — exactly two fields, `name` and `description`. `name` must equal the directory name. `description` is at most 1024 characters, third person, starts with "Use when", and contains trigger conditions ONLY — situations, symptoms, and Korean keyword triggers — never a summary of the skill's workflow. Rationale: an agent may follow a workflow summary in the description instead of reading the body, executing a shortcut version of the process. On Codex, description matching is the only automatic trigger path, so keyword coverage is load-bearing.

**Section skeleton for process skills:**

```markdown
---
name: <dir-name>
description: Use when <trigger conditions only>. Triggers: "<Korean keywords>", <English cues>.
---

# <Title>

Announce at start: "Using the forge <name> skill..."

## Overview       — core principle, 2-3 sentences
## Iron Law       — fenced block stating the non-negotiable rule
## When to Use / When NOT
## The Process    — numbered phases; each checklist instructs one todo per item
## Working Files  — exact docs/specs/ and .forge/ paths the skill reads and writes
## Red Flags      — | Excuse | Reality | table, at least 5 rows
## Handoff        — names the next forge skill
```

**Splitting rules** — SKILL.md stays at or under 500 lines (aim well under). Reference material beyond roughly 100 lines moves to `references/`, read only when needed. Executables go to `scripts/`, static assets to `assets/`. One directory level deep, no nesting.

**Portability** — bodies name actions, not tools ("create a todo", "dispatch a subagent", "run in the shell"), and cross-reference other skills by name only, as "the forge <name> skill". The full ruleset with the WHY behind each rule, the banned-token list the validator enforces, and the Claude/Codex difference table live in `references/portability-rules.md` — read that file before writing or reviewing any forge file.

## The Editing Loop

1. **Read first.** Read the target skill in full, plus `references/portability-rules.md`. For a new skill, also read one existing process skill as a structural model.
2. **Author the change** per the anatomy above. Adapt discipline patterns from proven sources; never copy harness-specific tool names or paths into a skill body.
3. **Validate.** Run in the shell: `bash scripts/validate.sh` from the repository root. It must print `validate: all checks passed`. A red run blocks commit even when the failing lines name files you did not touch — a push ships the whole plugin, so fix or escalate every failure before proceeding.
4. **Self-check for loopholes.** Search your changed files for banned tokens, then re-read the skill asking one question: "under deadline pressure, how would an agent argue its way around each gate?" Every plausible argument gets an explicit counter in the Red Flags table.
5. **Pressure-test** (see below). Required before push for new skills and for any edit that changes what an agent is instructed to do — gates, Iron Laws, Red Flags, process steps, checklists, or reference rules. Only edits that provably change no instruction (typos, formatting, link fixes) may skip the live test, and the adversarial self-read from step 4 still applies to them.
6. **Commit and push.** Conventional commit message (for example `feat(forge): tighten writing-specs approval gate`). Push is release — marketplace users pull updates from the repository, so only push what you would ship.

**Pre-ship checklist — create one todo per item and check each off with evidence:**

- [ ] Frontmatter has exactly `name` + `description`; name matches the directory
- [ ] Description: third person, starts "Use when", trigger conditions only, Korean keywords included, at most 1024 characters
- [ ] Body names actions not tools; cross-references read "the forge <name> skill"
- [ ] Process skill furniture present: announce line, Iron Law block, Red Flags table with at least 5 rows, terminal handoff
- [ ] SKILL.md at or under 500 lines; heavy material in `references/`; executables in `scripts/`
- [ ] `bash scripts/validate.sh` printed `validate: all checks passed` (fresh run, full output read)
- [ ] Pressure-tested if the change alters any instruction (fallback without subagents: adversarial self-read, noted as pending); adversarial self-read done in every case
- [ ] Committed with a conventional message and pushed

## Pressure-Testing Skills

A skill that only reads well is untested. Write a realistic scenario that tempts an agent to skip the skill's gates — combine at least two pressures such as a deadline, sunk cost ("the code is already written"), or an authority saying "just this once". Dispatch a fresh subagent with the scenario plus the skill content, without saying it is a test, and read what it actually does. Compliance means it followed the gates; anything else is a failure — quote its rationalization verbatim, add a counter to the skill's Red Flags table, and re-test until it complies. If no subagent capability is available, do not fabricate a run: perform the adversarial self-read from step 4 instead and note in the commit message that live pressure-testing is pending.

## The Forge System Map

Keep the whole system in view — a change to one skill often needs a matching handoff or routing edit in another.

| Skill | One line |
|---|---|
| using-forge | Router: check skills before any response; spec-first law; `.forge/` contract; platform adaptation. |
| writing-specs | Brainstorm to approved spec; modes new / change / clarify / sync; hard gate before any code. |
| writing-plans | Approved spec to task-level plan with R-ID / AC-ID traceability. |
| executing-plans | Task-by-task execution with a progress ledger and the spec-delta pause rule. |
| test-driven-development | Failing test before implementation code; red, green, refactor. |
| systematic-debugging | Reproduce, isolate, root-cause, then fix; no fix without an understood cause. |
| verifying-work | Fresh evidence before any completion claim; walks acceptance criteria; sets spec status implemented. |
| spec-viewer | Renders a spec into one self-contained tabbed HTML page under `.forge/viewer/`. |
| ui-design | Declare the visual system before UI code; numeric floors; anti-slop ban list. |
| writing-tone | Prose rules for anything humans read; concise English core plus Korean engineering communication. |
| maintaining-forge | This skill: how forge itself is changed, validated, tested, and released. |

## Working Files

This skill operates on the `ai-config-shared` repository, not a target project.

| What | Path |
|---|---|
| Skill bodies | `plugins/forge/skills/<skill-name>/SKILL.md` |
| Skill support files | `plugins/forge/skills/<skill-name>/references/`, `scripts/`, `assets/` |
| Plugin manifests | `plugins/forge/.claude-plugin/plugin.json`, `plugins/forge/.codex-plugin/plugin.json` |
| Marketplace manifests | `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json` (repo root) |
| Claude-only hooks | `plugins/forge/hooks/` |
| Validator | `scripts/validate.sh` |
| Dev install script | `scripts/install.sh` |
| Pressure-test scenarios and notes | `.forge/scratch/` (gitignored) |

## Red Flags

| Excuse | Reality |
|---|---|
| "It's a one-line wording tweak" | One line can open a loophole every future agent will take. Validate and re-read the gates. |
| "The skill is obviously clear" | Clear to the author is not clear to a fresh agent under pressure. Pressure-test it. |
| "Validate passed, ship it" | The validator checks structure, not behavior. A lint-clean gate can still be rationalized around. |
| "I'll test after pushing" | Push is release. Marketplace users pull the broken version before your test finishes. |
| "A workflow summary in the description will save agents time" | Agents follow the summary and skip the body. Descriptions carry trigger conditions only. |
| "Naming the exact tool is clearer" | Forge runs on two harnesses. A harness-specific tool name makes the other harness fabricate calls or stall. |
| "No subagents here, so skip the test" | The fallback is defined: adversarial self-read, noted as pending live test. Skipping silently is not the fallback. |
| "My edit doesn't touch a gate, so no test needed" | Any instruction text steers behavior. If the diff changes what an agent would do, pressure-test it; the self-read is never optional. |

## Handoff

**Forge change validated, pressure-tested, committed, and pushed. Next: the forge verifying-work skill before telling the user the change works — evidence before assertions.**
