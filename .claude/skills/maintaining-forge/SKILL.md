---
name: maintaining-forge
description: 'Use when creating, editing, reviewing, or testing Forge skills or changing Forge plugin manifests, hooks, validators, install scripts, or release documentation in this repository. Triggers: "스킬 수정", "스킬 추가", "forge 수정", "플러그인 수정", editing files under plugins/forge/.'
---

# Maintaining Forge

Use this skill as the repository-local entry point for Forge maintenance. The shared runbook is the source of truth.

## First Step

Before acting, read both files completely:

- `../../../.agent-runbooks/maintaining-forge/README.md`
- `../../../.agent-runbooks/maintaining-forge/references/portability-rules.md`

## Rules

- Do not duplicate maintenance procedures in this wrapper; update the runbook instead.
- If this wrapper and the runbook disagree, follow the runbook and fix this wrapper.
- Keep Marketplace user skills under `plugins/forge/skills/`; keep repository-only shared workflows under `.agent-runbooks/`.
