---
name: wechat_daily_editor
description: Daily wechat_factory pipeline — exactly 3 articles (EDU, MED health, FIN). YouTube trends default; structured layout (SCQA, Why-How-What), title variants, image-friendly H2s. See article_style.md + skills/wechat-title-variants + wechat-image-director.
---

# Wechat Daily Editor

When the user says "run today's wechat pipeline" or "执行今日公众号任务":

1. Create `wechat_factory/04_output/YYYY-MM-DD/` if not exists.

1b. **Before writing:** Read `wechat_factory/03_templates/article_style.md` end-to-end (主编视角、黄金圈、SCQA、段落/引用/分割线/emoji 列表、5 标题备选、Action Items、CTA、自检). Use `skills/wechat-title-variants/SKILL.md` for the five title styles in an HTML comment before H1. Use `skills/wechat-image-director/SKILL.md` so each H2 has concrete nouns for fig1/fig2.

2. **Exactly three articles** — one file each (no `_2` unless user explicitly asks for more):
   - **Education:** `EDU_article.md`
   - **Health / 健康:** `MED_article.md` (health, wellness, 医学科普 — not necessarily “medical AI paper”)
   - **Finance / 财经:** `FIN_article.md`

3. **Source mode (default = YouTube + 最新趋势)**  
   Unless the user explicitly asks for **papers only** / **学术论文** / **arXiv**:
   - For **each** of the three domains above, find **one** recent, trending YouTube video (past **24–72 hours** when possible): education, health, finance respectively.
   - Open URLs with browser tools; save snapshots to `wechat_factory/01_sources/web_snapshots/` as `YYYY-MM-DD_EDU_youtube_<slug>.txt`, `_MED_youtube_...`, `_FIN_youtube_...`.
   - Capture title, description, transcript/captions (or description + chapters if no transcript).
   - **Tone & structure:** 生动有趣、浅显易懂；每篇按 **Why→How→What** 或 **SCQA** 组织（见 `article_style.md` 按 EDU/MED/FIN 表）；**情绪化开头**（故事/热点/设问）；**每段不超过约 3 行手机屏**；金句用 `>`；**3 条 Action Items** + 统一 **点赞/在看/关注** CTA。

4. **Papers mode** — only if user says **只要论文** / **papers only** / **学术来源**:  
   One recent paper per domain → same three filenames `EDU_article.md`, `MED_article.md`, `FIN_article.md`, same tone where possible.

5. **Knowledge base:** After each article, append `日期 | 标题 | 来源` to the matching `02_knowledge_base/*.md` (YouTube URL or paper link).

6. **Images + upload (avoid duplicates):**  
   - **If this task was started by `run-daily-wechat.sh` (cron / daily script):** Do **not** run `./scripts/wechat-draft-upload.sh` or `./scripts/generate-images-and-upload.sh`. The shell script’s **Step 2** already runs `generate-images-and-upload.sh` after you return—calling upload from the agent **again** creates **a second copy of each draft** in the WeChat draft box.  
   - You may run `./scripts/run-gemini-images.sh` for each of the three `.md` files **before** you finish (optional); Step 2 will still run image gen for all `.md` in that folder (may regenerate). Safer: **skip image/upload scripts in the agent** for this daily job and let Step 2 handle everything.  
   - **If the user ran the pipeline only from chat** (no `run-daily-wechat.sh`): after the three files exist, run `./scripts/run-gemini-images.sh` per file, then **once** `./scripts/generate-images-and-upload.sh YYYY-MM-DD` (or `./scripts/wechat-draft-upload.sh` if images already exist).

7. **Self-review:** Before finishing each file, run the checklist in `article_style.md`（主编自检）; revise if any item clearly fails.

8. Do not delete `02_knowledge_base` or `03_templates`.

## Trigger phrases

- Default: "执行今日公众号任务", "run today's wechat pipeline" → **3 篇**，EDU + MED + FIN.
- Papers only: "今日只要论文", "use papers only today".
