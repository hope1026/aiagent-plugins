#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEST_ROOT"' EXIT

# Replacing dedicated exports removes obsolete skills without touching siblings.
mkdir -p "$TEST_ROOT/user-skills/web-app-design"
printf 'user-owned\n' >"$TEST_ROOT/user-skills/web-app-design/marker"
for destination in \
  codex/.agents/skills \
  claude/.claude/skills/forge/skills \
  antigravity/agent-skills; do
  for name in ui-design web-app-design website-design; do
    mkdir -p "$TEST_ROOT/export/$destination/$name"
    printf 'obsolete Forge skill\n' >"$TEST_ROOT/export/$destination/$name/SKILL.md"
  done
  mkdir -p "$TEST_ROOT/export/$destination/visual-docs/assets"
  printf 'obsolete visual template\n' >"$TEST_ROOT/export/$destination/visual-docs/assets/viewer-template.html"
done

for _ in 1 2; do
  bash "$ROOT/scripts/install.sh" --agent all --mode copy --plugin forge \
    --target-root "$TEST_ROOT/export" >/dev/null
  python3 - "$ROOT" "$TEST_ROOT" <<'CHECK'
from pathlib import Path
import sys

root, temporary = map(Path, sys.argv[1:])
source = root / 'plugins/forge/skills'
expected = {path.parent.name for path in source.glob('*/SKILL.md')}
assert not expected.intersection({'ui-design', 'web-app-design', 'website-design'})
assert {'visual-docs', 'verifying-work'} <= expected
for destination in ('codex/.agents/skills', 'claude/.claude/skills/forge/skills', 'antigravity/agent-skills'):
    installed = temporary / 'export' / destination
    assert {p.name for p in installed.iterdir()} == expected, destination
    assert {p.relative_to(installed / 'visual-docs').as_posix()
            for p in (installed / 'visual-docs').rglob('*') if p.is_file()} == {'SKILL.md'}, destination
    for name in ('visual-docs/SKILL.md',
                 'verifying-work/SKILL.md', 'verifying-work/references/ui-verification.md'):
        assert (installed / name).read_bytes() == (source / name).read_bytes(), (destination, name)
assert (temporary / 'user-skills/web-app-design/marker').read_text() == 'user-owned\n'
CHECK
done

echo "forge-ui-skill-install: all checks passed"
