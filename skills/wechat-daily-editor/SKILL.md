---
name: wechat_daily_editor
description: Daily wechat_factory —3 articles (EDU, MED, FIN). Default sources: latest popular YouTube + news buzz, NOT academic papers unless user asks. SCQA, hooks, footnotes, title variants, image director, editorial review.
---

# Wechat Daily Editor

When the user says "run today's wechat pipeline" or "执行今日公众号任务":

1. Create `wechat_factory/04_output/YYYY-MM-DD/` if not exists.

1b. **Before writing:** Read `wechat_factory/03_templates/article_style.md` end-to-end (含 **WeChat 风格硬约束**、Emotional_Goal、外链脚注约定). Use `skills/wechat-title-variants/SKILL.md` (五型标题注释)、`skills/wechat-image-director/SKILL.md` (情绪→画面 brief)、`skills/wechat-article-formatter/SKILL.md` (HTML/绿色主题/脚注逻辑)、`skills/wechat-editorial-review/SKILL.md` (事实→人设→爆款 三轮). Skim `IDENTITY.md` for 情绪锚点.

2. **Exactly three articles** — one file each (no `_2` unless user explicitly asks for more):
   - **Education:** `EDU_article.md`
   - **Health / 健康:** `MED_article.md` (health, wellness, 医学科普 — not necessarily “medical AI paper”)
   - **Finance / 财经:** `FIN_article.md`

3. **Source mode (default = 热门 YouTube + 大众新闻，不要默认论文)**  
   Unless the user explicitly asks for **papers only** / **学术论文** / **arXiv**:
   - For **each** of the three domains, pick **one primary source: a recent, popular YouTube video** (past **24–72 hours** when possible; prefer high engagement / clearly “trending” in that niche: EDU, health/wellness, finance).
   - **Secondary (recommended):** use search to find **1–2 mainstream news or tech-media articles** that discuss the same topic or same event—**for context and fact-checking**, not to replace the YouTube-first angle. This matches “what people are seeing in the news,” not journal papers.
   - **Do not** default to arXiv, PubMed, or PDF papers as the main story; academic citations are **out of scope** unless in **Papers mode**.
   - Open URLs with browser tools; save snapshots to `wechat_factory/01_sources/web_snapshots/` as `YYYY-MM-DD_EDU_youtube_<slug>.txt`, `_MED_youtube_...`, `_FIN_youtube_...` (and optional `YYYY-MM-DD_<domain>_news_<slug>.txt` for news pages).
   - Capture title, description, transcript/captions (or description + chapters if no transcript).
   - **Tone & structure:** 生动有趣、浅显易懂；每篇按 **Why→How→What** 或 **SCQA** 组织（见 `article_style.md` 按 EDU/MED/FIN 表）；**情绪化开头**（故事/热点/设问）；**每段不超过约 3 行手机屏**；金句用 `>`；**3 条 Action Items** + 统一 **点赞/在看/关注** CTA。
   - **Lists:** Every `-` / `1.` line must have text **on the same line or immediately on the next line** (no blank line in between). Never emit empty list markers — they become blank bullets in WeChat.
   - **正文配图（必须）**：每篇在 **两个** 合适的 `##` 小节末各插入一行 Markdown 图（与 `run-gemini-images.sh` 产出文件名一致），否则草稿里**只有封面、正文无图**：  
     `![配图](wechat_factory/05_assets/images/YYYY-MM-DD_EDU_fig1.png)` 与 `..._fig2.png`（MED/FIN 则换前缀）。日期用当天，`YYYY-MM-DD` 与 `EDU`/`MED`/`FIN` 与文件名一致。若漏写，`generate-images-and-upload.sh` 会在上传前用脚本自动补插，但**主动写好位置**阅读体验更好。

4. **Papers mode** — only if user says **只要论文** / **papers only** / **学术来源**:  
   One recent paper per domain → same three filenames `EDU_article.md`, `MED_article.md`, `FIN_article.md`, same tone where possible.

5. **Knowledge base:** After each article, append `日期 | 标题 | 来源` to the matching `02_knowledge_base/*.md` — **默认来源填主 YouTube 链接**（可附新闻 URL）；论文模式才填论文链接。

6. **Images + upload (avoid duplicates):**  
   - **If this task was started by `run-daily-wechat.sh` (cron / daily script):** Do **not** run `./scripts/wechat-draft-upload.sh` or `./scripts/generate-images-and-upload.sh`. The shell script’s **Step 2** already runs `generate-images-and-upload.sh` after you return—calling upload from the agent **again** creates **a second copy of each draft** in the WeChat draft box.  
   - You may run `./scripts/run-gemini-images.sh` for each of the three `.md` files **before** you finish (optional); Step 2 will still run image gen for all `.md` in that folder (may regenerate). Safer: **skip image/upload scripts in the agent** for this daily job and let Step 2 handle everything.  
   - **If the user ran the pipeline only from chat** (no `run-daily-wechat.sh`): after the three files exist, run `./scripts/run-gemini-images.sh` per file, then **once** `./scripts/generate-images-and-upload.sh YYYY-MM-DD` (or `./scripts/wechat-draft-upload.sh` if images already exist).

7. **Self-review:** Before finishing each file, run the checklist in `article_style.md`（主编自检）; revise if any item clearly fails.

8. Do not delete `02_knowledge_base` or `03_templates`.

## Trigger phrases

- Default: "执行今日公众号任务", "run today's wechat pipeline" → **3 篇**，EDU + MED + FIN.
- Papers only: "今日只要论文", "use papers only today".
