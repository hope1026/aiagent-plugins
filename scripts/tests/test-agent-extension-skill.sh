#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL_DIR="$ROOT/plugins/forge/skills/creating-agent-extensions"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

required=(
  "$SKILL_DIR/SKILL.md"
  "$SKILL_DIR/scripts/manage_extension.py"
  "$SKILL_DIR/references/authoring-providers.md"
  "$SKILL_DIR/references/layout-contract.md"
  "$SKILL_DIR/tests/test_manage_extension.py"
)

for path in "${required[@]}"; do
  [[ -f "$path" ]] || fail "missing ${path#$ROOT/}"
done

grep -q '^name: creating-agent-extensions$' "$SKILL_DIR/SKILL.md" || \
  fail "skill frontmatter name is missing"
grep -q 'NO NATIVE WRITE BEFORE A COMPLETE PREVIEW' "$SKILL_DIR/SKILL.md" || \
  fail "skill confirmation gate is missing"
grep -q 'This is an authoring workflow, not a distribution workflow' "$SKILL_DIR/SKILL.md" || \
  fail "skill distribution boundary is missing"
grep -q 'The request is only for hooks, rules, apps' "$SKILL_DIR/SKILL.md" || \
  fail "agent-specific component boundary is missing"
for action in plan init render validate; do
  grep -q "\`$action\`" "$SKILL_DIR/SKILL.md" || \
    fail "skill workflow misses $action"
done
grep -q -- '--confirm-user-write' "$SKILL_DIR/SKILL.md" || \
  fail "skill workflow misses user write confirmation"
grep -q 'Capability discovery' "$SKILL_DIR/references/authoring-providers.md" || \
  fail "provider capability discovery is missing"
grep -q 'Staging boundary' "$SKILL_DIR/references/authoring-providers.md" || \
  fail "provider staging boundary is missing"
grep -q 'Bundled fallback' "$SKILL_DIR/references/authoring-providers.md" || \
  fail "provider fallback is missing"
grep -q '.gemini/config/skills/<skill>/SKILL.md' "$SKILL_DIR/references/layout-contract.md" || \
  fail "Antigravity user skill target is missing"
grep -q '.gemini/config/mcp_config.json' "$SKILL_DIR/references/layout-contract.md" || \
  fail "Antigravity user MCP target is missing"
grep -q 'Agent-only hooks/rules/apps are not portable common components' "$SKILL_DIR/references/layout-contract.md" || \
  fail "agent-specific adapter extension point is missing"

git -C "$ROOT" check-ignore -q --no-index \
  plugins/forge/skills/creating-agent-extensions/tests/__pycache__/probe.pyc || \
  fail "Python cache files are not ignored"

python3 -m unittest discover \
  -s "$SKILL_DIR/tests" \
  -p 'test_*.py' \
  -v

printf 'agent extension skill: all checks passed\n'
