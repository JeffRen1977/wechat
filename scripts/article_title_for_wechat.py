#!/usr/bin/env python3
"""Print first Markdown H1 for WeChat draft title: UTF-8 safe, max 32 Unicode chars.
Usage: python3 article_title_for_wechat.py <article.md> [fallback_if_no_h1]
Avoids bash `head -c 32` which cuts multi-byte UTF-8 and produces / ? in titles."""
from __future__ import annotations

import sys
from pathlib import Path

WECHAT_TITLE_MAX = 32


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    fallback = sys.argv[2] if len(sys.argv) > 2 else (path.stem if path else "")
    if not path or not path.is_file():
        print(fallback, end="")
        return
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("# "):
            t = line[2:].strip()
            if not t:
                print(fallback, end="")
                return
            if len(t) > WECHAT_TITLE_MAX:
                t = t[:WECHAT_TITLE_MAX]
            print(t, end="")
            return
    print(fallback, end="")


if __name__ == "__main__":
    main()
