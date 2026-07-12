# Forge Portability Rules

Every forge skill must work unmodified on both Claude Code and Codex. These rules are what makes that true. The validator (`scripts/validate.sh`) enforces the mechanical subset; the rest is discipline. Each rule comes with its WHY — if you understand the failure a rule prevents, you will not be tempted to bend it.

Note on scope: the validator lints `SKILL.md` files only. This reference file may spell out banned tokens verbatim (it must, to document them); skill bodies must not contain them.

## 1. Frontmatter: exactly `name` and `description`

- `name` must equal the skill's directory name.
- No other fields.

**WHY:** Both harnesses implement the Agent Skills open standard, whose portable intersection is these two fields. Extra fields are at best ignored and at worst rejected by one harness. A name/directory mismatch breaks invocation-by-name.

## 2. Description: triggers only, third person, "Use when", ≤1024 chars, Korean keywords

- Starts with "Use when".
- Written in third person (it is injected into a system prompt).
- Contains ONLY triggering conditions: situations, symptoms, keywords. Ends with a `Triggers:` list including Korean keywords.
- NEVER summarizes the skill's process or workflow.

**WHY, rule by rule:**
- *Triggers only:* an agent may follow a workflow summary in the description instead of reading the body — it executes the two-line summary and skips the gates the body defines. Tested and observed; this is the single most damaging description mistake.
- *"Use when" + keywords:* the description is how an agent decides whether to load the body. On Codex there is no session-start hook, so description matching is the ONLY automatic trigger path — keyword coverage (including Korean, the user's working language) is load-bearing, not decoration.
- *≤1024 chars:* the standard's limit; longer descriptions fail to load.

## 3. Bodies in English; respond in the user's language

Skill files stay English (single maintained source, best model reliability). Every skill instructs the agent to respond to the user in the user's language, so the runtime experience adapts without forking the files.

## 4. Name actions, not tools — the banned-token list

Skill bodies describe WHAT to do, never WHICH harness tool does it.

Banned tokens (mirrors the validator's grep exactly):

```
TodoWrite | Task tool | Bash tool | Edit tool | Write tool
```

Also banned: `@`-path includes — anything matching `@.`, `@/`, or `@skills/`.

Write the action instead:

| Write this | Never this |
|---|---|
| create a todo / create one todo per checklist item | the todo-list tool by its Claude name |
| dispatch a subagent | the agent-dispatch tool by its Claude name |
| run in the shell | the shell tool by its Claude name |
| edit the file / write the file | the file-editing tools by their Claude names |

**WHY:** tool names differ per harness. Codex uses `update_plan` (todos), `shell` (commands), `apply_patch` (edits), and subagents only exist there under a `multi_agent` configuration. A hardcoded Claude tool name makes a Codex agent fabricate a nonexistent tool call or stall; an action name lets each harness bind its own tool. The forge using-forge skill carries the Codex mapping in its own reference file.

## 5. Cross-reference skills by name only

Refer to other skills as "the forge <name> skill" — e.g. "the forge writing-specs skill".

- Never `@`-path includes: they force-load files immediately (burning context before it is needed), and install paths differ per harness and per install mode, so the path is wrong somewhere.
- Never slash-command syntax: it is Claude-specific surface; on Codex invocation is `$skill-name` or implicit matching, so a slash reference points at nothing.

**WHY:** a name reference survives every install layout and lets each harness resolve the skill through its own mechanism.

## 6. Size and layout

- `SKILL.md` ≤500 lines (validator-enforced); aim well under.
- Reference material >100 lines → `references/`.
- Executables → `scripts/`; static assets → `assets/`.
- One level deep — no nested skill directories.

**WHY:** bodies are lazy-loaded but read whole; a bloated body taxes every invocation, while references are read only when needed. Fixed, shallow layout means agents navigate skills without exploration.

## 7. Working-directory contract (exact paths)

All skills cite the same paths so they can hand off to each other with no shared session state:

| Artifact | Path | Committed? |
|---|---|---|
| Specs (source of truth) | `docs/specs/NNN-<slug>/spec.md` | yes |
| Implementation plans | `.forge/plans/NNN-<slug>.md` | yes |
| Debug / root-cause notes | `.forge/debug/YYYY-MM-DD-<slug>.md` | yes |
| Research notes | `.forge/research/` | yes |
| Generated spec viewers | `.forge/viewer/` | no — self-ignoring `.gitignore` (`*`) |
| Scratch, ledgers, subagent briefs | `.forge/scratch/` | no — self-ignoring `.gitignore` (`*`) |

**WHY:** numbered dirs with fixed artifact names are navigable without search; the self-ignoring `.gitignore` trick avoids editing the target repo's own ignore file. Skills say "the forge working directory `.forge/`" so a future rename is one find-replace.

## 8. Process-skill discipline furniture

Every process skill includes: an announce line, an Iron Law fenced block, a Red Flags `| Excuse | Reality |` table (≥5 rows), a create-one-todo-per-checklist-item instruction wherever a checklist appears, and a terminal Handoff naming the next forge skill.

**WHY:** agents under pressure rationalize around soft guidance. Explicit counters to specific excuses, and an unambiguous next step, are the patterns that measurably survive pressure-testing.

## 9. Mechanical gates

- All JSON manifests must parse with `jq .`.
- `bash scripts/validate.sh` must print `validate: all checks passed` before every commit.

**WHY:** CI runs the same script on every push, and push is release — a red validator on main means every marketplace user pulls a broken plugin.

## Claude Code vs Codex differences

| Aspect | Claude Code | Codex |
|---|---|---|
| Skill invocation | `forge:skill-name` or automatic description matching; session-start injection of using-forge | `$skill-name` or implicit description matching only |
| Hooks | Auto-discovered from `plugins/forge/hooks/hooks.json`; SessionStart injects the using-forge body | No hook support; `.codex-plugin/plugin.json` omits the unsupported `hooks` field |
| Subagents | Native subagent dispatch available | Only under `multi_agent` configuration; otherwise execute sequentially — never fabricate subagent calls |
| Install paths (marketplace) | Managed plugin cache via the Claude marketplace manifest | `~/.codex/plugins/forge` via `.agents/plugins/marketplace.json` |
| Install paths (dev) | `~/.claude/skills/forge` whole-tree | Per-skill entries under `~/.agents/skills/<skill-name>` (symlinks followed on Unix; copies on Windows) |

Design consequence: anything Claude-only (hooks) is an enhancement, never a dependency. Every skill must function through description matching plus explicit invocation alone.
