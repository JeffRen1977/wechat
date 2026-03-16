---
name: wechat_from_inbox
description: From a link or pasted content (e.g. WhatsApp), create one WeChat draft article and upload it to the WeChat draft box.
---

# WeChat Draft from Link or Content

**Goal:** When the user sends **one link** or **pasted content** (e.g. via WhatsApp), create **one draft article** and **upload it to the WeChat draft box** so it appears in 微信公众平台 → 草稿箱.

1. **Create today's output folder** if needed: `wechat_factory/04_output/YYYY-MM-DD/`.

2. **Get the source**:
   - **If the user provided a URL**: Use browser/web tools to open the link and save the main text or HTML to `wechat_factory/01_sources/web_snapshots/` (e.g. `YYYY-MM-DD_inbox_<slug>.txt` or `.html`). If it is a PDF link, download to `wechat_factory/01_sources/papers_pdf/` and parse with `scripts/extract_pdf_text.sh` or equivalent.
   - **If the user pasted content**: Use that text directly as the source; optionally save a copy to `01_sources/web_snapshots/YYYY-MM-DD_inbox_paste.txt` for traceability.

3. **Read** `wechat_factory/03_templates/article_style.md` and `viral_titles.txt`, and relevant `02_knowledge_base/*.md` if the topic fits a domain (MED/FIN/EDU).

4. **Write one draft article** (1500–2000 chars, same style as daily pipeline) to  
   `wechat_factory/04_output/YYYY-MM-DD/INBOX_article.md`.  
   Use a single H1, H2/H3 structure, and follow `article_style.md`. Title ≤ 32 chars for WeChat.

5. **Generate cover + figures** (required for upload; WeChat API requires a cover per article):
   ```bash
   ./scripts/run-gemini-images.sh wechat_factory/04_output/YYYY-MM-DD/INBOX_article.md
   ```
   Produces `YYYY-MM-DD_INBOX_cover.png`, `_fig1.png`, `_fig2.png` in `05_assets/images/`. Ensure `~/.gemini-env` has `GEMINI_API_KEY`.

6. **Upload to WeChat draft box**:
   ```bash
   ./scripts/wechat-draft-upload.sh YYYY-MM-DD
   ```
   This uploads INBOX_article (with INBOX_cover) to 微信公众平台草稿箱. Ensure `~/.wechat-env` has `WECHAT_APPID` and `WECHAT_SECRET` (or `WECHAT_ACCESS_TOKEN`).

7. Do not delete `02_knowledge_base` or `03_templates`.

**Result:** One new draft in the WeChat draft box, created from the link or content the user sent.

## Trigger (e.g. WhatsApp)

- User sends a link → create one draft from that link and upload to WeChat draft box.
- User pastes content → create one draft from that content and upload to WeChat draft box.
- Explicit: "写一篇公众号文章，来源是这个链接/以下内容，并上传到草稿箱。"
