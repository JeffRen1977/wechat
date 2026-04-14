# Tools for wechat_factory Pipeline

## Deep Search (duckduckgo_search / web_search / brave_search)
- **Default (daily editor):** Find **YouTube** content on **latest trends** in **education, health, finance** — past **24–72 hours**, high relevance / buzz (e.g. `site:youtube.com` + 教育/财经/健康 + 最新/本周/热点). Pick videos per domain (EDU / MED-health / FIN). See `skills/wechat-daily-editor/SKILL.md`.
- **Papers (when user asks):** Latest AI / domain papers (24–48h). Prefer Nature, Lancet, arXiv, PubMed.
- **YouTube**: Also e.g. channel name + `latest video`, `YouTube finance news this week`.
- Free option: OpenClaw built-in `web_search` (group:web) or DuckDuckGo MCP (`duckduckgo-search`); no API key required.
- Example intent: "Search for recent medical AI papers in Nature Medicine."

## Web Browser (browser / puppeteer)
- Use to **open a URL** and save full text or HTML to `wechat_factory/01_sources/web_snapshots/`.
- **YouTube**: Open the watch URL; capture **title, description, transcript/captions** if shown on the page (or copy visible text). Save as `YYYY-MM-DD_<domain>_youtube_<slug>.txt` (e.g. `2026-03-20_EDU_youtube_khan.txt`). If no transcript, use description + chapter titles + on-page metadata.
- Filename format: `YYYY-MM-DD_<domain>_<slug>.html` or `.txt`.

## PDF Parser
- Read PDFs from `wechat_factory/01_sources/papers_pdf/`. Extract in order: abstract → methods → results → conclusion.
- If no PDF MCP is available, use `bash` to run: `scripts/extract_pdf_text.sh <path-to-pdf>` and then summarize the output.

## Filesystem (read, write, edit / MCP filesystem)
- **Read**: `wechat_factory/02_knowledge_base/*.md`, `wechat_factory/03_templates/*` (especially **`article_style.md`** for layout, SCQA, Action Items, CTA; **`viral_titles.txt`** for titles). Optional skills: `skills/wechat-title-variants/`, `skills/wechat-image-director/`.
- **Write**: Save articles to `wechat_factory/04_output/YYYY-MM-DD/MED_article.md` (and FIN_, EDU_, etc.).
- **Create** daily folder: `wechat_factory/04_output/$(date +%Y-%m-%d)/`.
- **Update knowledge base (dedup)**: After saving an article, append one line to the domain's `02_knowledge_base` file under the 「已解析论文」 section, format: `YYYY-MM-DD | 论文标题 | 来源` (e.g. medical_ai.md for MED, finance_ai.md for FIN, edu_ai.md for EDU).
- **Do not** delete or overwrite `02_knowledge_base` or `03_templates`.

## Ollama (local, optional)
- Use for **initial translation or dedup** of non-Chinese abstracts before sending to the main model (saves API cost). Call via `bash`: `scripts/ollama-translate.sh "English abstract text"` or pipe text into it.
- Model: default `llama3.3:70b`; override with `OLLAMA_MODEL=qwen2.5:7b` etc. if needed. Ensure the model is pulled: `ollama pull llama3.3:70b`.
- When to use: for non-Chinese paper abstracts, run through this script first, then pass the Chinese result to the main model for polish and article drafting.

## Image Gen
- Generate one cover image per article from title/abstract. Save to `wechat_factory/05_assets/images/` with name like `YYYY-MM-DD_MED_cover.png`.
- **Gemini (Nano Banana)**：When asked to generate cover or figures, run via **bash**: `./scripts/run-gemini-images.sh wechat_factory/04_output/YYYY-MM-DD/<PREFIX>_article.md`. Produces **1 cover + 2 content images** per article; prompts use **title + H2 section text** and **domain-locked palettes** (EDU/MED/FIN/INBOX) — see `scripts/gemini-gen-images.py`. Draft articles with **concrete nouns under each H2** for better fig relevance. This wrapper sources `~/.gemini-env` then runs the image script. Ensure `~/.gemini-env` contains `export GEMINI_API_KEY=...` (Agent does not load `~/.bashrc`). See IMPLEMENTATION.md 4.5.
- **All articles → images → WeChat draft**：Run `./scripts/generate-images-and-upload.sh [YYYY-MM-DD]` to generate 1 cover + 2 figs for each .md in that day’s output, then upload all to the WeChat draft box.
