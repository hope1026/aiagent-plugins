#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fail() { echo "FAIL: $1" >&2; exit 1; }

required=(
  ".agent-extensions/maintaining-forge/extension.json"
  ".agent-extensions/maintaining-forge/skills/maintaining-forge/SKILL.md"
  ".agent-extensions/maintaining-forge/skills/maintaining-forge/references/portability-rules.md"
  ".agent-extensions/maintaining-forge/adapters/codex/state.json"
  ".agent-extensions/maintaining-forge/adapters/claude-code/state.json"
  ".agent-extensions/maintaining-forge/adapters/antigravity/state.json"
  ".agents/skills/maintaining-forge/SKILL.md"
  ".claude/skills/maintaining-forge/SKILL.md"
)
for path in "${required[@]}"; do
  [[ -f "$ROOT_DIR/$path" ]] || fail "missing $path"
done

[[ ! -e "$ROOT_DIR/plugins/forge/skills/maintaining-forge" ]] || \
  fail "maintaining-forge must not ship in plugins/forge/skills"
[[ ! -e "$ROOT_DIR/.agent-runbooks" ]] || \
  fail "unsupported .agent-runbooks must be absent after canonical adoption"

cmp -s \
  "$ROOT_DIR/.agents/skills/maintaining-forge/SKILL.md" \
  "$ROOT_DIR/.claude/skills/maintaining-forge/SKILL.md" || \
  fail "shared .agents and Claude wrappers must match"

for wrapper in \
  "$ROOT_DIR/.agents/skills/maintaining-forge/SKILL.md" \
  "$ROOT_DIR/.claude/skills/maintaining-forge/SKILL.md"; do
  grep -q '../../../.agent-extensions/maintaining-forge/skills/maintaining-forge/SKILL.md' "$wrapper" || \
    fail "$wrapper does not reference the canonical skill"
done

python3 "$ROOT_DIR/plugins/forge/skills/creating-agent-extensions/scripts/manage_extension.py" \
  validate --extension "$ROOT_DIR/.agent-extensions/maintaining-forge" \
  | grep -q '"status": "PASS"' || fail "canonical extension validation failed"

if rg -n 'maintaining-forge' "$ROOT_DIR/plugins/forge" >/dev/null; then
  rg -n 'maintaining-forge' "$ROOT_DIR/plugins/forge" >&2
  fail "Forge user plugin still references maintaining-forge"
fi

grep -q '.agent-extensions/maintaining-forge/' "$ROOT_DIR/README.md" || \
  fail "README does not document repository-only Forge maintenance"

echo "layout: all checks passed"
