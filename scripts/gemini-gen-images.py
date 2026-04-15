#!/usr/bin/env python3
"""
Generate cover + 2--3 in-article images from a wechat_factory article using Gemini (Nano Banana).
Saves to wechat_factory/05_assets/images/ as YYYY-MM-DD_PREFIX_cover.png and YYYY-MM-DD_PREFIX_fig1.png etc.
Requires: pip install google-genai; env GEMINI_API_KEY or GOOGLE_API_KEY.
Usage:
  python scripts/gemini-gen-images.py wechat_factory/04_output/2026-03-15/MED_article.md
  python scripts/gemini-gen-images.py wechat_factory/04_output/2026-03-15/MED_article.md --date 2026-03-15 --prefix MED
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# Project root (parent of scripts/)
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
ASSETS_IMAGES = ROOT / "wechat_factory" / "05_assets" / "images"

# Default model: Gemini 2.5 Flash Image (Nano Banana) for speed; or gemini-3.1-flash-image-preview (Nano Banana 2)
GEMINI_IMAGE_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")


def _load_env_files():
    """Load KEY=value from ~/.gemini-env and ~/.wechat-env so GEMINI_API_KEY is available in cron/non-interactive runs."""
    home = Path.home()
    for name in (".gemini-env", ".wechat-env"):
        path = home / name
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" in line:
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip("'\"")
                if k:
                    os.environ.setdefault(k, v)


def load_client():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Set GEMINI_API_KEY or GOOGLE_API_KEY.", file=sys.stderr)
        sys.exit(1)
    from google import genai
    return genai.Client(api_key=api_key)


# Skip these H2s for fig prompts (not visual); still used as fallback if nothing else.
_FIG_HEADING_SKIP = re.compile(
    r"^(Three Action Items|Action Items|\d+\.\s*Action|互动|资源|参考|评论区|CTA|点赞|在看|"
    r"附录|参考文献)$",
    re.IGNORECASE,
)


def read_article(md_path: Path) -> tuple[str, list[str]]:
    """Return (title, list of section blobs for figures: heading + body up to next ##)."""
    text = md_path.read_text(encoding="utf-8")
    title = ""
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            title = m.group(1).strip()
            break
    # Each ## section: full body until next ## (better context for image model)
    section_re = re.compile(r"(?:^|\n)##\s+([^\n]+)\n([\s\S]*?)(?=\n##\s+|\Z)")
    section_prompts: list[str] = []
    for m in section_re.finditer(text):
        heading = m.group(1).strip()
        body = m.group(2).strip()
        if _FIG_HEADING_SKIP.match(heading):
            continue
        blob = f"Section title: {heading}\nKey content: {body}"
        section_prompts.append(blob[:1200])
    if len(section_prompts) < 2:
        for m in section_re.finditer(text):
            heading = m.group(1).strip()
            body = m.group(2).strip()
            blob = f"Section title: {heading}\nKey content: {body}"
            short = blob[:1200]
            if short not in section_prompts:
                section_prompts.append(short)
            if len(section_prompts) >= 4:
                break
    if not section_prompts:
        section_prompts = [f"Article excerpt:\n{text[:900]}"]
    return title, section_prompts


# English-only topic + visual direction by prefix (image model reads this; avoids wrong Chinese in pixels)
PREFIX_VISUAL = {
    "MED": (
        "healthcare, wellness, and medical technology",
        "3D or soft illustration, clean clinical trust, teal and white palette, soft lighting, "
        "no gore or body horror, single clear focal subject, 8k illustration feel",
    ),
    "FIN": (
        "finance, investing, and data-driven decisions",
        "minimalist business style, deep blue and white, abstract charts as geometric shapes only "
        "with no readable labels or numbers, premium editorial, single hero metaphor",
    ),
    "EDU": (
        "education technology, classrooms, and lifelong learning",
        "warm learning environment, soft natural daylight, friendly modern edtech, "
        "orange and cream accents optional, uncluttered, hopeful mood",
    ),
    "INBOX": (
        "technology, business, and current affairs",
        "modern editorial, neutral slate with one accent color, high clarity, one strong subject",
    ),
}

NO_TEXT_RULE = " Critical: do not include any text, words, letters, numbers, or characters in the image. The image must be purely visual: shapes, colors, figures, and composition only—no writing of any kind."


def generate_image(client, prompt: str, out_path: Path, style_hint: str = "clean, professional") -> bool:
    full_prompt = f"{prompt} Style: {style_hint}, suitable for a WeChat official account article cover or inline figure.{NO_TEXT_RULE}"
    try:
        response = client.models.generate_content(
            model=GEMINI_IMAGE_MODEL,
            contents=[full_prompt],
        )
    except Exception as e:
        print(f"Generate failed: {e}", file=sys.stderr)
        return False
    # Extract image from response (google-genai: response.candidates[0].content.parts or response.parts)
    parts = getattr(response, "candidates", None)
    if parts:
        parts = parts[0].content.parts if parts else []
    else:
        parts = getattr(response, "parts", []) or []
    for part in parts:
        try:
            if getattr(part, "as_image", None) is not None:
                img = part.as_image()
                img.save(str(out_path))
                print(f"Saved: {out_path}")
                return True
        except Exception:
            pass
        if getattr(part, "inline_data", None) is not None:
            data = getattr(part.inline_data, "data", None) or getattr(part.inline_data, "image", None)
            if data:
                raw = data if isinstance(data, bytes) else __import__("base64").b64decode(data)
                out_path.write_bytes(raw)
                print(f"Saved: {out_path}")
                return True
    print("No image in response.", file=sys.stderr)
    return False


def main():
    _load_env_files()
    parser = argparse.ArgumentParser(description="Generate cover + 2-3 images from article MD via Gemini.")
    parser.add_argument("article_md", type=Path, help="Path to article Markdown, e.g. 04_output/YYYY-MM-DD/MED_article.md")
    parser.add_argument("--date", default=None, help="Date segment for filenames (default: from path)")
    parser.add_argument("--prefix", default=None, help="Prefix for filenames, e.g. MED (default: from article name)")
    parser.add_argument("--num-figs", type=int, default=2, help="Number of in-article figures (default 2)")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts only, do not call API")
    args = parser.parse_args()

    md_path = args.article_md if args.article_md.is_absolute() else ROOT / args.article_md
    if not md_path.is_file():
        print(f"Not a file: {md_path}", file=sys.stderr)
        sys.exit(1)

    # Infer date and prefix from path if not given: .../2026-03-15/MED_article.md -> 2026-03-15, MED
    parent_name = md_path.parent.name
    stem = md_path.stem  # MED_article
    if re.match(r"^\d{4}-\d{2}-\d{2}$", parent_name):
        date = args.date or parent_name
    else:
        date = args.date or os.environ.get("WECHAT_DATE", "2026-03-15")
    prefix = args.prefix or (stem.replace("_article", "") if "_article" in stem else "MED")

    title, section_prompts = read_article(md_path)
    ASSETS_IMAGES.mkdir(parents=True, exist_ok=True)

    client = None if args.dry_run else load_client()

    pfx = prefix.upper()
    topic_en, domain_style = PREFIX_VISUAL.get(pfx, PREFIX_VISUAL["INBOX"])

    # 1) Cover: title + first substantive section so the scene matches the article, not only the domain
    title_short = (title or topic_en)[:120]
    context_snip = section_prompts[0][:500] if section_prompts else ""
    cover_prompt = (
        f"Create one striking cover image for a WeChat article. "
        f"Title theme: {title_short!r}. "
        f"Subject domain: {topic_en}. "
        f"Base the visual on specific subjects named in this excerpt (products, settings, metaphors — "
        f"even if the excerpt is Chinese, interpret visually; no text in image): {context_snip!r}. "
        f"One clear hero scene, not a collage, cinematic composition, high detail."
    )
    cover_path = ASSETS_IMAGES / f"{date}_{prefix}_cover.png"
    if args.dry_run:
        print(f"Cover prompt: {cover_prompt}\n-> {cover_path}")
    else:
        generate_image(client, cover_prompt, cover_path, style_hint=domain_style)

    # 2) In-article figures: tie to H2 section summaries when present (read_article fills these)
    num_figs = min(args.num_figs, max(len(section_prompts), 1))
    for i in range(num_figs):
        section_idea = section_prompts[i] if i < len(section_prompts) else topic_en
        section_idea = section_idea.strip()[:400]
        fig_prompt = (
            f"Editorial illustration for a specific section of a Chinese WeChat article. "
            f"Read the excerpt and depict the MAIN concrete subject or metaphor (tools, people, charts as shapes, "
            f"classroom, medical context, money/ledger abstraction — match the excerpt, not a generic stock photo). "
            f"Excerpt: {section_idea!r}. "
            f"Domain: {topic_en}. "
            f"Single focal subject, strong composition, no readable text in the image."
        )
        fig_path = ASSETS_IMAGES / f"{date}_{prefix}_fig{i+1}.png"
        if args.dry_run:
            print(f"Fig{i+1} prompt: {fig_prompt}\n-> {fig_path}")
        else:
            generate_image(client, fig_prompt, fig_path, style_hint=domain_style)

    return 0


if __name__ == "__main__":
    sys.exit(main())
