#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 - "$ROOT" <<'PY'
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile

root = Path(sys.argv[1])
hook = root / 'plugins/forge/hooks/session-start'
skill = root / 'plugins/forge/skills/using-forge/SKILL.md'

# Exercise both JSON encoders without depending on which one the host prefers.
with tempfile.TemporaryDirectory() as temporary:
    temporary = Path(temporary)
    outputs = []
    for use_jq in (False, True):
        if use_jq and not shutil.which('jq'):
            continue
        bindir = temporary / str(use_jq)
        bindir.mkdir()
        for command in ('bash', 'dirname', 'cat', 'python3') + (('jq',) if use_jq else ()):
            (bindir / command).symlink_to(shutil.which(command))
        result = subprocess.run([shutil.which('bash'), str(hook)],
            env={**os.environ, 'PATH': str(bindir)}, text=True, capture_output=True, check=True)
        payload = json.loads(result.stdout)['hookSpecificOutput']
        assert payload['hookEventName'] == 'SessionStart'
        context = payload['additionalContext']
        assert 'using-forge' in context
        assert skill.read_text() not in context, 'bootstrap eagerly injects the whole router'
        outputs.append(context)
    assert len(set(outputs)) == 1, 'JSON encoders disagree'

    # A partial installation should not inject an unusable skill entry.
    missing = temporary / 'missing/hooks/session-start'
    missing.parent.mkdir(parents=True)
    shutil.copy2(hook, missing)
    result = subprocess.run([shutil.which('bash'), str(missing)],
        text=True, capture_output=True, check=True)
    assert result.stdout == ''

print('forge bootstrap: all checks passed')
PY
