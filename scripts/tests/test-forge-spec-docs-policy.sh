#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fail() { echo "FAIL: $1" >&2; exit 1; }

WRITING_SPECS="$ROOT/plugins/forge/skills/writing-specs/SKILL.md"
SPEC_TEMPLATE="$ROOT/plugins/forge/skills/writing-specs/references/spec-template.md"
DELTA_TEMPLATE="$ROOT/plugins/forge/skills/writing-specs/references/spec-delta-template.md"
WRITING_PLANS="$ROOT/plugins/forge/skills/writing-plans/SKILL.md"
EXECUTING_PLANS="$ROOT/plugins/forge/skills/executing-plans/SKILL.md"
VERIFYING_WORK="$ROOT/plugins/forge/skills/verifying-work/SKILL.md"
USING_FORGE="$ROOT/plugins/forge/skills/using-forge/SKILL.md"
REVIEW_VIEWER="$ROOT/plugins/forge/skills/review-viewer/SKILL.md"
RENDERING_CONTRACT="$ROOT/plugins/forge/skills/review-viewer/references/rendering-contract.md"
VALIDATE="$ROOT/scripts/validate.sh"
MAINTAINER="$ROOT/.agent-extensions/maintaining-forge/skills/maintaining-forge/SKILL.md"
PORTABILITY="$ROOT/.agent-extensions/maintaining-forge/skills/maintaining-forge/references/portability-rules.md"
README="$ROOT/README.md"

grep -q 'schema: forge/spec@3' "$SPEC_TEMPLATE" || fail "template misses forge/spec@3"
for field in schema role status language kind areas components relatedSpecs; do
  grep -q "^$field:" "$SPEC_TEMPLATE" || fail "template misses $field frontmatter"
done
if grep -q '^id:' "$SPEC_TEMPLATE"; then
  fail "template still declares a document id"
fi
grep -q 'Markdown-only' "$MAINTAINER" || fail "maintainer misses Markdown-only lifecycle"
for heading in 'Requirements' 'Acceptance Criteria' 'Decisions & History'; do
  grep -q "^## $heading$" "$SPEC_TEMPLATE" || fail "template misses required semantic heading: $heading"
done
grep -q '^subtype: <optional-lowercase-kebab-case>$' "$SPEC_TEMPLATE" || fail "template misses optional subtype"
grep -q '^kind: <feature|system|interface|policy>$' "$SPEC_TEMPLATE" || fail "template misses exact kind enum"
grep -q '^areas: \["<area>"\]$' "$SPEC_TEMPLATE" || fail "template areas are not JSON strings"
grep -q '^components: \["<component>"\]$' "$SPEC_TEMPLATE" || fail "template components are not JSON strings"
grep -q '^## Documents$' "$SPEC_TEMPLATE" || fail "template misses bundle document inventory"
grep -q 'docs/specs/<semantic-bundle-name>/' "$WRITING_SPECS" || fail "writing-specs misses semantic bundle path"
grep -q 'full Requirement and Acceptance statement' "$WRITING_SPECS" || fail "writing-specs misses full-statement trace contract"
grep -q 'member path' "$WRITING_SPECS" || fail "writing-specs misses member-path contract"

if rg -n 'docs/specs/(NNN|OOO|[0-9]{3})-|docs/specs/[^` ]+/spec\.md|forge/spec@2|\.transitions\.json|R·AC|R/AC|R-ID|AC-ID|R and AC IDs|\bR[0-9]+\b|\bAC[0-9]+\b|requirements: \[R|acceptance: \[AC|Canonical Spec ID|Spec ID|spec ID' \
  "$ROOT/plugins/forge/skills" "$ROOT/.agent-extensions/maintaining-forge" "$README" \
  --glob 'SKILL.md' --glob '**/references/*.md' --glob '!**/tests/**' --glob '!**/fixtures/**' >/dev/null; then
  fail "active Forge instructions still contain legacy spec identity or trace syntax"
fi

# The production parser, not grep alone, must accept the canonical bundle fixture.
PYTHONPATH="$ROOT/plugins/forge/skills/writing-specs/scripts" python3 - \
  "$ROOT/plugins/forge/skills/writing-specs/tests/fixtures/spec-bundle/valid-multi-file" <<'PY'
from pathlib import Path
import sys
from spec_model import load_spec_bundle

