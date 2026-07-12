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

printf 'test-build-viewer: all checks passed\n'
