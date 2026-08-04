#!/usr/bin/env bash
set -euo pipefail

ROOT="${FORGE_ARTIFACT_TEST_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
ROOT="$(cd "$ROOT" && pwd -P)"
fail() { echo "FAIL: $1" >&2; exit 1; }

assert_migration_artifact() {
  local promoted="$ROOT/docs/research/2026-07-04-forge-plugin-design.md"
  local legacy="$ROOT/docs/specs/2026-07-04-forge-plugin-design.md"
  local expected_sha="fde1f774ce36fcb29e6daa6956526cc0eeb6f47a5b09c0bbd1d8876d91c92f2e"
  local actual_sha
  [[ -f "$promoted" ]] || fail "promoted Forge design record is missing"
  [[ ! -e "$legacy" ]] || fail "legacy Forge design record remains under docs/specs"
  actual_sha="$(shasum -a 256 "$promoted" | awk '{print $1}')"
  [[ "$actual_sha" == "$expected_sha" ]] || fail "promoted Forge design bytes differ from the immutable baseline"
  grep -Fq '> Artifact paths and Viewer lifecycle in this dated design are superseded by docs/specs/002-lifecycle-review-viewer/spec.md.' \
    "$promoted" || fail "promoted Forge design provenance is missing"
}

if [[ "${FORGE_ARTIFACT_MIGRATION_ASSERT_ONLY:-0}" == "1" ]]; then
  assert_migration_artifact
  printf 'test-forge-artifact-contract: migration assertion passed\n'
  exit 0
fi

USING_FORGE="$ROOT/plugins/forge/skills/using-forge/SKILL.md"
PORTABILITY="$ROOT/.agent-extensions/maintaining-forge/skills/maintaining-forge/references/portability-rules.md"
WRITING_PLANS="$ROOT/plugins/forge/skills/writing-plans/SKILL.md"
EXECUTING_PLANS="$ROOT/plugins/forge/skills/executing-plans/SKILL.md"
REVIEW_VIEWER="$ROOT/plugins/forge/skills/review-viewer/SKILL.md"

grep -q 'docs/plans/PPP-<slug>/plan.md' "$USING_FORGE"
grep -q 'NO PRODUCT-BEHAVIOR IMPLEMENTATION WITHOUT AN APPROVED SPEC' "$USING_FORGE"
grep -q '.forge/reviews/<review-id>/view.html' "$USING_FORGE" || fail "Review Viewer path missing"
grep -q 'Review Viewer.*no' "$PORTABILITY" || fail "portability table does not untrack Review Viewer"
grep -q 'docs/research/' "$ROOT/README.md"
grep -q 'docs/debug/' "$ROOT/README.md"
grep -q 'Related Specs' "$WRITING_PLANS"
grep -q 'docs/plans/PPP-<slug>/plan.md' "$WRITING_PLANS"
grep -q '0 or more' "$WRITING_PLANS"
grep -q 'requirements: \[R1' "$WRITING_PLANS" || fail "canonical requirements array missing"
grep -q 'acceptance: \[AC1' "$WRITING_PLANS" || fail "canonical acceptance array missing"
grep -q 'source-qualified' "$WRITING_PLANS" || fail "source-qualified task trace missing"
grep -q 'docs/plans/PPP-<slug>/plan.md' "$EXECUTING_PLANS"
grep -q 'Progress History' "$EXECUTING_PLANS"
grep -q '`fast` defaults to `root`' "$ROOT/plugins/forge/skills/executing-plans/references/adaptive-routing.md"
grep -q '`balanced` defaults to `subagent`' "$ROOT/plugins/forge/skills/executing-plans/references/adaptive-routing.md"
grep -q '`frontier` defaults to `root`' "$ROOT/plugins/forge/skills/executing-plans/references/adaptive-routing.md"
grep -q 'creating-agent-extensions' "$USING_FORGE"
grep -q '14 active user-execution skills listed above' "$ROOT/README.md"
grep -q '| `creating-agent-extensions` |' "$ROOT/README.md"
[[ ! -e "$ROOT/plugins/forge/skills/ui-design" ]]
grep -q 'Codex, Claude Code, and Antigravity' "$ROOT/.agent-extensions/maintaining-forge/skills/maintaining-forge/SKILL.md"
grep -q '.agent-extensions/' "$PORTABILITY"
grep -q 'python3 "$MANAGER" --help' "$ROOT/scripts/validate.sh"
grep -q 'docs/debug/' "$ROOT/plugins/forge/skills/systematic-debugging/SKILL.md"

