#!/usr/bin/env python3
"""
Convert Markdown to WeChat-friendly HTML: body-only, inline styles only.
WeChat strips <style> and external CSS; use this before draft/add.
Usage: python md_to_wechat_html.py <article.md> [--max-chars 19000]
"""
import re
import subprocess
import sys
from pathlib import Path

# Inline styles matching WeChat best practices (reference article layout)
# Use px/em; avoid position, transform, % for layout.
STYLES = {
    "h1": "font-size:22px;font-weight:bold;margin:0.6em 0;line-height:1.4;color:#1a1a1a",
    "h2": "font-size:18px;font-weight:bold;margin:0.8em 0 0.4em;line-height:1.4;color:#2c3e50",
    "h3": "font-size:16px;font-weight:bold;margin:0.8em 0 0.3em;line-height:1.5;color:#2c3e50",
    "h4": "font-size:15px;font-weight:bold;margin:0.6em 0 0.3em;line-height:1.5;color:#333",
    "p": "font-size:16px;color:#333;line-height:1.75;margin:0.5em 0;letter-spacing:0.3px",
    "ul": "margin:0.5em 0;padding-left:1.5em;line-height:1.75",
    "ol": "margin:0.5em 0;padding-left:1.5em;line-height:1.75",
    "li": "margin:0.25em 0;font-size:16px;color:#333",
    "blockquote": "margin:0.8em 0;padding-left:1em;border-left:3px solid #ddd;color:#555;font-size:15px;line-height:1.6",
    "img": "max-width:100%;height:auto;border-radius:6px;display:block;margin:0.8em 0",
}


def pandoc_to_html(md_path: Path) -> str:
    result = subprocess.run(
        ["pandoc", str(md_path), "-f", "markdown", "-t", "html", "--standalone"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def fix_list_items_for_wechat(html: str) -> str:
    """
    WeChat often renders <li><p>...</p></li> as empty bullets (drops inner <p>).
    Merge all <p> inside each <li> into one line with <br/> separators.
    """
    li_wrap = re.compile(
        r"<li([^>]*)>((?:\s*<p[^>]*>[\s\S]*?</p>\s*)+)</li>",
        re.IGNORECASE,
    )

    def merge_li(m: re.Match) -> str:
        attrs, inner = m.group(1), m.group(2)
        parts = re.findall(r"<p[^>]*>([\s\S]*?)</p>", inner, flags=re.IGNORECASE)
        chunks = [p.strip() for p in parts if p and p.strip()]
        if not chunks:
            return ""
        merged = "<br/>".join(chunks)
        return f"<li{attrs}>{merged}</li>"

    prev = None
    while prev != html:
        prev = html
        html = li_wrap.sub(merge_li, html)
    # Drop empty list items
    html = re.sub(r"<li[^>]*>\s*</li>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<li[^>]*>\s*<br\s*/?>\s*</li>", "", html, flags=re.IGNORECASE)
    return html


def add_emphasis_inline_styles(html: str) -> str:
    """WeChat keeps <strong>/<b> more reliably with explicit font-weight."""
    bold = "font-weight:bold;color:#1a1a1a"

    def strong_repl(m: re.Match) -> str:
        rest = m.group(1)
        if not rest.strip():
            return f'<strong style="{bold}">'
        if "style=" in rest.lower():
            return m.group(0)
        return f'<strong style="{bold}" {rest.strip()}>'

    html = re.sub(r"<strong([^>]*)>", strong_repl, html, flags=re.IGNORECASE)

    def b_repl(m: re.Match) -> str:
        rest = m.group(1)
        if not rest.strip():
            return f'<b style="{bold}">'
        if "style=" in rest.lower():
            return m.group(0)
        return f'<b style="{bold}" {rest.strip()}>'

    html = re.sub(r"<b([^>]*)>", b_repl, html, flags=re.IGNORECASE)
    return html


def extract_body(html: str) -> str:
    # Get content between <body> and </body>; strip the body tags.
    m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # No body: strip head and return the rest (e.g. fragment).
    html = re.sub(r"<head>.*?</head>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<!DOCTYPE[^>]*>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<html[^>]*>|</html>", "", html, flags=re.IGNORECASE)
    return html.strip()


def add_inline_styles(html: str) -> str:
    # Tags that often have important attrs (src, alt, href): prepend style, keep rest
    attr_tags = ("img", "a")
    for tag in attr_tags:
        if tag not in STYLES:
            continue
        style = STYLES[tag]
        # <img src="..."> -> <img style="..." src="...">
        html = re.sub(rf"<{tag}\s+", f'<{tag} style="{style}" ', html, flags=re.IGNORECASE)
        # <img> with no attrs
        html = re.sub(rf"<{tag}>", f'<{tag} style="{style}">', html, flags=re.IGNORECASE)
    # Block tags: replace full opening tag so WeChat gets clean inline style (id/class stripped by WeChat)
    for tag, style in STYLES.items():
        if tag in attr_tags:
            continue
        pattern = re.compile(rf"<{tag}(\s[^>]*)?>", re.IGNORECASE)
        html = pattern.sub(f'<{tag} style="{style}">', html)
    return html


def main() -> None:
    max_chars = 19000
    args = list(sys.argv[1:])
    if "--max-chars" in args:
        i = args.index("--max-chars")
        if i + 1 < len(args):
            max_chars = int(args[i + 1])
            del args[i : i + 2]
    if not args:
        print("Usage: md_to_wechat_html.py <article.md> [--max-chars 19000]", file=sys.stderr)
        sys.exit(1)
    md_path = Path(args[0])
    if not md_path.is_file():
        print("", end="")
        return
    raw = pandoc_to_html(md_path)
    if not raw:
        print("", end="")
        return
    body = extract_body(raw)
    body = fix_list_items_for_wechat(body)
    body = add_emphasis_inline_styles(body)
    out = add_inline_styles(body)
    if len(out) > max_chars:
        out = out[:max_chars]
    print(out, end="")


if __name__ == "__main__":
    main()
