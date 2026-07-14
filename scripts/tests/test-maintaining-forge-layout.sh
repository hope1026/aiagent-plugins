#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fail() { echo "FAIL: $1" >&2; exit 1; }

required=(
  ".agent-runbooks/README.md"
  ".agent-runbooks/maintaining-forge/README.md"
  ".agent-runbooks/maintaining-forge/references/portability-rules.md"
  ".agents/skills/maintaining-forge/SKILL.md"
  ".claude/skills/maintaining-forge/SKILL.md"
)
for path in "${required[@]}"; do
  [[ -f "$ROOT_DIR/$path" ]] || fail "missing $path"
done

[[ ! -e "$ROOT_DIR/plugins/forge/skills/maintaining-forge" ]] || \
  fail "maintaining-forge must not ship in plugins/forge/skills"

cmp -s \
  "$ROOT_DIR/.agents/skills/maintaining-forge/SKILL.md" \
  "$ROOT_DIR/.claude/skills/maintaining-forge/SKILL.md" || \
  fail "shared .agents and Claude wrappers must match"

for wrapper in \
  "$ROOT_DIR/.agents/skills/maintaining-forge/SKILL.md" \
  "$ROOT_DIR/.claude/skills/maintaining-forge/SKILL.md"; do
  grep -q '../../../.agent-runbooks/maintaining-forge/README.md' "$wrapper" || \
    fail "$wrapper does not reference the shared runbook"
  grep -q '../../../.agent-runbooks/maintaining-forge/references/portability-rules.md' "$wrapper" || \
    fail "$wrapper does not reference portability rules"
done

if rg -n 'maintaining-forge' "$ROOT_DIR/plugins/forge" >/dev/null; then
  rg -n 'maintaining-forge' "$ROOT_DIR/plugins/forge" >&2
  fail "Forge user plugin still references maintaining-forge"
fi

grep -q '.agent-runbooks/maintaining-forge/' "$ROOT_DIR/README.md" || \
  fail "README does not document repository-only Forge maintenance"

echo "layout: all checks passed"
