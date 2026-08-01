#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." && pwd)"
SKILL="$ROOT/plugins/forge/skills/review-viewer"
FIXTURES="$SKILL/tests/fixtures"
BUILDER="$SKILL/scripts/build-review-viewer.sh"
PYTHON_BUILDER="$SKILL/scripts/build_review_viewer.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

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

tree_digest() {
  local directory="$1"
  (
    cd "$directory"
    find . -path './.git' -prune -o -type f -print \
      | LC_ALL=C sort \
      | while IFS= read -r path; do shasum -a 256 "$path"; done
  ) | shasum -a 256 | awk '{print $1}'
}

run_builder() {
  (
    cd "$REPO"
    "$BUILDER" "$@"
  )
}

test -x "$BUILDER" || fail "shell entrypoint is not executable"
test -x "$PYTHON_BUILDER" || fail "Python entrypoint is not executable"
test -x "$SKILL/tests/test-build-review-viewer.sh" || fail "test entrypoint is not executable"
test ! -e "$SKILL/scripts/build-viewer.sh" || fail "old shell entrypoint still exists"
test ! -e "$SKILL/scripts/build_viewer.py" || fail "old Python entrypoint still exists"
test ! -e "$SKILL/tests/test-build-viewer.sh" || fail "old test entrypoint still exists"
test ! -e "$SKILL/references/content-patterns.md" || fail "manual content-pattern contract still exists"
test ! -e "$SKILL/tests/fixtures/basic-fragment.html" || fail "manual fragment fixture still exists"
test ! -e "$SKILL/tests/fixtures/invalid-fragment.html" || fail "invalid manual fragment fixture still exists"

cp -R "$FIXTURES/repository" "$TMP/repository"
REPO="$TMP/repository"
git -C "$REPO" init -q
git -C "$REPO" config user.name fixture
git -C "$REPO" config user.email fixture@example.invalid
git -C "$REPO" add .
git -C "$REPO" commit -qm fixture
mkdir -p "$REPO/nested/work"

SPEC_ARGS=(
  --mode spec
  --spec docs/specs/008-alpha/spec.md
  --comparison docs/specs/002-beta/spec.md
  --review-id spec-review
  --generated-at 2026-08-01T00:00:00Z
  --dry-run
  --format json
)
before="$(tree_digest "$REPO")"
(
  cd "$REPO/nested/work"
  "$BUILDER" "${SPEC_ARGS[@]}"
) >"$TMP/spec-one.json"
(
  cd "$REPO/nested/work"
  "$BUILDER" "${SPEC_ARGS[@]}"
) >"$TMP/spec-two.json"
cmp -s "$TMP/spec-one.json" "$TMP/spec-two.json" || fail "spec dry-run is not deterministic"
test "$before" = "$(tree_digest "$REPO")" || fail "spec dry-run wrote repository files"

python3 - "$TMP/spec-one.json" <<'PY'
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["mode"] == "spec"
assert payload["locale"] == "en"
assert payload["checkpoint"] == "working-tree"
assert payload["generated_at"] == "2026-08-01T00:00:00Z"
assert payload["output"] == ".forge/reviews/spec-review/view.html"
assert payload["mermaid_url"] == "https://cdn.jsdelivr.net/npm/mermaid@11.16.0/dist/mermaid.min.js"
assert payload["source_base"] == "../../../"
assert payload["freshness"] == "unverified"
assert payload["offline"] is False
assert [row["role"] for row in payload["sources"]] == ["primary_spec", "comparison_spec"]
assert payload["counts"]["primary"]["requirement"] == 3
assert payload["counts"]["comparison"]["002-beta"]["acceptance"] == 6
assert all(not pathlib.PurePosixPath(row["path"]).is_absolute() for row in payload["sources"])
PY

PLAN_ARGS=(
  --mode plan
  --plan docs/plans/001-demo/plan.md
  --review-id plan-review
  --locale ko
  --checkpoint source-model-ready
  --generated-at 2026-08-01T00:00:00Z
  --offline
  --dry-run
  --format json
)
before="$(tree_digest "$REPO")"
(
  cd "$REPO"
  "$BUILDER" "${PLAN_ARGS[@]}"
) >"$TMP/plan-one.json"
(
  cd "$REPO"
  "$BUILDER" "${PLAN_ARGS[@]}"
) >"$TMP/plan-two.json"
cmp -s "$TMP/plan-one.json" "$TMP/plan-two.json" || fail "plan dry-run is not deterministic"
test "$before" = "$(tree_digest "$REPO")" || fail "plan dry-run wrote repository files"

