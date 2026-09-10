#!/usr/bin/env bash
set -euo pipefail

ROOT="${FORGE_ARTIFACT_TEST_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
ROOT="$(cd "$ROOT" && pwd -P)"
fail() { echo "FAIL: $1" >&2; exit 1; }

USING_FORGE="$ROOT/plugins/forge/skills/using-forge/SKILL.md"
PORTABILITY="$ROOT/.agent-extensions/maintaining-forge/skills/maintaining-forge/references/portability-rules.md"
WRITING_PLANS="$ROOT/plugins/forge/skills/writing-plans/SKILL.md"
EXECUTING_PLANS="$ROOT/plugins/forge/skills/executing-plans/SKILL.md"
REVIEW_VIEWER="$ROOT/plugins/forge/skills/visual-docs/SKILL.md"

# Artifact authority is checked through parser behavior and side effects below.
[[ -f "$REVIEW_VIEWER" ]] || fail "visual-docs is missing"
[[ ! -e "$ROOT/plugins/forge/skills/spec-viewer" ]] || fail "retired skill remains"
[[ ! -e "$ROOT/plugins/forge/skills/ui-design" ]] || fail "retired UI router remains"

# Default structured-spec tooling validates Markdown without writing HTML.
TEMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEMP_ROOT"' EXIT
cp -R "$ROOT/plugins/forge/skills/writing-specs/tests/fixtures/spec-bundle-repository/valid-multi-bundle/." "$TEMP_ROOT/"
mkdir -p "$TEMP_ROOT/.forge/visual-docs/sentinel"
printf 'review-sentinel\n' > "$TEMP_ROOT/.forge/visual-docs/sentinel/view.html"
SENTINEL_BEFORE="$(shasum -a 256 "$TEMP_ROOT/.forge/visual-docs/sentinel/view.html" | awk '{print $1}')"
REVIEW_COUNT_BEFORE="$(find "$TEMP_ROOT/.forge/visual-docs" -type f | wc -l | tr -d ' ')"
bash "$ROOT/plugins/forge/skills/writing-specs/scripts/spec-docs.sh" \
  --repo-root "$TEMP_ROOT" validate --root docs/specs >/dev/null
SENTINEL_AFTER="$(shasum -a 256 "$TEMP_ROOT/.forge/visual-docs/sentinel/view.html" | awk '{print $1}')"
REVIEW_COUNT_AFTER="$(find "$TEMP_ROOT/.forge/visual-docs" -type f | wc -l | tr -d ' ')"
[[ "$SENTINEL_BEFORE" == "$SENTINEL_AFTER" ]] || fail "Markdown validation changed Visual Docs bytes"
[[ "$REVIEW_COUNT_BEFORE" == "$REVIEW_COUNT_AFTER" ]] || fail "Markdown validation changed Visual Docs file count"

CLI_HELP="$(bash "$ROOT/plugins/forge/skills/writing-specs/scripts/spec-docs.sh" --help)"
grep -q 'validate' <<<"$CLI_HELP" || fail "structured-spec CLI misses validate"
grep -q 'inspect' <<<"$CLI_HELP" || fail "structured-spec CLI misses inspect"
if grep -Eq '(^|[,{[:space:]])(build|check)([]},[:space:]]|$)' <<<"$CLI_HELP"; then
  fail "structured-spec CLI still exposes HTML page commands"
fi

printf 'test-forge-artifact-contract: all checks passed\n'
