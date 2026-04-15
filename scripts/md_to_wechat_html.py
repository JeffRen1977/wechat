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

import html
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


def strip_title_from_markdown_body(md_text: str) -> str:
    """Drop leading H1 (and optional duplicate H2) — WeChat draft title is set separately."""
    lines = md_text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return md_text
    title: str | None = None
    m = re.match(r"^\s*#(?!#)\s+(.*)$", lines[0])
    if not m:
        m = re.match(r"^\s*#(?!#)([^#\s].*)$", lines[0])
    if m:
        title = m.group(1).strip()
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines.pop(0)
    if title and lines:
        m2 = re.match(r"^\s*##\s+(.*)$", lines[0])
        if m2:
            h2 = m2.group(1).strip()
            if h2 == title or h2.replace(" ", "") == title.replace(" ", ""):
                lines = lines[1:]
                while lines and not lines[0].strip():
                    lines.pop(0)
    return "\n".join(lines) if lines else ""


def _renumber_ordered_list_runs(md_text: str) -> str:
    """After dropping empty `N.` lines, renumber each run so Pandoc emits <ol start=\"1\">."""
    lines = md_text.split("\n")
    out: list[str] = []
    i, n = 0, len(lines)
    while i < n:
        m = re.match(r"^(\s*)(\d+)\.\s+(.+)$", lines[i])
        if m and m.group(3).strip():
            indent = m.group(1)
            block: list[str] = [lines[i]]
            j = i + 1
            while j < n:
                if not lines[j].strip():
                    break
                m2 = re.match(r"^(\s*)(\d+)\.\s+(.+)$", lines[j])
                if m2 and m2.group(1) == indent and m2.group(3).strip():
                    block.append(lines[j])
                    j += 1
                else:
                    break
            for k, bl in enumerate(block, start=1):
                mm = re.match(r"^(\s*)\d+\.\s+(.+)$", bl)
                if mm:
                    out.append(f"{mm.group(1)}{k}. {mm.group(2)}")
            i = j
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def _markdown_list_line_has_no_visible_content(line: str) -> bool:
    """True if a bullet/ordered line has no readable body (empty link, ZWSP-only, `- ** **` → hr, etc.)."""
    m = re.match(r"^\s*[-*+]\s+(.*)$", line)
    if not m:
        m = re.match(r"^\s*\d+\.\s+(.*)$", line)
    if not m:
        return False
    rest = m.group(1).strip()
    if re.search(r"!\[[^\]]*\]\([^)]+\)", rest):
        return False
    rest = re.sub(r"\[([^\]]*)\]\([^)]+\)", lambda mm: mm.group(1) or "", rest)
    rest = html.unescape(rest)
    for ch in ("\u200b", "\u200c", "\u200d", "\ufeff", "\u2060"):
        rest = rest.replace(ch, "")
    rest = re.sub(r"[\u2000-\u200a\u202f\u205f\u3000]", " ", rest)
    rest = re.sub(r"[`*_~]+", "", rest)
    rest = " ".join(rest.split())
    if not rest:
        return True
    if re.fullmatch(r"[*_~.\s]+", rest):
        return True
    return False


def sanitize_empty_list_markers(md_text: str) -> str:
    """Remove lines that are only a list marker (common LLM glitch → empty bullets in WeChat)."""
    out_lines: list[str] = []
    for line in md_text.splitlines():
        if re.match(r"^\s*[-*+]\s*$", line):
            continue
        if re.match(r"^\s*\d+\.\s*$", line):
            continue
        if _markdown_list_line_has_no_visible_content(line):
            continue
        out_lines.append(line)
    return _renumber_ordered_list_runs("\n".join(out_lines))


def preprocess_markdown(md_text: str) -> str:
    """Insert blank line before lists glued to narrative (fixes Pandoc merging into one <p>)."""
    lines = md_text.split("\n")
    out: list[str] = []
    for i, line in enumerate(lines):
        if i > 0:
            prev = lines[i - 1]
            cur_m = re.match(r"^(\s{0,3})([-*+]|\d+\.)\s", line)
            prev_m = re.match(r"^(\s{0,3})([-*+]|\d+\.)\s", prev)
            prev_empty = not prev.strip()
            if cur_m and not prev_empty and not prev_m and prev.strip():
                if out and out[-1] != "":
                    out.append("")
        out.append(line)
    md_text = "\n".join(out)
    # "……干货：\n- item" -> real <ul>; without blank line Pandoc keeps bullets inside <p>.
    md_text = re.sub(r"([。：！？\.!?:])\n([-*+] )", r"\1\n\n\2", md_text)
    md_text = re.sub(r"([。：！？\.!?:])\n(\d+\.\s)", r"\1\n\n\2", md_text)
    return md_text


