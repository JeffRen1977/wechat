#!/usr/bin/env bash
# End-to-end daily pipeline: web search → parse → 5 articles → 1 cover + 2 images per article → upload to WeChat draft.
# Usage: ./scripts/run-daily-wechat.sh
# Cron: 0 8 * * * /home/renjeff/Documents/projects/wechat/scripts/run-daily-wechat.sh
# Requires: OpenClaw gateway running; ~/.gemini-env (GEMINI_API_KEY); ~/.wechat-env (WECHAT_APPID, WECHAT_SECRET).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
DATE="$(date +%Y-%m-%d)"
LOG="${LOG:-/tmp/wechat-pipeline.log}"
# Ensure openclaw (installed via nvm) is on PATH even under cron
export PATH="/home/renjeff/.nvm/versions/node/v22.22.0/bin:/usr/local/bin:/usr/bin:/bin:${PATH}"
cd "$WORKSPACE"

echo "[$(date -Iseconds)] Step 1/2: OpenClaw agent (search, parse, write 5 articles to 04_output/$DATE)." >> "$LOG"
if command -v openclaw &>/dev/null; then
  openclaw agent --agent main --message "执行今日公众号任务，产出 5 篇并保存到 04_output" --timeout 1200 >> "$LOG" 2>&1 || true
else
  echo "[$(date -Iseconds)] openclaw not in PATH." >> "$LOG"
  exit 1
fi

echo "[$(date -Iseconds)] Step 2/2: Generate 1 cover + 2 images per article, then upload to WeChat draft." >> "$LOG"
"$SCRIPT_DIR/generate-images-and-upload.sh" "$DATE" >> "$LOG" 2>&1 || true

echo "[$(date -Iseconds)] Daily pipeline finished." >> "$LOG"
