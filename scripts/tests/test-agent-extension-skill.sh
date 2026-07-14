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
  "$SKILL_DIR/references/layout-contract.md"
  "$SKILL_DIR/tests/test_manage_extension.py"
)

for path in "${required[@]}"; do
  [[ -f "$path" ]] || fail "missing ${path#$ROOT/}"
done

git -C "$ROOT" check-ignore -q --no-index \
  plugins/forge/skills/creating-agent-extensions/tests/__pycache__/probe.pyc || \
  fail "Python cache files are not ignored"

python3 -m unittest discover \
  -s "$SKILL_DIR/tests" \
  -p 'test_*.py' \
  -v

printf 'agent extension skill: all checks passed\n'
