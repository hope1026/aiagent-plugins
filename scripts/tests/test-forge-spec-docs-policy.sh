#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fail() { echo "FAIL: $1" >&2; exit 1; }

WRITING_SPECS="$ROOT/plugins/forge/skills/writing-specs/SKILL.md"
SPEC_TEMPLATE="$ROOT/plugins/forge/skills/writing-specs/references/spec-template.md"
WRITING_PLANS="$ROOT/plugins/forge/skills/writing-plans/SKILL.md"
EXECUTING_PLANS="$ROOT/plugins/forge/skills/executing-plans/SKILL.md"
VERIFYING_WORK="$ROOT/plugins/forge/skills/verifying-work/SKILL.md"
USING_FORGE="$ROOT/plugins/forge/skills/using-forge/SKILL.md"
VALIDATE="$ROOT/scripts/validate.sh"
MAINTAINER="$ROOT/.agent-extensions/maintaining-forge/skills/maintaining-forge/SKILL.md"

grep -q 'schema: forge/spec@1' "$SPEC_TEMPLATE" || fail "template misses forge/spec@1"
for field in schema id status language kind areas components relatedSpecs; do
  grep -q "^$field:" "$SPEC_TEMPLATE" || fail "template misses $field frontmatter"
done
grep -q 'generator.*template.*runtime.*asset' "$MAINTAINER" || fail "maintainer misses shared Spec Pages tooling gate"
grep -q 'spec-docs.sh.*build --root docs/specs --offline' "$MAINTAINER" || fail "maintainer misses full Spec Pages rebuild"
grep -q 'spec-docs.sh.*check --root docs/specs' "$MAINTAINER" || fail "maintainer misses Spec Pages check"
if grep -Fq 'spec-docs.sh --repo-root . build --root docs/specs --changed' "$MAINTAINER"; then
  fail "maintainer tooling gate incorrectly uses changed-only build"
fi
for heading in 'Overview' 'Requirements' 'Behavior & Flows' 'Data & Interfaces' 'Acceptance Criteria' 'Decisions & History'; do
  grep -q "^## $heading$" "$SPEC_TEMPLATE" || fail "template misses canonical heading: $heading"
done
grep -q '^kind: <feature|system|interface|policy>$' "$SPEC_TEMPLATE" || fail "template misses exact kind enum"
grep -q '^areas: \["<area>"\]$' "$SPEC_TEMPLATE" || fail "template areas are not JSON strings"
grep -q '^components: \["<component>"\]$' "$SPEC_TEMPLATE" || fail "template components are not JSON strings"

# The production parser, not grep alone, must accept the canonical template-shaped fixture.
PYTHONPATH="$ROOT/plugins/forge/skills/writing-specs/scripts" python3 - \
  "$ROOT/plugins/forge/skills/writing-specs/tests/fixtures/spec-model/001-valid-ko/spec.md" <<'PY'
from pathlib import Path
import sys
from spec_model import load_spec

path = Path(sys.argv[1])
document, diagnostics = load_spec(path, path.parents[1])
assert diagnostics == (), diagnostics
assert document is not None
assert document.metadata.schema == "forge/spec@1"
assert document.metadata.kind in {"feature", "system", "interface", "policy"}
assert "Data & Interfaces" in document.sections
PY

for command in 'validate --root docs/specs --baseline-ref HEAD' 'build --root docs/specs --changed' 'check --root docs/specs'; do
  grep -q "$command" "$WRITING_SPECS" || fail "writing-specs misses spec-docs transaction: $command"
done
grep -q 'docs/specs/.transitions.json' "$WRITING_SPECS" || fail 'writing-specs misses transition manifest'
grep -q 'replacement.*draft.*before.*old source' "$WRITING_SPECS" || fail 'writing-specs misses approval-first replacement gate'
grep -q 'explicit approval' "$WRITING_SPECS" || fail 'writing-specs misses explicit supersession approval'
grep -q 'registered isolated Git worktree' "$WRITING_SPECS" || fail 'writing-specs misses isolation gate'
grep -q 'expected clean HEAD' "$WRITING_SPECS" || fail 'writing-specs misses exact root precondition'
grep -q 'candidate commit' "$WRITING_SPECS" || fail 'writing-specs misses candidate commit gate'
grep -q 'HEAD.*index.*tracked.*untracked bytes' "$WRITING_SPECS" || fail 'writing-specs misses root byte fingerprint'
grep -q 'Review Viewer output count.*exactly zero' "$WRITING_SPECS" || fail 'writing-specs misses request-only zero gate'
grep -q 'one-to-one.*superseded.*docs/specs/.transitions.json' "$SPEC_TEMPLATE" || fail 'template misses identity supersession exception'
grep -q 'schema.*status.*diagnostics' "$WRITING_PLANS" || fail "writing-plans does not inspect typed lifecycle fields"
grep -q 'spec-docs.sh.*inspect.*--spec.*--format json' "$WRITING_PLANS" || fail "writing-plans misses inspect CLI"
grep -q 'spec-docs.sh.*inspect.*--spec.*--format json' "$EXECUTING_PLANS" || fail "executing-plans misses inspect CLI"
grep -q 'spec-docs.sh.*inspect.*--spec.*--format json' "$VERIFYING_WORK" || fail "verifying-work misses inspect CLI"
grep -q 'frontmatter.*status' "$VERIFYING_WORK" || fail "verifying-work misses frontmatter status transition"
grep -q 'build --root docs/specs --changed' "$VERIFYING_WORK" || fail "verifying-work misses page build after implemented"
grep -q 'check --root docs/specs' "$VERIFYING_WORK" || fail "verifying-work misses page check after implemented"
if rg -n 'set (the )?spec.*`?Status: implemented|set .*Status: implemented' \
  "$ROOT/plugins/forge/skills" --glob 'SKILL.md' >/dev/null; then
  fail "active lifecycle imperative still writes body Status"
fi

grep -q 'Spec Pages' "$USING_FORGE" || fail "using-forge misses durable Spec Pages"
grep -q '.forge/reviews/<review-id>/view.html' "$USING_FORGE" || fail "using-forge misses Review Viewer output"
grep -q 'review-viewer' "$USING_FORGE" || fail "using-forge misses review-viewer routing"
grep -qx '/.forge/' "$ROOT/.gitignore" || fail "root .forge ignore rule is not exact"

grep -Fq '"$SPEC_DOCS" --repo-root "$ROOT_DIR" validate' "$VALIDATE" || fail "validator misses explicit repo-root validate"
grep -Fq '"$SPEC_DOCS" --repo-root "$ROOT_DIR" check' "$VALIDATE" || fail "validator misses explicit repo-root check"

if rg -n 'forge spec-viewer skill|docs/specs/NNN-<slug>/view\.html|docs/plans/PPP-<slug>/view\.html' \
  "$ROOT/plugins/forge/skills" "$ROOT/README.md" >/dev/null; then
  fail "active lifecycle instructions retain legacy Viewer paths"
fi

echo "forge spec docs policy: all checks passed"
