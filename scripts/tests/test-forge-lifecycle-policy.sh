#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fail() { echo "FAIL: $1" >&2; exit 1; }

WRITING_SPECS="$ROOT_DIR/plugins/forge/skills/writing-specs/SKILL.md"
WRITING_PLANS="$ROOT_DIR/plugins/forge/skills/writing-plans/SKILL.md"
PLAN_VISUAL="$ROOT_DIR/plugins/forge/skills/writing-plans/references/plan-visual-structure.md"
REVIEW_VIEWER="$ROOT_DIR/plugins/forge/skills/visual-docs/SKILL.md"
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
grep -q 'visual-docs' "$WRITING_SPECS" || fail "writing-specs misses request-only handoff"
grep -q 'visual-docs' "$WRITING_PLANS" || fail "writing-plans misses request-only handoff"
grep -q 'visual-docs' "$EXECUTING_PLANS" || fail "executing-plans misses request-only handoff"

# Negative pressure: status/source changes never imply Visual Docs generation.
grep -qi 'Report possible staleness without reading or updating it' "$WRITING_SPECS" || \
  fail "negative pressure policy does not forbid assuming visual document freshness"
grep -qi 'transaction validates Markdown only' "$WRITING_SPECS" || \
  fail "negative pressure policy does not keep Markdown as the lifecycle artifact"
grep -q 'Source changes, approval, lifecycle status.*not generation requests' "$WRITING_SPECS" || \
  fail "status changes can still trigger Visual Docs generation"

# Positive pressure: explicit Visual Docs intent is enough; the agent resolves source/kind/id at handoff.
grep -qi 'Only an explicit user request.*permits one handoff' "$WRITING_SPECS" || fail "positive request intent is missing"
if grep -q 'request names the current source path\|request naming.*source.*mode.*view-id' "$WRITING_SPECS" "$WRITING_PLANS" "$EXECUTING_PLANS"; then
  fail "lifecycle wrongly requires the user to provide source, kind, and view-id"
fi
if rg -n 'explicit source/kind/view-id|Visual Docs still requires an exact request' \
  "$WRITING_SPECS" "$VERIFYING_WORK" "$README" >/dev/null; then
  fail "request overconstraint remains outside writer handoff"
fi
grep -q 'exactly one.*handoff\|one.*handoff' "$WRITING_SPECS" || fail "positive request does not cap handoff at one"
grep -q 'within the same request' "$REVIEW_VIEWER" || fail "visual-docs misses in-scope correction authority"
grep -q 'Inspect the actual reading path' "$REVIEW_VIEWER" || fail "visual-docs misses rendered verification"
if rg -n 'Run one build command|Do not add a second checker|NO STEP WITHOUT ITS COMPLETE CONTENT' "$REVIEW_VIEWER" "$VERIFYING_WORK" "$WRITING_PLANS" >/dev/null; then
  fail "obsolete build-count, verification, or full-code gate remains"
fi
grep -q -- '--dry-run --format json' "$REVIEW_VIEWER" || fail "visual-docs misses presentation preflight"
grep -q 'profile.*generic' "$REVIEW_VIEWER" || fail "visual-docs preflight does not catch generic degradation"
grep -q 'primary component' "$REVIEW_VIEWER" || fail "visual-docs preflight does not catch empty primary composition"
grep -q '## Iron Law' "$REVIEW_VIEWER" || fail "visual-docs misses its iron law"
grep -q 'Do not hand-edit any generated Visual Doc' "$REVIEW_VIEWER" || fail "visual-docs allows generated output hand edits"
grep -q 'create one checklist item' "$REVIEW_VIEWER" || fail "visual-docs misses its execution checklist"
grep -q '## Red Flags' "$REVIEW_VIEWER" || fail "visual-docs misses pressure counters"
grep -q 'the forge using-forge skill' "$REVIEW_VIEWER" || fail "visual-docs misses terminal lifecycle handoff"
grep -q 'visual candidate' "$REVIEW_VIEWER" || fail "visual-docs preflight misses source-backed visual candidates"
grep -q 'decorative diagram' "$REVIEW_VIEWER" || fail "visual-docs does not reject decorative diagrams"
grep -q 'meets or exceeds the relationship threshold' "$REVIEW_VIEWER" || fail "visual-docs threshold excludes boundary candidates"
grep -q 'every qualifying visual candidate' "$REVIEW_VIEWER" || fail "visual-docs can validate only one of several candidates"
grep -q 'ownership.*before.*matrix' "$REVIEW_VIEWER" || fail "visual-docs misses relation-shape precedence"
grep -q 'non-qualifying source block' "$REVIEW_VIEWER" || fail "visual-docs can drop mixed-source text fallbacks"
grep -q 'ownership or dependency before mapping' "$REVIEW_VIEWER" || fail "visual-docs precedence is incomplete"
grep -q 'Each derived visual.*source path.*Derived view' "$REVIEW_VIEWER" || fail "visual-docs misses visible per-visual provenance"

