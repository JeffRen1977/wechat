#!/usr/bin/env bash
# End-to-end daily pipeline: web search → parse → 3 articles (EDU, MED, FIN) → 1 cover + 2 images per article → upload to WeChat draft.
# Usage: ./scripts/run-daily-wechat.sh
# Cron: 0 8 * * * /home/renjeff/Documents/projects/wechat/scripts/run-daily-wechat.sh
# Requires: OpenClaw gateway running; OPENAI_API_KEY; ~/.wechat-env (WECHAT_APPID, WECHAT_SECRET).
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
  openclaw agent --agent main --message "执行今日公众号任务：现在直接完成，不要询问澄清问题，不要只回复确认。只产出 3 篇文章，且必须各 1 篇——教育 EDU_article.md、健康 MED_article.md、财经 FIN_article.md。必须创建并写入 wechat_factory/04_output/$DATE/EDU_article.md、wechat_factory/04_output/$DATE/MED_article.md、wechat_factory/04_output/$DATE/FIN_article.md；只有这 3 个文件都实际落盘后才可以结束回复。**素材默认：大众向热点——每个领域各选一支「最新、较热门」的 YouTube 视频为主**（优先近 24–72 小时、有讨论度）；可用搜索补充**主流新闻/科技媒体报道**同一话题，用于核对事实与找钩子。**不要**默认用 arXiv、学术论文或 PDF 当主线；仅当用户在本轮对话里明确要求「只要论文/学术来源」时才以论文为主。文风生动有趣、浅显易懂。不要额外写 MED_article_2 等第二篇，除非用户明确要求。保存到 04_output 当日文件夹。遵循 skills/wechat-daily-editor 与 wechat_factory/03_templates/article_style.md。**重要：不要执行 wechat-draft-upload.sh 或 generate-images-and-upload.sh**——本脚本在你完成后会自动执行第 2 步统一配图并上传；若在对话里再上传会导致草稿箱里同一篇文章出现两份。" --timeout 1800 >> "$LOG" 2>&1
else
  echo "[$(date -Iseconds)] openclaw not in PATH." >> "$LOG"
  exit 1
fi

OUT_DIR="$WORKSPACE/wechat_factory/04_output/$DATE"
missing=()
for article in EDU_article.md MED_article.md FIN_article.md; do
  if [[ ! -s "$OUT_DIR/$article" ]]; then
    missing+=("$article")
  fi
done
if (( ${#missing[@]} > 0 )); then
  echo "[$(date -Iseconds)] ERROR: daily article generation incomplete; missing/non-empty check failed for: ${missing[*]}" >> "$LOG"
  echo "[$(date -Iseconds)] ERROR: expected files under $OUT_DIR. Skipping image generation and WeChat upload." >> "$LOG"
  exit 2
fi

echo "[$(date -Iseconds)] Step 2/2: Generate 1 cover + 2 images per article, then upload to WeChat draft." >> "$LOG"
DAILY_ARTICLES_ONLY=1 "$SCRIPT_DIR/generate-images-and-upload.sh" "$DATE" >> "$LOG" 2>&1

echo "[$(date -Iseconds)] Daily pipeline finished." >> "$LOG"
