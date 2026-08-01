#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$TEST_DIR/.." && pwd)"
TEMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/forge-spec-pages-browser.XXXXXX")"
DEPENDENCY_ROOT="$TEMP_ROOT/dependencies"
BROWSER_ROOT="$TEMP_ROOT/browsers"
FIXTURE_ROOT="$TEMP_ROOT/repository"
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
cp "$TEST_DIR/browser/package.json" "$DEPENDENCY_ROOT/package.json"
cp "$TEST_DIR/browser/package-lock.json" "$DEPENDENCY_ROOT/package-lock.json"
cp "$TEST_DIR/browser/spec-pages.spec.mjs" "$DEPENDENCY_ROOT/spec-pages.spec.mjs"
cp -R "$TEST_DIR/fixtures/pages-repository" "$FIXTURE_ROOT"

(
  cd "$DEPENDENCY_ROOT"
  npm ci --ignore-scripts
  PLAYWRIGHT_BROWSERS_PATH="$BROWSER_ROOT" \
    npm exec -- playwright install chromium
)

"$SKILL_DIR/scripts/spec-docs.sh" \
  --repo-root "$FIXTURE_ROOT" \
  build --root docs/specs --offline

python3 -m http.server 4173 \
  --bind 127.0.0.1 \
  --directory "$FIXTURE_ROOT" \
  >"$TEMP_ROOT/server.log" 2>&1 &
SERVER_PID="$!"

ready=0
for _ in $(seq 1 40); do
  if curl --fail --silent --show-error \
    "http://127.0.0.1:4173/docs/specs/index.html" >/dev/null; then
    ready=1
    break
  fi
  sleep 0.25
done
if [[ "$ready" -ne 1 ]]; then
  echo "Spec Pages fixture server did not become ready within 10 seconds." >&2
  exit 1
fi

(
  cd "$DEPENDENCY_ROOT"
  FORGE_SPEC_PAGES_BASE_URL="http://127.0.0.1:4173" \
  PLAYWRIGHT_BROWSERS_PATH="$BROWSER_ROOT" \
    npm exec -- playwright test spec-pages.spec.mjs \
      --workers=1 --reporter=line
)
