#!/usr/bin/env bash
# Extract text from a PDF for wechat_factory pipeline.
# Usage: ./scripts/extract_pdf_text.sh wechat_factory/01_sources/papers_pdf/paper.pdf
set -e
PDF="$1"
if [[ -z "$PDF" || ! -f "$PDF" ]]; then
  echo "Usage: $0 <path-to-pdf>"
  exit 1
fi
if ! command -v pdftotext &>/dev/null; then
  echo "Install poppler-utils: sudo apt install poppler-utils  (or: brew install poppler)"
  exit 1
fi
pdftotext -layout -enc UTF-8 "$PDF" -
