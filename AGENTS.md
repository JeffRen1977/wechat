# Agents in this workspace

- **main** (default agent): Runs the daily wechat_factory pipeline (5 articles). Workspace paths are relative to this directory; output goes to `wechat_factory/04_output/YYYY-MM-DD/`.

**Image generation (cover/figures):** There is no separate MCP image tool. To generate images, run via **bash**: `./scripts/run-gemini-images.sh wechat_factory/04_output/YYYY-MM-DD/PREFIX_article.md` (the wrapper sources `~/.gemini-env` then runs the Python script). Output goes to `wechat_factory/05_assets/images/`. For a one-off test (e.g. 5.2_test_cover.png), run the wrapper with any existing article path; it creates cover and fig1/fig2. If the script prints “Set GEMINI_API_KEY”, the user must add `export GEMINI_API_KEY=...` to `~/.gemini-env`.
