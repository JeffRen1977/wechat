---
name: wechat_title_variants
description: Generate five WeChat title variants (suspense, benefit, contrast, warning, curiosity) before choosing H1; use with article_style.md.
---

# WeChat Title Variants（五型标题）

When drafting any `*_article.md` for wechat_factory:

1. Read `wechat_factory/03_templates/viral_titles.txt` for patterns.
2. For the same core topic, draft **exactly 5** candidate titles in this order:
   - **悬念型** — 留白、钩子（「到底……」「很少有人知道……」）
   - **收益型** — 读者获得感（「读完你会……」「3 分钟搞懂……」）
   - **对比型** — 对立或反差（「A 和 B」「过去 vs 现在」）
   - **警示型** — 风险与共情（「别忽视……」「再忙也要看……」）
   - **好奇型** — 趋势与热点（「为什么最近都在聊……」）
3. Put them in an HTML comment at the **top** of the Markdown (before H1), then set **one** line as `# …` (≤32 characters for WeChat).
4. Do not output five different H1s — only **one** H1 in the final file.

Example comment block:

```markdown
<!-- 标题备选：1.悬念：… 2.收益：… 3.对比：… 4.警示：… 5.好奇：… | 选用：3 -->
# 最终标题（≤32字）
```

Trigger: user asks for title options, 「多几个标题」, or you are starting EDU/MED/FIN/INBOX drafts.
