#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fail() { echo "FAIL: $1" >&2; exit 1; }
assert_has() { grep -Eq "$1" "$2" || fail "$2 is missing pattern: $1"; }
assert_not_has() { if grep -Eq "$1" "$2"; then fail "$2 contains forbidden pattern: $1"; fi; }

APP="$ROOT/plugins/forge/skills/web-app-design/SKILL.md"
SITE="$ROOT/plugins/forge/skills/website-design/SKILL.md"
REMOVED="$ROOT/plugins/forge/skills/ui-design"
ROUTER="$ROOT/plugins/forge/skills/using-forge/SKILL.md"
VIEWER="$ROOT/plugins/forge/skills/review-viewer/SKILL.md"
MAINTAINER="$ROOT/.agent-extensions/maintaining-forge/skills/maintaining-forge/SKILL.md"

for file in "$APP" "$SITE" "$VIEWER"; do [[ -f "$file" ]] || fail "missing skill: $file"; done
[[ ! -e "$REMOVED" ]] || fail "removed skill still exists: $REMOVED"

assert_has '^name: web-app-design$' "$APP"
assert_has 'browser.*PWA|PWA.*browser' "$APP"
assert_has 'Secondary ceiling' "$APP"
assert_has '44px hit area' "$APP"
assert_has 'viewport.*state matrix' "$APP"
assert_not_has 'owns native mobile|owns native desktop' "$APP"
assert_has '^name: website-design$' "$SITE"
assert_has 'Visual thesis' "$SITE"
assert_has 'Content hierarchy' "$SITE"
assert_has 'Imagery' "$SITE"
assert_has 'Responsive composition' "$SITE"
assert_has 'restrained motion' "$SITE"

assert_has 'Browser application UI.*web-app-design' "$ROUTER"
assert_has 'Public website.*website-design' "$ROUTER"
assert_has 'Review Viewer.*web-app-design|Spec Pages.*web-app-design' "$ROUTER"
assert_has 'review-viewer' "$ROUTER"
assert_not_has 'spec-viewer' "$ROUTER"
assert_has 'Review Viewer tooling.*web-app-design|review-viewer tooling.*web-app-design' "$APP"
assert_has 'Spec Pages tooling.*web-app-design' "$APP"
assert_has 'fixed Review Viewer generation' "$APP"
assert_has 'fixed Review Viewer generation' "$SITE"

assert_has '\| `web-app-design` \|' "$MAINTAINER"
assert_has '\| `website-design` \|' "$MAINTAINER"
assert_has '\| `review-viewer` \|' "$MAINTAINER"
assert_not_has '\| `spec-viewer` \|' "$MAINTAINER"
assert_has '14 active user-execution skills listed above' "$ROOT/README.md"
assert_not_has '\| `spec-viewer` \|' "$ROOT/README.md"
assert_has 'test-ui-design-skill-routing.sh' "$ROOT/.github/workflows/validate.yml"

echo "ui-design-skill-routing: all checks passed"