python3 - "$TMP/plan-one.json" <<'PY'
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["mode"] == "plan"
assert payload["locale"] == "ko"
assert payload["checkpoint"] == "source-model-ready"
assert payload["offline"] is True
assert [row["role"] for row in payload["sources"]] == [
    "primary_plan", "plan_progress", "plan_task",
    "related_spec_context", "related_spec_context",
]
assert payload["counts"]["primary"]["task"] == 2
assert payload["counts"]["primary"]["step"] == 3
assert "--dry-run" not in payload["rebuild_command"]
assert "--format" not in payload["rebuild_command"]
PY

before_pages="$(find "$REPO/docs/specs" -type f -name index.html -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 2>/dev/null || true)"
run_builder --mode spec --spec docs/specs/008-alpha/spec.md \
  --comparison docs/specs/002-beta/spec.md --review-id spec-final \
  --generated-at 2026-08-01T00:00:00Z --offline
test -f "$REPO/.forge/reviews/spec-final/view.html" || fail "spec final viewer was not generated"
after_pages="$(find "$REPO/docs/specs" -type f -name index.html -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 2>/dev/null || true)"
test "$before_pages" = "$after_pages" || fail "Review Viewer changed Spec Pages"
"$BUILDER" --check "$REPO/.forge/reviews/spec-final/view.html" \
  --repo-root "$REPO" --format json >"$TMP/spec-final-current.json"
python3 - "$TMP/spec-final-current.json" <<'PY'
import json, pathlib, sys
value = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert value["overall"] == "current"
assert value["aggregates"] == {
    "primary": "current", "comparison": "current", "context": "unverified"
}
PY

run_builder --mode plan --plan docs/plans/001-demo/plan.md \
  --review-id plan-final --locale ko --checkpoint source-model-ready \
  --generated-at 2026-08-01T00:00:00Z --offline
test -f "$REPO/.forge/reviews/plan-final/view.html" || fail "plan final viewer was not generated"
python3 "$SKILL/tests/fixtures/verify-mermaid-equality.py" \
  "$REPO/docs/plans/001-demo/plan.md" "$REPO/.forge/reviews/plan-final/view.html"
python3 "$SKILL/tests/fixtures/verify-mermaid-equality.py" \
  "$REPO/docs/specs/008-alpha/spec.md" "$REPO/.forge/reviews/plan-final/view.html"

mkdir -p "$TMP/outside-output"
ln -s "$TMP/outside-output" "$REPO/.forge/reviews/escape-output"
expect_exit 2 run_builder --mode spec --spec docs/specs/008-alpha/spec.md \
  --review-id escape-output --generated-at 2026-08-01T00:00:00Z
test "$(find "$TMP/outside-output" -type f | wc -l | tr -d ' ')" -eq 0 \
  || fail "escaped output parent wrote outside the repository"

expect_exit 2 run_builder --mode combined --spec docs/specs/008-alpha/spec.md --review-id bad --dry-run --format json
expect_exit 2 run_builder --mode spec --spec docs/specs/008-alpha/spec.md -c fragment.html --review-id bad --dry-run --format json
expect_exit 2 run_builder --mode spec --spec docs/specs/008-alpha/spec.md -o source.html --review-id bad --dry-run --format json
expect_exit 2 run_builder --mode spec --spec docs/specs/008-alpha/spec.md --plan docs/plans/001-demo/plan.md --review-id bad --dry-run --format json
expect_exit 2 run_builder --mode plan --plan docs/plans/001-demo/plan.md --comparison docs/specs/002-beta/spec.md --review-id bad --dry-run --format json
expect_exit 2 run_builder --mode spec --spec docs/specs/008-alpha/spec.md --progress docs/plans/001-demo/progress.md --review-id bad --dry-run --format json
expect_exit 2 run_builder --mode spec --spec docs/specs/008-alpha/spec.md --review-id ../escape --dry-run --format json

