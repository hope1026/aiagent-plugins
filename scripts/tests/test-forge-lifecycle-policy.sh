#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fail() { echo "FAIL: $1" >&2; exit 1; }

WRITING_SPECS="$ROOT_DIR/plugins/forge/skills/writing-specs/SKILL.md"
WRITING_PLANS="$ROOT_DIR/plugins/forge/skills/writing-plans/SKILL.md"
PLAN_VISUAL="$ROOT_DIR/plugins/forge/skills/writing-plans/references/plan-visual-structure.md"
REVIEW_VIEWER="$ROOT_DIR/plugins/forge/skills/review-viewer/SKILL.md"
EXECUTING_PLANS="$ROOT_DIR/plugins/forge/skills/executing-plans/SKILL.md"
ROUTING_REF="$ROOT_DIR/plugins/forge/skills/executing-plans/references/adaptive-routing.md"
CODEX_REF="$ROOT_DIR/plugins/forge/skills/using-forge/references/codex-tools.md"
VERIFYING_WORK="$ROOT_DIR/plugins/forge/skills/verifying-work/SKILL.md"
USING_FORGE="$ROOT_DIR/plugins/forge/skills/using-forge/SKILL.md"
README="$ROOT_DIR/README.md"

for file in "$WRITING_SPECS" "$WRITING_PLANS" "$REVIEW_VIEWER" "$EXECUTING_PLANS"; do
  grep -Eqi 'explicit (user )?request|explicitly requested' "$file" || fail "$file misses explicit user request gate"
done

grep -q 'Markdown is the default review path' "$WRITING_SPECS" || fail "writing-specs does not default to Markdown"
grep -q 'Spec Pages' "$WRITING_SPECS" || fail "writing-specs misses durable Spec Pages transaction"
grep -q 'review-viewer' "$WRITING_SPECS" || fail "writing-specs misses request-only handoff"
grep -q 'review-viewer' "$WRITING_PLANS" || fail "writing-plans misses request-only handoff"
grep -q 'review-viewer' "$EXECUTING_PLANS" || fail "executing-plans misses request-only handoff"

# Negative pressure: status/source changes never imply Review Viewer generation.
grep -qi 'existing Review Viewer.*never.*current\|never assume.*Review Viewer.*current' "$WRITING_SPECS" || \
  fail "negative pressure policy does not forbid assuming Viewer freshness"
grep -q 'source.*status.*Spec Pages.*same transaction\|Spec Pages.*same transaction.*status' "$WRITING_SPECS" || \
  fail "negative pressure policy does not keep Spec Pages in the source transaction"
grep -q 'status.*change.*not.*explicit.*request\|status.*change.*never.*request' "$WRITING_SPECS" || \
  fail "status changes can still trigger Review Viewer generation"

# Positive pressure: explicit Viewer intent is enough; the agent resolves source/mode/id at handoff.
grep -qi 'explicit Review Viewer intent\|explicitly asks.*Review Viewer' "$WRITING_SPECS" || fail "positive request intent is missing"
if grep -q 'request names the current source path\|request naming.*source.*mode.*review-id' "$WRITING_SPECS" "$WRITING_PLANS" "$EXECUTING_PLANS"; then
  fail "lifecycle wrongly requires the user to provide source, mode, and review-id"
fi
if rg -n 'explicit source/mode/review-id|Review Viewer still requires an exact request' \
  "$WRITING_SPECS" "$VERIFYING_WORK" "$README" >/dev/null; then
  fail "request overconstraint remains outside writer handoff"
fi
grep -q 'exactly one.*handoff\|one.*handoff' "$WRITING_SPECS" || fail "positive request does not cap handoff at one"
grep -q 'Run one build command' "$REVIEW_VIEWER" || fail "review-viewer does not enforce one build"

if rg -n 'score 2\+ uses|rebuild an existing Viewer|If a lifecycle Viewer exists, rebuild|rebuild it before the first checkpoint' \
  "$WRITING_SPECS" "$WRITING_PLANS" "$EXECUTING_PLANS" >/dev/null; then
  fail "automatic Viewer generation language remains"
fi

for term in fast balanced frontier; do
  grep -q "$term" "$EXECUTING_PLANS" || fail "executing-plans misses $term"
done
for term in impact uncertainty context_coupling verification_clarity parallel_group; do
  grep -q "$term" "$ROUTING_REF" || fail "adaptive routing reference misses $term"
done
grep -q 'maximum of 3 concurrent subagents' "$ROUTING_REF" || fail "adaptive routing reference misses default concurrency cap"
grep -q 'inherit the current model' "$CODEX_REF" || fail "Codex fallback does not inherit the current model"
grep -q 'subagents remain available' "$CODEX_REF" || fail "Codex model fallback incorrectly disables subagents"
grep -q 'requesting parallel execution does not' "$USING_FORGE" || fail "using-forge allows direct requests to bypass parallel safety"
grep -q 'overlapping writes remain sequential' "$ROUTING_REF" || fail "adaptive routing misses the user-pressure counter"
grep -q 'internal checkpoint' "$EXECUTING_PLANS" || fail "missing internal checkpoint"
grep -q 'notify checkpoint' "$EXECUTING_PLANS" || fail "missing notify checkpoint"
grep -q 'approval checkpoint' "$EXECUTING_PLANS" || fail "missing approval checkpoint"
grep -q 'approval gate' "$WRITING_PLANS" || fail "writing-plans misses approval metadata"
grep -q 'route evidence' "$VERIFYING_WORK" || fail "verifying-work misses route evidence review"
grep -q '\*\*Related Specs:\*\* None — <qualifying reason>' "$WRITING_PLANS" || fail "spec-free Related Specs one-line form missing"
grep -q '### Task 3: Login endpoint (008 R2, R4, AC2)' "$WRITING_PLANS" || fail "single-spec task trace is not source-qualified"
grep -q 'Multi-spec AC Coverage.*source-qualified\|multi-spec AC Coverage.*source-qualified' "$WRITING_PLANS" || fail "multi-spec AC coverage namespace rule missing"
grep -q 'including single-spec plans' "$PLAN_VISUAL" || fail "visual trace omits single-spec source qualification"
grep -q 'progress.md.*long history.*multiple independent executors' "$WRITING_PLANS" || fail "progress.md creation gate is incomplete"
grep -q 'tasks/\*\.md.*large plan.*independent ownership.*parallel execution.*independent approval' "$WRITING_PLANS" || fail "tasks/*.md creation gate is incomplete"
grep -q 'Before deleting.*plan.*permanent decisions.*spec.*research' "$WRITING_PLANS" || fail "plan deletion promotion gate is missing"
grep -q 'entry `id`.*inspect `id`' "$WRITING_PLANS" || fail "Related Specs id/inspect id gate missing"
grep -q 'repository-contained.*path' "$WRITING_PLANS" || fail "Related Specs containment gate missing"
grep -q 'duplicate spec IDs' "$WRITING_PLANS" || fail "duplicate Related Specs id gate missing"
grep -q 'requirements.*acceptance.*inspect arrays' "$WRITING_PLANS" || fail "Related Specs item existence gate missing"
if grep -Eq '### Task [0-9]+: .+ \(R[0-9]' "$WRITING_PLANS"; then
  fail "unqualified task trace example remains"
fi

echo "forge lifecycle policy: all checks passed"
