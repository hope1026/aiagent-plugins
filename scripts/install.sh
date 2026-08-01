#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

AGENT="all"
MODE="copy"
PLUGIN="all"
TARGET_ROOT=""

usage() {
  cat <<'EOF'
Usage: scripts/install.sh [--agent codex|claude|antigravity|all] [--mode copy|link] [--plugin forge|all] [--target-root ABSOLUTE_PATH]

Dev-mode install from a local checkout. For end users, prefer the GitHub
marketplace install (see README.md).

Defaults:
  --agent all
  --mode copy
  --plugin all

Targets without --target-root:
  Codex:  per-skill entries under ~/.agents/skills/<skill-name>
          plus ~/.agents/plugins/marketplace.json (absolute local paths)
  Claude: ~/.claude/skills/<plugin-name> (whole plugin tree)

Isolated targets with --target-root:
  Codex:       <root>/codex/.agents/...
  Claude Code: <root>/claude/.claude/...
  Antigravity: <root>/antigravity/agent-skills/...

Notes:
  --mode link gives live edits (edit repo -> instantly active).
  --agent all preserves the Codex + Claude behavior unless --target-root is set.
  Antigravity export requires --target-root.
  On Windows (Git Bash/MSYS/Cygwin) symlinks are unreliable; copy is forced.
EOF
}

