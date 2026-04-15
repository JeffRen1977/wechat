#!/usr/bin/env python3
"""
If a daily article .md has no ![...](..._fig1.png) / fig2.png, insert them after the 1st and 2nd ## sections
so Pandoc emits <img> and wechat-draft-upload can upload body images.

Run after gemini-gen-images (files exist) and before wechat-draft-upload.
Usage: python3 scripts/ensure_article_image_refs.py <path/to/EDU_article.md>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def infer_date_prefix(md_path: Path) -> tuple[str, str]:
    parent = md_path.parent.name
    stem = md_path.stem
    prefix = stem.replace("_article", "") if "_article" in stem else stem
    if re.match(r"^\d{4}-\d{2}-\d{2}$", parent):
        return parent, prefix
    raise SystemExit(f"Cannot infer date from path: {md_path}")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: ensure_article_image_refs.py <article.md>", file=sys.stderr)
        return 1
    md_path = Path(sys.argv[1])
    if not md_path.is_file():
        return 1
    date, prefix = infer_date_prefix(md_path)
    rel1 = f"wechat_factory/05_assets/images/{date}_{prefix}_fig1.png"
    rel2 = f"wechat_factory/05_assets/images/{date}_{prefix}_fig2.png"
    text = md_path.read_text(encoding="utf-8", errors="replace")
    if f"{date}_{prefix}_fig1.png" in text and f"{date}_{prefix}_fig2.png" in text:
        return 0
    line1 = f"![配图]({rel1})\n"
    line2 = f"![配图]({rel2})\n"
    parts = re.split(r"(?m)(?=^##\s+)", text)
    if len(parts) >= 3:
        p1 = parts[1].rstrip() + "\n\n" + line1 + "\n"
        p2 = parts[2].rstrip() + "\n\n" + line2 + "\n"
        new_text = parts[0] + p1 + p2 + "".join(parts[3:])
    elif len(parts) == 2:
        p1 = parts[1].rstrip() + "\n\n" + line1 + "\n\n" + line2 + "\n"
        new_text = parts[0] + p1
    else:
        new_text = text.rstrip() + "\n\n---\n\n" + line1 + "\n" + line2 + "\n"
    md_path.write_text(new_text, encoding="utf-8")
    print(f"Inserted fig1/fig2 refs into {md_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