# Explicit plan auxiliaries are accepted only in plan mode and preserve lexical task order.
(
  cd "$REPO"
  "$BUILDER" --mode plan --plan docs/plans/001-demo/plan.md \
    --progress docs/plans/001-demo/progress.md \
    --tasks-dir docs/plans/001-demo/tasks \
    --review-id explicit-plan --generated-at 2026-08-01T00:00:00Z \
    --dry-run --format json
) >"$TMP/explicit-plan.json"
python3 - "$TMP/explicit-plan.json" <<'PY'
import json, pathlib, sys
value = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert [row["role"] for row in value["sources"][:3]] == [
    "primary_plan", "plan_progress", "plan_task",
]
assert "--progress docs/plans/001-demo/progress.md" in value["rebuild_command"]
assert "--tasks-dir docs/plans/001-demo/tasks" in value["rebuild_command"]
PY

# Build a malformed/current matrix fixture directly; --check must stay read-only and never regenerate it.
mkdir -p "$REPO/.forge/reviews/checker"
python3 - "$REPO" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
source = root / "docs/specs/008-alpha/spec.md"
manifest = {
    "review_id": "checker",
    "mode": "spec",
    "locale": "en",
    "generated_at": "2026-08-01T00:00:00Z",
    "checkpoint": "working-tree",
    "commit": None,
    "rebuild_command": "build-review-viewer.sh --mode spec",
    "source_base": "../../../",
    "offline": False,
    "counts": {"primary": {"requirement": 3}, "comparison": {}, "context": {}},
    "freshness": "unverified",
    "sources": [{
        "role": "primary_spec",
        "namespace": "current--008-alpha",
        "path": "docs/specs/008-alpha/spec.md",
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "requirements": ["R1", "R2", "R3"],
        "acceptance": ["AC1"],
    }]
}
viewer = root / ".forge/reviews/checker/view.html"
viewer.write_text(
    '<script type="application/json" id="forge-source-manifest">'
    + json.dumps(manifest, sort_keys=True)
    + "</script>\n",
    encoding="utf-8",
)
PY

viewer="$REPO/.forge/reviews/checker/view.html"
before="$(tree_digest "$REPO")"
"$BUILDER" --check "$viewer" --repo-root "$REPO" --format json >"$TMP/current.json"
test "$before" = "$(tree_digest "$REPO")" || fail "current checker wrote repository files"
python3 - "$TMP/current.json" <<'PY'
import json, pathlib, sys
value = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert value["overall"] == "current"
assert value["aggregates"]["primary"] == "current"
assert value["sources"] == [["current--008-alpha", "docs/specs/008-alpha/spec.md", "current"]]
PY

cp "$REPO/docs/specs/008-alpha/spec.md" "$TMP/alpha.original"
printf '\nstale\n' >>"$REPO/docs/specs/008-alpha/spec.md"
expect_exit 1 "$BUILDER" --check "$viewer" --repo-root "$REPO" --format json
cp "$TMP/command.stdout" "$TMP/stale.json"
python3 - "$TMP/stale.json" <<'PY'
import json, pathlib, sys
assert json.loads(pathlib.Path(sys.argv[1]).read_text())["overall"] == "stale"
PY
cp "$TMP/alpha.original" "$REPO/docs/specs/008-alpha/spec.md"

mv "$REPO/docs/specs/008-alpha/spec.md" "$TMP/alpha.missing"
expect_exit 1 "$BUILDER" --check "$viewer" --repo-root "$REPO" --format json
cp "$TMP/command.stdout" "$TMP/missing.json"
python3 - "$TMP/missing.json" <<'PY'
import json, pathlib, sys
assert json.loads(pathlib.Path(sys.argv[1]).read_text())["overall"] == "missing"
PY
mv "$TMP/alpha.missing" "$REPO/docs/specs/008-alpha/spec.md"

printf '<script type="application/json" id="forge-source-manifest">{bad}</script>\n' >"$REPO/.forge/reviews/checker/bad.html"
expect_exit 1 "$BUILDER" --check "$REPO/.forge/reviews/checker/bad.html" --repo-root "$REPO" --format json
cp "$TMP/command.stdout" "$TMP/malformed.json"
python3 - "$TMP/malformed.json" <<'PY'
import json, pathlib, sys
value = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert value["overall"] == "malformed"
assert value["aggregates"] == {
    "primary": "unverified", "comparison": "unverified", "context": "unverified"
}
PY

before="$(tree_digest "$REPO")"
expect_exit 1 "$BUILDER" --check "$REPO/.forge/reviews/checker/bad.html" --repo-root "$REPO" --format json
test "$before" = "$(tree_digest "$REPO")" || fail "malformed checker wrote repository files"

echo "test-build-review-viewer: all checks passed"
