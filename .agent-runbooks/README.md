# Agent Runbooks

This directory is the shared source of truth for aiagent-plugins repository workflows.

Keep Claude Code, Codex, and Antigravity entry skills thin. Tool-specific metadata belongs in
`.claude/skills/` or `.agents/skills/`; detailed procedures, commands, scripts,
references, validation steps, and reporting requirements live here.

## Runbook Groups

- `maintaining-forge/`: Forge skill authoring, portability, validation, pressure testing, and release gates.

## Wrapper Rule

If a Claude Code, Codex, or Antigravity skill disagrees with a runbook, the runbook wins.
Update wrappers instead of duplicating detailed procedures outside this directory.
