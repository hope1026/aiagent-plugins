#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

grep -q 'docs/plans/PPP-<slug>/plan.md' "$ROOT/plugins/forge/skills/using-forge/SKILL.md"
grep -q 'docs/specs/NNN-<slug>/view.html' "$ROOT/plugins/forge/skills/using-forge/SKILL.md"
grep -q 'docs/plans/PPP-<slug>/view.html' "$ROOT/.agent-runbooks/maintaining-forge/references/portability-rules.md"
! grep -q '| Plans | `.forge/plans/' "$ROOT/.agent-runbooks/maintaining-forge/references/portability-rules.md"
grep -q 'docs/research/' "$ROOT/README.md"
grep -q 'docs/debug/' "$ROOT/README.md"
grep -q 'Related Specs' "$ROOT/plugins/forge/skills/writing-plans/SKILL.md"
grep -q 'docs/plans/PPP-<slug>/plan.md' "$ROOT/plugins/forge/skills/writing-plans/SKILL.md"
grep -q '0 or more' "$ROOT/plugins/forge/skills/writing-plans/SKILL.md"
! grep -q 'same `NNN` as the spec' "$ROOT/plugins/forge/skills/writing-plans/SKILL.md"
! grep -q 'combined review path' "$ROOT/plugins/forge/skills/writing-plans/references/plan-visual-structure.md"
grep -q 'docs/plans/PPP-<slug>/plan.md' "$ROOT/plugins/forge/skills/executing-plans/SKILL.md"
grep -q 'Progress History' "$ROOT/plugins/forge/skills/executing-plans/SKILL.md"
! grep -q 'progress-NNN' "$ROOT/plugins/forge/skills/executing-plans/SKILL.md"
! grep -q 'combined Viewer' "$ROOT/plugins/forge/skills/executing-plans/SKILL.md"
grep -q 'docs/debug/' "$ROOT/plugins/forge/skills/systematic-debugging/SKILL.md"
grep -q 'docs/specs/NNN-<slug>/view.html' "$ROOT/plugins/forge/skills/spec-viewer/SKILL.md"
grep -q 'docs/plans/PPP-<slug>/view.html' "$ROOT/plugins/forge/skills/spec-viewer/SKILL.md"
! grep -q '| `combined`' "$ROOT/plugins/forge/skills/spec-viewer/SKILL.md"
grep -q '`unverified`' "$ROOT/plugins/forge/skills/spec-viewer/SKILL.md"
! grep -q 'Combined mode' "$ROOT/plugins/forge/skills/spec-viewer/references/content-patterns.md"

printf 'test-forge-artifact-contract: all checks passed\n'
