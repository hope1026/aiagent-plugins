#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

assert_has() {
  local pattern="$1"
  local file="$2"
  grep -Eq "$pattern" "$file" || fail "$file is missing pattern: $pattern"
}

assert_not_has() {
  local pattern="$1"
  local file="$2"
  if grep -Eq "$pattern" "$file"; then
    fail "$file contains forbidden pattern: $pattern"
  fi
}

APP="$ROOT/plugins/forge/skills/web-app-design/SKILL.md"
SITE="$ROOT/plugins/forge/skills/website-design/SKILL.md"
REMOVED="$ROOT/plugins/forge/skills/ui-design"
ROUTER="$ROOT/plugins/forge/skills/using-forge/SKILL.md"
VIEWER="$ROOT/plugins/forge/skills/spec-viewer/SKILL.md"
MAINTAINER="$ROOT/.agent-extensions/maintaining-forge/skills/maintaining-forge/SKILL.md"

for file in "$APP" "$SITE"; do
  [[ -f "$file" ]] || fail "missing skill: $file"
done
[[ ! -e "$REMOVED" ]] || fail "removed skill still exists: $REMOVED"

assert_has '^name: web-app-design$' "$APP"
assert_has 'browser.*PWA|PWA.*browser' "$APP"
assert_has 'Secondary ceiling' "$APP"
assert_has '44px hit area' "$APP"
assert_has 'viewport.*state matrix' "$APP"
assert_has '1px' "$APP"
assert_not_has 'owns native mobile|owns native desktop' "$APP"

assert_has '^name: website-design$' "$SITE"
assert_has 'Visual thesis' "$SITE"
assert_has 'Content hierarchy' "$SITE"
assert_has 'Imagery' "$SITE"
assert_has 'Responsive composition' "$SITE"
assert_has 'restrained motion' "$SITE"
assert_not_has 'table geometry.*required|required.*table geometry' "$SITE"

assert_has 'Browser application UI.*web-app-design' "$ROUTER"
assert_has 'Public website.*website-design' "$ROUTER"
assert_has 'one classification question' "$ROUTER"
assert_has 'Native mobile or desktop app.*specialist skill is not available' "$ROUTER"
assert_has 'Viewer shell.*web-app-design' "$ROUTER"
assert_not_has 'ui-design' "$ROUTER"

assert_has 'Building a browser application UI.*web-app-design' "$VIEWER"
assert_has 'Building a public website.*website-design' "$VIEWER"
assert_has 'Changing the Viewer shell.*web-app-design' "$VIEWER"
assert_not_has 'Building product UI.*ui-design' "$VIEWER"

assert_has '\| `web-app-design` \|' "$MAINTAINER"
assert_has '\| `website-design` \|' "$MAINTAINER"
assert_not_has '\| `ui-design` \|' "$MAINTAINER"

assert_has '\| `web-app-design` \|' "$ROOT/README.md"
assert_has '\| `website-design` \|' "$ROOT/README.md"
assert_has '14 active user-execution skills listed above' "$ROOT/README.md"
assert_not_has '\| `ui-design` \|' "$ROOT/README.md"

jq -e '.keywords | index("web-app-design") != null' \
  "$ROOT/plugins/forge/.claude-plugin/plugin.json" >/dev/null ||
  fail "Claude manifest is missing web-app-design keyword"
jq -e '.keywords | index("website-design") != null' \
  "$ROOT/plugins/forge/.claude-plugin/plugin.json" >/dev/null ||
  fail "Claude manifest is missing website-design keyword"
jq -e '.keywords | index("ui-design") == null' \
  "$ROOT/plugins/forge/.claude-plugin/plugin.json" >/dev/null ||
  fail "Claude manifest still exposes ui-design keyword"
assert_has 'web-app-design' "$ROOT/plugins/forge/.codex-plugin/plugin.json"
assert_has 'website-design' "$ROOT/plugins/forge/.codex-plugin/plugin.json"

assert_has 'test-ui-design-skill-routing.sh' "$ROOT/.github/workflows/validate.yml"

echo "ui-design-skill-routing: all checks passed"
