---
name: wechat_daily_editor
description: Run the daily wechat_factory pipeline: search → read → title → write → save (5 articles).
---

# Wechat Daily Editor

When the user says "run today's wechat pipeline" or "执行今日公众号任务":
1. Create `wechat_factory/04_output/YYYY-MM-DD/` if not exists.
2. For each domain (MED, FIN, EDU, plus two more as configured): use Search to find one recent paper, fetch or download to 01_sources, parse (PDF or snapshot), then read 02_knowledge_base and 03_templates/viral_titles.txt and article_style.md, draft one article 1500–2000 chars, write to 04_output/YYYY-MM-DD/<DOMAIN>_article.md.
3. **Update knowledge base for dedup**: After each article, append one line to the domain's knowledge base under 「已解析论文」 in format: `日期 | 标题 | 来源`. Use `02_knowledge_base/medical_ai.md` for MED, `finance_ai.md` for FIN, `edu_ai.md` for EDU. This avoids reusing the same paper later.
4. Optionally generate cover images to 05_assets/images/.
5. Do not delete 02_knowledge_base or 03_templates.
