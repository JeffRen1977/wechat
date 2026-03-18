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

# Upload one image as permanent material (cover) and return media_id
upload_image() {
  local path="$1"
  if [[ ! -f "$path" ]]; then return 1; fi
  curl -s -X POST "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=$WECHAT_ACCESS_TOKEN&type=image" \
    -F "media=@$path" | jq -r '.media_id'
}

# Upload an in-article image and return the WeChat-hosted URL (for <img src="...">)
upload_body_image() {
  local path="$1"
  if [[ ! -f "$path" ]]; then echo ""; return; fi
  curl -s -X POST "https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token=$WECHAT_ACCESS_TOKEN" \
    -F "media=@$path" | jq -r '.url'
}

# Convert MD to WeChat-friendly HTML (body-only, inline styles; WeChat ignores <style>)
md_to_wechat_html() {
  local md="$1"
  if [[ ! -f "$md" ]]; then echo ""; return; fi
  python3 "$SCRIPT_DIR/md_to_wechat_html.py" "$md" --max-chars 19000
}

# Build title from first # line or filename
get_title() {
  local md="$1"
  local base="$2"
  local t
  t=$(grep -m1 '^# ' "$md" 2>/dev/null | sed 's/^# //' | head -c 32)
  if [[ -n "$t" ]]; then echo "$t"; else echo "$base"; fi
}

# Find a cover for prefix; fallback: try first segment (MED_article_2 -> MED) or any DATE cover
find_cover() {
  local prefix="$1"
  local c="$IMG_DIR/${DATE}_${prefix}_cover.png"
  [[ -f "$c" ]] && echo "$c" && return
  c="$IMG_DIR/${DATE}_${prefix}_cover.jpg"
  [[ -f "$c" ]] && echo "$c" && return
  # e.g. MED_article_2 -> try MED
  local short="${prefix%%_*}"
  [[ -n "$short" ]] && c="$IMG_DIR/${DATE}_${short}_cover.png" && [[ -f "$c" ]] && echo "$c" && return
  # fallback: any cover for this date
  for f in "$IMG_DIR"/${DATE}_*_cover.png "$IMG_DIR"/${DATE}_*_cover.jpg; do
    [[ -f "$f" ]] && echo "$f" && return
  done
  return 1
}

for md in "$OUT_DIR"/*.md; do
  [[ -f "$md" ]] || continue
  base=$(basename "$md" .md)
  prefix="${base%_article}"
  cover=$(find_cover "$prefix") || true
  if [[ -z "$cover" || ! -f "$cover" ]]; then
    echo "No cover for $base, skip." >> "$LOG"
    continue
  fi
  thumb_media_id=$(upload_image "$cover")
  if [[ -z "$thumb_media_id" || "$thumb_media_id" == "null" ]]; then
    echo "Upload cover failed: $cover" >> "$LOG"
    continue
  fi
  title=$(get_title "$md" "$base")
  content=$(md_to_wechat_html "$md")

  # Replace local image src paths in HTML with WeChat-hosted URLs for body images.
  # We look for <img ... src="..."> and, for any src that points under 05_assets/images,
  # upload the corresponding file via upload_body_image, then rewrite the src.
  tmp_html="$content"
  img_re='<img[^>]*src="([^"]+)"[^>]*>'
  while [[ "$tmp_html" =~ $img_re ]]; do
    img_tag="${BASH_REMATCH[0]}"
    src="${BASH_REMATCH[1]}"
    # Only rewrite non-HTTP(S) sources (local images)
    if [[ "$src" != http://* && "$src" != https://* ]]; then
      img_path=""
      if [[ "$src" == *"05_assets/images/"* ]]; then
        # Normalize anything containing 05_assets/images/ to IMG_DIR/<rest>
        rel="${src#*05_assets/images/}"
        img_path="$IMG_DIR/$rel"
      else
        # Fallback: resolve relative to the Markdown file directory
        img_dir="$(cd "$(dirname "$md")" && pwd)"
        if [[ -n "$img_dir" ]]; then
          # Use subshell to avoid changing cwd
          img_path="$(cd "$img_dir" && realpath "$src" 2>/dev/null || echo "")"
        fi
      fi
      if [[ -n "$img_path" && -f "$img_path" ]]; then
        img_url=$(upload_body_image "$img_path")
        if [[ -n "$img_url" && "$img_url" != "null" ]]; then
          # Replace all occurrences of this src with the WeChat URL in the full content
          content="${content//$src/$img_url}"
        else
          echo "Upload body image failed for $img_path" >> "$LOG"
        fi
      else
        echo "Body image path not found for src=$src (md=$md)" >> "$LOG"
      fi
    fi
    # Move past this <img> to find the next one
    tmp_html="${tmp_html#*${img_tag}}"
  done
  # Build a single-article payload so each .md becomes its own draft.
  one=$(jq -n \
    --arg title "$title" \
    --arg content "$content" \
    --arg thumb "$thumb_media_id" \
    '{article_type:"news",title:$title,content:$content,thumb_media_id:$thumb,need_open_comment:0,only_fans_can_comment:0}')

  BODY="{\"articles\":[${one}]}"
  RESP=$(curl -s -X POST "https://api.weixin.qq.com/cgi-bin/draft/add?access_token=$WECHAT_ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$BODY")
  media_id=$(echo "$RESP" | jq -r '.media_id')
  if [[ -z "$media_id" || "$media_id" == "null" ]]; then
    echo "draft/add failed for $base: $RESP" >> "$LOG"
    echo "draft/add failed for $base: $RESP" >&2
    continue
  fi
  echo "[$(date -Iseconds)] Draft uploaded for $base: media_id=$media_id (date=$DATE)" >> "$LOG"
  echo "media_id=$media_id ($base)"
done
