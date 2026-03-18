# Agents in this workspace

- **main** (default agent): Runs the daily wechat_factory pipeline (5 articles). Workspace paths are relative to this directory; output goes to `wechat_factory/04_output/YYYY-MM-DD/`.

**WhatsApp / link or pasted content:** When the user sends **one link** or **pasted content** (e.g. via WhatsApp), the agent must follow the **wechat-from-inbox** skill: (1) fetch the link or use the content, (2) write one article to `wechat_factory/04_output/YYYY-MM-DD/INBOX_article.md`, (3) run `./scripts/run-gemini-images.sh .../INBOX_article.md` to generate cover + 2 figures, (4) run `./scripts/wechat-draft-upload.sh YYYY-MM-DD` to upload to the WeChat draft box. See `skills/wechat-from-inbox/SKILL.md`. To test from the CLI without WhatsApp: `./scripts/run-inbox-wechat.sh <URL or path to text file>`.

**Image generation (cover/figures):** There is no separate MCP image tool. To generate images, run via **bash**: `./scripts/run-gemini-images.sh wechat_factory/04_output/YYYY-MM-DD/PREFIX_article.md` (the wrapper sources `~/.gemini-env` then runs the Python script). Output goes to `wechat_factory/05_assets/images/`. For a one-off test (e.g. 5.2_test_cover.png), run the wrapper with any existing article path; it creates cover and fig1/fig2. If the script prints “Set GEMINI_API_KEY”, the user must add `export GEMINI_API_KEY=...` to `~/.gemini-env`.
