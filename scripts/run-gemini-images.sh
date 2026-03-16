#!/usr/bin/env bash
# Wrapper: load ~/.gemini-env then run gemini-gen-images.py (for Agent or cron).
# Usage: ./scripts/run-gemini-images.sh wechat_factory/04_output/YYYY-MM-DD/PREFIX_article.md
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
[[ -f "$HOME/.gemini-env" ]] && source "$HOME/.gemini-env"
[[ -f "$HOME/.wechat-env" ]] && source "$HOME/.wechat-env"
exec "$ROOT/.venv/bin/python3" "$SCRIPT_DIR/gemini-gen-images.py" "$@"
