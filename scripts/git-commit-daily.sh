#!/usr/bin/env bash
# Commit and push daily wechat_factory output (04_output, 05_assets). For use in cron (e.g. 23:00).
# Usage: ./scripts/git-commit-daily.sh [YYYY-MM-DD]
#   If no date, uses today. Only commits if there are changes.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATE="${1:-$(date +%Y-%m-%d)}"
LOG="${LOG:-/tmp/wechat-git-commit.log}"

cd "$ROOT"
git add wechat_factory/04_output wechat_factory/05_assets 2>/dev/null || true
if git diff --staged --quiet 2>/dev/null; then
  echo "[$(date -Iseconds)] No changes to commit (date=$DATE)." >> "$LOG"
  exit 0
fi
git commit -m "Daily wechat output $DATE" >> "$LOG" 2>&1 || true
if git push >> "$LOG" 2>&1; then
  echo "[$(date -Iseconds)] Pushed daily output ($DATE)." >> "$LOG"
else
  echo "[$(date -Iseconds)] git push failed (check $LOG)." >> "$LOG"
  exit 1
fi
