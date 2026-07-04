#!/usr/bin/env bash
set -euo pipefail
usage() { echo "usage: build-viewer.sh -c content.html -t 'Title' -s 'status' -o out.html [--offline]"; exit 2; }
CONTENT="" TITLE="" STATUS="" OUT="" OFFLINE=0
while [[ $# -gt 0 ]]; do case "$1" in
  -c) CONTENT="$2"; shift 2;; -t) TITLE="$2"; shift 2;; -s) STATUS="$2"; shift 2;;
  -o) OUT="$2"; shift 2;; --offline) OFFLINE=1; shift;; *) usage;;
esac; done
[[ -f "$CONTENT" && -n "$TITLE" && -n "$OUT" ]] || usage
TPL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/assets/viewer-template.html"
MERMAID_TMP="$(mktemp)"
trap 'rm -f "$MERMAID_TMP"' EXIT
if [[ "$OFFLINE" -eq 1 ]]; then
  echo "<script>" > "$MERMAID_TMP"
  curl -fsSL "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js" >> "$MERMAID_TMP"
  echo "</script>" >> "$MERMAID_TMP"
else
  echo '<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>' > "$MERMAID_TMP"
fi
mkdir -p "$(dirname "$OUT")"
awk -v title="$TITLE" -v status="$STATUS" -v generated="$(date +%Y-%m-%d)" \
    -v content_file="$CONTENT" -v mermaid_file="$MERMAID_TMP" '
  # literal replacement: safe when values contain & or \ (awk gsub would mangle them)
  function repl(s, tag, val,    n, out) {
    while ((n = index(s, tag)) > 0) { out = out substr(s, 1, n - 1) val; s = substr(s, n + length(tag)) }
    return out s
  }
  /\{\{CONTENT\}\}/ { while ((getline line < content_file) > 0) print line; close(content_file); next }
  /\{\{MERMAID\}\}/ { while ((getline line < mermaid_file) > 0) print line; close(mermaid_file); next }
  { $0 = repl($0, "{{TITLE}}", title); $0 = repl($0, "{{STATUS}}", status); $0 = repl($0, "{{GENERATED}}", generated); print }
' "$TPL" > "$OUT"
echo "built: $OUT"
