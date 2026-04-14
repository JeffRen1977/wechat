#!/usr/bin/env python3
"""
Convert Markdown to WeChat-friendly HTML: body-only, inline styles only.
WeChat strips <style> and external CSS; use this before draft/add.

- Optional theme: WECHAT_MD_HTML_THEME=minimal|green (or --theme minimal|green)
- External http(s) links -> visible label + [n] superscript + "参考与链接" footer
  (disable with WECHAT_MD_HTML_FOOTNOTES=0)
- Optional outer wrapper: WECHAT_MD_HTML_WRAP_SECTION=1

Usage: python md_to_wechat_html.py <article.md> [--max-chars 19000] [--theme minimal|green]
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

# Inline styles: px/em; avoid position, transform, % for layout.
STYLES_MINIMAL = {
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
    "a": "color:#2563eb;text-decoration:underline",
}

STYLES_GREEN = {
    **STYLES_MINIMAL,
    "h2": "font-size:18px;font-weight:bold;margin:0.8em 0 0.4em;line-height:1.4;color:#0d5c3d",
    "h3": "font-size:16px;font-weight:bold;margin:0.8em 0 0.3em;line-height:1.5;color:#0d5c3d",
    "blockquote": (
        "margin:0.8em 0;padding:0.6em 0.6em 1em;border-left:3px solid #0d7d4d;"
        "color:#444;font-size:15px;line-height:1.6;background-color:#f8fcf9"
    ),
    "a": "color:#0b6b4a;text-decoration:underline",
}


def get_styles(theme: str) -> dict[str, str]:
    t = (theme or "minimal").lower().strip()
    if t in ("green", "wechat-green", "g"):
        return dict(STYLES_GREEN)
    return dict(STYLES_MINIMAL)


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
    li_wrap = re.compile(
        r"<li([^>]*)>((?:\s*<p[^>]*>[\s\S]*?</p>\s*)+)</li>",
        re.IGNORECASE,
    )

    def merge_li(m: re.Match[str]) -> str:
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
    html = re.sub(r"<li[^>]*>\s*</li>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<li[^>]*>\s*<br\s*/?>\s*</li>", "", html, flags=re.IGNORECASE)
    return html


def add_emphasis_inline_styles(html: str) -> str:
    bold = "font-weight:bold;color:#1a1a1a"

    def strong_repl(m: re.Match[str]) -> str:
        rest = m.group(1)
        if not rest.strip():
            return f'<strong style="{bold}">'
        if "style=" in rest.lower():
            return m.group(0)
        return f'<strong style="{bold}" {rest.strip()}>'

    html = re.sub(r"<strong([^>]*)>", strong_repl, html, flags=re.IGNORECASE)

    def b_repl(m: re.Match[str]) -> str:
        rest = m.group(1)
        if not rest.strip():
            return f'<b style="{bold}">'
        if "style=" in rest.lower():
            return m.group(0)
        return f'<b style="{bold}" {rest.strip()}>'

    html = re.sub(r"<b([^>]*)>", b_repl, html, flags=re.IGNORECASE)
    return html


def extract_body(html: str) -> str:
    m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    html = re.sub(r"<head>.*?</head>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<!DOCTYPE[^>]*>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<html[^>]*>|</html>", "", html, flags=re.IGNORECASE)
    return html.strip()


def external_links_to_footnotes(html: str, accent_color: str) -> str:
    """
    Replace <a href="http...">label</a> with label + [n] superscript; append URL list.
    Non-http(s) links (anchors, mailto) unchanged.
    """
    url_to_num: dict[str, int] = {}
    order: list[str] = []
    tag_re = re.compile(
        r'<a\s+[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>',
        re.IGNORECASE,
    )

    def repl(m: re.Match[str]) -> str:
        href = m.group(1).strip()
        inner_html = m.group(2).strip()
        if not re.match(r"https?://", href, re.I):
            return m.group(0)
        if href not in url_to_num:
            url_to_num[href] = len(order) + 1
            order.append(href)
        n = url_to_num[href]
        label = re.sub(r"<[^>]+>", "", inner_html)
        label = label.strip()
        if not label:
            label = href
        if len(label) > 48:
            label = label[:45] + "…"
        inner_stripped = re.sub(r"<[^>]+>", "", inner_html).strip()
        if inner_stripped:
            body = inner_html
        else:
            body = label
        sup_style = (
            f"font-size:11px;color:{accent_color};vertical-align:super;font-weight:600;"
            "margin-left:2px"
        )
        return f'<span style="color:#333">{body}</span><sup style="{sup_style}">[{n}]</sup>'

    new_html = tag_re.sub(repl, html)
    if not order:
        return new_html

    ref_box = (
        "font-size:13px;color:#666;line-height:1.6;margin-top:1.4em;padding:0.8em 0 0;"
        f"border-top:2px solid {accent_color}"
    )
    title_div = (
        f"font-size:14px;font-weight:bold;color:{accent_color};margin:0 0 0.5em"
    )
    items = "".join(
        f'<div style="margin:0.35em 0;font-size:13px;color:#555;word-break:break-all">'
        f'<span style="color:{accent_color};font-weight:600">[{i + 1}]</span> {url}</div>'
        for i, url in enumerate(order)
    )
    footer = (
        f'<section style="{ref_box}">'
        f'<div style="{title_div}">参考与链接</div>{items}</section>'
    )
    return new_html + footer


def add_inline_styles(html: str, styles: dict[str, str]) -> str:
    attr_tags = ("img", "a")
    for tag in attr_tags:
        if tag not in styles:
            continue
        style = styles[tag]
        html = re.sub(rf"<{tag}\s+", f'<{tag} style="{style}" ', html, flags=re.IGNORECASE)
        html = re.sub(rf"<{tag}>", f'<{tag} style="{style}">', html, flags=re.IGNORECASE)
    for tag, style in styles.items():
        if tag in attr_tags:
            continue
        pattern = re.compile(rf"<{tag}(\s[^>]*)?>", re.IGNORECASE)
        html = pattern.sub(f'<{tag} style="{style}">', html)
    return html


def maybe_wrap_section(html: str) -> str:
    v = os.environ.get("WECHAT_MD_HTML_WRAP_SECTION", "").strip().lower()
    if v not in ("1", "true", "yes", "on"):
        return html
    wrap = "padding:2px 8px;margin:0"
    return f'<section style="{wrap}">{html}</section>'


def main() -> None:
    max_chars = 19000
    theme = os.environ.get("WECHAT_MD_HTML_THEME", "minimal").lower().strip()
    args = list(sys.argv[1:])
    if "--max-chars" in args:
        i = args.index("--max-chars")
        if i + 1 < len(args):
            max_chars = int(args[i + 1])
            del args[i : i + 2]
    if "--theme" in args:
        i = args.index("--theme")
        if i + 1 < len(args):
            theme = args[i + 1].lower().strip()
            del args[i : i + 2]
    if not args:
        print(
            "Usage: md_to_wechat_html.py <article.md> [--max-chars 19000] [--theme minimal|green]",
            file=sys.stderr,
        )
        sys.exit(1)
    md_path = Path(args[0])
    if not md_path.is_file():
        print("", end="")
        return

    styles = get_styles(theme)
    accent = "#0d7d4d" if theme in ("green", "wechat-green", "g") else "#5a6c7d"

    raw = pandoc_to_html(md_path)
    if not raw:
        print("", end="")
        return
    body = extract_body(raw)
    body = fix_list_items_for_wechat(body)
    foot_on = os.environ.get("WECHAT_MD_HTML_FOOTNOTES", "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )
    if foot_on:
        body = external_links_to_footnotes(body, accent_color=accent)
    body = add_emphasis_inline_styles(body)
    out = add_inline_styles(body, styles)
    out = maybe_wrap_section(out)
    if len(out) > max_chars:
        out = out[:max_chars]
    print(out, end="")


if __name__ == "__main__":
    main()
