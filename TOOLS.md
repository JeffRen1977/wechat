# Tools for wechat_factory Pipeline

## Deep Search (duckduckgo_search / web_search / brave_search)
- Use to find **latest AI papers** (past 24–48 hours). Prefer sources: Nature, Lancet, arXiv, PubMed.
- Free option: OpenClaw built-in `web_search` (group:web) or DuckDuckGo MCP (`duckduckgo-search`); no API key required.
- Example intent: "Search for recent medical AI papers in Nature Medicine."

## Web Browser (browser / puppeteer)
- Use to **open a URL** and save full text or HTML to `wechat_factory/01_sources/web_snapshots/`.
- Filename format: `YYYY-MM-DD_<domain>_<slug>.html` or `.txt`.

## PDF Parser
- Read PDFs from `wechat_factory/01_sources/papers_pdf/`. Extract in order: abstract → methods → results → conclusion.
- If no PDF MCP is available, use `bash` to run: `scripts/extract_pdf_text.sh <path-to-pdf>` and then summarize the output.

## Filesystem (read, write, edit / MCP filesystem)
- **Read**: `wechat_factory/02_knowledge_base/*.md`, `wechat_factory/03_templates/*`.
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
- **Gemini (Nano Banana)**：When asked to generate cover or figures, run via **bash**: `./scripts/run-gemini-images.sh wechat_factory/04_output/YYYY-MM-DD/<PREFIX>_article.md`. This wrapper sources `~/.gemini-env` then runs the image script. Ensure `~/.gemini-env` contains `export GEMINI_API_KEY=...` (Agent does not load `~/.bashrc`). See IMPLEMENTATION.md 4.5.
