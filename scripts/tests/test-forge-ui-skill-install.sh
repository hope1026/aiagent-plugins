#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_HOME="$(mktemp -d)"
trap 'rm -rf "$TEST_HOME"' EXIT

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

mkdir -p "$TEST_HOME/.agents/skills/ui-design"
printf 'stale forge copy\n' >"$TEST_HOME/.agents/skills/ui-design/SKILL.md"
mkdir -p "$TEST_HOME/.agents/skills/user-owned"
printf 'preserve\n' >"$TEST_HOME/.agents/skills/user-owned/marker"

RECOVERY="$TEST_HOME/recovery/ui-design"
mkdir -p "$(dirname "$RECOVERY")"
mv "$TEST_HOME/.agents/skills/ui-design" "$RECOVERY"

for _ in 1 2; do
  HOME="$TEST_HOME" bash "$ROOT/scripts/install.sh" \
    --agent codex --mode copy --plugin forge >/dev/null
done

[[ -f "$TEST_HOME/.agents/skills/web-app-design/SKILL.md" ]] ||
  fail "Codex web-app-design was not installed"
[[ -f "$TEST_HOME/.agents/skills/website-design/SKILL.md" ]] ||
  fail "Codex website-design was not installed"
[[ ! -e "$TEST_HOME/.agents/skills/ui-design" ]] ||
  fail "Codex ui-design was recreated"
[[ -f "$RECOVERY/SKILL.md" ]] ||
  fail "Codex stale skill recovery copy is missing"
[[ -f "$TEST_HOME/.agents/skills/user-owned/marker" ]] ||
  fail "Codex user-owned skill was modified"

mkdir -p "$TEST_HOME/.claude/skills/forge/skills/ui-design"
printf 'stale forge copy\n' \
  >"$TEST_HOME/.claude/skills/forge/skills/ui-design/SKILL.md"

for _ in 1 2; do
  HOME="$TEST_HOME" bash "$ROOT/scripts/install.sh" \
    --agent claude --mode copy --plugin forge >/dev/null
done

[[ -f "$TEST_HOME/.claude/skills/forge/skills/web-app-design/SKILL.md" ]] ||
  fail "Claude web-app-design was not installed"
[[ -f "$TEST_HOME/.claude/skills/forge/skills/website-design/SKILL.md" ]] ||
  fail "Claude website-design was not installed"
[[ ! -e "$TEST_HOME/.claude/skills/forge/skills/ui-design" ]] ||
  fail "Claude ui-design was recreated"

echo "forge-ui-skill-install: all checks passed"
