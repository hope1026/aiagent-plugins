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
for name in ('web-app-design', 'website-design', 'visual-docs'):
    source = skills / name / 'SKILL.md'
    frontmatter = source.read_text().split('---', 2)[1]
    assert re.search(r'^name: '+re.escape(name)+r'$', frontmatter, re.M), source
    assert re.search(r'^description:\s*\S', frontmatter, re.M), source
assert not (skills / 'ui-design').exists()
for platform in ('.claude-plugin', '.codex-plugin'):
    manifest = json.loads((root / 'plugins/forge' / platform / 'plugin.json').read_text())
    assert (root / 'plugins/forge' / manifest['skills']).resolve() == skills.resolve()
print('ui-design entry points: all checks passed')
PY
