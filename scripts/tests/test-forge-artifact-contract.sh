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

grep -q 'docs/plans/PPP-<slug>/plan.md' "$USING_FORGE"
grep -q 'NO DURABLE CONTRACT CHANGE WITHOUT AN APPROVED CANONICAL SPEC OR SPEC DELTA' "$USING_FORGE"
grep -q '.forge/visual-docs/<view-id>/view.html' "$USING_FORGE" || fail "Visual Docs path missing"
grep -q 'Brief, Plan, or Spec Visual Doc.*| no |' "$PORTABILITY" || fail "portability table does not untrack local Visual Docs"
grep -q 'Project Handbook.*docs/project-viewer/index.html.*| yes,' "$PORTABILITY" || fail "portability table does not track the Project Handbook"
grep -q 'docs/research/' "$ROOT/README.md"
grep -q 'docs/debug/' "$ROOT/README.md"
grep -q 'Related Specs' "$WRITING_PLANS"
grep -q 'docs/plans/PPP-<slug>/plan.md' "$WRITING_PLANS"
grep -Eq '0 or more|zero or more' "$WRITING_PLANS"
grep -q -- '- bundle: docs/specs/<semantic-bundle-name>/' "$WRITING_PLANS" || fail "canonical bundle path missing"
grep -q 'Governing statements:' "$WRITING_PLANS" || fail "full-statement task trace missing"
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

[[ -f "$REVIEW_VIEWER" ]] || fail "visual-docs is missing"
[[ ! -e "$ROOT/plugins/forge/skills/spec-viewer" ]] || fail "removed spec-viewer skill remains"
grep -q 'explicit request' "$REVIEW_VIEWER" || fail "visual-docs request gate missing"
grep -q '.forge/visual-docs/<view-id>/view.html' "$REVIEW_VIEWER" || fail "visual-docs output path missing"
grep -q 'within the same request' "$REVIEW_VIEWER" || fail "visual-docs correction scope missing"
grep -q 'requested result is verified' "$REVIEW_VIEWER" || fail "visual verification boundary missing"
grep -Fq 'Keep every identifier exact' "$REVIEW_VIEWER" || fail "visual-docs exact identifier contract missing"
grep -Fq 'Do not use raw internal tokens as reader-facing headings' "$REVIEW_VIEWER" || fail "visual-docs human explanation contract missing"
grep -Fq 'Identity and explanation are separate layers' "$ROOT/plugins/forge/skills/visual-docs/references/rendering-contract.md" || fail "visual-docs rendering language contract missing"
grep -q 'Tooling changes use normal regression evidence' "$ROOT/plugins/forge/skills/verifying-work/SKILL.md" || fail "tooling verification boundary missing"
grep -q 'test-forge-artifact-contract.sh' "$ROOT/.github/workflows/validate.yml"
grep -q 'test-forge-spec-docs-policy.sh' "$ROOT/.github/workflows/validate.yml" || fail "CI misses spec docs policy"

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
