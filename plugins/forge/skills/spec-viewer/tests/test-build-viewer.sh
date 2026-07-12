#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." && pwd)"
SKILL="$ROOT/plugins/forge/skills/spec-viewer"
FIXTURES="$SKILL/tests/fixtures"
BUILDER="$SKILL/scripts/build-viewer.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

OUT="$TMP/basic-review.html"
FORGE_MERMAID_BUNDLE="$FIXTURES/mermaid-stub.js" \
  bash "$BUILDER" \
    --mode combined \
    --locale ko \
    --spec "$FIXTURES/basic-spec.md" \
    --plan "$FIXTURES/basic-plan.md" \
    -c "$FIXTURES/basic-fragment.html" \
    -t "무엇을 검토해야 할까?" \
    -s approved \
    --offline \
    -o "$OUT"

grep -q '<html lang="ko">' "$OUT"
grep -q '"mode": "combined"' "$OUT"
grep -q '"locale": "ko"' "$OUT"
grep -q '"task": 2' "$OUT"
grep -q '"step": 3' "$OUT"
grep -q '"requirement": 2' "$OUT"
grep -q '"acceptance": 2' "$OUT"
grep -q '"mermaid": 1' "$OUT"
grep -q '"freshness": "current"' "$OUT"
grep -q 'data-tab="overview"' "$OUT"
grep -q '>개요</button>' "$OUT"
grep -q 'window.mermaid' "$OUT"
grep -q 'rel="icon" href="data:image/svg+xml' "$OUT"
grep -q 'font-variant-numeric: tabular-nums' "$OUT"
grep -q '\.diagram-scroll' "$OUT"
grep -q '\.table-scroll' "$OUT"
grep -q 'min-width: 48rem' "$OUT"
grep -q 'min-height: 44px' "$OUT"
grep -q 'mermaid-error-message' "$OUT"
grep -q '\[data-step\]' "$OUT"
grep -q 'checkboxState.ac' "$OUT"
grep -q 'checkboxState.step' "$OUT"
if grep -q 'src="https://cdn.jsdelivr.net/npm/mermaid' "$OUT"; then
  echo "offline output references the Mermaid CDN" >&2
  exit 1
fi

MUSTACHE_OUT="$TMP/mustache-offline.html"
FORGE_MERMAID_BUNDLE="$FIXTURES/mermaid-mustache-stub.js" \
  bash "$BUILDER" \
    --mode spec --locale ko \
    --spec "$FIXTURES/basic-spec.md" \
    -c "$FIXTURES/basic-fragment.html" \
    -t "Bundle token" -s approved --offline \
    -o "$MUSTACHE_OUT"
grep -q 'bundleTemplate = "{{NAV_LABEL}} / {{SOURCE_MANIFEST}}"' "$MUSTACHE_OUT"

AUTO_OUT="$TMP/basic-spec.html"
bash "$BUILDER" \
  --mode spec \
  --locale en \
  --spec "$FIXTURES/basic-spec.md" \
  -c "$FIXTURES/basic-fragment.html" \
  -t "What should I review?" \
  -s approved \
  -o "$AUTO_OUT"

grep -q '"mode": "spec"' "$AUTO_OUT"
grep -q '>Overview</button>' "$AUTO_OUT"
grep -q 'src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"' "$AUTO_OUT"

SCALE="$TMP/001-scale"
python3 "$FIXTURES/generate-scale-fixture.py" "$SCALE"
SCALE_OUT="$TMP/001-scale-review.html"
FORGE_MERMAID_BUNDLE="$FIXTURES/mermaid-stub.js" \
  bash "$BUILDER" \
    --mode combined \
    --locale ko \
    --spec "$SCALE/spec.md" \
    --plan "$SCALE/plan.md" \
    -c "$SCALE/fragment.html" \
    -t "전체 구현 경로가 요구사항을 어떻게 충족할까?" \
    -s approved \
    --offline \
    -o "$SCALE_OUT"

grep -q '"task": 22' "$SCALE_OUT"
grep -q '"step": 110' "$SCALE_OUT"
grep -q '"requirement": 190' "$SCALE_OUT"
grep -q '"acceptance": 105' "$SCALE_OUT"
grep -q '"mermaid": 9' "$SCALE_OUT"
test "$(grep -c 'class="tab-panel"' "$SCALE_OUT")" -eq 6
test "$(grep -o 'data-route="Expedition Route ' "$SCALE_OUT" | wc -l | tr -d ' ')" -eq 8
test "$(grep -o 'class="mermaid"' "$SCALE_OUT" | wc -l | tr -d ' ')" -eq 9
test "$(grep -o 'id="Task[0-9]*"' "$SCALE_OUT" | sort -u | wc -l | tr -d ' ')" -eq 22
test "$(grep -o 'data-step="Task[0-9]*-Step[0-9]*"' "$SCALE_OUT" | wc -l | tr -d ' ')" -eq 110
test "$(grep -o 'id="R[0-9]*"' "$SCALE_OUT" | sort -u | wc -l | tr -d ' ')" -eq 190
test "$(grep -o 'data-ac="AC[0-9]*"' "$SCALE_OUT" | wc -l | tr -d ' ')" -eq 105
grep -q 'href="#R190"' "$SCALE_OUT"
grep -q 'href="#Task22"' "$SCALE_OUT"
grep -q 'href="#Task22-Step1"' "$SCALE_OUT"
grep -q 'data-origin="Spec source"' "$SCALE_OUT"
grep -q 'data-origin="Plan source"' "$SCALE_OUT"
grep -q 'data-origin="Derived view"' "$SCALE_OUT"
test "$(grep -o '읽는 법:' "$SCALE_OUT" | wc -l | tr -d ' ')" -ge 10
test "$(grep -o '모바일 요약' "$SCALE_OUT" | wc -l | tr -d ' ')" -eq 9
python3 "$FIXTURES/verify-mermaid-equality.py" "$SCALE/spec.md" "$SCALE_OUT"

(
  cd "$TMP"
  bash "$BUILDER" --mode spec --locale ko --spec "$SCALE/spec.md" -c "$SCALE/fragment.html" -t "Spec" -s approved
  bash "$BUILDER" --mode plan --locale ko --spec "$SCALE/spec.md" --plan "$SCALE/plan.md" -c "$SCALE/fragment.html" -t "Plan" -s approved
  bash "$BUILDER" --mode combined --locale ko --spec "$SCALE/spec.md" --plan "$SCALE/plan.md" -c "$SCALE/fragment.html" -t "Review" -s approved
)
test -f "$TMP/.forge/viewer/001-scale.html"
test -f "$TMP/.forge/viewer/001-scale-plan.html"
test -f "$TMP/.forge/viewer/001-scale-review.html"

sleep 0.01
touch "$SCALE/spec.md"
STALE_OUT="$TMP/001-scale-stale.html"
bash "$BUILDER" \
  --mode spec --locale ko \
  --spec "$SCALE/spec.md" \
  -c "$SCALE/fragment.html" \
  -t "스펙은 최신 상태일까?" -s approved \
  -o "$STALE_OUT"
grep -q '"freshness": "stale"' "$STALE_OUT"

printf 'test-build-viewer: all checks passed\n'
