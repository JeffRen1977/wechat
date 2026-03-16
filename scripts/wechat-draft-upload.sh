#!/usr/bin/env bash
# Upload wechat_factory output (articles + cover images) to WeChat Official Account draft box.
# Requires: curl, jq, pandoc. Env: WECHAT_APPID, WECHAT_SECRET (or WECHAT_ACCESS_TOKEN).
# Usage: ./scripts/wechat-draft-upload.sh [YYYY-MM-DD]
#   If no date, uses today. Reads from wechat_factory/04_output/YYYY-MM-DD and 05_assets/images/.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# Load WeChat credentials (e.g. for cron); optional if already in environment
[[ -f "$HOME/.wechat-env" ]] && source "$HOME/.wechat-env"
DATE="${1:-$(date +%Y-%m-%d)}"
OUT_DIR="$ROOT/wechat_factory/04_output/$DATE"
IMG_DIR="$ROOT/wechat_factory/05_assets/images"
LOG="${LOG:-/tmp/wechat-draft-upload.log}"

if [[ ! -d "$OUT_DIR" ]]; then
  echo "Missing $OUT_DIR. Run pipeline first or pass YYYY-MM-DD." >> "$LOG"
  exit 1
fi

# Access token: use WECHAT_ACCESS_TOKEN or fetch with WECHAT_APPID + WECHAT_SECRET
if [[ -z "$WECHAT_ACCESS_TOKEN" ]]; then
  if [[ -z "$WECHAT_APPID" || -z "$WECHAT_SECRET" ]]; then
    echo "Set WECHAT_ACCESS_TOKEN or (WECHAT_APPID and WECHAT_SECRET)." >> "$LOG"
    exit 1
  fi
  RESP=$(curl -s "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=$WECHAT_APPID&secret=$WECHAT_SECRET")
  WECHAT_ACCESS_TOKEN=$(echo "$RESP" | jq -r '.access_token')
  if [[ -z "$WECHAT_ACCESS_TOKEN" || "$WECHAT_ACCESS_TOKEN" == "null" ]]; then
    echo "Failed to get access_token: $RESP" >> "$LOG"
    exit 1
  fi
fi

# Upload one image and return media_id
upload_image() {
  local path="$1"
  if [[ ! -f "$path" ]]; then return 1; fi
  curl -s -X POST "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=$WECHAT_ACCESS_TOKEN&type=image" \
    -F "media=@$path" | jq -r '.media_id'
}

# Convert MD to HTML (strip style if needed), max ~20k chars for WeChat
md_to_wechat_html() {
  local md="$1"
  if [[ ! -f "$md" ]]; then echo ""; return; fi
  pandoc "$md" -f markdown -t html --standalone 2>/dev/null | head -c 19000
}

# Build title from first # line or filename
get_title() {
  local md="$1"
  local base="$2"
  local t
  t=$(grep -m1 '^# ' "$md" 2>/dev/null | sed 's/^# //' | head -c 32)
  if [[ -n "$t" ]]; then echo "$t"; else echo "$base"; fi
}

ARTICLES_JSON=""
for md in "$OUT_DIR"/*.md; do
  [[ -f "$md" ]] || continue
  base=$(basename "$md" .md)
  # e.g. MED_article -> MED
  prefix="${base%_article}"
  cover="$IMG_DIR/${DATE}_${prefix}_cover.png"
  if [[ ! -f "$cover" ]]; then cover="$IMG_DIR/${DATE}_${prefix}_cover.jpg"; fi
  if [[ ! -f "$cover" ]]; then
    echo "No cover for $base, skip or use placeholder." >> "$LOG"
    continue
  fi
  thumb_media_id=$(upload_image "$cover")
  if [[ -z "$thumb_media_id" || "$thumb_media_id" == "null" ]]; then
    echo "Upload cover failed: $cover" >> "$LOG"
    continue
  fi
  title=$(get_title "$md" "$base")
  content=$(md_to_wechat_html "$md")
  # Omit digest so WeChat auto-fills from content (avoids 45004 description size limit)
  one=$(jq -n \
    --arg title "$title" \
    --arg content "$content" \
    --arg thumb "$thumb_media_id" \
    '{article_type:"news",title:$title,content:$content,thumb_media_id:$thumb,need_open_comment:0,only_fans_can_comment:0}')
  if [[ -z "$ARTICLES_JSON" ]]; then ARTICLES_JSON="$one"; else ARTICLES_JSON="$ARTICLES_JSON,$one"; fi
done

if [[ -z "$ARTICLES_JSON" ]]; then
  echo "No articles built. Check covers in $IMG_DIR and MD in $OUT_DIR." >> "$LOG"
  echo "No articles built. See $LOG" >&2
  exit 1
fi

# POST draft/add
BODY="{\"articles\":[$ARTICLES_JSON]}"
RESP=$(curl -s -X POST "https://api.weixin.qq.com/cgi-bin/draft/add?access_token=$WECHAT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$BODY")
media_id=$(echo "$RESP" | jq -r '.media_id')
if [[ -z "$media_id" || "$media_id" == "null" ]]; then
  echo "draft/add failed: $RESP" >> "$LOG"
  echo "draft/add failed: $RESP" >&2
  exit 1
fi
echo "[$(date -Iseconds)] Draft uploaded: media_id=$media_id (date=$DATE)" >> "$LOG"
echo "media_id=$media_id"
