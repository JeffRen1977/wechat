---
name: wechat_daily_editor
description: Run the daily wechat_factory pipeline: search → read → title → write → save (5 articles).
---

# Wechat Daily Editor

When the user says "run today's wechat pipeline" or "执行今日公众号任务":
1. Create `wechat_factory/04_output/YYYY-MM-DD/` if not exists.
2. For each domain (MED, FIN, EDU, plus two more as configured): use Search to find one recent paper, fetch or download to 01_sources, parse (PDF or snapshot), then read 02_knowledge_base and 03_templates/viral_titles.txt and article_style.md, draft one article 1500–2000 chars, write to 04_output/YYYY-MM-DD/<DOMAIN>_article.md.
3. **Update knowledge base for dedup**: After each article, append one line to the domain's knowledge base under 「已解析论文」 in format: `日期 | 标题 | 来源`. Use `02_knowledge_base/medical_ai.md` for MED, `finance_ai.md` for FIN, `edu_ai.md` for EDU. This avoids reusing the same paper later.
4. For each article: generate **1 cover + 2 content images** (run `./scripts/run-gemini-images.sh wechat_factory/04_output/YYYY-MM-DD/<PREFIX>_article.md` for each .md). Saves to 05_assets/images/ as DATE_PREFIX_cover.png, DATE_PREFIX_fig1.png, DATE_PREFIX_fig2.png.
5. After images: upload to WeChat draft (run `./scripts/wechat-draft-upload.sh` with the date, or run `./scripts/generate-images-and-upload.sh` to do images for all articles then upload in one go).
6. Do not delete 02_knowledge_base or 03_templates.
