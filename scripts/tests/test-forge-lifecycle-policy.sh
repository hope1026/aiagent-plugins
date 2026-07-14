#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fail() { echo "FAIL: $1" >&2; exit 1; }

WRITING_SPECS="$ROOT_DIR/plugins/forge/skills/writing-specs/SKILL.md"
WRITING_PLANS="$ROOT_DIR/plugins/forge/skills/writing-plans/SKILL.md"
SPEC_VIEWER="$ROOT_DIR/plugins/forge/skills/spec-viewer/SKILL.md"
EXECUTING_PLANS="$ROOT_DIR/plugins/forge/skills/executing-plans/SKILL.md"
ROUTING_REF="$ROOT_DIR/plugins/forge/skills/executing-plans/references/adaptive-routing.md"
CODEX_REF="$ROOT_DIR/plugins/forge/skills/using-forge/references/codex-tools.md"
VERIFYING_WORK="$ROOT_DIR/plugins/forge/skills/verifying-work/SKILL.md"
USING_FORGE="$ROOT_DIR/plugins/forge/skills/using-forge/SKILL.md"

for file in "$WRITING_SPECS" "$WRITING_PLANS" "$SPEC_VIEWER"; do
  grep -qi 'explicit user request' "$file" || fail "$file misses explicit user request gate"
done

grep -q 'Markdown is the default review path' "$WRITING_SPECS" || \
  fail "writing-specs does not default to Markdown"
grep -q 'ask whether the user wants a Viewer' "$WRITING_SPECS" || \
  fail "writing-specs does not ask after completion"
grep -q 'ask whether the user wants a `plan` Viewer' "$WRITING_PLANS" || \
  fail "writing-plans does not ask after completion"

if rg -n 'score 2\+ uses|rebuild an existing Viewer|complex plan.*use the forge spec-viewer' \
  "$WRITING_SPECS" "$WRITING_PLANS" >/dev/null; then
  fail "automatic Viewer generation language remains"
fi

grep -qi 'explicit user request' "$EXECUTING_PLANS" || \
  fail "executing-plans misses explicit Viewer update gate"
grep -q 'may be reported as stale' "$EXECUTING_PLANS" || \
  fail "executing-plans misses stale Viewer notice"
if rg -n 'If a lifecycle Viewer exists, rebuild|rebuild it before the first checkpoint' \
  "$EXECUTING_PLANS" >/dev/null; then
  fail "executing-plans still rebuilds Viewer automatically"
fi

for term in fast balanced frontier; do
  grep -q "$term" "$EXECUTING_PLANS" || fail "executing-plans misses $term"
done

for term in impact uncertainty context_coupling verification_clarity parallel_group; do
  grep -q "$term" "$ROUTING_REF" || fail "adaptive routing reference misses $term"
done

grep -q 'maximum of 3 concurrent subagents' "$ROUTING_REF" || \
  fail "adaptive routing reference misses default concurrency cap"
grep -q 'inherit the current model' "$CODEX_REF" || \
  fail "Codex fallback does not inherit the current model"
grep -q 'subagents remain available' "$CODEX_REF" || \
  fail "Codex model fallback incorrectly disables subagents"
if rg -n 'one fresh subagent per plan task|close_agent' "$CODEX_REF" >/dev/null; then
  fail "Codex reference promises mechanical dispatch or unavailable lifecycle tools"
fi
grep -q 'requesting parallel execution does not' "$USING_FORGE" || \
  fail "using-forge allows direct requests to bypass parallel safety"
grep -q 'overlapping writes remain sequential' "$ROUTING_REF" || \
  fail "adaptive routing misses the user-pressure counter"

grep -q 'internal checkpoint' "$EXECUTING_PLANS" || fail "missing internal checkpoint"
grep -q 'notify checkpoint' "$EXECUTING_PLANS" || fail "missing notify checkpoint"
grep -q 'approval checkpoint' "$EXECUTING_PLANS" || fail "missing approval checkpoint"
grep -q 'without waiting for the user' "$EXECUTING_PLANS" || \
  fail "internal or notify flow still waits for the user"
if rg -n 'report to the user after every task|checkpoint is the user.s review gate' \
  "$EXECUTING_PLANS" >/dev/null; then
  fail "per-task user checkpoint language remains"
fi
grep -q 'approval gate' "$WRITING_PLANS" || fail "writing-plans misses approval metadata"
grep -q 'route evidence' "$VERIFYING_WORK" || fail "verifying-work misses route evidence review"

echo "forge lifecycle policy: all checks passed"
