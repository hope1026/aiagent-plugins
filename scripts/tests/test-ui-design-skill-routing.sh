#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# Routing decisions need scenario evaluation. This gate checks distributable
# entry points and links, without dictating pixels, declarations, or wording.
python3 - "$ROOT" <<'PY'
from pathlib import Path
import json
import re
import sys
root = Path(sys.argv[1])
skills = root / 'plugins/forge/skills'
for name in ('verifying-work', 'visual-docs'):
    source = skills / name / 'SKILL.md'
    frontmatter = source.read_text().split('---', 2)[1]
    assert re.search(r'^name: '+re.escape(name)+r'$', frontmatter, re.M), source
    assert re.search(r'^description:\s*\S', frontmatter, re.M), source
for name in ('ui-design', 'web-app-design', 'website-design'):
    assert not (skills / name).exists(), name
reference = skills / 'verifying-work/references/ui-verification.md'
assert reference.is_file()
assert 'references/ui-verification.md' in (skills / 'verifying-work/SKILL.md').read_text()
for source in skills.rglob('*.md'):
    if 'tests' in source.parts:
        continue
    assert not re.search(r'the forge (?:web-app-design|website-design) skill', source.read_text()), source
for platform in ('.claude-plugin', '.codex-plugin'):
    manifest = json.loads((root / 'plugins/forge' / platform / 'plugin.json').read_text())
    assert (root / 'plugins/forge' / manifest['skills']).resolve() == skills.resolve()
    assert not re.search(r'web-app-design|website-design', json.dumps(manifest)), platform
print('UI verification entry points: all checks passed')
PY
