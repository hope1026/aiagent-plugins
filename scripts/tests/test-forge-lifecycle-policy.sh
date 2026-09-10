#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Validate the resources an agent is directed to load. Natural-language choices
# are evaluated with realistic requests, not required phrases or step counts.
python3 - "$ROOT" <<'PY'
from pathlib import Path
import re
import sys
root = Path(sys.argv[1])
skills = root / 'plugins/forge/skills'
for skill in sorted(skills.glob('*/SKILL.md')):
    text = skill.read_text()
    for reference in set(re.findall(r'(?<![\w/])references/[a-z0-9-]+\.md', text)):
        target = skill.parent / reference
        assert target.is_file(), (skill, reference)
        assert target.read_text().strip(), target
    assert text.split('---', 2)[2].strip(), skill
print('forge lifecycle resources: all checks passed')
PY
