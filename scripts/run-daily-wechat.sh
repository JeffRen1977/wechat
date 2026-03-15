#!/usr/bin/env bash
# Run the daily wechat_factory pipeline via OpenClaw default agent.
# Usage: ./scripts/run-daily-wechat.sh
# Cron: 0 8 * * * /home/renjeff/Documents/projects/wechat/scripts/run-daily-wechat.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG="${LOG:-/tmp/wechat-pipeline.log}"
export PATH="${PATH:-/usr/local/bin:/usr/bin:/bin}"
cd "$WORKSPACE"
echo "[$(date -Iseconds)] Starting daily wechat pipeline." >> "$LOG"
if command -v openclaw &>/dev/null; then
  openclaw agent --message "执行今日公众号任务，产出 5 篇并保存到 04_output" >> "$LOG" 2>&1 || true
else
  echo "[$(date -Iseconds)] openclaw not in PATH." >> "$LOG"
  exit 1
fi
echo "[$(date -Iseconds)] Finished." >> "$LOG"
