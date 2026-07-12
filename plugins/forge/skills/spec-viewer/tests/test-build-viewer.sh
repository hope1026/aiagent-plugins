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
grep -q '<details class="source-summary">' "$SPEC_OUT"
grep -q 'data-source-path="spec.md"' "$SPEC_OUT"
grep -q 'data-freshness-overall>unverified</span>' "$SPEC_OUT"
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

bash "$BUILDER" --check "$PLAN_OUT"
cp "$PLAN_DIR/plan.md" "$PLAN_DIR/plan.md.original"
printf '\nchanged\n' >> "$PLAN_DIR/plan.md"
if bash "$BUILDER" --check "$PLAN_OUT"; then
  echo "stale Viewer unexpectedly passed --check" >&2
  exit 1
fi
mv "$PLAN_DIR/plan.md.original" "$PLAN_DIR/plan.md"

mv "$PLAN_DIR/progress.md" "$PLAN_DIR/progress.md.missing"
if bash "$BUILDER" --check "$PLAN_OUT"; then
  echo "Viewer with a missing source unexpectedly passed --check" >&2
  exit 1
fi
mv "$PLAN_DIR/progress.md.missing" "$PLAN_DIR/progress.md"

INVALID_OUT="$TMP/invalid-manifest.html"
printf '<html><script type="application/json" id="forge-source-manifest">{bad}</script></html>\n' > "$INVALID_OUT"
if bash "$BUILDER" --check "$INVALID_OUT"; then
  echo "invalid manifest unexpectedly passed --check" >&2
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

SCALE="$TMP/scale"
python3 "$FIXTURES/generate-scale-fixture.py" "$SCALE"
SCALE_SPEC="$SCALE/specs/001-scale"
SCALE_PLAN="$SCALE/plans/001-scale"

FORGE_MERMAID_BUNDLE="$FIXTURES/mermaid-stub.js" \
  bash "$BUILDER" --mode spec --locale ko \
    --spec "$SCALE_SPEC/spec.md" -c "$SCALE_SPEC/fragment.html" \
    -t "스펙은 무엇을 요구할까?" -s approved --offline
FORGE_MERMAID_BUNDLE="$FIXTURES/mermaid-stub.js" \
  bash "$BUILDER" --mode plan --locale ko \
    --plan "$SCALE_PLAN/plan.md" --progress "$SCALE_PLAN/progress.md" \
    --tasks-dir "$SCALE_PLAN/tasks" -c "$SCALE_PLAN/fragment.html" \
    -t "계획은 어떻게 실행될까?" -s active --offline

grep -q '"requirement": 190' "$SCALE_SPEC/view.html"
grep -q '"acceptance": 105' "$SCALE_SPEC/view.html"
grep -q '"mermaid": 9' "$SCALE_SPEC/view.html"
grep -q '"task": 22' "$SCALE_PLAN/view.html"
grep -q '"step": 110' "$SCALE_PLAN/view.html"
grep -q '"requirement": 0' "$SCALE_PLAN/view.html"
grep -q '"acceptance": 0' "$SCALE_PLAN/view.html"
test "$(grep -c 'class="tab-panel"' "$SCALE_SPEC/view.html")" -eq 6
test "$(grep -c 'class="tab-panel"' "$SCALE_PLAN/view.html")" -eq 6
test "$(grep -o 'data-route="Expedition Route ' "$SCALE_PLAN/view.html" | wc -l | tr -d ' ')" -eq 8
test "$(grep -o 'id="Task[0-9]*"' "$SCALE_PLAN/view.html" | sort -u | wc -l | tr -d ' ')" -eq 22
test "$(grep -o 'data-step="Task[0-9]*-Step[0-9]*"' "$SCALE_PLAN/view.html" | wc -l | tr -d ' ')" -eq 110
test "$(grep -o 'id="R[0-9]*"' "$SCALE_SPEC/view.html" | sort -u | wc -l | tr -d ' ')" -eq 190
test "$(grep -o 'data-ac="AC[0-9]*"' "$SCALE_SPEC/view.html" | wc -l | tr -d ' ')" -eq 105
grep -q 'data-origin="Spec source"' "$SCALE_SPEC/view.html"
grep -q 'data-origin="Plan source"' "$SCALE_PLAN/view.html"
grep -q 'data-origin="Derived view"' "$SCALE_PLAN/view.html"
! grep -q 'data-origin="Spec source"' "$SCALE_PLAN/view.html"
python3 "$FIXTURES/verify-mermaid-equality.py" "$SCALE_SPEC/spec.md" "$SCALE_SPEC/view.html"
bash "$BUILDER" --check "$SCALE_SPEC/view.html"
bash "$BUILDER" --check "$SCALE_PLAN/view.html"

printf 'test-build-viewer: all checks passed\n'
