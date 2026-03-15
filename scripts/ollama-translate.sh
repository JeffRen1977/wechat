#!/usr/bin/env bash
# Translate text to Chinese using local Ollama (saves API cost before main model polish).
# Usage: echo "English abstract..." | ./scripts/ollama-translate.sh
#    or: ./scripts/ollama-translate.sh "English abstract..."
# Requires: ollama, and run once: ollama pull llama3.3:70b  (or qwen2.5:7b)
set -e
OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.3:70b}"
TEXT="${1:-$(cat)}"
if [[ -z "$TEXT" ]]; then
  echo "Usage: $0 <text>   or   echo <text> | $0" >&2
  exit 1
fi
if ! command -v ollama &>/dev/null; then
  echo "Ollama not found. Install: https://ollama.com" >&2
  exit 1
fi
ollama run "$OLLAMA_MODEL" "将以下英文内容翻译为中文，保持专业术语准确。只输出译文，不要解释。

---
$TEXT
---"
