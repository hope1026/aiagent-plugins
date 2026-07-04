# Tone Overlay Skills Implementation Plan

> **For agentic workers:** execute with the forge executing-plans skill,
> task by task with checkpoints. Steps use checkbox (`- [ ]`) syntax for tracking.

**Spec:** `docs/specs/001-tone-overlays/spec.md`

**Goal:** Add purpose-specific marketing and operations tone overlays while keeping `writing-tone` as the single base natural prose skill.

**Architecture:** `writing-tone` remains the base skill and carries natural-writing rules in `references/style-rules.md`. `marketing-tone` and `operations-tone` are new Forge skills under `plugins/forge/skills/` that explicitly layer on top of `writing-tone`. `operations-private` keeps WEPPY-specific workflows while delegating generic tone guidance to the new Forge overlays.

**Tech Stack:** Agent Skills Markdown, JSON plugin manifests, Bash validation with `scripts/validate.sh`.

## Global Constraints

- Do not create a `natural-writing-tone` skill.
- Keep Forge skill bodies portable: no harness-specific tool names and no path includes.
- Keep each `SKILL.md` under 500 lines and frontmatter limited to `name` and `description`.
- Preserve existing uncommitted user changes in `/Users/han-byeol/Work/operations-private`.
- Do not remove WEPPY-specific workflows, links, safety rules, support templates, metrics rules, or routing.

## AC Coverage

| AC | Tasks |
|---|---|
| AC1 | 1, 3 |
| AC2 | 2, 3 |
| AC3 | 2, 3 |
| AC4 | 4 |
| AC5 | 3 |
| AC6 | 5 |

### Task 1: Base Writing Tone Update (R1 · AC1)

**Files:**
- Modify: `plugins/forge/skills/writing-tone/SKILL.md`
- Modify: `plugins/forge/skills/writing-tone/references/style-rules.md`

**Interfaces:**
- Consumes: existing `writing-tone` skill.
- Produces: one base natural prose skill that every overlay can reference by name.

- [x] **Step 1: Verify there is no duplicate base tone skill**

Run: `find plugins/forge/skills -maxdepth 1 -type d -name '*natural*' -print`
Expected: no output.

- [x] **Step 2: Update `writing-tone` frontmatter and overview**

Edit `plugins/forge/skills/writing-tone/SKILL.md` so the description mentions natural, human-readable prose and non-AI-like wording. Keep the skill name `writing-tone`.

- [x] **Step 3: Add base natural-writing rules**

Edit `plugins/forge/skills/writing-tone/references/style-rules.md` to add rules that remove AI-like openings, generic reassurance, over-polished phrasing, and filler. Keep the existing English and Korean mechanics.

- [x] **Step 4: Verify duplicate absence and base wording**

Run: `rg -n "natural-writing-tone|AI-like|non-AI-like|사람" plugins/forge/skills/writing-tone plugins/forge/skills`
Expected: `natural-writing-tone` appears only in the spec/plan if searched repo-wide, and `writing-tone` contains the base natural-writing guidance.

### Task 2: Purpose Overlay Skills (R2, R3, R4, R5, R6, R7 · AC2, AC3)

**Files:**
- Create: `plugins/forge/skills/marketing-tone/SKILL.md`
- Create: `plugins/forge/skills/operations-tone/SKILL.md`

**Interfaces:**
- Consumes: the forge `writing-tone` skill as the base layer.
- Produces: `marketing-tone` and `operations-tone` skills discoverable by Forge/Codex/Claude.

- [x] **Step 1: Create `marketing-tone`**

Create `plugins/forge/skills/marketing-tone/SKILL.md` with frontmatter name `marketing-tone`, description starting with `Use when`, and body instructions to apply `writing-tone` first, then write fact-based, confident, trust-building marketing copy without unsupported hype.

- [x] **Step 2: Create `operations-tone`**

Create `plugins/forge/skills/operations-tone/SKILL.md` with frontmatter name `operations-tone`, description starting with `Use when`, and body instructions to apply `writing-tone` first, then lead customer/operations replies with confirmed status, user impact, action plan, customer action required, and next update criteria.

- [x] **Step 3: Encode root-cause restraint**

In `operations-tone`, add the rule that cause details stay out unless requested, confirmed, safe to share, and useful for customer action. Include status wording examples such as `The issue has been confirmed`, `We are preparing a fix`, and `No action is needed on your side`.

- [x] **Step 4: Verify overlay frontmatter**

Run: `for f in plugins/forge/skills/marketing-tone/SKILL.md plugins/forge/skills/operations-tone/SKILL.md; do sed -n '1,12p' "$f"; done`
Expected: each frontmatter block has only `name` and `description`, and each description contains `Use when`.

