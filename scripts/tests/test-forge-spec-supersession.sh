#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SPEC_DOCS="$ROOT/plugins/forge/skills/writing-specs/scripts/spec-docs.sh"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/forge-spec-supersession.XXXXXX")"
REPO="$TEST_ROOT/repository"

cleanup() {
  chmod -R u+w "$TEST_ROOT" >/dev/null 2>&1 || true
  find "$TEST_ROOT" -depth -delete >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

fail() {
  echo "forge-spec-supersession: $*" >&2
  exit 1
}

expect_failure() {
  local label="$1"
  shift
  if "$@" >"$TEST_ROOT/$label.stdout" 2>"$TEST_ROOT/$label.stderr"; then
    fail "$label unexpectedly succeeded"
  fi
}

fingerprint() {
  python3 - "$1" <<'PY'
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys

repo = Path(sys.argv[1]).resolve()

def git(*args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True
    ).stdout

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

index_path = Path(git("rev-parse", "--git-path", "index").decode().strip())
if not index_path.is_absolute():
    index_path = repo / index_path

tracked = [item.decode() for item in git("ls-files", "-z").split(b"\0") if item]
untracked = [
    item.decode()
    for item in git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
    if item
]
payload = {
    "head": git("rev-parse", "HEAD").decode().strip(),
    "index": digest(index_path),
    "tracked": [(item, digest(repo / item)) for item in sorted(tracked)],
    "untracked": [(item, digest(repo / item)) for item in sorted(untracked)],
}
encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
print(hashlib.sha256(encoded.encode()).hexdigest())
PY
}

viewer_count() {
  local repo="$1"
  local count=0
  if [[ -d "$repo/.forge/reviews" ]]; then
    count="$((count + $(find "$repo/.forge/reviews" -type f | wc -l | tr -d ' ')))"
  fi
  if [[ -d "$repo/docs/specs" ]]; then
    count="$((count + $(find "$repo/docs/specs" -name view.html -type f | wc -l | tr -d ' ')))"
  fi
  if [[ -d "$repo/docs/plans" ]]; then
    count="$((count + $(find "$repo/docs/plans" -name view.html -type f | wc -l | tr -d ' ')))"
  fi
  echo "$count"
}

write_old_spec() {
  local path="$1"
  mkdir -p "$(dirname "$path")"
  command cat >"$path" <<'EOF'
---
schema: forge/spec@1
id: 001-history
status: implemented
language: en
kind: system
areas: ["forge"]
components: ["spec-docs"]
relatedSpecs: []
---
# Historical contract

## Overview

The active contract still includes migration history.

## Requirements

- R1. The system preserves the active contract.

## Behavior & Flows

The contract remains observable.

## Data & Interfaces

The source is a structured spec.

## Acceptance Criteria

- AC1 (R1): Validation observes the active contract.

## Decisions & History

- 2026-08-01 [DECISION] Initial history.
EOF
}

write_replacement_spec() {
  local path="$1"
  mkdir -p "$(dirname "$path")"
  command cat >"$path" <<'EOF'
---
schema: forge/spec@1
id: 001-current
status: approved
language: en
kind: system
areas: ["forge"]
components: ["spec-docs"]
relatedSpecs: []
---
# Current contract

## Overview

The active spec contains current facts only.

## Requirements

- R1. The system exposes the current contract.

## Behavior & Flows

The current contract remains observable.

## Data & Interfaces

The source is a structured spec.

## Acceptance Criteria

- AC1 (R1): Validation observes only the current contract.

## Decisions & History

- 2026-08-02 [DECISION] Current-state identity approved.
EOF
}

write_consumer() {
  local path="$1"
  local target_id="$2"
  local target_dir="$3"
  mkdir -p "$(dirname "$path")"
  command cat >"$path" <<EOF
---
schema: forge/spec@1
id: 002-consumer
status: approved
language: en
kind: system
areas: ["forge"]
components: ["spec-docs"]
relatedSpecs: [{"id": "$target_id", "relation": "dependsOn"}]
---
# Consumer

## Overview

The consumer links to [the active contract](../$target_dir/spec.md).

## Requirements

- R1. The consumer references the active contract.

## Behavior & Flows

The relation is explicit.

## Data & Interfaces

The interface is the related spec identity.

## Acceptance Criteria

- AC1 (R1): Validation resolves the active relation and link.

## Decisions & History

- 2026-08-01 [DECISION] Initial consumer.
EOF
}

apply_cutover() {
  local candidate="$1"
  local old="$candidate/docs/specs/001-history/spec.md"
  local old_sha
  old_sha="$(shasum -a 256 "$old" | awk '{print $1}')"
  write_replacement_spec "$candidate/docs/specs/001-current/spec.md"
  write_consumer "$candidate/docs/specs/002-consumer/spec.md" "001-current" "001-current"
  mkdir -p "$candidate/docs/plans/001-history"
  printf '# Preserved migration evidence\n' >"$candidate/docs/plans/001-history/evidence.md"
  printf '%s\n' \
    '{"schema":"forge/spec-transitions@1","transitions":[{"fromId":"001-history","fromPath":"docs/specs/001-history/spec.md","fromSourceSha256":"'"$old_sha"'","disposition":"superseded","toId":"001-current","toPath":"docs/specs/001-current/spec.md","evidencePath":"docs/plans/001-history/evidence.md","reason":"Keep active specs limited to current facts."}]}' \
    >"$candidate/docs/specs/.transitions.json"
  rm "$candidate/docs/specs/001-history/spec.md"
  rm "$candidate/docs/specs/001-history/index.html"
}

new_candidate() {
  local name="$1"
  local candidate="$TEST_ROOT/$name"
  git -C "$REPO" worktree add --detach "$candidate" HEAD >/dev/null
  echo "$candidate"
}

drop_candidate() {
  git -C "$REPO" worktree remove --force "$1" >/dev/null
}

assert_root_unchanged() {
  local before="$1"
  local label="$2"
  local after
  after="$(fingerprint "$REPO")"
  [[ "$before" == "$after" ]] || fail "$label changed production root bytes"
  [[ "$(viewer_count "$REPO")" -eq 0 ]] || fail "$label created a Review Viewer"
}

mkdir -p "$REPO/docs/specs"
write_old_spec "$REPO/docs/specs/001-history/spec.md"
write_consumer "$REPO/docs/specs/002-consumer/spec.md" "001-history" "001-history"
git -C "$REPO" init -q
git -C "$REPO" config user.name fixture
git -C "$REPO" config user.email fixture@example.invalid
bash "$SPEC_DOCS" --repo-root "$REPO" build --root docs/specs --offline >/dev/null
git -C "$REPO" add .
git -C "$REPO" commit -qm baseline
BASELINE_HEAD="$(git -C "$REPO" rev-parse HEAD)"
ROOT_FINGERPRINT="$(fingerprint "$REPO")"

candidate="$(new_candidate old-source-present)"
apply_cutover "$candidate"
git -C "$candidate" show HEAD:docs/specs/001-history/spec.md >"$candidate/docs/specs/001-history/spec.md"
expect_failure old-source-present bash "$SPEC_DOCS" --repo-root "$candidate" validate --root docs/specs --baseline-ref HEAD
drop_candidate "$candidate"
assert_root_unchanged "$ROOT_FINGERPRINT" old-source-present

candidate="$(new_candidate bad-sha)"
apply_cutover "$candidate"
python3 - "$candidate/docs/specs/.transitions.json" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
path.write_text(path.read_text().replace('"fromSourceSha256":"', '"fromSourceSha256":"b'))
PY
expect_failure bad-sha bash "$SPEC_DOCS" --repo-root "$candidate" validate --root docs/specs --baseline-ref HEAD
drop_candidate "$candidate"
assert_root_unchanged "$ROOT_FINGERPRINT" bad-sha

candidate="$(new_candidate stale-reference)"
apply_cutover "$candidate"
git -C "$candidate" show HEAD:docs/specs/002-consumer/spec.md >"$candidate/docs/specs/002-consumer/spec.md"
expect_failure stale-reference bash "$SPEC_DOCS" --repo-root "$candidate" validate --root docs/specs --baseline-ref HEAD
drop_candidate "$candidate"
assert_root_unchanged "$ROOT_FINGERPRINT" stale-reference

candidate="$(new_candidate invalid-replacement)"
apply_cutover "$candidate"
python3 - "$candidate/docs/specs/001-current/spec.md" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
path.write_text(path.read_text().replace('status: approved', 'status: broken'))
PY
expect_failure invalid-replacement bash "$SPEC_DOCS" --repo-root "$candidate" build --root docs/specs --offline
drop_candidate "$candidate"
assert_root_unchanged "$ROOT_FINGERPRINT" invalid-replacement

candidate="$(new_candidate stale-page)"
apply_cutover "$candidate"
bash "$SPEC_DOCS" --repo-root "$candidate" build --root docs/specs --offline >/dev/null
printf '\ncorrupt\n' >>"$candidate/docs/specs/001-current/index.html"
expect_failure stale-page bash "$SPEC_DOCS" --repo-root "$candidate" check --root docs/specs
drop_candidate "$candidate"
assert_root_unchanged "$ROOT_FINGERPRINT" stale-page

candidate="$(new_candidate late-drift)"
apply_cutover "$candidate"
bash "$SPEC_DOCS" --repo-root "$candidate" validate --root docs/specs --baseline-ref HEAD
bash "$SPEC_DOCS" --repo-root "$candidate" build --root docs/specs --offline >/dev/null
bash "$SPEC_DOCS" --repo-root "$candidate" check --root docs/specs
git -C "$candidate" add .
git -C "$candidate" -c user.name=fixture -c user.email=fixture@example.invalid commit -qm candidate
CANDIDATE_COMMIT="$(git -C "$candidate" rev-parse HEAD)"
printf '\nlocal drift\n' >>"$REPO/docs/specs/002-consumer/spec.md"
git -C "$REPO" add docs/specs/002-consumer/spec.md
printf 'preserve untracked bytes\n' >"$REPO/local-note.txt"
DIRTY_FINGERPRINT="$(fingerprint "$REPO")"
if [[ "$(git -C "$REPO" rev-parse HEAD)" == "$BASELINE_HEAD" ]] \
  && git -C "$REPO" diff --quiet \
  && git -C "$REPO" diff --cached --quiet \
  && [[ -z "$(git -C "$REPO" ls-files --others --exclude-standard)" ]]; then
  git -C "$REPO" merge --ff-only "$CANDIDATE_COMMIT" >/dev/null
  fail "late dirty root was promoted"
fi
[[ "$DIRTY_FINGERPRINT" == "$(fingerprint "$REPO")" ]] || fail "late promotion refusal changed dirty root bytes"
git -C "$REPO" reset --hard -q "$BASELINE_HEAD"
rm "$REPO/local-note.txt"
drop_candidate "$candidate"
[[ "$(git -C "$REPO" rev-parse HEAD)" == "$BASELINE_HEAD" ]] || fail "dirty fixture cleanup changed HEAD"
git -C "$REPO" diff --quiet || fail "dirty fixture cleanup left tracked changes"
git -C "$REPO" diff --cached --quiet || fail "dirty fixture cleanup left index changes"
[[ -z "$(git -C "$REPO" ls-files --others --exclude-standard)" ]] || fail "dirty fixture cleanup left untracked files"

candidate="$(new_candidate success)"
apply_cutover "$candidate"
bash "$SPEC_DOCS" --repo-root "$candidate" validate --root docs/specs --baseline-ref HEAD
bash "$SPEC_DOCS" --repo-root "$candidate" build --root docs/specs --offline >/dev/null
bash "$SPEC_DOCS" --repo-root "$candidate" check --root docs/specs
git -C "$candidate" add .
git -C "$candidate" -c user.name=fixture -c user.email=fixture@example.invalid commit -qm candidate
CANDIDATE_COMMIT="$(git -C "$candidate" rev-parse HEAD)"
[[ "$(git -C "$REPO" rev-parse HEAD)" == "$BASELINE_HEAD" ]] || fail "root HEAD drifted before promotion"
git -C "$REPO" diff --quiet || fail "root tracked bytes are dirty before promotion"
git -C "$REPO" diff --cached --quiet || fail "root index is dirty before promotion"
[[ -z "$(git -C "$REPO" ls-files --others --exclude-standard)" ]] || fail "root has untracked bytes before promotion"
git -C "$REPO" merge --ff-only "$CANDIDATE_COMMIT" >/dev/null
drop_candidate "$candidate"

test ! -e "$REPO/docs/specs/001-history/spec.md" || fail "old source survived promotion"
test ! -e "$REPO/docs/specs/001-history/index.html" || fail "old page survived promotion"
for path in \
  docs/specs/.transitions.json \
  docs/specs/001-current/spec.md \
  docs/specs/001-current/index.html \
  docs/specs/index.html \
  docs/plans/001-history/evidence.md; do
  test -f "$REPO/$path" || fail "successful promotion misses $path"
done
bash "$SPEC_DOCS" --repo-root "$REPO" validate --root docs/specs --baseline-ref "$BASELINE_HEAD"
bash "$SPEC_DOCS" --repo-root "$REPO" check --root docs/specs
[[ "$(viewer_count "$REPO")" -eq 0 ]] || fail "successful promotion created a Review Viewer"

echo "forge-spec-supersession: all checks passed"
