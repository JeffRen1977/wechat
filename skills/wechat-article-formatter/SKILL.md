---
name: wechat_article_formatter
description: WeChat-oriented layout — hooks, visual rhythm, footnote links, optional green theme HTML; pairs with scripts/md_to_wechat_html.py and article_style.md.
---

# WeChat Article Formatter（公众号排版与 HTML约定）

借鉴成熟「Markdown → 公众号 HTML」思路：**内联样式**、**配色主题**、**外链不下沉到正文可点链接**（转文末参考列表），避免 AI 稿显得「外链乱飞、不像公号」。

## 1. 写作侧（Markdown）

- 遵循 `wechat_factory/03_templates/article_style.md` 中的 **WeChat 风格硬约束**（钩子、视觉断点、emoji、评论区互动）。
- **外链**：正文中照常写 `[可见文字](https://...)`。发布流水线里 **`md_to_wechat_html.py` 会将 http(s) 链接转为文内 `[n]` 角标 + 文末「参考与链接」**，无需手写 HTML。
- **不要**在 Markdown 里塞 `<style>` 或外链 CSS；公众号会丢。
- 若需强调区块，优先 **`>` 引用块** 与 **加粗**，少用自定义 HTML（除非你知道微信后台会保留该标签）。

## 2. 生成 HTML 侧（脚本）

- 转换命令：`python3 scripts/md_to_wechat_html.py <文章.md> [--max-chars 19000]`
- **绿色系主题**（可选，对标常见「公号绿」）：  
  `WECHAT_MD_HTML_THEME=green python3 scripts/md_to_wechat_html.py ...`  
 默认 `minimal` 为现有灰蓝标题 + 灰引用条。
- **外层留白**（可选）：`WECHAT_MD_HTML_WRAP_SECTION=1` 时在正文外包一层带 `padding` 的 `<section>`（部分后台可保留）。

## 3. Agent 何时用本 Skill

- 用户关心「排版像不像公众号」「链接怎么处理」时，说明上述约定。
- 改模板或改 `md_to_wechat_html.py` 后，提醒用户同步 OpenClaw workspace 与 `~/.wechat-env` 环境（若用 cron）。

Do not delete `wechat_factory/02_knowledge_base` or `03_templates`.
