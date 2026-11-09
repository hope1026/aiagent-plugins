---
name: maintaining-forge
description: 'Use when creating, editing, reviewing, or testing Forge skills or changing Forge plugin manifests, hooks, validators, install scripts, or release documentation in this repository. Triggers: "스킬 수정", "스킬 추가", "forge 수정", "플러그인 수정", editing files under plugins/forge/.'
---

# Maintaining Forge

Use this repository-only runbook when creating, editing, reviewing, or testing Forge skills, plugin metadata, hooks, validators, installation scripts, or release documentation. Ordinary use of Forge in another project does not need this runbook.

Respond in the user's language. Distributed Forge skills and repository-local adapter skills stay in English.

## Source and distribution boundaries

| Workflow | Detailed source | Entry points | Distribution |
|---|---|---|---|
| Marketplace user skill | `plugins/forge/skills/<skill-name>/` | Portable `SKILL.md` | Forge plugin |
| Repository-only workflow | `.agent-extensions/<extension-name>/` | Generated `.agents/skills/` and `.claude/skills/` adapters | Excluded from the plugin |

For repository-only changes, edit the owned canonical source and render adapters through the forge creating-agent-extensions skill's manager. Never hand-edit wrappers or ownership state. Stop on unowned collisions or live adapter drift; reconcile through an explicit user decision. Preserve unrelated work.

For distributed authoring or review, read `references/portability-rules.md`. It owns frontmatter, language, path, layout, and platform constraints. Keep instructions focused on useful outcomes and concrete conditions; move conditional detail to references and avoid mandatory ceremonies or duplicated platform procedures.

## Edit and verify

1. Read each affected skill or runbook completely and the relevant owning contracts and consumers. Reuse unchanged context. Classify the source using the boundary table above.
2. Make the smallest complete change. Follow existing authorization; use the forge writing-specs skill when durable meaning changes. Keep ordinary Spec and Plan work Markdown-only. Generate or refresh Visual Docs only for an explicit request; maintainer fixtures remain isolated from repository visual outputs.
3. For an owned repository extension, validate its existing state before editing and render adapters after changing canonical content. Use manager validation to confirm parity; repair canonical or ownership problems through the owning workflow rather than editing hashes.
4. Run `bash scripts/validate.sh` from the repository root. Require `validate: all checks passed` for the current final state before commit. It checks plugin and extension metadata, adapter parity, and structured Specs; it does not establish behavior.
5. Review the diff for ambiguity, authority, missing safety conditions, and unnecessary artifacts, questions, or repeated checks. Apply the behavioral evaluation below to instruction changes. Correct demonstrated problems and recheck affected evidence; do not accumulate speculative restrictions.
6. Keep meaningful results and limitations in the existing work record. Use the forge verifying-work skill to assess completion against the affected contract and requested result, reusing applicable evidence. Commit only when authorized, using a conventional message.

No duplicate checklist is required. Source integrity, behavior, and release permission are separate: a validator pass alone does not authorize publication. A wording change that changes instructions still needs behavioral evaluation; typo, formatting-only, and link fixes need an adversarial self-read but may skip live evaluation.

## Behavioral evaluation

Give a fresh agent a realistic task combining at least two pressures, such as a deadline, sunk cost, or a demand for a one-time exception. Supply the entry skill and necessary sources without labeling the task as a test. Keep actions within the available environment and authorization.

Inspect the agent's actual output and any artifacts for the requested outcome, preserved contracts, regression protection, and recovery. Also inspect unnecessary questions, artifacts, test additions, repeated execution, and blocked progress. A prescribed phrase or sequence is not the success criterion. Use the same model and environment for comparisons; identify simulated scenarios and agent evaluations accurately rather than claiming native integration or measured performance.

For a representative instruction change, use an available fresh agent, review its result, correct demonstrated defects, and rerun affected scenarios. Reuse evidence whose relevant instructions and inputs remain unchanged. If independent execution is unavailable, perform an adversarial self-read and report live evaluation as pending. That supports a limited local report, not a passed live release gate. Keep observations under `.forge/scratch/` or promote useful evidence to `docs/evidence/`.

## Release gate

Pushing publishes the Marketplace state. Do not push until the user has authorized release, final validation has passed, and required live behavioral evidence is complete. Do not waive these conditions for a small edit or promise to test afterward.

Before push, inspect the entire commit range ahead of the configured upstream. If it changes `plugins/forge/skills/`:

1. Read the upstream versions from `plugins/forge/.claude-plugin/plugin.json` and `plugins/forge/.codex-plugin/plugin.json`.
2. Increase the Claude base version above the upstream release version.
3. Use the same base version for Codex with a fresh UTC `+codex.YYYYMMDDHHMMSS` suffix.
4. Re-run validation after manifest edits. Stop if either manifest is unchanged, base versions differ, or the suffix is not fresh.

Several local skill commits may share one release bump when published together. Inspect the whole outgoing range, not only the latest commit. Release remains separate from local implementation and verification.

## Rule ownership

| Owner | Responsibility |
|---|---|
| `using-forge` | Intent, authority, task context, and execution selection; conditional domain references |
| `writing-specs` | Canonical meaning, serialization, and source transactions |
| `writing-plans` / `executing-plans` | Executable outcomes, coordination, and progress |
| `systematic-debugging` / `test-driven-development` | Evidence-led diagnosis and useful or required test-first work |
| `verifying-work` | Completion evidence and lifecycle claims |
| `visual-docs` | Requested derived explanations and reading checks |
| `writing-tone` with marketing/operations overlays | Human-readable prose and purpose-specific communication |
| `creating-agent-extensions` | Canonical extension layout, native adapters, and ownership |

Link the owning skill instead of copying its complete procedure into another entry point. Keep concise safety reminders where a skill can be entered independently.

## Repository locations

| Purpose | Path |
|---|---|
| Marketplace skills | `plugins/forge/skills/` |
| Canonical local extensions | `.agent-extensions/` |
| Generated native adapters | `.agents/skills/`, `.claude/skills/` |
| Plugin manifests | `plugins/forge/.claude-plugin/plugin.json`, `plugins/forge/.codex-plugin/plugin.json` |
| Marketplace manifests | `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json` |
| Optional hooks | `plugins/forge/hooks/` |
| Validator / development install | `scripts/validate.sh`, `scripts/install.sh` |
| Local evaluation notes | `.forge/scratch/` |
| Durable contracts / work plans | `docs/specs/`, project-chosen paths under `docs/plans/` |

Other artifact locations and lifecycles belong to the corresponding execution skill and project convention.