[[ -f "$REVIEW_VIEWER" ]] || fail "review-viewer is missing"
[[ ! -e "$ROOT/plugins/forge/skills/spec-viewer" ]] || fail "legacy spec-viewer remains"
grep -q 'explicit request' "$REVIEW_VIEWER" || fail "review-viewer request gate missing"
grep -q '.forge/reviews/<review-id>/view.html' "$REVIEW_VIEWER" || fail "review-viewer output path missing"
grep -q 'Run one build command' "$REVIEW_VIEWER" || fail "review-viewer build-once contract missing"
grep -q 'successful single build ends generation' "$REVIEW_VIEWER" || fail "fixed generation boundary missing"
grep -q 'Review Viewer tooling' "$ROOT/plugins/forge/skills/verifying-work/SKILL.md" || fail "tooling verification boundary missing"
grep -q 'test-forge-artifact-contract.sh' "$ROOT/.github/workflows/validate.yml"
grep -q 'test-forge-spec-docs-policy.sh' "$ROOT/.github/workflows/validate.yml" || fail "CI misses spec docs policy"

# Default structured-spec tooling validates Markdown without writing HTML.
TEMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEMP_ROOT"' EXIT
cp -R "$ROOT/plugins/forge/skills/writing-specs/tests/fixtures/repository/valid-repository/." "$TEMP_ROOT/"
mkdir -p "$TEMP_ROOT/.forge/reviews/sentinel"
printf 'review-sentinel\n' > "$TEMP_ROOT/.forge/reviews/sentinel/view.html"
SENTINEL_BEFORE="$(shasum -a 256 "$TEMP_ROOT/.forge/reviews/sentinel/view.html" | awk '{print $1}')"
REVIEW_COUNT_BEFORE="$(find "$TEMP_ROOT/.forge/reviews" -type f | wc -l | tr -d ' ')"
bash "$ROOT/plugins/forge/skills/writing-specs/scripts/spec-docs.sh" \
  --repo-root "$TEMP_ROOT" validate --root docs/specs >/dev/null
SENTINEL_AFTER="$(shasum -a 256 "$TEMP_ROOT/.forge/reviews/sentinel/view.html" | awk '{print $1}')"
REVIEW_COUNT_AFTER="$(find "$TEMP_ROOT/.forge/reviews" -type f | wc -l | tr -d ' ')"
[[ "$SENTINEL_BEFORE" == "$SENTINEL_AFTER" ]] || fail "Markdown validation changed Review Viewer bytes"
[[ "$REVIEW_COUNT_BEFORE" == "$REVIEW_COUNT_AFTER" ]] || fail "Markdown validation changed Review Viewer file count"

CLI_HELP="$(bash "$ROOT/plugins/forge/skills/writing-specs/scripts/spec-docs.sh" --help)"
grep -q 'validate' <<<"$CLI_HELP" || fail "structured-spec CLI misses validate"
grep -q 'inspect' <<<"$CLI_HELP" || fail "structured-spec CLI misses inspect"
if grep -Eq '(^|[,{[:space:]])(build|check)([]},[:space:]]|$)' <<<"$CLI_HELP"; then
  fail "structured-spec CLI still exposes HTML page commands"
fi

assert_migration_artifact

printf 'test-forge-artifact-contract: all checks passed\n'
