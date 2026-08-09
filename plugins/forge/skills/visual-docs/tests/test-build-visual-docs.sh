#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." && pwd)"
SKILL="$ROOT/plugins/forge/skills/visual-docs"
FIXTURES="$SKILL/tests/fixtures/repository"
BUILDER="$SKILL/scripts/build-visual-docs.sh"
TMP="$(mktemp -d)"
trap 'find "$TMP" -depth -delete >/dev/null 2>&1 || true' EXIT

fail() {
  echo "test-build-visual-docs: $*" >&2
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

mkdir -p "$REPO/.forge/work/demo"
cp "$SKILL/tests/fixtures/brief.md" "$REPO/.forge/work/demo/brief.md"

(
  cd "$REPO"
  "$BUILDER" --kind spec \
    --spec docs/specs/semantic-spec-bundles \
    --comparison docs/specs/supporting-policy \
    --view-id bundle-view --locale ko \
    --generated-at 2026-08-09T00:00:00Z --dry-run --format json
) >"$TMP/spec.json"

python3 - "$TMP/spec.json" <<'PY'
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["kind"] == "spec"
assert payload["locale"] == "ko"
assert [row["path"] for row in payload["bundles"]] == [
    "docs/specs/semantic-spec-bundles",
    "docs/specs/supporting-policy",
]
assert len(payload["member_sources"]) == 6
assert payload["document_sources"] == []
assert all(row["bundle_sha256"] for row in payload["member_sources"])
assert "--spec docs/specs/semantic-spec-bundles" in payload["rebuild_command"]
assert "--comparison docs/specs/supporting-policy" in payload["rebuild_command"]
assert "statement-traceability-and-validation.md" not in payload["rebuild_command"]
PY

(
  cd "$REPO"
  "$BUILDER" --kind spec \
    --spec docs/specs/semantic-spec-bundles \
    --comparison docs/specs/supporting-policy \
    --view-id bundle-view --locale ko \
    --generated-at 2026-08-09T00:00:00Z --offline
)

VIEWER="$REPO/.forge/visual-docs/bundle-view/view.html"
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
  "$BUILDER" --kind plan --plan docs/plans/001-demo/plan.md \
    --view-id plan-view --generated-at 2026-08-09T00:00:00Z \
    --dry-run --format json
) >"$TMP/plan.json"
python3 - "$TMP/plan.json" <<'PY'
import json, pathlib, sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert [row["role"] for row in payload["document_sources"]] == [
    "primary_plan", "plan_progress", "plan_task",
]
assert {row["role"] for row in payload["bundles"]} == {"related_spec_context"}
assert len(payload["member_sources"]) == 6
assert payload["rebuild_command"].startswith(
    "build-visual-docs.sh --kind plan --plan docs/plans/001-demo/plan.md"
)
PY

(
  cd "$REPO"
  "$BUILDER" --kind brief --brief .forge/work/demo/brief.md \
    --view-id brief-view --generated-at 2026-08-09T00:00:00Z \
    --dry-run --format json
) >"$TMP/brief.json"
python3 - "$TMP/brief.json" <<'PY'
import json, pathlib, sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["kind"] == "brief"
assert payload["output_lifecycle"] == "local"
assert payload["output"] == ".forge/visual-docs/brief-view/view.html"
assert payload["rebuild_command"].startswith(
    "build-visual-docs.sh --kind brief --brief .forge/work/demo/brief.md"
)
PY

(
  cd "$REPO"
  "$BUILDER" --kind project --project-map docs/project/project-map.md \
    --view-id handbook --locale ko --generated-at 2026-08-09T00:00:00Z \
    --dry-run --format json
) >"$TMP/project.json"
python3 - "$TMP/project.json" <<'PY'
import json, pathlib, sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["kind"] == "project"
assert payload["output_lifecycle"] == "tracked"
assert payload["output"] == "docs/project-viewer/index.html"
assert payload["project_map"] == "docs/project/project-map.md"
assert payload["declared_specs"] == ["docs/specs/semantic-spec-bundles"]
assert payload["repository_evidence_sources"]
PY

(
  cd "$REPO"
  "$BUILDER" --kind project --project-map docs/project/project-map.md \
    --view-id handbook --locale ko --generated-at 2026-08-09T00:00:00Z --offline
)
test -f "$REPO/docs/project-viewer/index.html" || fail "Project Handbook was not generated"
"$BUILDER" --check "$REPO/docs/project-viewer/index.html" \
  --repo-root "$REPO" --format json >"$TMP/project-current.json"
python3 - "$TMP/project-current.json" <<'PY'
import json, pathlib, sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["overall"] == "current"
assert payload["aggregates"] == {
    "primary": "current", "comparison": "unverified", "context": "current"
}
PY

# A member file is deliberately invalid build input; normal spec input is the bundle directory.
expect_exit 2 bash -c "cd '$REPO' && '$BUILDER' --kind spec \
  --spec docs/specs/semantic-spec-bundles/semantic-spec-bundle-contract.md \
  --view-id invalid-member --dry-run --format json"
expect_exit 2 bash -c "cd '$REPO' && '$BUILDER' --kind combined \
  --spec docs/specs/semantic-spec-bundles --view-id invalid-mode \
  --dry-run --format json"

echo "test-build-visual-docs: all checks passed"
