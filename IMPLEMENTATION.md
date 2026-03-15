# Step-by-Step Implementation Guide — WeChat 公众号自动化

本文档基于 [DESIGN.md](./DESIGN.md)，给出**分阶段实现步骤**、**OpenClaw 技能与工具说明**、**测试方案**以及**与 OpenClaw 的协作方式**。每个 Skill/工具都会说明其在 OpenClaw 中的**功能与用途**。

---

## Part A: Implementation Phases (Step-by-Step)

以下每个 Phase 都附带**详细设置步骤**与**可复制执行的命令/代码**。

---

### Phase 0: Prerequisites

| Step | Action | Purpose |
|------|--------|---------|
| 0.1 | 安装并配置 OpenClaw（Gateway + 至少一个 Agent） | 多智能体运行环境 |
| 0.2 | 准备 Claude API（或兼容端点）与 Ollama 本地 | 认知/创作用云端模型 + 初筛/翻译用本地模型 |
| 0.3 | 初始化 Git 仓库于 `wechat/` 或 `~/.openclaw/workspace`（若 workspace 指向此处） | 版本控制与回滚 |

#### Phase 0 详细设置

**0.1 安装 OpenClaw**

- 安装方式（任选其一）：
  - **npm（全局）：**
    ```bash
    npm install -g openclaw
    ```
  - **从源码：**
    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw && npm install && npm run build
    ```
- 初始化配置与 workspace：
  ```bash
  openclaw setup
  # 或按提示：openclaw onboard / openclaw configure
  ```
- 确认 Gateway 可启动：
  ```bash
  openclaw gateway start
  # 或 openclaw start（视版本而定）
  ```
- **单 Agent（默认）**：无需 `agents.list`。OpenClaw 使用 `agents.defaults`，默认 agentId 为 `main`，workspace 取 `agents.defaults.workspace`（你已设为 wechat 目录）。
- **多 Agent**：在 `~/.openclaw/openclaw.json` 中增加 `agents.list` 数组，至少保留一个 Agent；每个元素需有 `id`、`workspace`，可指定其一为 `default: true`。见下方「Agent 配置说明」。

**0.2 云端模型 API（OpenAI / Gemini / Claude）与 Ollama**

可使用 **OpenAI**、**Google Gemini** 或 Claude 作为主模型。**安全**：一律用环境变量或 `~/.openclaw/.env` 存 Key，不要写进 `openclaw.json` 或提交到 Git；若 Key 曾泄露，请到对应控制台轮换。

- **OpenAI：**
  - 在 `~/.openclaw/openclaw.json` 的 `auth.profiles` 中已有 `openai:default` 时，Key 可通过环境变量或 `~/.openclaw/credentials/` 提供（具体以 OpenClaw 文档为准）。
  - 环境变量方式（推荐）：
    ```bash
    export OPENAI_API_KEY="sk-proj-..."
    ```
  - 在 `agents.defaults.model.primary` 中指定模型，例如：`"openai/gpt-5.1-codex"` 或 `"openai/gpt-4o"`。

- **Google Gemini：**
  - 从 [Google AI Studio](https://aistudio.google.com/) 获取 API Key，用环境变量：
    ```bash
    export GEMINI_API_KEY="AIza..."
    # 或部分版本使用：export GOOGLE_API_KEY="AIza..."
    ```
  - 在 `openclaw.json` 中配置 Google provider（若尚未配置），并将默认模型改为 Gemini，例如：
    ```json
    "agents": {
      "defaults": {
        "model": { "primary": "google/gemini-2.0-flash" }
      }
    }
    ```
  - 常见模型名：`google/gemini-2.0-flash`、`google/gemini-1.5-pro`、`google/gemini-1.5-flash`。

- **Claude（可选）：**
  - 若使用 Anthropic，设置 `export ANTHROPIC_API_KEY="sk-ant-..."`，并在配置中指定 `anthropic/claude-sonnet-4-5` 等。

- **可选：一次设置多个 Key（`.env`）**  
  在 `~/.openclaw/.env` 中写（勿提交到 Git，`chmod 600 ~/.openclaw/.env`）：
  ```bash
  OPENAI_API_KEY=sk-proj-...
  GEMINI_API_KEY=AIza...
  ```
  OpenClaw 若支持从该文件加载，启动时会自动注入；否则在 shell 配置（如 `~/.bashrc`）里 `export` 上述变量。

- **Ollama（本地，用于初筛/翻译）：**
  - 安装：
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
  - 拉取模型（用于初筛/翻译）：
    ```bash
    ollama pull llama3.3:70b
    # 或 ollama pull qwen2.5:7b（机器资源较小时）
    ```
  - 验证：
    ```bash
    ollama run llama3.3:70b "Translate to Chinese: Hello world"
    ```

**Agent 配置说明（单 Agent vs 多 Agent）**

- **仅用默认一个 Agent（当前推荐）**：不写 `agents.list`，只保留 `agents.defaults`。例如你当前配置：
  ```json
  "agents": {
    "defaults": {
      "workspace": "/home/renjeff/Documents/projects/wechat",
      "model": { "primary": "openai/gpt-5.1-codex" }
    }
  }
  ```
  此时 OpenClaw 使用 agentId `main`，workspace 即 wechat 目录；无需再配 `agents.list`。

- **多 Agent（例如再增加 wechat-editor）**：增加 `agents.list`，并可选 `bindings` 做路由。示例：
  ```json
  "agents": {
    "defaults": {
      "workspace": "/home/renjeff/.openclaw/workspace",
      "model": { "primary": "openai/gpt-5.1-codex" }
    },
    "list": [
      {
        "id": "main",
        "default": true,
        "workspace": "/home/renjeff/.openclaw/workspace"
      },
      {
        "id": "wechat-editor",
        "name": "Wechat Editor",
        "workspace": "/home/renjeff/Documents/projects/wechat"
      }
    ]
  }
  ```
  至少保留一个 Agent；若需把某通道/账号绑定到 wechat-editor，再在顶层增加 `bindings`（见 [OpenClaw Multi-Agent](https://docs.openclaw.ai/concepts/multi-agent)）。

**0.3 Git 仓库**

- 若 workspace 即为本 wechat 项目目录（推荐，即 `/home/renjeff/Documents/projects/wechat`）：
  ```bash
  cd /home/renjeff/Documents/projects/wechat
  git init
  git add . && git commit -m "Initial commit"
  git remote add origin https://github.com/JeffRen1977/wechat.git
  git push -u origin main
  ```
- 若 workspace 为 `~/.openclaw/workspace`（需先将 wechat_factory 复制或软链到该目录）：
  ```bash
  cd ~/.openclaw/workspace
  git init
  git add AGENTS.md SOUL.md TOOLS.md wechat_factory/ memory/ 2>/dev/null || true
  git add -A && git commit -m "Add workspace and wechat_factory"
  git remote add origin <your-private-repo-url>
  git push -u origin main
  ```

---

### Phase 1: Workspace & wechat_factory 对接

| Step | Action | Purpose |
|------|--------|---------|
| 1.1 | 确定 workspace 根目录：`~/.openclaw/workspace` 或项目内 `wechat/` | 所有文件类工具的相对路径以此为基准 |
| 1.2 | 若 workspace 在 `~/.openclaw/workspace`：将 `wechat_factory` 复制或软链到 `~/.openclaw/workspace/wechat_factory` | 让 Agent 能通过相对路径访问 01_sources～05_assets |
| 1.3 | 若 workspace 即 `wechat/`：则 `wechat_factory/` 已在项目内，无需迁移 | 开发与生产可共用同一目录 |
| 1.4 | 在 workspace 根目录确保存在 `AGENTS.md`、`SOUL.md`、`TOOLS.md`（OpenClaw 约定） | 会话加载与工具可见性 |

#### Phase 1 详细设置

**1.1 确定 workspace 根目录**

- 查看当前配置：
  ```bash
  cat ~/.openclaw/openclaw.json | grep -A2 workspace
  ```
- 常见两种选择：
  - **A**：`~/.openclaw/workspace`（OpenClaw 默认）
  - **B**：项目目录，例如 `/home/renjeff/Documents/projects/wechat`
- 若选 B，在 `openclaw.json` 中设置（具体键名以官方文档为准）：
  ```json
  {
    "agent": { "workspace": "/home/renjeff/Documents/projects/wechat" }
  }
  ```
  或对指定 Agent 设置：
  ```json
  {
    "agents": {
      "list": [
        { "id": "wechat-editor", "workspace": "/home/renjeff/Documents/projects/wechat" }
      ]
    }
  }
  ```

**1.2 将 wechat_factory 放入 ~/.openclaw/workspace（仅当 workspace 为 A 时）**

- 复制（独立副本）：
  ```bash
  cp -r /home/renjeff/Documents/projects/wechat/wechat_factory ~/.openclaw/workspace/
  ```
- 或软链（与项目同步）：
  ```bash
  ln -s /home/renjeff/Documents/projects/wechat/wechat_factory ~/.openclaw/workspace/wechat_factory
  ```

**1.3 workspace 即 wechat 时**

- 无需操作；Agent 工作目录已是 `wechat/`，相对路径 `wechat_factory/04_output/` 即项目内路径。

**1.4 创建 OpenClaw 约定的 workspace 引导文件**

在 **workspace 根目录**（即 `~/.openclaw/workspace` 或 `wechat/`）创建以下文件（若不存在）：

- **AGENTS.md**（简要说明本 workspace 的 Agent 角色与 wechat 任务）：
  ```markdown
  # Agents in this workspace

  - **main** (default agent): Runs the daily wechat_factory pipeline (5 articles). Workspace paths are relative to this directory; output goes to `wechat_factory/04_output/YYYY-MM-DD/`.
  ```

- **SOUL.md**（Agent 人格与行为边界，可按需精简）：
  ```markdown
  # Soul

  You are a content assistant for the wechat_factory pipeline. Stay on task: discover papers, extract insights, draft articles, and write to wechat_factory. Do not delete 02_knowledge_base or 03_templates. Use TOOLS.md for tool usage.
  ```

- **TOOLS.md**（本 Phase 可先写占位，Phase 2 会补全）：
  ```markdown
  # Tools for wechat_factory

  - **Filesystem**: Read/write under `wechat_factory/`. Create `04_output/YYYY-MM-DD/`, write `MED_article.md` etc. Do not delete knowledge_base or templates.
  - (Search, Browser, PDF, Image Gen will be documented in Phase 2.)
  ```

若 OpenClaw 已通过 `openclaw setup` 生成过这些文件，只需在原有基础上**追加** wechat 相关段落即可。

---

### Phase 2: MCP Skills & Tools 配置

| Step | Action | Purpose |
|------|--------|---------|
| 2.1 | 在 `~/.openclaw/openclaw.json` 中仅配置 `tools`（不添加 `mcpServers`），见下方 2.1 详细 | 为 Agent 提供搜索、文件、浏览器等内置能力 |
| 2.2 | 在 workspace 的 `TOOLS.md` 中列出本项目会用到的工具及用途（给 Agent 看的说明） | 引导 Agent 在正确场景调用正确工具 |
| 2.3 | 可选：在 `workspace/skills/` 下为 wechat 流水线写专用 Skill（如 `wechat-daily-editor`），在 SKILL.md 中引用 MCP 工具与步骤 | 把「每日 5 篇」流程固化为可复用技能 |
| 2.4 | 重启 Gateway；若已配置 MCP，执行 `openclaw mcp list` 校验；否则确认 `tools.allow` 含 `group:web` 等即可 | 确保工具在运行时可用 |

#### Phase 2 详细设置

**2.1 编辑 ~/.openclaw/openclaw.json，仅配置 tools（不添加 mcpServers）**

当前我们**已移除** `mcpServers`：OpenClaw 2026.3.13 不识别顶层键 `mcpServers`，会报 `Unrecognized key: "mcpServers"` 并拒绝启动，因此**不要在** openclaw.json 中添加 `mcpServers`。只配置 **tools**，使用内置能力即可。

**本方案使用：**

- **搜索**：内置 `group:web` → `web_search`、`web_fetch`（免费，无需 API Key）。
- **文件与运行**：`group:fs`、`group:runtime`、`browser`，由 OpenClaw 自带。

在配置文件中**仅**加入或合并以下 `tools` 块（勿添加 `mcpServers`）：

```json
{
  "tools": {
    "profile": "coding",
    "allow": ["group:fs", "group:web", "group:runtime", "browser"]
  }
}
```

说明：

- **group:fs**：读写 workspace（含 wechat_factory）。
- **group:web**：`web_search`、`web_fetch`，用于查论文与抓取页面。
- **group:runtime**：`exec`/`bash`，用于运行 `scripts/extract_pdf_text.sh` 等。
- **browser**：内置浏览器工具，抓取网页。
- **PDF**：无 PDF MCP 时，用 `bash` 调用 `scripts/extract_pdf_text.sh <path-to-pdf>`，再对 stdout 做总结；见 2.3。
- **若将来你的 OpenClaw 版本支持** `mcpServers`，可再按 Part E 的示例添加 DuckDuckGo、filesystem、puppeteer 等（可选）。

**2.2 编写 workspace/TOOLS.md（给 Agent 看的工具说明）**

在 workspace 根目录的 `TOOLS.md` 中写入（或替换为）以下内容，便于 Agent 正确调用工具：

```markdown
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
```

**2.3 可选：workspace/skills/wechat-daily-editor 与 PDF 脚本**

- 创建 Skill 目录：
  ```bash
  mkdir -p /home/renjeff/Documents/projects/wechat/skills/wechat-daily-editor
  ```
  若 workspace 是 `~/.openclaw/workspace`，则：
  ```bash
  mkdir -p ~/.openclaw/workspace/skills/wechat-daily-editor
  ```

- **skills/wechat-daily-editor/SKILL.md**：
  ```markdown
  ---
  name: wechat_daily_editor
  description: Run the daily wechat_factory pipeline: search → read → title → write → save (5 articles).
  ---

  # Wechat Daily Editor

  When the user says "run today's wechat pipeline" or "执行今日公众号任务":
  1. Create `wechat_factory/04_output/YYYY-MM-DD/` if not exists.
  2. For each domain (MED, FIN, EDU, plus two more as configured): use Search to find one recent paper, fetch or download to 01_sources, parse (PDF or snapshot), then read 02_knowledge_base and 03_templates/viral_titles.txt and article_style.md, draft one article 1500–2000 chars, write to 04_output/YYYY-MM-DD/<DOMAIN>_article.md.
  3. Optionally generate cover images to 05_assets/images/.
  4. Do not delete 02_knowledge_base or 03_templates.
  ```

- **可选：本地 PDF 提取脚本**（当没有 PDF MCP 时，由 Agent 通过 `bash` 调用）。在项目内创建 `scripts/extract_pdf_text.sh`：
  ```bash
  #!/usr/bin/env bash
  # Usage: ./scripts/extract_pdf_text.sh wechat_factory/01_sources/papers_pdf/paper.pdf
  set -e
  PDF="$1"
  if ! command -v pdftotext &>/dev/null; then
    echo "Install poppler-utils: sudo apt install poppler-utils"
    exit 1
  fi
  pdftotext -layout -enc UTF-8 "$PDF" -
  ```
 安装依赖：`sudo apt install poppler-utils`（或 macOS: `brew install poppler`）。Agent 可用 `exec`/`bash` 调用此脚本，再对 stdout 做总结。

**2.4 重启并校验**

```bash
openclaw gateway restart
```

若你的版本支持并在 openclaw.json 中配置了 `mcpServers`，再执行 `openclaw mcp list`，预期看到 `duckduckgo-search`、`filesystem`、`puppeteer` 等。若版本不支持 `mcpServers`（如 2026.3.13），则跳过 mcp list，确认 `tools.profile` / `tools.allow` 含 `group:web`、`group:fs`、`browser` 等即可。若有报错，查看 Gateway 日志。

---

### Phase 3: Agent 指令与每日流程

**当前实现：单 Agent（main）**，无需单独的 wechat-editor 或 `agents.list`。workspace 指向 wechat 项目，每日流程由 workspace 内的 AGENTS.md、SOUL.md 与 skills/wechat-daily-editor 提供。

| Step | Action | Purpose |
|------|--------|---------|
| 3.1 | 确认 `agents.defaults.workspace` 指向 wechat 项目目录（见 3.1 详细） | 默认 Agent 的工作目录含 wechat_factory |
| 3.2 | 每日动作清单已写在 workspace 的 **AGENTS.md**、**SOUL.md** 及 **skills/wechat-daily-editor/SKILL.md** | 驱动扫描→研读→拟题→撰稿→归档→配图 |
| 3.3 | 不添加 `agents.list`；不创建 `~/.openclaw/agents/wechat-editor/` | 与 OpenClaw 2026.3.13 兼容，避免未支持的 instructions 等键 |
| 3.4 | 配置 Cron 或 OpenClaw 内置调度，每日触发**默认 Agent** 执行今日任务 | 自动化日更 |

#### Phase 3 详细设置

**3.1 确认 workspace（单 Agent）**

在 `~/.openclaw/openclaw.json` 中确保 **仅**使用 `agents.defaults`，**不要**添加 `agents.list`：

```json
{
  "agents": {
    "defaults": {
      "workspace": "/home/renjeff/Documents/projects/wechat",
      "model": { "primary": "openai/gpt-5.1-codex" }
    }
  }
}
```

workspace 即 wechat 项目根，内含 **AGENTS.md**、**SOUL.md**、**TOOLS.md**、`wechat_factory/`、`skills/wechat-daily-editor/` 等。OpenClaw 默认 Agent（main）以此为工作目录，并从此处加载上述引导文件与技能。

**3.2 每日流程来源**

- **AGENTS.md**：说明本 workspace 用于 wechat_factory，输出到 `wechat_factory/04_output/YYYY-MM-DD/`。
- **SOUL.md**：约束 Agent 专注流水线、不删除 knowledge_base/templates、参考 TOOLS.md。
- **skills/wechat-daily-editor/SKILL.md**：当用户说「执行今日公众号任务」或「run today's wechat pipeline」时，按步骤执行扫描→抓取→拟题→撰稿→保存（详见该文件）。

无需在 `~/.openclaw/agents/` 下创建 wechat-editor 或 INSTRUCTIONS.md。

**3.3 为何不用 wechat-editor（可选阅读）**

OpenClaw 2026.3.13 不支持 `agents.list` 中的 `instructions` 键，且单 Agent 已能满足「一个 workspace 跑 wechat 流水线」的需求，因此当前实现不创建 `~/.openclaw/agents/wechat-editor/`，也不配置 `agents.list`。若后续版本支持多 Agent 且你需要独立 wechat-editor（如单独绑定通道），再按官方文档添加 `agents.list` 与对应目录。

**3.4 配置 Cron 定时触发**

- **方式 A（推荐）**：使用项目内脚本（会 cd 到 workspace、写日志到 `$LOG`，默认 `/tmp/wechat-pipeline.log`）：
  ```bash
  # 每天 8:00
  0 8 * * * /home/renjeff/Documents/projects/wechat/scripts/run-daily-wechat.sh
  ```
  脚本内部调用 `openclaw agent --message "执行今日公众号任务，产出 5 篇并保存到 04_output"`。
- **方式 B**：直接写 cron（需保证 cron 运行时 `openclaw` 在 PATH 且当前目录或环境正确）：
  ```bash
  0 8 * * * cd /home/renjeff/Documents/projects/wechat && openclaw agent --message "执行今日公众号任务，产出 5 篇并保存到 04_output" >> /tmp/wechat-pipeline.log 2>&1
  ```
  实际命令需根据 OpenClaw 的 CLI 用法调整（如 `openclaw run`、`openclaw chat` 等）。
- 或使用 OpenClaw 自带的 **cron** 工具（若已启用）：在界面或配置中添加每日任务，消息内容同上。
- 可选：再加一条 cron 在 23:00 对 workspace 做 Git 提交（见 Phase 4.3）。

---

### Phase 4: 外部工具与发布链

| Step | Action | Purpose |
|------|--------|---------|
| 4.1 | 安装并配置 Ollama，拉取 Qwen2.5 / Llama3.3，用于初筛、翻译、去重 | 降低成本，减少 Claude 调用量 |
| 4.2 | 安装 Pandoc 或 Markdown-to-WeChat，编写脚本将 `04_output/YYYY-MM-DD/*.md` 转为公众号 HTML | 完成发布前格式转换 |
| 4.3 | 配置系统 Cron：定时运行 OpenClaw 任务 + 可选 Git 提交（如每日 23:00 提交 04_output） | 稳定性与可回滚 |
| 4.4 | 在 02_knowledge_base 与 03_templates 中逐步填充领域知识与标题句式 | 提高选题与文案质量 |

#### Phase 4 详细设置

**4.1 Ollama（已在 Phase 0 提及，此处补充调用方式）**

- 项目内已提供 **`scripts/ollama-translate.sh`**：对英文摘要先经本地 Ollama 翻译成中文，再交给主模型润色，以降低成本。用法：
  ```bash
  echo "English abstract..." | ./scripts/ollama-translate.sh
  # 或
  ./scripts/ollama-translate.sh "English abstract..."
  ```
  默认模型为 `llama3.3:70b`；可设置 `OLLAMA_MODEL=qwen2.5:7b` 等覆盖。使用前需已拉取模型：`ollama pull llama3.3:70b`。
- **TOOLS.md** 已说明：对非中文摘要可先通过 `scripts/ollama-translate.sh` 翻译，再将中文结果交给主模型撰稿。
- 在 Agent 或 Skill 中约定：对候选摘要列表中的英文内容先调用此脚本（通过 `bash`），再对译文进行润色与扩写。

**4.2 Pandoc / Markdown-to-WeChat 脚本**

- 安装 Pandoc：
  ```bash
  sudo apt install pandoc   # Debian/Ubuntu
  # 或 brew install pandoc  # macOS
  ```
- 在项目内创建脚本 `scripts/md2wechat.sh`：
  ```bash
  #!/usr/bin/env bash
  # Usage: ./scripts/md2wechat.sh wechat_factory/04_output/2026-03-15
  set -e
  DIR="${1:-wechat_factory/04_output/$(date +%Y-%m-%d)}"
  OUT="${DIR}/html"
  mkdir -p "$OUT"
  for f in "$DIR"/*.md; do
    [ -f "$f" ] || continue
    base=$(basename "$f" .md)
    pandoc "$f" -f markdown -t html -o "$OUT/${base}.html" --standalone
  done
  echo "HTML written to $OUT"
  ```
  chmod +x scripts/md2wechat.sh。公众号后台可复制 `OUT/*.html` 内容粘贴（或再经一次样式内联工具）。

**4.2b 带图、正确排版并存入公众号草稿箱**

目标：内容**带封面图与配图**、**正确排版**，并自动**存入微信公众平台草稿箱**（详见 [PUBLISHING.md](./PUBLISHING.md)）。

- 流水线需确保每篇文章在 `05_assets/images/` 下有对应封面（如 `YYYY-MM-DD_MED_cover.png`），并在撰稿步骤中引用；正文内配图可选。
- 使用 **`scripts/wechat-draft-upload.sh [YYYY-MM-DD]`**：读取 `04_output/YYYY-MM-DD/` 下 Markdown 与 `05_assets/images/` 下封面，将 MD 转为 HTML，上传封面为永久素材，调用微信「新增草稿」接口写入草稿箱。
- **依赖**：`curl`、`jq`、`pandoc`。**凭证**：环境变量 `WECHAT_APPID` + `WECHAT_SECRET`，或直接设置 `WECHAT_ACCESS_TOKEN`（勿提交到 Git）。
- 使用示例：
  ```bash
  export WECHAT_APPID=your_appid
  export WECHAT_SECRET=your_secret
  ./scripts/wechat-draft-upload.sh    # 上传当日
  # 或 ./scripts/wechat-draft-upload.sh 2026-03-15
  ```
  成功后可在公众平台后台「草稿箱」中查看、编辑后群发或发布。

**4.3 Cron：OpenClaw + Git 提交**

- **4.3a 每日流水线（8:00）**：已由 `scripts/run-daily-wechat.sh` 实现；Cron 只需调用该脚本（见 Phase 3.4）。
- **4.3b 每日 Git 提交（23:00，可选）**：使用 `scripts/git-commit-daily.sh`，将当日 `04_output`、`05_assets` 的变更 add/commit/push；无变更则跳过。
- 编辑 crontab：`crontab -e`，添加（路径按实际修改）：
  ```cron
  # 每天 8:00 执行 wechat 流水线
  0 8 * * * /home/renjeff/Documents/projects/wechat/scripts/run-daily-wechat.sh

  # 每天 23:00 提交并推送当日产出（可选）
  0 23 * * * /home/renjeff/Documents/projects/wechat/scripts/git-commit-daily.sh
  ```
  完整示例见 `scripts/cron.example`。

**4.4 填充 02_knowledge_base 与 03_templates**

- **02_knowledge_base**：`medical_ai.md`、`finance_ai.md`、`edu_ai.md` 已填充术语表、已解析论文列表格式（日期 | 标题 | 来源）及政策/趋势摘要；可随运行逐步追加「已解析论文」行。
- **03_templates/viral_titles.txt**：已加入多条高点击标题句式，每行一句；Agent 可据此生成并择优。
- **03_templates/article_style.md**：已规定单 H1、H2/H3、段落/加粗/引用/列表、配图路径（`05_assets/images/`），与 DESIGN、PUBLISHING 一致。

---

### Phase 5: 测试与上线

| Step | Action | Purpose |
|------|--------|---------|
| 5.1 | 单链路测试：手动触发一次「单领域单篇」（见 Part C） | 验证 感知→认知→创作→存储 全链路 |
| 5.2 | 工具级测试：分别验证搜索、抓取、PDF 解析、写文件、图像生成 | 快速定位故障点 |
| 5.3 | 日产出测试：连续 2～3 天跑满 5 篇，检查 04_output 与 05_assets | 验证产能与稳定性 |
| 5.4 | 发布链测试：Markdown → HTML → 公众号后台粘贴（或 API） | 验证最后一公里 |

#### Phase 5 详细操作

**5.1 单链路测试**

目的：验证「感知 → 认知 → 创作 → 存储」全链路，**只做单领域单篇**，便于快速定位问题。对应 Part C 的 C.2。

**前置条件**

- Phase 0～4 已完成：OpenClaw 可启动，workspace 指向本项目目录（含 `wechat_factory/`），工具已开放（如 `group:fs`、`group:web`、`browser` 等）。
- `02_knowledge_base`、`03_templates` 已填充（见 4.4）；`04_output`、`05_assets` 目录存在（可为空）。

**操作步骤**

1. **启动 OpenClaw**  
   在终端启动 Gateway/Agent（如 `openclaw gateway start` 或按你本地方式），并打开与**默认 Agent** 的对话界面。

2. **发送单链路指令**  
   在对话中输入下面**其中一条**（可复制，日期按当天替换；路径为相对 workspace 根）：

   - **医疗 AI（推荐先测）**  
     ```text
     只做一篇：医疗 AI。从搜索开始，选一篇近期（过去 7 天）的高质量论文或报道，抓取或下载到 01_sources，解析内容，拟一个吸引人的标题（可参考 wechat_factory/03_templates/viral_titles.txt），写一篇 1500 字左右的文章，保存到 wechat_factory/04_output/$(date +%Y-%m-%d)/MED_article.md。请遵循 wechat_factory/03_templates/article_style.md 的格式。
     ```
   - **金融 AI**  
     ```text
     只做一篇：金融 AI。从搜索开始，选一篇近期金融/量化/NLP 相关论文或报告，抓取或下载到 01_sources，解析后拟题并撰写约 1500 字文章，保存到 wechat_factory/04_output/$(date +%Y-%m-%d)/FIN_article.md。格式遵循 wechat_factory/03_templates/article_style.md。
     ```
   - **教育 AI**  
     ```text
     只做一篇：教育 AI。从搜索开始，选一篇教育/学习分析/ITS 相关论文或报道，抓取到 01_sources，解析后拟题并撰写约 1500 字文章，保存到 wechat_factory/04_output/$(date +%Y-%m-%d)/EDU_article.md。格式遵循 wechat_factory/03_templates/article_style.md。
     ```

   **说明**：若在 Cursor/终端里复制，`$(date +%Y-%m-%d)` 会被 shell 展开为当天日期；若在 OpenClaw 网页输入框里粘贴，Agent 通常能理解“今天”并生成对应日期目录。为保险起见，可把 `$(date +%Y-%m-%d)` 直接改成具体日期，如 `2026-03-15`。

3. **观察 Agent 行为**  
   Agent 应按顺序：**搜索**（如 24h 内医疗 AI 论文）→ **选一篇** → **抓取/下载**（保存到 `01_sources/papers_pdf/` 或 `01_sources/web_snapshots/`）→ **解析**（摘要/结论）→ **拟题**（可参考 `viral_titles.txt`）→ **撰稿** → **写入** `04_output/YYYY-MM-DD/` 下对应 `MED_article.md`（或 FIN/EDU）。若某步失败，Agent 可能重试或报错；记下失败步骤便于做 5.2 工具级测试。

4. **验收检查**  
   - **路径**：`wechat_factory/04_output/YYYY-MM-DD/` 下存在 `MED_article.md`（或 FIN/EDU）。
   - **内容**：打开文件，确认约 1500 字、单 H1、H2/H3 结构、段落与引用符合 `article_style.md`；标题与正文风格可参考 `viral_titles.txt` 与知识库。
   - **可选**：若配置了图像生成，检查 `05_assets/images/` 是否有对应封面；正文中是否引用了 `02_knowledge_base` 的术语或趋势。

5. **（可选）更新知识库**  
   若希望后续去重：把本次解析的论文按「日期 | 标题 | 来源」追加到 `02_knowledge_base/medical_ai.md`（或 finance/edu）的「已解析论文」列表。

**若未产出文件**

- 先确认 workspace 是否为项目根（即包含 `wechat_factory/`）；若 workspace 是别的目录，路径需相应调整或在该目录下建立 `wechat_factory` 结构。
- 再按 **5.2** 做工具级测试：分别验证搜索、抓取、写文件等是否可用，定位是搜索无结果、抓取失败、还是写盘权限/路径错误。
- 查看 Agent 对话中的报错或工具返回；若为「无合适论文」，可放宽时间范围（如过去 30 天）或换一个领域重试。

**5.2 工具级测试**

- 按 Part C 表格逐项：在对话中分别请求“用搜索查…”“打开某 URL 并保存到 web_snapshots”“读取某 PDF 并总结”“在 04_output 下创建目录并写入 test.md”“生成一张封面到 05_assets/images”。确认每步成功且路径正确。

**5.3 日产出测试**

- 连续 2～3 天在固定时间触发“执行今日公众号任务”（或依赖 Cron）。每天检查 `04_output/YYYY-MM-DD/` 下是否有 5 个 md 文件、命名正确、内容非空；检查 Cron 与 Git 是否按 4.3 执行。

**5.4 发布链测试**

目的：把 `04_output` 中的文章落到公众号（草稿箱），可**手动粘贴**或**API 上传**。需要 **pandoc**（`sudo apt install pandoc`）用于 Markdown→HTML。

**方式 A：手动粘贴到公众号后台（无需 API 凭证）**

1. **生成 HTML**（在项目根目录）：
   ```bash
   ./scripts/md2wechat.sh wechat_factory/04_output/2026-03-15
   ```
   产出在 `wechat_factory/04_output/2026-03-15/html/`，例如 `MED_article.html`。

2. **在浏览器中打开该 HTML 文件**（如 `file:///.../04_output/2026-03-15/html/MED_article.html`），全文选中（Ctrl+A），复制（Ctrl+C）。

3. **登录微信公众平台** → 素材管理 / 新建图文 → **正文框**内粘贴（Ctrl+V）。标题可复制文章内第一个 H1（如「一篇搞懂 AMIE：…」），摘要可填前一两句。在后台**上传并设置封面图**（公众号要求必填），保存为草稿或直接群发。

4. **检查**：版式、分段、加粗是否正常；若正文有配图，需在后台正文中再插入图片（本脚本仅转正文，不处理文内图 URL）。

**方式 B：API 上传到草稿箱（需公众号凭证 + 封面图）**

1. **封面图**：公众号 API 要求每篇必有封面。将封面放到 `wechat_factory/05_assets/images/`，命名：`YYYY-MM-DD_MED_cover.png`（或 `.jpg`）。例如 2026-03-15 的医疗篇即 `2026-03-15_MED_cover.png`。无封面时 `wechat-draft-upload.sh` 会跳过该篇。

2. **凭证**：在 shell 中设置（勿提交到 Git）：
   ```bash
   export WECHAT_APPID="你的AppID"
   export WECHAT_SECRET="你的AppSecret"
   ```

3. **上传草稿**：
   ```bash
   ./scripts/wechat-draft-upload.sh 2026-03-15
   ```
   成功会输出 `media_id=...`，并在公众号后台「草稿箱」中看到该图文。

4. **依赖**：脚本内部用 pandoc 转 HTML、curl 调微信 API、jq 解析 JSON；未安装则 `sudo apt install pandoc curl jq`。

**当前你这一篇（2026-03-15 MED_article）**：若暂无封面图，用**方式 A** 即可完成 5.4（先装 pandoc，生成 HTML 后复制到公众号后台并手动上传一张封面）。之后有封面图或多篇时，再用**方式 B** 做端到端上传。

---

## Part B: OpenClaw Skills & Tools — 功能与用途

以下按 DESIGN.md 中的「必需 Skills」列出，并说明在 OpenClaw 中**各自的作用**、**典型调用场景**以及**配置要点**。OpenClaw 通过 **MCP (Model Context Protocol)** 接入外部能力，工具由 Gateway 路由到对应 MCP Server。

---

### 1. Deep Search（深度搜索）

| 项目 | 说明 |
|------|------|
| **在 OpenClaw 中的角色** | 为 Agent 提供**实时、突破 LLM 知识截止日期**的检索能力，用于发现 2025/2026 年最新论文与报道。 |
| **功能** | 执行关键词/句子搜索，返回标题、链接、摘要等；可限定时间范围（如 past 24 hours）。 |
| **典型用途** | 感知层「扫描」：查找过去 24 小时内医疗/金融/教育 AI 高引论文、顶刊动态、会议预印本。 |
| **推荐 MCP / 实现** | 使用 **Google Search** 或 **Brave Search** 的 MCP Server（如 `@modelcontextprotocol/server-brave-search` 或等效 Google 封装）。 |
| **配置要点** | 在 `openclaw.json` 的 `mcpServers` 中配置 `brave-search` 或 `google-search`，并写入 API Key（若需要）。Agent 通过工具名（如 `brave_search`）调用。 |
| **TOOLS.md 建议描述** | “Deep Search：用于查找最新 AI 论文与新闻，请在过去 24h 内检索并优先选择高影响来源（Nature、Lancet、arXiv 等）。” |

---

### 2. Web Browser（网页抓取）

| 项目 | 说明 |
|------|------|
| **在 OpenClaw 中的角色** | 让 Agent **像用户一样访问网页**，获取 arXiv、PubMed、Medium 等页面的全文或结构化内容，而不仅依赖搜索摘要。 |
| **功能** | 打开 URL、等待渲染、提取正文/元数据、截图（可选）；可保存 HTML 或纯文本到 workspace。 |
| **典型用途** | 感知层「抓取」：将论文摘要页或博客全文保存到 `01_sources/web_snapshots/`；认知层补充 PDF 以外的信息。 |
| **推荐 MCP / 实现** | **Puppeteer** 或 **Playwright** 的 MCP Server（如 `@modelcontextprotocol/server-puppeteer` 或社区 Playwright MCP）。OpenClaw 也自带 `browser` 工具（若已启用 `group:ui`）。 |
| **配置要点** | 若用自带 `browser`，需在 `tools.allow` 中保留 `browser`；若用 MCP，则配置对应 server 的 command/args。 |
| **TOOLS.md 建议描述** | “Web Browser：访问指定 URL 并提取正文或保存快照到 wechat_factory/01_sources/web_snapshots/，用于抓取论文页面和报道全文。” |

---

### 3. PDF Parser（论文解析）

| 项目 | 说明 |
|------|------|
| **在 OpenClaw 中的角色** | 对**长 PDF（如 30+ 页论文）**进行结构化解析，避免一次性塞满上下文；按章节/图表提取核心逻辑与结论。 |
| **功能** | 读取 PDF → 分页或分段 → 提取文本与图表描述（或 OCR）；可选「sequential-strategy」：先目录/摘要，再方法/实验/结论，逐段喂给 LLM。 |
| **典型用途** | 认知层「研读」：从 `01_sources/papers_pdf/` 取 PDF，输出结构化摘要、关键结论、与 02_knowledge_base 的对比要点。 |
| **推荐 MCP / 实现** | 使用支持「分段阅读」的 PDF 工具或 MCP（名称可能为 `pdf`、`document` 或通过自定义 Skill 调用本地脚本 + `pdftotext`/PyMuPDF）。sequential-strategy 可在 Agent 指令中约定：先 summary，再 methods，再 results。 |
| **配置要点** | 若 MCP 提供 `read_pdf` 或 `extract_pdf_section`，在 `mcpServers` 中配置；否则可通过 `exec`/`bash` 调用本地 PDF 工具，并在 TOOLS.md 中说明用法。 |
| **TOOLS.md 建议描述** | “PDF Parser：读取 wechat_factory/01_sources/papers_pdf/ 下的 PDF，按摘要→方法→结果→结论顺序提取要点，供后续撰稿使用。” |

---

### 4. Filesystem（本地文件）

| 项目 | 说明 |
|------|------|
| **在 OpenClaw 中的角色** | 让 Agent **在 workspace 内创建目录、读写文件、重命名、整理**，实现 01_sources 与 04_output 的自动化管理。 |
| **功能** | 读文件、写文件、编辑、创建目录、移动/重命名；路径通常相对于 workspace 根。 |
| **典型用途** | 存储层：将成文写入 `04_output/YYYY-MM-DD/MED_article.md`；感知层：保存快照到 `01_sources/web_snapshots/`；整理：按日期建目录、按领域命名文件。 |
| **推荐 MCP / 实现** | OpenClaw 内置 `group:fs`（`read`, `write`, `edit`, `apply_patch`）；也可用 **MCP filesystem server**（如 `@modelcontextprotocol/server-filesystem`）限定到 workspace 子目录，增强隔离。 |
| **配置要点** | 默认已具备 `group:fs`；若使用 MCP filesystem，在 `mcpServers` 中指定 `command` 和 `args`（例如根目录为 workspace 或 `wechat_factory`）。 |
| **TOOLS.md 建议描述** | “Filesystem：在 wechat_factory 下创建 04_output/YYYY-MM-DD、写入文章 Markdown、保存 01_sources 下的 PDF 与快照；请勿删除 02_knowledge_base 与 03_templates。” |

---

### 5. Image Gen（图像生成）

| 项目 | 说明 |
|------|------|
| **在 OpenClaw 中的角色** | 根据**文章摘要或标题**生成**科技感/学术感封面图**，保存到 05_assets，供公众号排版使用。 |
| **功能** | 输入文本 prompt → 调用图像模型（如 DALL·E、Flux）→ 保存 PNG/JPEG 到指定路径。 |
| **典型用途** | 创作层「配图」：在撰稿完成后，用摘要生成封面，路径写入文章 Frontmatter 或文末说明。 |
| **推荐 MCP / 实现** | **dalle-node**、**flux-mcp** 或其它 Image Gen 类 MCP；若 OpenClaw 有内置 `image` 工具且支持文生图，也可使用。 |
| **配置要点** | 在 `mcpServers` 中配置对应 Image MCP，传入 API Key 或本地模型地址；在 TOOLS.md 中约定输出目录为 `wechat_factory/05_assets/images/` 及命名规则（如 `YYYY-MM-DD_MED_cover.png`）。 |
| **TOOLS.md 建议描述** | “Image Gen：根据文章标题或摘要生成一张科技感封面图，保存到 wechat_factory/05_assets/images/，文件名含日期与领域标识。” |

---

### 6. OpenClaw 内置工具组（补充）

| 工具/组 | 在本项目中的用途 |
|---------|------------------|
| **group:web** | `web_search`、`web_fetch`：可部分替代 Deep Search（若未配置 Brave/Google MCP），用于抓取公开页面内容。 |
| **group:fs** | 见上 Filesystem，读写 workspace。 |
| **group:runtime** | `exec`/`bash`：调用 Ollama、Pandoc、Git、本地 PDF 脚本等外部命令。 |
| **group:memory** | `memory_search`、`memory_get`：跨会话记忆，可存「已写过的选题」避免重复。 |
| **browser** | 若未用独立 MCP，可用内置 browser 做简单网页抓取。 |

在 `openclaw.json` 中可通过 `tools.profile: "coding"` 或 `tools.allow: ["group:fs", "group:web", "browser", ...]` 控制上述工具对默认 Agent 的可见性。

---

## Part C: Testing Strategy

### C.1 工具级测试（不跑完整流水线）

| 测试项 | 操作 | 预期 |
|--------|------|------|
| Deep Search | 在 OpenClaw 中发指令：“用搜索查过去 24 小时 Nature Medicine 的 AI 论文” | 返回若干链接与摘要 |
| Web Browser | “打开 [某篇 arXiv 摘要链接]，把页面正文保存到 wechat_factory/01_sources/web_snapshots/test.txt” | 文件生成且内容合理 |
| PDF Parser | “读取 wechat_factory/01_sources/papers_pdf/ 下的 [某 PDF]，总结摘要和结论” | 输出结构化摘要 |
| Filesystem | “在 wechat_factory/04_output/ 下创建 2026-03-15，并写入一个 test.md” | 目录与文件存在 |
| Image Gen | “根据‘医疗 AI 诊断新突破’生成一张封面，保存到 05_assets/images/” | 图片生成且路径正确 |

### C.2 单链路测试（单领域单篇 E2E）

1. **输入**：指定一个领域（如医疗 AI）和日期（如今天）。
2. **步骤**：Agent 按 INSTRUCTIONS 执行：搜索 → 选一篇 → 抓取/下载 → 解析 PDF 或快照 → 拟题 → 撰稿 → 写入 `04_output/YYYY-MM-DD/MED_article.md`。
3. **预期**：生成一篇 1500–2000 字、符合 `article_style.md` 的 Markdown；无报错；可选的封面在 `05_assets/images/`。
4. **验收**：人工快速浏览标题与正文质量，检查是否引用 02_knowledge_base、是否与 03_templates 风格一致。

### C.3 日产出与稳定性测试

- 连续 2～3 天定时触发「每日 5 篇」流程。
- 检查：`04_output/YYYY-MM-DD/` 下是否每天 5 个文件、命名正确、内容非空；Cron 与 Git 是否按预期执行；OpenClaw 崩溃后 Cron 是否能重启任务。

### C.4 发布链测试

- 取一篇 `04_output` 下的 Markdown，用 Pandoc 或 Markdown-to-WeChat 转为 HTML，粘贴到公众号后台（或通过 API）。
- 检查：版式、图片链接、字数与样式是否符合公众号要求。

---

## Part D: How to Work with OpenClaw

### D.1 Workspace 与 wechat_factory 的关系

- **Workspace** 是 OpenClaw Agent 的「当前工作目录」；所有相对路径（如 `wechat_factory/04_output/`）都相对于 workspace 根。
- **两种常见做法**：  
  - **A**：workspace = `~/.openclaw/workspace`，其下放 `wechat_factory/`（复制或软链自本项目）。  
  - **B**：workspace = 本项目目录 `wechat/`，则 `wechat_factory/` 已在其中。
- 在 `AGENTS.md` 或 Agent 的配置里注明：「本 Agent 的产出目录为 workspace 下的 wechat_factory/04_output，素材在 01_sources，知识库在 02_knowledge_base。」

### D.2 多 Agent 分工（可选）

- **当前实现**：单 Agent（main）专门执行「每日 5 篇」流程；绑定 Cron 或定时触发；工具开放 `group:fs`、`group:web`、browser 等。
- **若日后用多 Agent**：可增加 wechat-editor，绑定 Cron 或通道；其他 Agent 可限制为 `tools.profile: "messaging"` 等，避免误动 wechat_factory。

### D.3 指令与记忆

- **每日流程**：当前写在 workspace 的 **AGENTS.md**、**SOUL.md** 与 **skills/wechat-daily-editor/SKILL.md**；可追加「遇到 PDF 无法解析时改用 web_snapshots」「标题从 viral_titles.txt 中选型」等规则。
- **MEMORY.md / memory/YYYY-MM-DD.md**：记录已选题、已写标题，配合 `memory_search` 做去重与连续性。
- **TOOLS.md**：如上 Part B，用自然语言描述每个工具在本项目中的用途与路径约定，减少 Agent 误用。

### D.4 定时运行方式

- **方式 1**：系统 Cron 调用 OpenClaw CLI，例如每日 8:00 执行一次「默认 Agent 执行今日任务」（无需指定 agent id）。
- **方式 2**：OpenClaw 的 `cron` 工具（若已启用）在网关内配置每日任务，触发对应 Agent。
- **方式 3**：外部调度器（如 GitHub Actions、Jenkins）在指定时间调用 OpenClaw API 或 CLI。

任选其一，确保进程异常退出时有重启（如 Cron 每分钟检查进程是否存在并拉起）。

### D.5 配置与密钥

- **MCP API Keys**（Brave/Google Search、DALL·E 等）：放在 `~/.openclaw/` 或环境变量，不要写入 workspace 或提交到 Git。
- **openclaw.json**：可引用环境变量（若支持），例如 `"args": ["-y", "some-mcp", "--api-key", "${BRAVE_API_KEY}"]`。

---

## Part E: MCP Server 配置示例（openclaw.json 片段）

**注意：** 仅当你的 OpenClaw 版本**支持**顶层键 `mcpServers` 时使用；否则会报 `Unrecognized key: "mcpServers"` 并导致 Gateway 无法启动（见 2.1 版本说明）。

以下为**示例结构**，实际包名与参数以官方文档为准。请勿将 API Key 写进版本库。

```json
{
  "mcpServers": {
    "duckduckgo-search": {
      "command": "npx",
      "args": ["-y", "@oevortex/ddg_search@latest"],
      "transport": "stdio"
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": { "BRAVE_API_KEY": "<your-key>" },
      "transport": "stdio"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/renjeff/Documents/projects/wechat/wechat_factory"],
      "transport": "stdio"
    }
  },
  "tools": {
    "profile": "coding",
    "allow": ["group:fs", "group:web", "group:runtime", "browser"]
  }
}
```

说明：

- **duckduckgo-search**：免费搜索，无需 API Key；**brave-search**：需 Brave API Key，对应 Part B 的 Deep Search。
- **filesystem**：将 MCP 文件操作限定到 `wechat_factory`，对应 Part B 的 Filesystem。
- **browser**：若为 OpenClaw 内置，无需在 mcpServers 中配置；若用 Puppeteer/Playwright MCP，需再加一条 server。
- **PDF / Image Gen**：需按你实际采用的 MCP 包名与参数补充到 `mcpServers`。

---

## Part F: 小结

| 主题 | 文档位置 |
|------|----------|
| 实现阶段 | Part A：Phase 0～5 |
| 各 Skill/工具在 OpenClaw 中的功能与用途 | Part B：Deep Search、Web Browser、PDF Parser、Filesystem、Image Gen + 内置组 |
| 测试 | Part C：工具级 → 单链路 E2E → 日产出 → 发布链 |
| 与 OpenClaw 协作 | Part D：Workspace、多 Agent、指令与记忆、定时、密钥 |
| MCP 配置示例 | Part E：openclaw.json 片段 |

按 Phase 0 → 1 → 2 → 3 → 4 → 5 顺序执行，并在每阶段用 Part C 的测试做验证，即可在 OpenClaw 上实现 DESIGN.md 中的公众号自动化流水线，且每个技能与工具的角色清晰、可维护。