path = Path(sys.argv[1])
bundle, diagnostics = load_spec_bundle(path, path.parents[3])
assert diagnostics == (), diagnostics
assert bundle is not None
assert bundle.metadata.schema == "forge/spec@3"
assert bundle.metadata.kind in {"feature", "system", "interface", "policy"}
assert len(bundle.members) == 2
PY

grep -q 'validate --root docs/specs --baseline-ref HEAD' "$WRITING_SPECS" || fail "writing-specs misses validation transaction"
CLI_HELP="$(bash "$ROOT/plugins/forge/skills/writing-specs/scripts/spec-docs.sh" --help)"
grep -q 'validate' <<<"$CLI_HELP" || fail "spec-docs CLI misses validate"
grep -q 'inspect' <<<"$CLI_HELP" || fail "spec-docs CLI misses inspect"
if grep -Eq '(^|[,{[:space:]])(build|check)([]},[:space:]]|$)' <<<"$CLI_HELP"; then
  fail "spec-docs CLI still exposes Spec Pages commands"
fi
grep -q 'docs/specs/.bundle-transitions.json' "$WRITING_SPECS" || fail 'writing-specs misses bundle transition manifest'
grep -q 'replacement.*Spec Delta.*before touching.*current source' "$WRITING_SPECS" || fail 'writing-specs misses approval-first replacement gate'
grep -q 'explicit approval' "$WRITING_SPECS" || fail 'writing-specs misses explicit supersession approval'
grep -q 'registered isolated Git worktree' "$WRITING_SPECS" || fail 'writing-specs misses isolation gate'
grep -q 'expected clean HEAD' "$WRITING_SPECS" || fail 'writing-specs misses exact root precondition'
grep -q 'candidate commit' "$WRITING_SPECS" || fail 'writing-specs misses candidate commit gate'
grep -q 'HEAD.*index.*tracked.*untracked bytes' "$WRITING_SPECS" || fail 'writing-specs misses root byte fingerprint'
grep -q 'Review Viewer output count.*exactly zero' "$WRITING_SPECS" || fail 'writing-specs misses request-only zero gate'
grep -q 'one-to-one.*superseded.*docs/specs/.bundle-transitions.json' "$SPEC_TEMPLATE" || fail 'template misses bundle supersession exception'
grep -q 'schema.*status.*diagnostics' "$WRITING_PLANS" || fail "writing-plans does not inspect typed lifecycle fields"
grep -q 'spec-docs.sh.*inspect.*--spec.*--format json' "$WRITING_PLANS" || fail "writing-plans misses inspect CLI"
grep -q 'spec-docs.sh.*inspect.*--spec.*--format json' "$EXECUTING_PLANS" || fail "executing-plans misses inspect CLI"
grep -q 'spec-docs.sh.*inspect.*--spec.*--format json' "$VERIFYING_WORK" || fail "verifying-work misses inspect CLI"
grep -q 'Canonical Spec lifecycle.*status.*implemented' "$VERIFYING_WORK" || fail "verifying-work misses Canonical lifecycle status transition"
grep -q 'run the writer transaction' "$VERIFYING_WORK" || fail "verifying-work misses validation after implemented"
if rg -n 'set (the )?spec.*`?Status: implemented|set .*Status: implemented' \
  "$ROOT/plugins/forge/skills" --glob 'SKILL.md' >/dev/null; then
  fail "active lifecycle imperative still writes body Status"
fi

grep -q '.forge/reviews/<review-id>/view.html' "$USING_FORGE" || fail "using-forge misses Review Viewer output"
grep -q 'review-viewer' "$USING_FORGE" || fail "using-forge misses review-viewer routing"
grep -qx '/.forge/' "$ROOT/.gitignore" || fail "root .forge ignore rule is not exact"

grep -Fq '"$SPEC_DOCS" --repo-root "$ROOT_DIR" validate' "$VALIDATE" || fail "validator misses explicit repo-root validate"

if rg -n 'Spec Pages|build --root docs/specs|check --root docs/specs' \
  "$WRITING_SPECS" "$WRITING_PLANS" "$EXECUTING_PLANS" "$VERIFYING_WORK" "$USING_FORGE" "$MAINTAINER" >/dev/null; then
  fail "active lifecycle retains automatic HTML generation"
fi

if rg -n 'forge spec-viewer skill|docs/specs/NNN-<slug>/view\.html|docs/plans/PPP-<slug>/view\.html' \
  "$ROOT/plugins/forge/skills" "$ROOT/README.md" >/dev/null; then
  fail "active lifecycle instructions retain legacy Viewer paths"
fi

echo "forge spec docs policy: all checks passed"