if rg -n 'score 2\+ uses|rebuild an existing Viewer|If a lifecycle Viewer exists, rebuild|rebuild it before the first checkpoint' \
  "$WRITING_SPECS" "$WRITING_PLANS" "$EXECUTING_PLANS" >/dev/null; then
  fail "automatic Viewer generation language remains"
fi

if rg -n 'Spec Pages|build --root docs/specs|check --root docs/specs' \
  "$WRITING_SPECS" "$WRITING_PLANS" "$EXECUTING_PLANS" "$VERIFYING_WORK" >/dev/null; then
  fail "active lifecycle retains automatic HTML generation"
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
grep -q 'A preference never waives dependency, write-overlap, verification, or root-ownership gates' "$ROUTING_REF" || fail "routing allows direct requests to bypass parallel safety"
grep -q 'overlapping writes remain sequential' "$ROUTING_REF" || fail "adaptive routing misses the user-pressure counter"
grep -q 'internal checkpoint' "$EXECUTING_PLANS" || fail "missing internal checkpoint"
grep -q 'notify checkpoint' "$EXECUTING_PLANS" || fail "missing notify checkpoint"
grep -q 'approval checkpoint' "$EXECUTING_PLANS" || fail "missing approval checkpoint"
grep -q 'approval gate' "$WRITING_PLANS" || fail "writing-plans misses approval metadata"
grep -q 'route evidence' "$VERIFYING_WORK" || fail "verifying-work misses route evidence review"
grep -q '\*\*Related Specs:\*\* None — Canonical Spec impact: no; <high-complexity reason>' "$WRITING_PLANS" || fail "spec-free Related Specs one-line form missing"
grep -q -- '- bundle: docs/specs/<semantic-bundle-name>/' "$WRITING_PLANS" || fail "Related Specs does not use a bundle path"
grep -q 'Governing statements:' "$WRITING_PLANS" || fail "task statement trace is missing"
grep -q 'exact heading text' "$WRITING_PLANS" || fail "task statement trace does not preserve full headings"
grep -q 'Requirement → Acceptance Criterion → Task' "$PLAN_VISUAL" || fail "visual trace omits full-statement flow"
grep -q 'progress.md.*long history.*multiple independent executors' "$WRITING_PLANS" || fail "progress.md creation gate is incomplete"
grep -q 'tasks/\*\.md.*large plan.*independent ownership.*parallel execution.*independent approval' "$WRITING_PLANS" || fail "tasks/*.md creation gate is incomplete"
grep -qi 'Before deleting.*plan.*permanent decisions.*Canonical Spec.*docs/research' "$WRITING_PLANS" || fail "plan deletion promotion gate is missing"
grep -qi 'repository-contained.*bundle path' "$WRITING_PLANS" || fail "Related Specs containment gate missing"
grep -q 'unique normalized bundle paths' "$WRITING_PLANS" || fail "duplicate Related Specs bundle gate missing"
grep -q 'exact linked Requirement and Acceptance statement' "$WRITING_PLANS" || fail "Related Specs statement existence gate missing"

# Scale verification and planning without weakening logic or authority boundaries.
TDD="$ROOT_DIR/plugins/forge/skills/test-driven-development/SKILL.md"
APP="$ROOT_DIR/plugins/forge/skills/web-app-design/SKILL.md"
grep -q 'NEW LOGIC AND BEHAVIORAL FIXES NEED AN OBSERVED FAILING TEST' "$TDD" || fail "logic lost its regression gate"
grep -q 'Do not install a test framework just to assert a label' "$TDD" || fail "presentation changes still require test infrastructure"
grep -q 'Focused adjustment' "$APP" || fail "UI lacks a focused path"
grep -q 'Partial change or restoration of an implemented baseline' "$WRITING_PLANS" || fail "plan scope cannot follow partial changes"
grep -q 'Do not write the implementation twice' "$WRITING_PLANS" || fail "plan still duplicates implementation"
grep -q 'same unchanged implementation' "$VERIFYING_WORK" || fail "verification evidence cannot be reused safely"
grep -q 'already given for a concrete proposal' "$WRITING_PLANS" || fail "concrete approval reuse missing"

echo "forge lifecycle policy: all checks passed"
