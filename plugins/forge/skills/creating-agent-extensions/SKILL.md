---
name: creating-agent-extensions
description: 'Use when creating a skill, MCP definition, or combined agent extension that must work from one canonical source across Codex, Claude Code, and Antigravity. Triggers: "에이전트 확장 생성", "공통 스킬", "여러 에이전트", "MCP 만들기", "cross-agent skill", "portable MCP".'
---

# Creating Agent Extensions

Announce at start: "Using the forge creating-agent-extensions skill to create one canonical extension with agent-native adapters."

Respond to the user in the user's language. This skill file stays in English.

## Overview

Create agent-neutral skill and MCP sources under `.agent-extensions/`. Use the bundled manager for deterministic structure and validation. Detailed authoring instructions are completed in the workflow integration Task after the manager contract is implemented.

## Current Contract

Read `references/layout-contract.md`, then use `scripts/manage_extension.py` for `plan`, `init`, `render`, and `validate` actions. Do not publish, release, or create Marketplace packages as part of this workflow.

## Handoff

After the extension manager and workflow are complete, use the forge verifying-work skill against the approved spec.
