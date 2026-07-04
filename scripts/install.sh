#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

AGENT="all"
MODE="copy"
PLUGIN="all"

usage() {
  cat <<'EOF'
Usage: scripts/install.sh [--agent codex|claude|all] [--mode copy|link] [--plugin forge|all]

Dev-mode install from a local checkout. For end users, prefer the GitHub
marketplace install (see README.md).

Defaults:
  --agent all
  --mode copy
  --plugin all

Targets:
  Codex:  per-skill entries under ~/.agents/skills/<skill-name>
          plus ~/.agents/plugins/marketplace.json (absolute local paths)
  Claude: ~/.claude/skills/<plugin-name> (whole plugin tree)

Notes:
  --mode link gives live edits (edit repo -> instantly active).
  On Windows (Git Bash/MSYS/Cygwin) symlinks are unreliable; copy is forced.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT="${2:-}"; shift 2 ;;
    --mode) MODE="${2:-}"; shift 2 ;;
    --plugin) PLUGIN="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ "$AGENT" == "all" || "$AGENT" == "codex" || "$AGENT" == "claude" ]] || {
  echo "--agent must be codex, claude, or all" >&2; exit 2; }
[[ "$MODE" == "copy" || "$MODE" == "link" ]] || {
  echo "--mode must be copy or link" >&2; exit 2; }
[[ "$PLUGIN" == "all" || -d "$ROOT_DIR/plugins/$PLUGIN" ]] || {
  echo "--plugin must be 'all' or an existing directory under plugins/" >&2; exit 2; }

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    if [[ "$MODE" == "link" ]]; then
      echo "note: symlinks are unreliable on Windows; forcing --mode copy"
      MODE="copy"
    fi
    ;;
esac

plugin_list() {
  if [[ "$PLUGIN" == "all" ]]; then
    for d in "$ROOT_DIR"/plugins/*/; do basename "$d"; done
  else
    echo "$PLUGIN"
  fi
}

install_tree() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  rm -rf "$dst"
  if [[ "$MODE" == "link" ]]; then
    ln -s "$src" "$dst"
  else
    cp -R "$src" "$dst"
  fi
}

install_codex() {
  local skills_dir="$HOME/.agents/skills"
  mkdir -p "$skills_dir"
  while IFS= read -r plugin; do
    for skill_dir in "$ROOT_DIR/plugins/$plugin/skills"/*/; do
      [[ -d "$skill_dir" ]] || continue
      local name; name="$(basename "$skill_dir")"
      install_tree "${skill_dir%/}" "$skills_dir/$name"
      echo "installed Codex skill: $skills_dir/$name ($MODE)"
    done
  done < <(plugin_list)

  # Personal marketplace with absolute paths to this checkout
  local mp_dir="$HOME/.agents/plugins"
  mkdir -p "$mp_dir"
  jq --arg root "$ROOT_DIR" \
    '.plugins |= map(if .source.source == "local" then .source.path = ($root + "/" + (.source.path | ltrimstr("./"))) else . end)' \
    "$ROOT_DIR/.agents/plugins/marketplace.json" > "$mp_dir/marketplace.json"
  echo "installed Codex marketplace: $mp_dir/marketplace.json"
}

install_claude() {
  while IFS= read -r plugin; do
    local dst="$HOME/.claude/skills/$plugin"
    install_tree "$ROOT_DIR/plugins/$plugin" "$dst"
    echo "installed Claude Code skills-directory plugin: $dst ($MODE)"
  done < <(plugin_list)
  echo "note: SessionStart hooks only run for marketplace-installed plugins;"
  echo "      for the full experience use: /plugin marketplace add hope1026/aiagent-plugins"
}

case "$AGENT" in
  all) install_codex; install_claude ;;
  codex) install_codex ;;
  claude) install_claude ;;
esac

echo "install complete (dev mode). Recommended for end users: GitHub marketplace install — see README.md."