usage_error() {
  echo "$1" >&2
  usage >&2
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)
      [[ $# -ge 2 ]] || usage_error "--agent requires a value"
      AGENT="$2"; shift 2 ;;
    --mode)
      [[ $# -ge 2 ]] || usage_error "--mode requires a value"
      MODE="$2"; shift 2 ;;
    --plugin)
      [[ $# -ge 2 ]] || usage_error "--plugin requires a value"
      PLUGIN="$2"; shift 2 ;;
    --target-root)
      [[ $# -ge 2 ]] || usage_error "--target-root requires a value"
      TARGET_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) usage_error "unknown argument: $1" ;;
  esac
done

[[ "$AGENT" == "all" || "$AGENT" == "codex" || "$AGENT" == "claude" || "$AGENT" == "antigravity" ]] ||
  usage_error "--agent must be codex, claude, antigravity, or all"
[[ "$MODE" == "copy" || "$MODE" == "link" ]] ||
  usage_error "--mode must be copy or link"
[[ "$PLUGIN" == "all" || -d "$ROOT_DIR/plugins/$PLUGIN" ]] ||
  usage_error "--plugin must be 'all' or an existing directory under plugins/"
if [[ "$AGENT" == "antigravity" && -z "$TARGET_ROOT" ]]; then
  usage_error "--agent antigravity requires --target-root"
fi

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

canonical_target_root() {
  python3 - "$1" <<'PY'
import os
import pathlib
import sys

raw = sys.argv[1]
if not raw or not os.path.isabs(raw):
    raise SystemExit("--target-root must be an absolute path")
if any(part in {".", ".."} for part in raw.split(os.sep)):
    raise SystemExit("--target-root must not contain '.' or '..' components")

path = pathlib.Path(raw)
# macOS exposes its real temporary tree through the stable /var -> /private/var
# system alias. Accept that platform alias, but inspect every component below
# the canonical prefix so user-created symlink destinations still fail closed.
if (
    sys.platform == "darwin"
    and len(path.parts) > 1
    and path.parts[1] == "var"
    and os.path.islink("/var")
    and os.path.realpath("/var") == "/private/var"
):
    path = pathlib.Path("/private/var", *path.parts[2:])
current = pathlib.Path(path.anchor)
for part in path.parts[1:]:
    current /= part
    if os.path.lexists(current) and current.is_symlink():
        raise SystemExit(f"--target-root has a symlink component: {current}")

if os.path.lexists(path) and not path.is_dir():
    raise SystemExit("--target-root must name a directory")

probe = path
while not os.path.lexists(probe):
    if probe.parent == probe:
        raise SystemExit("--target-root has no existing parent")
    probe = probe.parent
mode = probe.stat().st_mode
if mode & 0o222 == 0 or not os.access(probe, os.W_OK | os.X_OK):
    raise SystemExit(f"--target-root is not writable: {probe}")

print(path)
PY
}

assert_no_existing_symlink() {
  local path="$1"
  [[ -e "$path" || -L "$path" ]] || return 0
  [[ -d "$path" && ! -L "$path" ]] ||
    usage_error "isolated install destination must be a real directory: $path"
  if find "$path" -type l -print -quit | grep -q .; then
    usage_error "isolated install destination contains a symlink: $path"
  fi
}

run_isolated_install() {
  local resolved
  if ! resolved="$(canonical_target_root "$TARGET_ROOT" 2>&1)"; then
    usage_error "$resolved"
  fi
  TARGET_ROOT="$resolved"
  mkdir -p "$TARGET_ROOT"
  local actual
  actual="$(cd "$TARGET_ROOT" && pwd -P)"
  [[ "$actual" == "$TARGET_ROOT" ]] ||
    usage_error "--target-root did not resolve to the requested path"

  local -a children=()
  case "$AGENT" in
    all) children=(codex claude antigravity) ;;
    codex) children=(codex) ;;
    claude) children=(claude) ;;
    antigravity) children=(antigravity) ;;
  esac
  local child
  for child in "${children[@]}"; do
    assert_no_existing_symlink "$TARGET_ROOT/$child"
  done

  local stage="$TARGET_ROOT/.forge-install.stage.$$"
  local backup="$TARGET_ROOT/.forge-install.backup.$$"
  [[ ! -e "$stage" && ! -e "$backup" ]] ||
    usage_error "isolated install transaction path already exists"
  mkdir -p "$stage" "$backup"
  FORGE_INSTALL_STAGE="$stage"
  FORGE_INSTALL_BACKUP="$backup"
  FORGE_INSTALL_PROMOTED=()
  FORGE_INSTALL_BACKED_UP=()
  FORGE_INSTALL_PROMOTION_ACTIVE=0
  cleanup_isolated_transaction() {
    local path
    for path in "${FORGE_INSTALL_STAGE:-}" "${FORGE_INSTALL_BACKUP:-}"; do
      [[ -n "$path" ]] || continue
      case "$path" in
        "$TARGET_ROOT"/.forge-install.*) ;;
        *) echo "refusing unsafe install transaction cleanup: $path" >&2; continue ;;
      esac
      [[ ! -e "$path" ]] || find "$path" -depth -delete >/dev/null 2>&1 || true
    done
  }
  rollback_isolated_promotion() {
    local index item
    for ((index=${#FORGE_INSTALL_PROMOTED[@]} - 1; index >= 0; index--)); do
      item="${FORGE_INSTALL_PROMOTED[index]}"
      [[ ! -e "$TARGET_ROOT/$item" ]] ||
        find "$TARGET_ROOT/$item" -depth -delete >/dev/null 2>&1 || true
    done
    for item in "${FORGE_INSTALL_BACKED_UP[@]}"; do
      [[ ! -e "$FORGE_INSTALL_BACKUP/$item" ]] ||
        mv "$FORGE_INSTALL_BACKUP/$item" "$TARGET_ROOT/$item" >/dev/null 2>&1 || true
    done
  }
  finish_isolated_transaction() {
    local result="$?"
    if [[ "${FORGE_INSTALL_PROMOTION_ACTIVE:-0}" -eq 1 ]]; then
      rollback_isolated_promotion
    fi
    cleanup_isolated_transaction
    return "$result"
  }
  interrupt_isolated_transaction() {
    local signal="$1" result=143
    [[ "$signal" != INT ]] || result=130
    trap - INT TERM
    if [[ "${FORGE_INSTALL_PROMOTION_ACTIVE:-0}" -eq 1 ]]; then
      rollback_isolated_promotion
      FORGE_INSTALL_PROMOTION_ACTIVE=0
    fi
    cleanup_isolated_transaction
    echo "isolated install interrupted by $signal; previous exports restored" >&2
    trap - EXIT
    exit "$result"
  }
  trap finish_isolated_transaction EXIT
  trap 'interrupt_isolated_transaction INT' INT
  trap 'interrupt_isolated_transaction TERM' TERM

  local copy_count=0
  stage_tree() {
    local src="$1" staged_dst="$2" final_dst="$3"
    mkdir -p "$(dirname "$staged_dst")"
    if [[ "$MODE" == "link" ]]; then
      ln -s "$src" "$staged_dst"
    else
      cp -R "$src" "$staged_dst"
    fi
    copy_count=$((copy_count + 1))
    if [[ -n "${FORGE_INSTALL_TEST_FAIL_AFTER_COPY:-}" &&
          "$copy_count" -ge "$FORGE_INSTALL_TEST_FAIL_AFTER_COPY" ]]; then
      echo "injected copy failure after $copy_count staged write(s)" >&2
      return 70
    fi
    echo "installed isolated export: $final_dst ($MODE)"
  }

  stage_codex() {
    local skills="$stage/codex/.agents/skills"
    while IFS= read -r plugin; do
      local skill_dir name
      for skill_dir in "$ROOT_DIR/plugins/$plugin/skills"/*/; do
        [[ -d "$skill_dir" ]] || continue
        name="$(basename "$skill_dir")"
        stage_tree "${skill_dir%/}" "$skills/$name" \
          "$TARGET_ROOT/codex/.agents/skills/$name"
      done
    done < <(plugin_list)
    mkdir -p "$stage/codex/.agents/plugins"
    jq --arg root "$ROOT_DIR" \
      '.plugins |= map(if .source.source == "local" then .source.path = ($root + "/" + (.source.path | ltrimstr("./"))) else . end)' \
      "$ROOT_DIR/.agents/plugins/marketplace.json" \
      >"$stage/codex/.agents/plugins/marketplace.json"
    echo "installed isolated export: $TARGET_ROOT/codex/.agents/plugins/marketplace.json (copy)"
  }

  stage_claude() {
    while IFS= read -r plugin; do
      stage_tree "$ROOT_DIR/plugins/$plugin" \
        "$stage/claude/.claude/skills/$plugin" \
        "$TARGET_ROOT/claude/.claude/skills/$plugin"
    done < <(plugin_list)
  }

  stage_antigravity() {
    while IFS= read -r plugin; do
      local skill_dir name
      for skill_dir in "$ROOT_DIR/plugins/$plugin/skills"/*/; do
        [[ -d "$skill_dir" ]] || continue
        name="$(basename "$skill_dir")"
        stage_tree "${skill_dir%/}" "$stage/antigravity/agent-skills/$name" \
          "$TARGET_ROOT/antigravity/agent-skills/$name"
      done
    done < <(plugin_list)
  }

  case "$AGENT" in
    all) stage_codex; stage_claude; stage_antigravity ;;
    codex) stage_codex ;;
    claude) stage_claude ;;
    antigravity) stage_antigravity ;;
  esac

  FORGE_INSTALL_PROMOTION_ACTIVE=1
  for child in "${children[@]}"; do
    if [[ -e "$TARGET_ROOT/$child" ]]; then
      FORGE_INSTALL_BACKED_UP+=("$child")
      if ! mv "$TARGET_ROOT/$child" "$backup/$child"; then
        rollback_isolated_promotion
        FORGE_INSTALL_PROMOTION_ACTIVE=0
        cleanup_isolated_transaction
        echo "isolated install backup failed for $child" >&2
        return 1
      fi
    fi
    if [[ "${FORGE_INSTALL_TEST_FAIL_PROMOTION:-}" == "$child" ]]; then
      rollback_isolated_promotion
      FORGE_INSTALL_PROMOTION_ACTIVE=0
      cleanup_isolated_transaction
      echo "injected promotion failure for $child" >&2
      return 71
    fi
    FORGE_INSTALL_PROMOTED+=("$child")
    if [[ "${FORGE_INSTALL_TEST_SIGNAL_PROMOTION:-}" == "$child" ]]; then
      kill -TERM "$$"
    fi
    if ! mv "$stage/$child" "$TARGET_ROOT/$child"; then
      rollback_isolated_promotion
      FORGE_INSTALL_PROMOTION_ACTIVE=0
      cleanup_isolated_transaction
      echo "isolated install promotion failed for $child" >&2
      return 1
    fi
  done

  FORGE_INSTALL_PROMOTION_ACTIVE=0
  cleanup_isolated_transaction
  unset FORGE_INSTALL_STAGE FORGE_INSTALL_BACKUP FORGE_INSTALL_PROMOTED
  unset FORGE_INSTALL_BACKED_UP FORGE_INSTALL_PROMOTION_ACTIVE
  trap - EXIT INT TERM
}

if [[ -n "$TARGET_ROOT" ]]; then
  run_isolated_install
else
  case "$AGENT" in
    all) install_codex; install_claude ;;
    codex) install_codex ;;
    claude) install_claude ;;
  esac
fi

echo "install complete (dev mode). Recommended for end users: GitHub marketplace install — see README.md."
