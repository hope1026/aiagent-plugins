#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SPEC_ROOT="$REPO_ROOT/docs/specs"
SPEC_DOCS="$REPO_ROOT/plugins/forge/skills/writing-specs/scripts/spec-docs.sh"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

expected_roots=(
  "tone-overlay-skills/tone-overlay-skill-contract.md"
  "review-viewer-lifecycle/human-readable-review-viewer.md"
  "forge-repository-maintenance/forge-repository-maintenance-contract.md"
  "adaptive-execution-routing/adaptive-execution-routing-and-checkpoints.md"
  "cross-agent-extension-creation/cross-agent-extension-creation.md"
  "forge-ui-design-skill-separation/forge-ui-design-skill-separation.md"
  "semantic-spec-bundles/semantic-spec-bundle-contract.md"
  "canonical-spec-workflow/canonical-spec-and-work-artifact-boundaries.md"
)

for relative_root in "${expected_roots[@]}"; do
  [[ -f "$SPEC_ROOT/$relative_root" ]] || fail "missing migrated Spec Bundle root: $relative_root"
done

numeric_directories="$(find "$SPEC_ROOT" -mindepth 1 -maxdepth 1 -type d -name '[0-9]*' -print)"
[[ -z "$numeric_directories" ]] || fail "numeric Spec Bundle directories remain: $numeric_directories"

generic_members="$(find "$SPEC_ROOT" -mindepth 2 -maxdepth 2 -type f -name 'spec.md' -print)"
[[ -z "$generic_members" ]] || fail "generic spec.md members remain: $generic_members"

if rg -n --glob '*.md' \
  'forge/spec@2|^id:[[:space:]]|^- (R[0-9]+\.|AC[0-9]+ )|\b(MODIFIED|ADDED|REMOVED)[[:space:]]+—|\b(R[0-9]+|AC[0-9]+)\b' \
  "$SPEC_ROOT"; then
  fail "migrated active Spec Bundles contain legacy author-facing locators"
fi

"$SPEC_DOCS" --repo-root "$REPO_ROOT" validate --root docs/specs

echo "spec bundle migration contract tests passed"
