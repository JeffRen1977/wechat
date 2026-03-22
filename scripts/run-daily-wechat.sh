#!/usr/bin/env bash
# End-to-end daily pipeline: web search → parse → 3 articles (EDU, MED, FIN) → 1 cover + 2 images per article → upload to WeChat draft.
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

echo "[$(date -Iseconds)] Step 1/2: OpenClaw agent (search, parse, write 3 articles to 04_output/$DATE)." >> "$LOG"
if command -v openclaw &>/dev/null; then
  openclaw agent --agent main --message "执行今日公众号任务：只产出 3 篇文章，且必须各 1 篇——教育 EDU_article.md、健康 MED_article.md、财经 FIN_article.md。默认以 YouTube 上对应领域的最新趋势与热门/新发布视频为主要素材（优先近几天内有讨论度的内容）；文风生动有趣、浅显易懂。仅当用户明确要求学术论文时才以论文为主。不要额外写 MED_article_2 等第二篇，除非用户明确要求。保存到 04_output 当日文件夹。遵循 skills/wechat-daily-editor 与 wechat_factory/03_templates/article_style.md。**重要：不要执行 wechat-draft-upload.sh 或 generate-images-and-upload.sh**——本脚本在你完成后会自动执行第 2 步统一配图并上传；若在对话里再上传会导致草稿箱里同一篇文章出现两份。" --timeout 1200 >> "$LOG" 2>&1 || true
else
  echo "[$(date -Iseconds)] openclaw not in PATH." >> "$LOG"
  exit 1
fi

echo "[$(date -Iseconds)] Step 2/2: Generate 1 cover + 2 images per article, then upload to WeChat draft." >> "$LOG"
"$SCRIPT_DIR/generate-images-and-upload.sh" "$DATE" >> "$LOG" 2>&1 || true

echo "[$(date -Iseconds)] Daily pipeline finished." >> "$LOG"
