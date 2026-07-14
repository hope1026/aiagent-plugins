#!/usr/bin/env bash
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

err() { echo "FAIL: $1"; FAIL=1; }

# 1. JSON manifests parse
for f in "$ROOT_DIR"/plugins/*/.claude-plugin/plugin.json \
         "$ROOT_DIR"/plugins/*/.codex-plugin/plugin.json \
         "$ROOT_DIR"/.claude-plugin/marketplace.json \
         "$ROOT_DIR"/.agents/plugins/marketplace.json; do
  [[ -f "$f" ]] || continue
  jq . "$f" >/dev/null 2>&1 || err "invalid JSON: $f"
done

# 2. Every plugin dir has both manifests, and manifest name matches dir name
for plugin_dir in "$ROOT_DIR"/plugins/*/; do
  pname="$(basename "$plugin_dir")"
  for manifest in .claude-plugin/plugin.json .codex-plugin/plugin.json; do
    if [[ ! -f "$plugin_dir$manifest" ]]; then
      err "$pname: missing $manifest"
      continue
    fi
    mname="$(jq -r '.name' "$plugin_dir$manifest" 2>/dev/null)"
    [[ "$mname" == "$pname" ]] || err "$pname: $manifest name '$mname' != dir name"
    mskills="$(jq -r '.skills // empty' "$plugin_dir$manifest" 2>/dev/null)"
    [[ "$mskills" == "./skills/" ]] || err "$pname: $manifest skills must be './skills/'"
  done
done

# 3. Marketplace sources resolve to existing dirs
if [[ -f "$ROOT_DIR/.agents/plugins/marketplace.json" ]]; then
  while IFS= read -r p; do
    [[ -d "$ROOT_DIR/$p" ]] || err "marketplace path missing: $p (.agents)"
  done < <(jq -r '.plugins[].source.path // empty' "$ROOT_DIR/.agents/plugins/marketplace.json")
fi
if [[ -f "$ROOT_DIR/.claude-plugin/marketplace.json" ]]; then
  while IFS= read -r p; do
    [[ -d "$ROOT_DIR/$p" ]] || err "marketplace path missing: $p (.claude-plugin)"
  done < <(jq -r '.plugins[].source | if type == "object" then empty else . end' "$ROOT_DIR/.claude-plugin/marketplace.json" | grep '^\./' || true)
fi

# 4. Skill checks (all plugins)
while IFS= read -r skill; do
  dir="$(dirname "$skill")"
  name="$(basename "$dir")"
  [[ "$name" == _* ]] && continue

  # frontmatter block exists
  head -1 "$skill" | grep -q '^---$' || { err "$name: missing frontmatter"; continue; }
  fm="$(awk '/^---$/{n++; next} n==1{print} n>=2{exit}' "$skill")"

  echo "$fm" | grep -q '^name:' || err "$name: frontmatter missing 'name'"
  echo "$fm" | grep -q '^description:' || err "$name: frontmatter missing 'description'"

  fmname="$(echo "$fm" | sed -n 's/^name:[[:space:]]*//p')"
  [[ "$fmname" == "$name" ]] || err "$name: frontmatter name '$fmname' != dir name"

  desc="$(echo "$fm" | sed -n 's/^description:[[:space:]]*//p')"
  [[ "${#desc}" -le 1024 ]] || err "$name: description ${#desc} chars (>1024)"
  echo "$desc" | grep -qi 'use when' || err "$name: description must contain 'Use when'"
  dfirst="${desc:0:1}"
  if [[ "$dfirst" != "'" && "$dfirst" != '"' ]] && echo "$desc" | grep -q ': '; then
    err "$name: description containing ': ' must be YAML-quoted"
  fi

  # body line cap
  lines="$(wc -l < "$skill")"
  [[ "$lines" -le 500 ]] || err "$name: SKILL.md $lines lines (>500)"

  # portability: banned harness-specific tokens
  banned='TodoWrite|Task tool|Bash tool|Edit tool|Write tool'
  if grep -nE "$banned" "$skill" >/dev/null; then
    err "$name: banned harness-specific token: $(grep -nE "$banned" "$skill" | head -3 | tr '\n' ' ')"
  fi
  if grep -nE '@(\.|/|skills/)' "$skill" >/dev/null; then
    err "$name: banned @-path include: $(grep -nE '@(\.|/|skills/)' "$skill" | head -3 | tr '\n' ' ')"
  fi
done < <(
  {
    find "$ROOT_DIR/plugins" -name SKILL.md -not -path '*/node_modules/*'
    for root in \
      "$ROOT_DIR/.agent-extensions"/*/skills \
      "$ROOT_DIR/.agents/skills" \
      "$ROOT_DIR/.claude/skills"; do
      [[ -d "$root" ]] && find "$root" -name SKILL.md -not -path '*/node_modules/*'
    done
  } | sort
)

# 5. Cross-agent extension manager interface is executable without optional dependencies.
if [[ -f "$ROOT_DIR/plugins/forge/skills/creating-agent-extensions/scripts/manage_extension.py" ]]; then
  MANAGER="$ROOT_DIR/plugins/forge/skills/creating-agent-extensions/scripts/manage_extension.py"
  python3 "$MANAGER" --help \
    >/dev/null 2>&1 || err "creating-agent-extensions: manager --help failed"
  for manifest in "$ROOT_DIR"/.agent-extensions/*/extension.json; do
    [[ -f "$manifest" ]] || continue
    extension_dir="$(dirname "$manifest")"
    extension_name="$(basename "$extension_dir")"
    if ! extension_output="$(python3 "$MANAGER" validate --extension "$extension_dir" 2>&1)"; then
      err "$extension_name: extension validation failed: $extension_output"
    fi
  done
else
  err "creating-agent-extensions: missing manager script"
fi

if [[ "$FAIL" -eq 0 ]]; then
  echo "validate: all checks passed"
else
  exit 1
fi
