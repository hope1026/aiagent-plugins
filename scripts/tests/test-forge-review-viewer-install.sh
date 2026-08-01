#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/forge-release-install.XXXXXX")"
INSTALL_TARGET_ROOT="$TEST_ROOT/install"
TEST_HOME="$TEST_ROOT/home"
TRACE="$TEST_ROOT/install.trace"

cleanup() {
  chmod -R u+w "$TEST_ROOT" >/dev/null 2>&1 || true
  find "$TEST_ROOT" -depth -delete >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

fail() {
  echo "forge-review-viewer-install: $*" >&2
  exit 1
}

expect_exit() {
  local expected="$1"
  shift
  set +e
  "$@" >"$TEST_ROOT/command.stdout" 2>"$TEST_ROOT/command.stderr"
  local actual="$?"
  set -e
  [[ "$actual" -eq "$expected" ]] ||
    fail "expected exit $expected, got $actual: $*"
}

sha256() {
  shasum -a 256 "$1" | awk '{print $1}'
}

assert_inside_target_trace() {
  local line destination
  while IFS= read -r line; do
    [[ "$line" == installed\ * ]] || continue
    destination="${line#installed *: }"
    destination="${destination% (*}"
    case "$destination" in
      "$INSTALL_CANONICAL_ROOT"/*) ;;
      *) fail "installer trace escaped target root: $destination" ;;
    esac
  done <"$TRACE"
}

test -x "$ROOT/scripts/install.sh" || fail "installer is not executable"
grep -Fq 'test-forge-review-viewer-install.sh' "$ROOT/.github/workflows/validate.yml" ||
  fail "CI does not run the isolated install test"
grep -Fq 'run-spec-pages-browser.sh' "$ROOT/.github/workflows/validate.yml" ||
  fail "CI does not run the Spec Pages browser harness"
grep -Fq 'run-review-viewer-browser.sh' "$ROOT/.github/workflows/validate.yml" ||
  fail "CI does not run the Review Viewer browser harness"
grep -Fq 'mcr.microsoft.com/playwright:v1.55.0-noble' "$ROOT/.github/workflows/validate.yml" ||
  fail "CI browser job is not pinned to Playwright 1.55.0 noble"

mkdir -p "$TEST_HOME"
HOME="$TEST_HOME" bash "$ROOT/scripts/install.sh" \
  --agent all --mode copy --plugin forge --target-root "$INSTALL_TARGET_ROOT" \
  >"$TRACE"
INSTALL_CANONICAL_ROOT="$(cd "$INSTALL_TARGET_ROOT" && pwd -P)"

CODEX_SKILLS="$INSTALL_CANONICAL_ROOT/codex/.agents/skills"
CLAUDE_SKILLS="$INSTALL_CANONICAL_ROOT/claude/.claude/skills/forge/skills"
ANTIGRAVITY_SKILLS="$INSTALL_CANONICAL_ROOT/antigravity/agent-skills"

for skills in "$CODEX_SKILLS" "$CLAUDE_SKILLS" "$ANTIGRAVITY_SKILLS"; do
  test -x "$skills/writing-specs/scripts/spec-docs.sh" ||
    fail "missing installed spec-docs.sh: $skills"
  test -x "$skills/review-viewer/scripts/build-review-viewer.sh" ||
    fail "missing installed Review Viewer builder: $skills"
  test -f "$skills/writing-specs/assets/mermaid.min.js" ||
    fail "missing installed offline Mermaid asset: $skills"
  test ! -e "$skills/spec-viewer" ||
    fail "retired spec-viewer was installed: $skills"
done

test ! -e "$TEST_HOME/.agents" || fail "--target-root wrote Codex data to HOME"
test ! -e "$TEST_HOME/.claude" || fail "--target-root wrote Claude data to HOME"
assert_inside_target_trace

# One committed source fixture makes provenance stable across all three exports.
cp -R "$ROOT/plugins/forge/skills/writing-specs/tests/fixtures/pages-repository" \
  "$TEST_ROOT/pages-source"
git -C "$TEST_ROOT/pages-source" init -q
git -C "$TEST_ROOT/pages-source" config user.name fixture
git -C "$TEST_ROOT/pages-source" config user.email fixture@example.invalid
git -C "$TEST_ROOT/pages-source" add .
git -C "$TEST_ROOT/pages-source" commit -qm fixture

cp -R "$ROOT/plugins/forge/skills/review-viewer/tests/fixtures/repository" \
  "$TEST_ROOT/review-source"
git -C "$TEST_ROOT/review-source" init -q
git -C "$TEST_ROOT/review-source" config user.name fixture
git -C "$TEST_ROOT/review-source" config user.email fixture@example.invalid
git -C "$TEST_ROOT/review-source" add .
git -C "$TEST_ROOT/review-source" commit -qm fixture

declare -a INSPECT_HASHES=()
declare -a PAGE_HASHES=()
declare -a REVIEW_HASHES=()
index=0
for agent in codex claude antigravity; do
  case "$agent" in
    codex) skills="$CODEX_SKILLS" ;;
    claude) skills="$CLAUDE_SKILLS" ;;
    antigravity) skills="$ANTIGRAVITY_SKILLS" ;;
  esac
  pages_repo="$TEST_ROOT/pages-$agent"
  review_repo="$TEST_ROOT/review-$agent"
  cp -R "$TEST_ROOT/pages-source" "$pages_repo"
  cp -R "$TEST_ROOT/review-source" "$review_repo"

  "$skills/writing-specs/scripts/spec-docs.sh" --repo-root "$pages_repo" \
    validate --root docs/specs
  "$skills/writing-specs/scripts/spec-docs.sh" --repo-root "$pages_repo" \
    inspect --spec docs/specs/001-basic/spec.md --format json \
    >"$TEST_ROOT/$agent.inspect.json"
  "$skills/writing-specs/scripts/spec-docs.sh" --repo-root "$pages_repo" \
    build --root docs/specs --offline >/dev/null
  "$skills/writing-specs/scripts/spec-docs.sh" --repo-root "$pages_repo" \
    check --root docs/specs

  (
    cd "$review_repo"
    "$skills/review-viewer/scripts/build-review-viewer.sh" \
      --mode spec --spec docs/specs/008-alpha/spec.md \
      --review-id install-proof --generated-at 2026-08-01T00:00:00Z --offline
  ) >/dev/null

  INSPECT_HASHES[index]="$(sha256 "$TEST_ROOT/$agent.inspect.json")"
  PAGE_HASHES[index]="$(sha256 "$pages_repo/docs/specs/001-basic/index.html")"
  REVIEW_HASHES[index]="$(sha256 "$review_repo/.forge/reviews/install-proof/view.html")"
  index=$((index + 1))
done

for hashes_name in INSPECT_HASHES PAGE_HASHES REVIEW_HASHES; do
  eval 'hashes=("${'"$hashes_name"'[@]}")'
  [[ "${hashes[0]}" == "${hashes[1]}" && "${hashes[1]}" == "${hashes[2]}" ]] ||
    fail "$hashes_name differs across installed exports"
done

# A target must be absolute, normalized, writable, and free of symlink components.
expect_exit 2 bash "$ROOT/scripts/install.sh" --agent all --plugin forge \
  --target-root 'relative/../escape'
test ! -e "$ROOT/relative" || fail "relative escape created a repository path"

mkdir -p "$TEST_ROOT/symlink-outside" "$TEST_ROOT/symlink-parent"
ln -s "$TEST_ROOT/symlink-outside" "$TEST_ROOT/symlink-parent/link"
expect_exit 2 bash "$ROOT/scripts/install.sh" --agent all --plugin forge \
  --target-root "$TEST_ROOT/symlink-parent/link/install"
test -z "$(find "$TEST_ROOT/symlink-outside" -mindepth 1 -print -quit)" ||
  fail "symlink escape wrote outside target"

mkdir -p "$TEST_ROOT/readonly"
chmod 500 "$TEST_ROOT/readonly"
expect_exit 2 bash "$ROOT/scripts/install.sh" --agent all --plugin forge \
  --target-root "$TEST_ROOT/readonly"
test -z "$(find "$TEST_ROOT/readonly" -mindepth 1 -print -quit)" ||
  fail "read-only target received a partial install"
chmod 700 "$TEST_ROOT/readonly"

mkdir -p "$TEST_ROOT/fault-target"
printf 'preserve\n' >"$TEST_ROOT/fault-target/marker"
set +e
FORGE_INSTALL_TEST_FAIL_AFTER_COPY=1 bash "$ROOT/scripts/install.sh" \
  --agent all --mode copy --plugin forge \
  --target-root "$TEST_ROOT/fault-target" \
  >"$TEST_ROOT/fault.stdout" 2>"$TEST_ROOT/fault.stderr"
fault_status="$?"
set -e
[[ "$fault_status" -ne 0 ]] || fail "partial-copy fault fixture unexpectedly succeeded"
grep -Fq 'injected copy failure' "$TEST_ROOT/fault.stderr" ||
  fail "partial-copy failure was not actionable"
test "$(<"$TEST_ROOT/fault-target/marker")" = preserve ||
  fail "partial-copy failure changed pre-existing target data"
for child in codex claude antigravity; do
  test ! -e "$TEST_ROOT/fault-target/$child" ||
    fail "partial-copy failure promoted $child"
done
test -z "$(find "$TEST_ROOT/fault-target" -maxdepth 1 -name '.forge-install.*' -print -quit)" ||
  fail "partial-copy failure left staging data"

mkdir -p \
  "$TEST_ROOT/promotion-target/codex" \
  "$TEST_ROOT/promotion-target/claude" \
  "$TEST_ROOT/promotion-target/antigravity"
for child in codex claude antigravity; do
  printf 'preserve-%s\n' "$child" >"$TEST_ROOT/promotion-target/$child/sentinel"
done
set +e
FORGE_INSTALL_TEST_FAIL_PROMOTION=claude bash "$ROOT/scripts/install.sh" \
  --agent all --mode copy --plugin forge \
  --target-root "$TEST_ROOT/promotion-target" \
  >"$TEST_ROOT/promotion.stdout" 2>"$TEST_ROOT/promotion.stderr"
promotion_status="$?"
set -e
[[ "$promotion_status" -ne 0 ]] || fail "promotion fault fixture unexpectedly succeeded"
grep -Fq 'injected promotion failure' "$TEST_ROOT/promotion.stderr" ||
  fail "promotion failure was not actionable"
for child in codex claude antigravity; do
  test "$(<"$TEST_ROOT/promotion-target/$child/sentinel")" = "preserve-$child" ||
    fail "promotion failure did not restore $child"
done
test -z "$(find "$TEST_ROOT/promotion-target" -maxdepth 1 -name '.forge-install.*' -print -quit)" ||
  fail "promotion failure left transaction data"

mkdir -p \
  "$TEST_ROOT/signal-target/codex" \
  "$TEST_ROOT/signal-target/claude" \
  "$TEST_ROOT/signal-target/antigravity"
for child in codex claude antigravity; do
  printf 'preserve-%s\n' "$child" >"$TEST_ROOT/signal-target/$child/sentinel"
done
set +e
FORGE_INSTALL_TEST_SIGNAL_PROMOTION=claude bash "$ROOT/scripts/install.sh" \
  --agent all --mode copy --plugin forge \
  --target-root "$TEST_ROOT/signal-target" \
  >"$TEST_ROOT/signal.stdout" 2>"$TEST_ROOT/signal.stderr"
signal_status="$?"
set -e
[[ "$signal_status" -ne 0 ]] || fail "promotion signal fixture unexpectedly succeeded"
grep -Fq 'isolated install interrupted' "$TEST_ROOT/signal.stderr" ||
  fail "promotion signal was not actionable"
for child in codex claude antigravity; do
  test "$(<"$TEST_ROOT/signal-target/$child/sentinel")" = "preserve-$child" ||
    fail "promotion signal did not restore $child"
done
test -z "$(find "$TEST_ROOT/signal-target" -maxdepth 1 -name '.forge-install.*' -print -quit)" ||
  fail "promotion signal left transaction data"

expect_exit 2 bash "$ROOT/scripts/install.sh" --agent antigravity --plugin forge

echo "forge-review-viewer-install: all checks passed"
