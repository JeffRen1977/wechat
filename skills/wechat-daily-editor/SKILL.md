---
name: wechat_daily_editor
description: Run the daily wechat_factory pipeline: search → read → title → write → save (5 articles).
---

# Wechat Daily Editor

When the user says "run today's wechat pipeline" or "执行今日公众号任务":
1. Create `wechat_factory/04_output/YYYY-MM-DD/` if not exists.
2. For each domain (MED, FIN, EDU, plus two more as configured): use Search to find one recent paper, fetch or download to 01_sources, parse (PDF or snapshot), then read 02_knowledge_base and 03_templates/viral_titles.txt and article_style.md, draft one article 1500–2000 chars, write to 04_output/YYYY-MM-DD/<DOMAIN>_article.md.
3. Optionally generate cover images to 05_assets/images/.
4. Do not delete 02_knowledge_base or 03_templates.
