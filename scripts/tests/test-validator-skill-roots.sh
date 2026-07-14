#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROBE="$ROOT_DIR/.agent-extensions/validator-probe/skills/validator-probe"
WRAPPER="$ROOT_DIR/.agents/skills/maintaining-forge/SKILL.md"
BACKUP="$(mktemp)"
cp "$WRAPPER" "$BACKUP"
trap 'cp "$BACKUP" "$WRAPPER"; rm -f "$BACKUP"; rm -rf "$ROOT_DIR/.agent-extensions/validator-probe"' EXIT

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
  echo "FAIL: validate.sh ignored canonical .agent-extensions skills" >&2
  exit 1
fi

grep -q 'validator-probe: banned harness-specific token' <<<"$output" || {
  echo "FAIL: expected validator-probe failure was not reported" >&2
  printf '%s\n' "$output" >&2
  exit 1
}

rm -rf "$ROOT_DIR/.agent-extensions/validator-probe"
printf '\n# drift probe\n' >> "$WRAPPER"

if output="$(bash "$ROOT_DIR/scripts/validate.sh" 2>&1)"; then
  echo "FAIL: validate.sh ignored canonical adapter drift" >&2
  exit 1
fi

grep -q 'maintaining-forge: extension validation failed' <<<"$output" || {
  echo "FAIL: expected extension drift failure was not reported" >&2
  printf '%s\n' "$output" >&2
  exit 1
}

echo "validator roots: all checks passed"