### Task 3: Forge Catalog and Metadata (R10 · AC1, AC2, AC3, AC5)

**Files:**
- Modify: `README.md`
- Modify: `plugins/forge/.codex-plugin/plugin.json`
- Modify: `plugins/forge/.claude-plugin/plugin.json`
- Modify: `docs/specs/2026-07-04-forge-plugin-design.md`

**Interfaces:**
- Consumes: existing Forge plugin catalog.
- Produces: docs and manifests that advertise the two overlay skills and describe `writing-tone` as the base prose layer.

- [x] **Step 1: Update README skill catalog**

Add `marketing-tone` and `operations-tone` to the Forge skill catalog. Change the `writing-tone` row to say it is the base natural prose layer.

- [x] **Step 2: Update plugin descriptions and keywords**

Edit both plugin manifests so their descriptions or long descriptions mention marketing and operations tone overlays. Add manifest keywords for `marketing`, `operations`, and `customer-support` where the manifest has keywords.

- [x] **Step 3: Update governing design spec**

Edit `docs/specs/2026-07-04-forge-plugin-design.md` to mention the added overlay skills and the decision to keep `writing-tone` as the base. Append a dated `[CHANGE]` entry rather than rewriting the whole historical design.

- [x] **Step 4: Verify catalog**

Run: `rg -n "writing-tone|marketing-tone|operations-tone" README.md plugins/forge/.codex-plugin/plugin.json plugins/forge/.claude-plugin/plugin.json docs/specs/2026-07-04-forge-plugin-design.md`
Expected: all three skills are present where the catalog is maintained.

### Task 4: operations-private Deduplication (R8, R9 · AC4)

**Files:**
- Modify: `/Users/han-byeol/Work/operations-private/.agents/skills/weppy-github-customer-response/SKILL.md`
- Modify: `/Users/han-byeol/Work/operations-private/.agents/skills/weppy-roblox-mcp-social-copy/SKILL.md`
- Modify: `/Users/han-byeol/Work/operations-private/.agents/skills/weppy-ops-command-center/SKILL.md`

**Interfaces:**
- Consumes: new Forge `marketing-tone` and `operations-tone` skill names.
- Produces: WEPPY-specific skills that delegate generic tone rules while retaining product-specific workflows.

- [x] **Step 1: Snapshot current operations-private diff**

Run: `git -C /Users/han-byeol/Work/operations-private diff -- .agents/skills/weppy-github-customer-response/SKILL.md`
Expected: existing user edits are visible and must remain in the final diff.

- [x] **Step 2: Deduplicate customer response tone**

Edit `weppy-github-customer-response` to say public replies should use the Forge `operations-tone` skill for general customer-facing tone. Keep WEPPY-specific tone rules that are safety, release, billing, uninstall, or template-specific.

- [x] **Step 3: Deduplicate social copy tone**

Edit `weppy-roblox-mcp-social-copy` to say general marketing copy should use the Forge `marketing-tone` skill. Keep WEPPY-specific voice, channel, product naming, install links, hashtags, approved examples, and platform rules.

- [x] **Step 4: Update command center routing**

Edit `weppy-ops-command-center` to mention the Forge overlays when routing to customer response or social copy work, without changing the WEPPY workflow order.

- [x] **Step 5: Verify user edits are preserved**

Run: `git -C /Users/han-byeol/Work/operations-private diff -- .agents/skills/weppy-github-customer-response/SKILL.md .agents/skills/weppy-roblox-mcp-social-copy/SKILL.md .agents/skills/weppy-ops-command-center/SKILL.md`
Expected: pre-existing release/update wording edits remain; generic tone duplication is reduced or delegated.

### Task 5: Validation and Acceptance Walk (R1-R10 · AC6)

**Files:**
- Read: `docs/specs/001-tone-overlays/spec.md`
- Read: changed files from Tasks 1-4

**Interfaces:**
- Consumes: completed implementation.
- Produces: validation evidence for final reporting.

- [x] **Step 1: Run Forge validator**

Run: `bash scripts/validate.sh`
Expected: `validate: all checks passed`.

- [x] **Step 2: Verify no duplicate natural skill exists**

Run: `find plugins/forge/skills -maxdepth 1 -type d -name 'natural-writing-tone' -print`
Expected: no output.

- [x] **Step 3: Verify AC coverage manually**

Read `docs/specs/001-tone-overlays/spec.md` and changed files. Confirm AC1-AC6 are satisfied with evidence from command output or file content.

- [x] **Step 4: Report final status**

Summarize changed files, operations-private deduplication, and validation results to the user.
