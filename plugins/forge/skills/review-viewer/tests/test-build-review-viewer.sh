#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." && pwd)"
SKILL="$ROOT/plugins/forge/skills/review-viewer"
FIXTURES="$SKILL/tests/fixtures/repository"
BUILDER="$SKILL/scripts/build-review-viewer.sh"
TMP="$(mktemp -d)"
trap 'find "$TMP" -depth -delete >/dev/null 2>&1 || true' EXIT

fail() {
  echo "test-build-review-viewer: $*" >&2
  exit 1
}

expect_exit() {
  local expected="$1"
  shift
  set +e
  "$@" >"$TMP/command.stdout" 2>"$TMP/command.stderr"
  local actual="$?"
  set -e
  test "$actual" -eq "$expected" || fail "expected exit $expected, got $actual: $*"
}

cp -R "$FIXTURES" "$TMP/repository"
REPO="$TMP/repository"
git -C "$REPO" init -q
git -C "$REPO" config user.name fixture
git -C "$REPO" config user.email fixture@example.invalid
git -C "$REPO" add .
git -C "$REPO" commit -qm fixture

(
  cd "$REPO"
  "$BUILDER" --mode spec \
    --spec docs/specs/semantic-spec-bundles \
    --comparison docs/specs/supporting-policy \
    --review-id bundle-review --locale ko \
    --generated-at 2026-08-09T00:00:00Z --dry-run --format json
) >"$TMP/spec.json"

python3 - "$TMP/spec.json" <<'PY'
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["mode"] == "spec"
assert payload["locale"] == "ko"
assert [row["path"] for row in payload["bundles"]] == [
    "docs/specs/semantic-spec-bundles",
    "docs/specs/supporting-policy",
]
assert len(payload["member_sources"]) == 6
assert payload["plan_sources"] == []
assert all(row["bundle_sha256"] for row in payload["member_sources"])
assert "--spec docs/specs/semantic-spec-bundles" in payload["rebuild_command"]
assert "--comparison docs/specs/supporting-policy" in payload["rebuild_command"]
assert "statement-traceability-and-validation.md" not in payload["rebuild_command"]
PY

(
  cd "$REPO"
  "$BUILDER" --mode spec \
    --spec docs/specs/semantic-spec-bundles \
    --comparison docs/specs/supporting-policy \
    --review-id bundle-review --locale ko \
    --generated-at 2026-08-09T00:00:00Z --offline
)

VIEWER="$REPO/.forge/reviews/bundle-review/view.html"
test -f "$VIEWER" || fail "bundle viewer was not generated"
"$BUILDER" --check "$VIEWER" --repo-root "$REPO" --format json >"$TMP/current.json"
python3 - "$TMP/current.json" <<'PY'
import json, pathlib, sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["overall"] == "current"
assert payload["aggregates"] == {
    "primary": "current", "comparison": "current", "context": "unverified"
}
PY

printf '\nchanged\n' >>"$REPO/docs/specs/semantic-spec-bundles/statement-traceability-and-validation.md"
expect_exit 1 "$BUILDER" --check "$VIEWER" --repo-root "$REPO" --format json
python3 - "$TMP/command.stdout" <<'PY'
import json, pathlib, sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["overall"] == "stale"
assert payload["aggregates"]["primary"] == "stale"
assert any("statement-traceability-and-validation.md" in item for item in payload["diagnostics"])
PY

git -C "$REPO" checkout -q -- docs/specs/semantic-spec-bundles/statement-traceability-and-validation.md

(
  cd "$REPO"
  "$BUILDER" --mode plan --plan docs/plans/001-demo/plan.md \
    --review-id plan-review --generated-at 2026-08-09T00:00:00Z \
    --dry-run --format json
) >"$TMP/plan.json"
python3 - "$TMP/plan.json" <<'PY'
import json, pathlib, sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert [row["role"] for row in payload["plan_sources"]] == [
    "primary_plan", "plan_progress", "plan_task",
]
assert {row["role"] for row in payload["bundles"]} == {"related_spec_context"}
assert len(payload["member_sources"]) == 6
assert payload["rebuild_command"].startswith(
    "build-review-viewer.sh --mode plan --plan docs/plans/001-demo/plan.md"
)
PY

# A member file is deliberately invalid build input; normal spec input is the bundle directory.
expect_exit 2 bash -c "cd '$REPO' && '$BUILDER' --mode spec \
  --spec docs/specs/semantic-spec-bundles/semantic-spec-bundle-contract.md \
  --review-id invalid-member --dry-run --format json"
expect_exit 2 bash -c "cd '$REPO' && '$BUILDER' --mode combined \
  --spec docs/specs/semantic-spec-bundles --review-id invalid-mode \
  --dry-run --format json"

echo "test-build-review-viewer: all checks passed"
