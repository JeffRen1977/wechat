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
- **Do not** delete or overwrite `02_knowledge_base` or `03_templates`.

## Image Gen (if configured)
- Generate one cover image per article from title/abstract. Save to `wechat_factory/05_assets/images/` with name like `YYYY-MM-DD_MED_cover.png`.
