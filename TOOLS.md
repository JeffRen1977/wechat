# Tools for wechat_factory Pipeline

## Deep Search (duckduckgo_search / web_search / brave_search)
- **Default (daily editor) — 大众热点，非论文：** 每篇稿子的主素材必须是 **最新、较热门的 YouTube 视频**（教育 / 健康 / 财经各一），时间窗 **24–72 小时** 为佳；可再用搜索补 **主流新闻、科技媒体、社交平台** 上与该热点一致的报道（帮助核对事实、找钩子），**不要**把 arXiv / 学术论文当默认来源。检索示例：`site:youtube.com` +（教育|财经|健康|养生|理财）+（最新|本周|热门|热搜）. See `skills/wechat-daily-editor/SKILL.md`.
- **Popular news (same default):** e.g. Reuters/Bloomberg/央视/澎湃/36氪等**新闻向**关键词 + 领域词；用于佐证或补充 YouTube 话题，而非替代「有一支主视频」的设定（除非用户改规则）。
- **Papers (explicit opt-in only):** When the user asks for **papers /学术论文 / arXiv only**, then search latest domain papers (24–48h). Prefer Nature, Lancet, arXiv, PubMed.
- **YouTube**: Also e.g. channel name + `latest video`, `YouTube finance news this week`.
- Free option: OpenClaw built-in `web_search` (group:web) or DuckDuckGo MCP (`duckduckgo-search`); no API key required.
- Example intents (default pipeline): "Find a trending YouTube video in the past 48h about AI in personal finance, high views or buzz." / **Papers mode:** "Search recent medical AI papers in Nature Medicine."

## Web Browser (browser / puppeteer)
- Use to **open a URL** and save full text or HTML to `wechat_factory/01_sources/web_snapshots/`.
- **YouTube**: Open the watch URL; capture **title, description, transcript/captions** if shown on the page (or copy visible text). Save as `YYYY-MM-DD_<domain>_youtube_<slug>.txt` (e.g. `2026-03-20_EDU_youtube_khan.txt`). If no transcript, use description + chapter titles + on-page metadata.
- Filename format: `YYYY-MM-DD_<domain>_<slug>.html` or `.txt`.

## PDF Parser
- Read PDFs from `wechat_factory/01_sources/papers_pdf/`. Extract in order: abstract → methods → results → conclusion.
- If no PDF MCP is available, use `bash` to run: `scripts/extract_pdf_text.sh <path-to-pdf>` and then summarize the output.

## Filesystem (read, write, edit / MCP filesystem)
- **Read**: `wechat_factory/02_knowledge_base/*.md`, `wechat_factory/03_templates/*` (especially **`article_style.md`**, **`viral_titles.txt`**). Skills: `wechat-title-variants`, `wechat-image-director`, `wechat-article-formatter` (HTML theme + link footnotes), `wechat-editorial-review` (3-pass). **`IDENTITY.md`**: Emotional_Goal per vertical.
- **Write**: Save articles to `wechat_factory/04_output/YYYY-MM-DD/MED_article.md` (and FIN_, EDU_, etc.).
- **Create** daily folder: `wechat_factory/04_output/$(date +%Y-%m-%d)/`.
- **Update knowledge base (dedup)**: After saving an article, append one line under 「已解析论文 / 选题记录」, format: `YYYY-MM-DD | 标题 | 来源` — **来源写主 YouTube 链接或新闻 URL**；仅论文模式才写 arXiv 等。
- **Do not** delete or overwrite `02_knowledge_base` or `03_templates`.

## Ollama (local, optional)
- Use for **initial translation or dedup** of non-Chinese abstracts before sending to the main model (saves API cost). Call via `bash`: `scripts/ollama-translate.sh "English abstract text"` or pipe text into it.
- Model: default `llama3.3:70b`; override with `OLLAMA_MODEL=qwen2.5:7b` etc. if needed. Ensure the model is pulled: `ollama pull llama3.3:70b`.
- When to use: for non-Chinese paper abstracts, run through this script first, then pass the Chinese result to the main model for polish and article drafting.

## Image Gen
- Generate one cover image per article from title/abstract. Save to `wechat_factory/05_assets/images/` with name like `YYYY-MM-DD_MED_cover.png`.
- **Gemini (Nano Banana)**：When asked to generate cover or figures, run via **bash**: `./scripts/run-gemini-images.sh wechat_factory/04_output/YYYY-MM-DD/<PREFIX>_article.md`. Produces **1 cover + 2 content images** per article; prompts use **title + H2 section text** and **domain-locked palettes** (EDU/MED/FIN/INBOX) — see `scripts/gemini-gen-images.py`. Draft articles with **concrete nouns under each H2** for better fig relevance. This wrapper sources `~/.gemini-env` then runs the image script. Ensure `~/.gemini-env` contains `export GEMINI_API_KEY=...` (Agent does not load `~/.bashrc`). See IMPLEMENTATION.md 4.5.
- **All articles → images → WeChat draft**：Run `./scripts/generate-images-and-upload.sh [YYYY-MM-DD]` to generate 1 cover + 2 figs for each .md in that day’s output, then upload all to the WeChat draft box.
