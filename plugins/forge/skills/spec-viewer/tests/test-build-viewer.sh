#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." && pwd)"
SKILL="$ROOT/plugins/forge/skills/spec-viewer"
FIXTURES="$SKILL/tests/fixtures"
BUILDER="$SKILL/scripts/build-viewer.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

SPEC_DIR="$TMP/specs/001-basic"
PLAN_DIR="$TMP/plans/001-basic"
mkdir -p "$SPEC_DIR" "$PLAN_DIR/tasks"
cp "$FIXTURES/basic-spec.md" "$SPEC_DIR/spec.md"
cp "$FIXTURES/basic-plan.md" "$PLAN_DIR/plan.md"
printf '# Progress\n\nNo completed tasks.\n' > "$PLAN_DIR/progress.md"
printf '### Task 3: Extra task\n\n- [ ] **Step 1: Extra step**\n' > "$PLAN_DIR/tasks/003-extra.md"

FORGE_MERMAID_BUNDLE="$FIXTURES/mermaid-stub.js" \
  bash "$BUILDER" \
    --mode spec --locale ko \
    --spec "$SPEC_DIR/spec.md" \
    -c "$FIXTURES/basic-fragment.html" \
    -t "스펙에서 무엇을 확인해야 할까?" -s approved --offline

FORGE_MERMAID_BUNDLE="$FIXTURES/mermaid-stub.js" \
  bash "$BUILDER" \
    --mode plan --locale ko \
    --plan "$PLAN_DIR/plan.md" \
    --progress "$PLAN_DIR/progress.md" \
    --tasks-dir "$PLAN_DIR/tasks" \
    -c "$FIXTURES/basic-fragment.html" \
    -t "계획에서 무엇을 확인해야 할까?" -s active --offline

SPEC_OUT="$SPEC_DIR/view.html"
PLAN_OUT="$PLAN_DIR/view.html"
test -f "$SPEC_OUT"
test -f "$PLAN_OUT"

grep -q '<html lang="ko">' "$SPEC_OUT"
grep -q '"mode": "spec"' "$SPEC_OUT"
grep -q '"mode": "plan"' "$PLAN_OUT"
grep -q '"path": "spec.md"' "$SPEC_OUT"
grep -q '"path": "plan.md"' "$PLAN_OUT"
grep -q '"path": "progress.md"' "$PLAN_OUT"
grep -q '"path": "tasks/003-extra.md"' "$PLAN_OUT"
grep -q '"task": 3' "$PLAN_OUT"
grep -q '"step": 4' "$PLAN_OUT"
grep -q '"freshness": "unverified"' "$SPEC_OUT"
grep -q '"freshness": "unverified"' "$PLAN_OUT"
grep -q '>개요</button>' "$SPEC_OUT"
grep -q 'window.mermaid' "$SPEC_OUT"
grep -q 'rel="icon" href="data:image/svg+xml' "$SPEC_OUT"
grep -q 'font-variant-numeric: tabular-nums' "$SPEC_OUT"
grep -q '\.diagram-scroll' "$SPEC_OUT"
grep -q '\.table-scroll' "$SPEC_OUT"
grep -q 'min-width: 48rem' "$SPEC_OUT"
grep -q 'min-height: 44px' "$SPEC_OUT"
grep -q 'mermaid-error-message' "$SPEC_OUT"
grep -q '\[data-step\]' "$PLAN_OUT"
grep -q 'checkboxState.ac' "$SPEC_OUT"
grep -q 'checkboxState.step' "$PLAN_OUT"

if grep -q 'src="https://cdn.jsdelivr.net/npm/mermaid' "$SPEC_OUT"; then
  echo "offline output references the Mermaid CDN" >&2
  exit 1
fi

if bash "$BUILDER" \
  --mode combined \
  --spec "$SPEC_DIR/spec.md" \
  --plan "$PLAN_DIR/plan.md" \
  -c "$FIXTURES/basic-fragment.html" -t "Invalid" 2>/dev/null; then
  echo "combined mode unexpectedly succeeded" >&2
  exit 1
fi

MUSTACHE_OUT="$TMP/mustache-offline.html"
FORGE_MERMAID_BUNDLE="$FIXTURES/mermaid-mustache-stub.js" \
  bash "$BUILDER" \
    --mode spec --locale ko --spec "$SPEC_DIR/spec.md" \
    -c "$FIXTURES/basic-fragment.html" \
    -t "Bundle token" -s approved --offline -o "$MUSTACHE_OUT"
grep -q 'bundleTemplate = "{{NAV_LABEL}} / {{SOURCE_MANIFEST}}"' "$MUSTACHE_OUT"

AUTO_OUT="$TMP/basic-spec.html"
bash "$BUILDER" \
  --mode spec --locale en --spec "$SPEC_DIR/spec.md" \
  -c "$FIXTURES/basic-fragment.html" \
  -t "What should I review?" -s approved -o "$AUTO_OUT"
grep -q '"mode": "spec"' "$AUTO_OUT"
grep -q '>Overview</button>' "$AUTO_OUT"
grep -q 'src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"' "$AUTO_OUT"

printf 'test-build-viewer: all checks passed\n'
