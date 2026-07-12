#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

grep -q 'docs/plans/PPP-<slug>/plan.md' "$ROOT/plugins/forge/skills/using-forge/SKILL.md"
grep -q 'docs/specs/NNN-<slug>/view.html' "$ROOT/plugins/forge/skills/using-forge/SKILL.md"
grep -q 'docs/plans/PPP-<slug>/view.html' "$ROOT/.agent-runbooks/maintaining-forge/references/portability-rules.md"
! grep -q '| Plans | `.forge/plans/' "$ROOT/.agent-runbooks/maintaining-forge/references/portability-rules.md"
grep -q 'docs/research/' "$ROOT/README.md"
grep -q 'docs/debug/' "$ROOT/README.md"

printf 'test-forge-artifact-contract: all checks passed\n'
