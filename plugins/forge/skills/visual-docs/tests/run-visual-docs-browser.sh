#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$TEST_DIR/.." && pwd)"
WRITING_SPECS="$(cd "$SKILL_DIR/../writing-specs" && pwd)"
TEMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/forge-visual-docs-browser.XXXXXX")"
DEPENDENCY_ROOT="$TEMP_ROOT/dependencies"
BROWSER_ROOT="${FORGE_VISUAL_DOCS_BROWSER_CACHE:-$TEMP_ROOT/browsers}"
REPOSITORY_ROOT="$TEMP_ROOT/repository"
SERVER_PID=""

cleanup() {
  if [[ -n "$SERVER_PID" ]]; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    wait "$SERVER_PID" >/dev/null 2>&1 || true
  fi
  find "$TEMP_ROOT" -depth -delete >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

mkdir -p "$DEPENDENCY_ROOT" "$BROWSER_ROOT"
cp "$WRITING_SPECS/tests/browser/package.json" "$DEPENDENCY_ROOT/package.json"
cp "$WRITING_SPECS/tests/browser/package-lock.json" "$DEPENDENCY_ROOT/package-lock.json"
cp "$TEST_DIR/browser/visual-docs.spec.mjs" "$DEPENDENCY_ROOT/visual-docs.spec.mjs"
cp -R "$TEST_DIR/fixtures/repository" "$REPOSITORY_ROOT"
cp -R "$REPOSITORY_ROOT/docs/specs/semantic-spec-bundles" \
  "$REPOSITORY_ROOT/docs/specs/comparison-review-contract"
cp -R "$REPOSITORY_ROOT/docs/specs/semantic-spec-bundles" \
  "$REPOSITORY_ROOT/docs/specs/system-view-contract"
perl -pi -e 's/subtype: workflow/subtype: combat-system/' \
  "$REPOSITORY_ROOT/docs/specs/system-view-contract/semantic-spec-bundle-contract.md"

(
  cd "$WRITING_SPECS/assets"
  shasum -a 256 --strict -c mermaid.sha256
)
cp "$WRITING_SPECS/assets/mermaid.min.js" "$DEPENDENCY_ROOT/vendored-mermaid.min.js"

git -C "$REPOSITORY_ROOT" init -q
git -C "$REPOSITORY_ROOT" config user.name fixture
git -C "$REPOSITORY_ROOT" config user.email fixture@example.invalid
git -C "$REPOSITORY_ROOT" add .
git -C "$REPOSITORY_ROOT" commit -qm fixture

(
  cd "$DEPENDENCY_ROOT"
  npm ci --ignore-scripts
  PLAYWRIGHT_BROWSERS_PATH="$BROWSER_ROOT" npm exec -- playwright install chromium
)

(
  cd "$REPOSITORY_ROOT"
  "$SKILL_DIR/scripts/build-visual-docs.sh" --kind spec \
    --spec docs/specs/semantic-spec-bundles \
    --comparison docs/specs/comparison-review-contract \
    --view-id spec-cdn --generated-at 2026-08-01T00:00:00Z
  "$SKILL_DIR/scripts/build-visual-docs.sh" --kind spec \
    --spec docs/specs/system-view-contract \
    --view-id system-cdn --locale ko --generated-at 2026-08-01T00:00:00Z
  "$SKILL_DIR/scripts/build-visual-docs.sh" --kind plan \
    --plan docs/plans/001-demo/plan.md --view-id plan-offline \
    --generated-at 2026-08-01T00:00:00Z --offline
  "$SKILL_DIR/scripts/build-visual-docs.sh" --kind plan \
    --plan docs/plans/002-invalid/plan.md --view-id invalid-offline \
    --generated-at 2026-08-01T00:00:00Z --offline
  "$SKILL_DIR/scripts/build-visual-docs.sh" --kind project \
    --project-map docs/project/project-map.md --view-id project-handbook \
    --locale ko --generated-at 2026-08-01T00:00:00Z --offline
)

PORT="$(python3 -c 'import socket; value=socket.socket(); value.bind(("127.0.0.1", 0)); print(value.getsockname()[1]); value.close()')"
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$REPOSITORY_ROOT" \
  >"$TEMP_ROOT/server.log" 2>&1 &
SERVER_PID="$!"

ready=0
for _ in $(seq 1 40); do
  if curl --fail --silent --show-error \
    "http://127.0.0.1:$PORT/.forge/visual-docs/spec-cdn/view.html" >/dev/null; then
    ready=1
    break
  fi
  sleep 0.25
done
if [[ "$ready" -ne 1 ]]; then
  echo "Visual Docs fixture server did not become ready within 10 seconds." >&2
  exit 1
fi

(
  cd "$DEPENDENCY_ROOT"
  FORGE_VISUAL_DOCS_BASE_URL="http://127.0.0.1:$PORT" \
  FORGE_VISUAL_DOCS_REPOSITORY="$REPOSITORY_ROOT" \
  FORGE_VISUAL_DOCS_MERMAID="$DEPENDENCY_ROOT/vendored-mermaid.min.js" \
  PLAYWRIGHT_BROWSERS_PATH="$BROWSER_ROOT" \
    npm exec -- playwright test visual-docs.spec.mjs --workers=1 --reporter=line
)

test ! -e "$SKILL_DIR/node_modules"
test ! -e "$SKILL_DIR/playwright-report"
test ! -e "$SKILL_DIR/test-results"
test "$(find "$SKILL_DIR" -type f -name view.html | wc -l | tr -d ' ')" -eq 0
