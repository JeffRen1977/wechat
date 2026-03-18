#!/usr/bin/env bash
# Trigger the "inbox" pipeline: one WeChat article from a link or pasted content,
# then generate cover+figures and upload to WeChat draft box.
# Usage: ./scripts/run-inbox-wechat.sh <URL or path to text file>
# Example: ./scripts/run-inbox-wechat.sh "https://example.com/article"
# Example: ./scripts/run-inbox-wechat.sh wechat_factory/01_sources/web_snapshots/paste.txt
# Requires: OpenClaw gateway running; ~/.gemini-env (GEMINI_API_KEY); ~/.wechat-env (WeChat credentials).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
export PATH="/home/renjeff/.nvm/versions/node/v22.22.0/bin:/usr/local/bin:/usr/bin:/bin:${PATH}"
LOG="${LOG:-/tmp/wechat-inbox.log}"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <URL or path to text file>" >&2
  echo "Example: $0 'https://techcrunch.com/...'" >&2
  echo "Example: $0 wechat_factory/01_sources/web_snapshots/paste.txt" >&2
  exit 1
fi

INPUT="$1"
cd "$WORKSPACE"

if [[ "$INPUT" == http://* || "$INPUT" == https://* ]]; then
  MSG="请根据这个链接写一篇公众号文章，并上传到草稿箱。链接：$INPUT"
else
  MSG="请根据以下文件中的内容写一篇公众号文章，并上传到草稿箱。内容文件路径：$INPUT"
fi

echo "[$(date -Iseconds)] Inbox pipeline: $INPUT" >> "$LOG"
if command -v openclaw &>/dev/null; then
  openclaw agent --agent main --message "$MSG" --timeout 1200 >> "$LOG" 2>&1 || true
else
  echo "[$(date -Iseconds)] openclaw not in PATH." >> "$LOG"
  exit 1
fi
echo "[$(date -Iseconds)] Inbox pipeline finished. Check $LOG and WeChat draft box." >> "$LOG"
echo "Done. Check $LOG and WeChat draft box."
