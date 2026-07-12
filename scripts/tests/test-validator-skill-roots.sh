#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROBE="$ROOT_DIR/.agents/skills/validator-probe"
trap 'rm -rf "$PROBE"' EXIT

mkdir -p "$PROBE"
printf '%s\n' \
  '---' \
  'name: validator-probe' \
  'description: Use when validating a temporary repository skill.' \
  '---' \
  '' \
  '# Validator Probe' \
  '' \
  'Task tool' > "$PROBE/SKILL.md"

if output="$(bash "$ROOT_DIR/scripts/validate.sh" 2>&1)"; then
  echo "FAIL: validate.sh ignored .agents/skills" >&2
  exit 1
fi

grep -q 'validator-probe: banned harness-specific token' <<<"$output" || {
  echo "FAIL: expected validator-probe failure was not reported" >&2
  printf '%s\n' "$output" >&2
  exit 1
}

echo "validator roots: all checks passed"
