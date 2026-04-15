#!/usr/bin/env bash
# For a given day: generate 1 cover + 2 content images per article, then upload all to WeChat draft.
# Usage: ./scripts/generate-images-and-upload.sh [YYYY-MM-DD]
#   If no date, uses today. Requires ~/.gemini-env (GEMINI_API_KEY) and ~/.wechat-env (WeChat credentials).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATE="${1:-$(date +%Y-%m-%d)}"
OUT_DIR="$ROOT/wechat_factory/04_output/$DATE"
LOG="${LOG:-/tmp/wechat-images-upload.log}"

echo "[$(date -Iseconds)] Generating images for $DATE (1 cover + 2 figs per article), then uploading." >> "$LOG"
cd "$ROOT"

if [[ ! -d "$OUT_DIR" ]]; then
  echo "Missing $OUT_DIR. Run the daily pipeline first." >> "$LOG"
  echo "Missing $OUT_DIR. Run the daily pipeline first." >&2
  exit 1
fi

for md in "$OUT_DIR"/*.md; do
  [[ -f "$md" ]] || continue
  echo "[$(date -Iseconds)] Images for $(basename "$md")" >> "$LOG"
  ./scripts/run-gemini-images.sh "$md" >> "$LOG" 2>&1 || true
  # Body images only appear in WeChat if Markdown contains ![...](..._figN.png); agents often omit them.
  python3 "$SCRIPT_DIR/ensure_article_image_refs.py" "$md" >> "$LOG" 2>&1 || true
done

echo "[$(date -Iseconds)] Uploading to WeChat draft." >> "$LOG"
[[ -f "$HOME/.wechat-env" ]] && source "$HOME/.wechat-env"
./scripts/wechat-draft-upload.sh "$DATE" >> "$LOG" 2>&1 || true
echo "[$(date -Iseconds)] Done. Check $LOG and WeChat draft box." >> "$LOG"
echo "Done. Check $LOG and WeChat draft box."
