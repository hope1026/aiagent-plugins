#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fail() { echo "FAIL: $1" >&2; exit 1; }

WRITING_SPECS="$ROOT_DIR/plugins/forge/skills/writing-specs/SKILL.md"
WRITING_PLANS="$ROOT_DIR/plugins/forge/skills/writing-plans/SKILL.md"
SPEC_VIEWER="$ROOT_DIR/plugins/forge/skills/spec-viewer/SKILL.md"

for file in "$WRITING_SPECS" "$WRITING_PLANS" "$SPEC_VIEWER"; do
  grep -qi 'explicit user request' "$file" || fail "$file misses explicit user request gate"
done

grep -q 'Markdown is the default review path' "$WRITING_SPECS" || \
  fail "writing-specs does not default to Markdown"
grep -q 'ask whether the user wants a Viewer' "$WRITING_SPECS" || \
  fail "writing-specs does not ask after completion"
grep -q 'ask whether the user wants a Viewer' "$WRITING_PLANS" || \
  fail "writing-plans does not ask after completion"

if rg -n 'score 2\+ uses|rebuild an existing Viewer|complex plan.*use the forge spec-viewer' \
  "$WRITING_SPECS" "$WRITING_PLANS" >/dev/null; then
  fail "automatic Viewer generation language remains"
fi

echo "forge lifecycle policy: all checks passed"
