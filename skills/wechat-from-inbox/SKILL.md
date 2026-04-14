---
name: wechat_from_inbox
description: From a link or pasted content (e.g. WhatsApp), create one WeChat article, generate cover+figures, and upload to the WeChat draft box. Must run all steps including bash commands.
---

# WeChat Draft from Link or Content (WhatsApp pipeline)

**Goal:** When the user sends **one link** or **pasted content** (e.g. via WhatsApp), you must:

1. Create **one draft article** from that link or content.
2. **Generate pictures** for it (1 cover + 2 figures).
3. **Upload to the WeChat draft box** (微信公众平台 → 草稿箱).

Do **all** of the following steps in order. Do not skip the bash commands.

---

## Step 1: Create output folder

Create `wechat_factory/04_output/YYYY-MM-DD/` if it does not exist (use today’s date as YYYY-MM-DD).

---

## Step 2: Get the source

- **If the user provided a URL:** Use browser/web tools to open the link. Save the main text or HTML to `wechat_factory/01_sources/web_snapshots/` (e.g. `YYYY-MM-DD_inbox_<slug>.txt` or `.html`). **If the URL is YouTube** (`youtube.com`, `youtu.be`): capture **title, description, transcript/captions** (or visible page text + chapters); save as `YYYY-MM-DD_inbox_youtube_<slug>.txt`. If the link is a PDF, download to `wechat_factory/01_sources/papers_pdf/` and parse with `scripts/extract_pdf_text.sh` or equivalent. Use the fetched content as the source for writing the article.
- **If the user pasted content:** Use that text directly as the source. Optionally save a copy to `wechat_factory/01_sources/web_snapshots/YYYY-MM-DD_inbox_paste.txt`.

---

## Step 3: Read templates

Read `wechat_factory/03_templates/article_style.md`（含 WeChat 硬约束、评论区互动、外链脚注）and `viral_titles.txt`. Optionally `IDENTITY.md`, `skills/wechat-editorial-review/SKILL.md`, `skills/wechat-article-formatter/SKILL.md`. Use relevant `02_knowledge_base/*.md` if the topic fits MED/FIN/EDU.

---

## Step 4: Write the draft article

Write **one** article (**1500–2000 字**, same style as the daily pipeline) — **生动有趣、浅显易懂**，面向普通读者；遵循 `article_style.md`（黄金圈/SCQA、短段、引用块、3 条 Action Items、CTA、标题五选一注释）。Save to:

`wechat_factory/04_output/YYYY-MM-DD/INBOX_article.md`

- Use a **single H1** (title), then **H2/H3** for sections. Follow `article_style.md`. Title ≤ 32 characters (WeChat limit).
- **Add Markdown image placeholders** so the generated figures appear in the draft body. Use today’s date (YYYY-MM-DD) and the prefix `INBOX`. Example (place one or two in the middle of the article):
  - `![配图](wechat_factory/05_assets/images/YYYY-MM-DD_INBOX_fig1.png)`
  - `![配图](wechat_factory/05_assets/images/YYYY-MM-DD_INBOX_fig2.png)`
  Images will be created in the next step; the upload script will replace these with WeChat URLs.

---

## Step 5: Generate cover + figures (required)

You **must** run this command from the **workspace root** (the repo root containing `wechat_factory/` and `scripts/`):

```bash
./scripts/run-gemini-images.sh wechat_factory/04_output/YYYY-MM-DD/INBOX_article.md
```

Replace YYYY-MM-DD with the same date used in step 4. This creates:

- `wechat_factory/05_assets/images/YYYY-MM-DD_INBOX_cover.png`
- `wechat_factory/05_assets/images/YYYY-MM-DD_INBOX_fig1.png`
- `wechat_factory/05_assets/images/YYYY-MM-DD_INBOX_fig2.png`

Requires `~/.gemini-env` with `GEMINI_API_KEY`. If the command fails, report the error and do not skip.

---

## Step 6: Upload to WeChat draft box (required)

You **must** run this command from the **workspace root**:

```bash
./scripts/wechat-draft-upload.sh YYYY-MM-DD
```

Replace YYYY-MM-DD with the same date. This uploads `INBOX_article.md` (with cover and body images) to the WeChat Official Account draft box. Requires `~/.wechat-env` with `WECHAT_APPID` and `WECHAT_SECRET` (or `WECHAT_ACCESS_TOKEN`). If the command fails, report the error.

---

## Step 7: Confirm and reply

Do not delete `wechat_factory/02_knowledge_base` or `wechat_factory/03_templates`. Reply to the user (e.g. in WhatsApp) that the article was created from their link/content, images were generated, and the draft was uploaded to the WeChat draft box; they can check 微信公众平台 → 草稿箱.

---

## When to use this (trigger)

- User sends **a single link** → treat as “create one WeChat article from this link, add pictures, upload to draft.”
- User sends **pasted content** (long text) → treat as “create one WeChat article from this content, add pictures, upload to draft.”
- Explicit: “写一篇公众号文章，来源是这个链接/以下内容，并上传到草稿箱。”
