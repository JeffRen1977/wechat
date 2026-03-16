---
name: wechat_from_inbox
description: Generate one WeChat article from a user-provided link or pasted content (e.g. from WhatsApp).
---

# WeChat Article from Link or Content

When the user sends **one link** or **pasted content** (e.g. via WhatsApp or chat) and wants a WeChat article from it:

1. **Create today's output folder** if needed: `wechat_factory/04_output/YYYY-MM-DD/`.

2. **Get the source**:
   - **If the user provided a URL**: Use browser/web tools to open the link and save the main text or HTML to `wechat_factory/01_sources/web_snapshots/` (e.g. `YYYY-MM-DD_inbox_<slug>.txt` or `.html`). If it is a PDF link, download to `wechat_factory/01_sources/papers_pdf/` and parse with `scripts/extract_pdf_text.sh` or equivalent.
   - **If the user pasted content**: Use that text directly as the source; optionally save a copy to `01_sources/web_snapshots/YYYY-MM-DD_inbox_paste.txt` for traceability.

3. **Read** `wechat_factory/03_templates/article_style.md` and `viral_titles.txt`, and relevant `02_knowledge_base/*.md` if the topic fits a domain (MED/FIN/EDU).

4. **Write one article** (1500–2000 chars, same style as daily pipeline) to  
   `wechat_factory/04_output/YYYY-MM-DD/INBOX_article.md`.  
   Use a single H1, H2/H3 structure, and follow `article_style.md`. Title ≤ 32 chars for WeChat.

5. **Optional — images and upload**:
   - Generate cover + 2 figures:  
     `./scripts/run-gemini-images.sh wechat_factory/04_output/YYYY-MM-DD/INBOX_article.md`  
     (produces `YYYY-MM-DD_INBOX_cover.png`, `_fig1.png`, `_fig2.png` in `05_assets/images/`).
   - Upload to WeChat draft:  
     `./scripts/wechat-draft-upload.sh YYYY-MM-DD`  
     (includes INBOX_article if INBOX_cover exists).

6. Do not delete `02_knowledge_base` or `03_templates`.

## Trigger phrases (for OpenClaw / WhatsApp integration)

- User sends a link: treat as "generate one WeChat article from this link."
- User pastes long text: treat as "generate one WeChat article from this content."
- Explicit: "写一篇公众号文章，来源是这个链接/以下内容。"
