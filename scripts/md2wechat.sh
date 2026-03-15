#!/usr/bin/env bash
# Convert wechat_factory daily output Markdown to standalone HTML for WeChat.
# Usage: ./scripts/md2wechat.sh [dir]
#   dir defaults to wechat_factory/04_output/YYYY-MM-DD (today)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"
DIR="${1:-wechat_factory/04_output/$(date +%Y-%m-%d)}"
OUT="${DIR}/html"
mkdir -p "$OUT"
for f in "$DIR"/*.md; do
  [[ -f "$f" ]] || continue
  base=$(basename "$f" .md)
  pandoc "$f" -f markdown -t html -o "$OUT/${base}.html" --standalone
done
echo "HTML written to $OUT"