def pandoc_to_html(md_path: Path | None = None, *, md_text: str | None = None) -> str:
    if md_text is not None:
        result = subprocess.run(
            ["pandoc", "-f", "markdown", "-t", "html", "--standalone"],
            input=md_text,
            capture_output=True,
            text=True,
            timeout=30,
        )
    else:
        result = subprocess.run(
            ["pandoc", str(md_path), "-f", "markdown", "-t", "html", "--standalone"],
            capture_output=True,
            text=True,
            timeout=30,
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


def _li_inner_has_meaningful_content(inner: str) -> bool:
    """Whether <li> inner should be kept: visible text after tags, or an image (not hr-only / empty <a>)."""
    if re.search(r"<img\b", inner, re.I):
        return True
    t = html.unescape(inner)
    t = re.sub(r"<script[\s\S]*?</script>", "", t, flags=re.I)
    t = re.sub(r"<style[\s\S]*?</style>", "", t, flags=re.I)
    t = re.sub(r"<hr\b[^>]*/?>", " ", t, flags=re.I)
    plain = re.sub(r"<[^>]+>", " ", t)
    plain = re.sub(
        r"&nbsp;|&#160;|&#8203;|&#x200b;|&ZeroWidthSpace;|&#xfeff;|&#x2060;",
        " ",
        plain,
        flags=re.IGNORECASE,
    )
    for ch in ("\u200b", "\u200c", "\u200d", "\ufeff", "\u2060"):
        plain = plain.replace(ch, "")
    plain = re.sub(r"[\u2000-\u200a\u202f\u205f\u3000\u00a0]", " ", plain)
    plain = " ".join(plain.split())
    return bool(plain)


def flatten_li_newlines(html: str) -> str:
    """WeChat draft UI often treats newlines inside <li> as extra bullets; use single-line items.
    Only rewrites innermost <li> blocks so nested lists are not corrupted."""
    li_block = re.compile(r"(<li\b[^>]*>)([\s\S]*?)(</li>)", re.I)
    changed = True
    while changed:
        changed = False
        for m in li_block.finditer(html):
            inner = m.group(2)
            if re.search(r"<li\b", inner, re.I):
                continue
            new_inner = re.sub(r"[\r\n]+", " ", inner)
            new_inner = re.sub(r" {2,}", " ", new_inner).strip()
            if new_inner != inner:
                html = html[: m.start()] + m.group(1) + new_inner + m.group(3) + html[m.end() :]
                changed = True
                break
    return html


def remove_empty_list_items(html: str) -> str:
    """Remove <li> blocks with no visible content; innermost-first for nested lists."""
    li_block = re.compile(r"<li\b([^>]*)>([\s\S]*?)</li>", re.I)
    changed = True
    while changed:
        changed = False
        for m in li_block.finditer(html):
            inner = m.group(2)
            if re.search(r"<li\b", inner, re.I):
                continue
            if _li_inner_has_meaningful_content(inner):
                continue
            html = html[: m.start()] + html[m.end() :]
            changed = True
            break
    return html


def remove_empty_lists(html: str) -> str:
    """Drop <ul>/<ol> that have no <li> left (after empty-item removal)."""
    prev = None
    while prev != html:
        prev = html
        html = re.sub(r"<ul[^>]*>\s*</ul>", "", html, flags=re.IGNORECASE)
        html = re.sub(r"<ol[^>]*>\s*</ol>", "", html, flags=re.IGNORECASE)
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

    # <b> must not match <blockquote>, <br>, <body> — require > or whitespace after "b"
    html = re.sub(r"<b(?=[\s/>])([^>]*)>", b_repl, html, flags=re.IGNORECASE)
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

    md_raw = md_path.read_text(encoding="utf-8", errors="replace")
    md_raw = strip_title_from_markdown_body(md_raw)
    md_raw = sanitize_empty_list_markers(md_raw)
    md_raw = preprocess_markdown(md_raw)
    raw = pandoc_to_html(md_text=md_raw)
    if not raw:
        print("", end="")
        return
    body = extract_body(raw)
    body = fix_list_items_for_wechat(body)
    body = flatten_li_newlines(body)
    body = remove_empty_list_items(body)
    body = remove_empty_lists(body)
    foot_on = os.environ.get("WECHAT_MD_HTML_FOOTNOTES", "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )
    if foot_on:
        body = external_links_to_footnotes(body, accent_color=accent)
        body = remove_empty_list_items(body)
        body = remove_empty_lists(body)
    body = add_emphasis_inline_styles(body)
    out = add_inline_styles(body, styles)
    out = maybe_wrap_section(out)
    if len(out) > max_chars:
        out = out[:max_chars]
    print(out, end="")


if __name__ == "__main__":
    main()
