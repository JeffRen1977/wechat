#!/usr/bin/env bash
# Wrapper: load local env files then run OpenAI image generation (for Agent or cron).
# Usage: ./scripts/run-image-generation.sh wechat_factory/04_output/YYYY-MM-DD/PREFIX_article.md
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
[[ -f "$HOME/.openai-env" ]] && source "$HOME/.openai-env"
[[ -f "$HOME/.wechat-env" ]] && source "$HOME/.wechat-env"
exec "$ROOT/.venv/bin/python3" "$SCRIPT_DIR/image-generation.py" "$@"
