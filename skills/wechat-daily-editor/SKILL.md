---
name: wechat_daily_editor
description: Daily wechat_factory pipeline — exactly 3 articles (EDU, MED health, FIN). Default source is YouTube latest trends; tone 生动有趣、浅显易懂. Papers only when user asks.
---

# Wechat Daily Editor

When the user says "run today's wechat pipeline" or "执行今日公众号任务":

1. Create `wechat_factory/04_output/YYYY-MM-DD/` if not exists.

2. **Exactly three articles** — one file each (no `_2` unless user explicitly asks for more):
   - **Education:** `EDU_article.md`
   - **Health / 健康:** `MED_article.md` (health, wellness, 医学科普 — not necessarily “medical AI paper”)
   - **Finance / 财经:** `FIN_article.md`

3. **Source mode (default = YouTube + 最新趋势)**  
   Unless the user explicitly asks for **papers only** / **学术论文** / **arXiv**:
   - For **each** of the three domains above, find **one** recent, trending YouTube video (past **24–72 hours** when possible): education, health, finance respectively.
   - Open URLs with browser tools; save snapshots to `wechat_factory/01_sources/web_snapshots/` as `YYYY-MM-DD_EDU_youtube_<slug>.txt`, `_MED_youtube_...`, `_FIN_youtube_...`.
   - Capture title, description, transcript/captions (or description + chapters if no transcript).
   - **Tone:** 生动有趣、浅显易懂 — 像跟朋友讲「最近网上在聊什么」；专业词用人话一句带过；可加设问、类比；保留来源链接供知识库记录。

4. **Papers mode** — only if user says **只要论文** / **papers only** / **学术来源**:  
   One recent paper per domain → same three filenames `EDU_article.md`, `MED_article.md`, `FIN_article.md`, same tone where possible.

5. **Knowledge base:** After each article, append `日期 | 标题 | 来源` to the matching `02_knowledge_base/*.md` (YouTube URL or paper link).

6. **Images + upload (avoid duplicates):**  
   - **If this task was started by `run-daily-wechat.sh` (cron / daily script):** Do **not** run `./scripts/wechat-draft-upload.sh` or `./scripts/generate-images-and-upload.sh`. The shell script’s **Step 2** already runs `generate-images-and-upload.sh` after you return—calling upload from the agent **again** creates **a second copy of each draft** in the WeChat draft box.  
   - You may run `./scripts/run-gemini-images.sh` for each of the three `.md` files **before** you finish (optional); Step 2 will still run image gen for all `.md` in that folder (may regenerate). Safer: **skip image/upload scripts in the agent** for this daily job and let Step 2 handle everything.  
   - **If the user ran the pipeline only from chat** (no `run-daily-wechat.sh`): after the three files exist, run `./scripts/run-gemini-images.sh` per file, then **once** `./scripts/generate-images-and-upload.sh YYYY-MM-DD` (or `./scripts/wechat-draft-upload.sh` if images already exist).

7. Do not delete `02_knowledge_base` or `03_templates`.

## Trigger phrases

- Default: "执行今日公众号任务", "run today's wechat pipeline" → **3 篇**，EDU + MED + FIN.
- Papers only: "今日只要论文", "use papers only today".
