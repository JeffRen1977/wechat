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
    ollama pull qwen2.5:7b
    # 或 ollama pull llama3.3:70b（按机器配置选择）
    ```
  - 验证：
    ```bash
    ollama run qwen2.5:7b "Translate to Chinese: Hello world"
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

  - **wechat-editor**: Runs the daily wechat_factory pipeline (5 articles). Workspace paths are relative to this directory; output goes to `wechat_factory/04_output/YYYY-MM-DD/`.
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
| 2.1 | 在 `~/.openclaw/openclaw.json` 中配置 `mcpServers`（见 Part B） | 为 Agent 提供搜索、浏览器、PDF、文件、图像等能力 |
| 2.2 | 在 workspace 的 `TOOLS.md` 中列出本项目会用到的工具及用途（给 Agent 看的说明） | 引导 Agent 在正确场景调用正确工具 |
| 2.3 | 可选：在 `workspace/skills/` 下为 wechat 流水线写专用 Skill（如 `wechat-daily-editor`），在 SKILL.md 中引用 MCP 工具与步骤 | 把「每日 5 篇」流程固化为可复用技能 |
| 2.4 | 重启 Gateway，执行 `openclaw mcp list` 校验 MCP 连接 | 确保工具在运行时可用 |

#### Phase 2 详细设置

**2.1 编辑 ~/.openclaw/openclaw.json，添加 mcpServers**

**免费搜索选项（无需 API Key）：**

- **OpenClaw 内置**：若 `tools.allow` 包含 `group:web`，则已有 `web_search`、`web_fetch`，可直接用，无需额外 MCP。
- **DuckDuckGo MCP（推荐）**：使用 `@oevortex/ddg_search`，无需 API Key，运行 `npx -y @oevortex/ddg_search@latest` 即可。下方示例用 `duckduckgo-search` 替代 Brave。

在配置文件中加入或合并以下块（路径请按你的环境替换；**勿将真实 API Key 提交到 Git**）：

```json
{
  "mcpServers": {
    "duckduckgo-search": {
      "command": "npx",
      "args": ["-y", "@oevortex/ddg_search@latest"],
      "transport": "stdio"
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/renjeff/Documents/projects/wechat/wechat_factory"
      ],
      "transport": "stdio"
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
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

- **搜索**：`duckduckgo-search` 免费、无需 API Key。若需 Brave/Google，可改为 `brave-search` 或 `google-search` MCP，并配置对应 Key。
- `filesystem` 的第三个参数必须是**绝对路径**，指向你的 `wechat_factory` 目录（或 workspace 根，再在 TOOLS.md 中约定子路径）。
- **Google Search MCP**：若需 Google 检索，在 `mcpServers` 中增加一条，例如 `"google-search": { "command": "npx", "args": ["-y", "<package-name>"], "env": { "GOOGLE_API_KEY": "" }, "transport": "stdio" }`；具体包名与 env 以 npm 页面为准（如 `@modelcontextprotocol/server-google-search` 或等效）。
- **PDF**：若没有现成 PDF MCP，用 `exec`/`bash` 调用项目内 `scripts/extract_pdf_text.sh <path-to-pdf>`，再对 stdout 做总结；见下方 2.3 可选脚本。
- **Image Gen**：若需自动生成封面，可增加 DALL·E 或 Flux 的 MCP（如 `@modelcontextprotocol/server-dalle` 或社区 flux-mcp），在 `mcpServers` 中配置对应 `command`/`args`/`env`，并在 TOOLS.md 中说明输出目录为 `wechat_factory/05_assets/images/`。

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

**2.4 重启并校验 MCP**

```bash
openclaw gateway restart
openclaw mcp list
```

预期看到 `brave-search`、`filesystem`、`puppeteer` 等（视你配置的 server 而定）。若有报错，查看 Gateway 日志。

---

### Phase 3: Agent 指令与每日流程

| Step | Action | Purpose |
|------|--------|---------|
| 3.1 | 为负责「公众号内容」的 Agent 创建或指定目录（如 `~/.openclaw/agents/wechat-editor/`） | 独立身份、workspace、记忆 |
| 3.2 | 在该 Agent 的 `INSTRUCTIONS.md`（或等价指令文件）中写入 DESIGN.md 第 6 节的「每日动作清单」 | 驱动扫描→研读→拟题→撰稿→归档→配图 |
| 3.3 | 将该 Agent 的 `workspace` 指向包含 `wechat_factory` 的目录 | 保证读写路径一致 |
| 3.4 | 配置 Cron 或 OpenClaw 内置调度，每日定时触发该 Agent 的「执行今日任务」 | 自动化日更 |

#### Phase 3 详细设置

**3.1 创建 wechat-editor Agent 目录**

OpenClaw 的 Agent 配置方式：**单 Agent** 时仅用 `agents.defaults`（无需 `list`）；**多 Agent** 时在 `openclaw.json` 的 `agents.list` 中为每个 Agent 指定 `id`、`workspace` 等。也可用 CLI 添加：`openclaw agents add wechat-editor`。若你手动创建 agent 目录（例如放 INSTRUCTIONS.md）：

```bash
mkdir -p ~/.openclaw/agents/wechat-editor
```

**3.2 编写 INSTRUCTIONS.md**

在 `~/.openclaw/agents/wechat-editor/` 下创建 `INSTRUCTIONS.md`（或你的 OpenClaw 版本所识别的指令文件名，如 `SYSTEM.md`）：

```markdown
# Wechat Editor Agent — Daily Pipeline

## Role
You run the "AI 行业前哨" wechat_factory pipeline. Output 5 articles per day (Medical, Finance, Education + 2 more domains as configured).

## Daily Steps (run in order)

1. **Scan**
   - Use Deep Search (brave_search / web_search) to find in the **past 24 hours**: high-impact papers or news in [Medical AI], [Finance AI], [Education AI] (and two other domains).
   - Prefer: Nature, Lancet, Nature Medicine, arXiv, PubMed, top venues.

2. **Fetch & Read**
   - Download or open each selected link. Save PDFs to `wechat_factory/01_sources/papers_pdf/`, or save page content to `wechat_factory/01_sources/web_snapshots/`.
   - Use PDF Parser (or `scripts/extract_pdf_text.sh` + summarize) to get: abstract, key methods, results, conclusion. Compare with `wechat_factory/02_knowledge_base/<domain>_ai.md` for novelty.

3. **Title**
   - Read `wechat_factory/03_templates/viral_titles.txt`. Generate 5 candidate titles per article, pick the best one for click-through.

4. **Draft**
   - Style: like 机器之心. Length: 1500–2000 characters. Format: Markdown per `wechat_factory/03_templates/article_style.md`.
   - Write one article per domain.

5. **Save**
   - Ensure folder exists: `wechat_factory/04_output/YYYY-MM-DD/` (today’s date).
   - Write: `MED_article.md`, `FIN_article.md`, `EDU_article.md`, and two more (e.g. `TECH_article.md`, `POLICY_article.md`).

6. **Cover (optional)**
   - For each article, use Image Gen to create a cover from title/abstract; save to `wechat_factory/05_assets/images/` with name `YYYY-MM-DD_<DOMAIN>_cover.png`.

## Rules
- Do not delete or overwrite `02_knowledge_base` or `03_templates`.
- If a PDF cannot be parsed, use the web snapshot content instead.
- Use TOOLS.md in the workspace for tool names and paths.
```

**3.3 在 openclaw.json 中绑定 workspace**

在 `~/.openclaw/openclaw.json` 中为该 Agent 指定 workspace：**单 Agent** 时只改 `agents.defaults.workspace`；**多 Agent** 时在 `agents.list` 中增加一条，例如：

```json
{
  "agents": {
    "list": [
      {
        "id": "wechat-editor",
        "name": "Wechat Editor",
        "workspace": "/home/renjeff/Documents/projects/wechat",
        "instructions": "~/.openclaw/agents/wechat-editor/INSTRUCTIONS.md"
      }
    ]
  }
}
```

若 OpenClaw 通过文件路径加载指令，可能只需 `instructions` 指向上述文件；若通过 UI 或其它键名加载，请以官方文档为准。

**3.4 配置 Cron 定时触发**

- 假设 OpenClaw CLI 支持通过 agent id 发一条“执行今日任务”消息，可写成 cron（示例：每天 8:00 执行）：
  ```bash
  0 8 * * * OPENCLAW_AGENT=wechat-editor openclaw agent --message "执行今日公众号任务，产出 5 篇并保存到 04_output"
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

- 在 Agent 指令或 Skill 中可约定：对“候选摘要列表”先调用本地 Ollama 做翻译或去重，再把结果交给 Claude 润色。示例（在 bash 中测试）：
  ```bash
  ollama run qwen2.5:7b "将以下英文摘要翻译为中文：<paste abstract>"
  ```
- 若通过 OpenClaw 的 `exec`/`bash` 调用，需在 INSTRUCTIONS 或 TOOLS.md 中写明：何时用 Ollama（例如“对非中文摘要先调用 ollama 翻译”）。

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

**4.3 Cron：OpenClaw + Git 提交**

- 编辑 crontab：`crontab -e`
- 添加（按实际路径和 CLI 修改）：
  ```cron
  # 每天 8:00 执行 wechat 流水线
  0 8 * * * cd /home/renjeff/Documents/projects/wechat && openclaw agent --message "执行今日公众号任务" 2>&1 | tee -a /tmp/wechat-pipeline.log

  # 每天 23:00 提交当日产出（可选）
  0 23 * * * cd /home/renjeff/Documents/projects/wechat && git add wechat_factory/04_output wechat_factory/05_assets && git diff --staged --quiet || git commit -m "Daily wechat output $(date +%Y-%m-%d)" && git push
  ```

**4.4 填充 02_knowledge_base 与 03_templates**

- 编辑 `wechat_factory/02_knowledge_base/medical_ai.md`（及 finance、edu）：加入术语表、已解析论文列表（日期 | 标题 | 来源）、政策/趋势摘要。
- 编辑 `wechat_factory/03_templates/viral_titles.txt`：每行一句标题句式或示例。
- 编辑 `wechat_factory/03_templates/article_style.md`：规定 H1/H2/H3、段落、引用、配图路径等，与 DESIGN 一致。

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

- 在 OpenClaw 中对该 Agent 发送一条消息，例如：
  - “只做一篇：医疗 AI。从搜索开始，选一篇论文，抓取或下载，解析，拟题，写一篇 1500 字文章保存到 wechat_factory/04_output/$(date +%Y-%m-%d)/MED_article.md。”
- 检查：该日期目录下是否出现 `MED_article.md`，内容是否完整、符合风格。

**5.2 工具级测试**

- 按 Part C 表格逐项：在对话中分别请求“用搜索查…”“打开某 URL 并保存到 web_snapshots”“读取某 PDF 并总结”“在 04_output 下创建目录并写入 test.md”“生成一张封面到 05_assets/images”。确认每步成功且路径正确。

**5.3 日产出测试**

- 连续 2～3 天在固定时间触发“执行今日公众号任务”（或依赖 Cron）。每天检查 `04_output/YYYY-MM-DD/` 下是否有 5 个 md 文件、命名正确、内容非空；检查 Cron 与 Git 是否按 4.3 执行。

**5.4 发布链测试**

- 取一篇 `04_output/YYYY-MM-DD/*.md`，运行：
  ```bash
  ./scripts/md2wechat.sh wechat_factory/04_output/YYYY-MM-DD
  ```
- 打开生成的 `html/*.html`，复制到公众号后台，检查版式与图片；若有 API 发布，再测一次端到端发布。

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

在 `openclaw.json` 中可通过 `tools.profile: "coding"` 或 `tools.allow: ["group:fs", "group:web", "browser", ...]` 控制上述工具对 wechat-editor Agent 的可见性。

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

- **wechat-editor**：专门执行「每日 5 篇」流程；绑定 Cron 或定时触发；工具开放 `group:fs`、`group:web`、browser、PDF、Image Gen、Search。
- **support / 其他**：若存在，可限制为 `tools.profile: "messaging"` 等，避免误动 wechat_factory。

### D.3 指令与记忆

- **INSTRUCTIONS.md**：放入 DESIGN.md 第 6 节的每日动作清单；可追加「遇到 PDF 无法解析时改用 web_snapshots」「标题从 viral_titles.txt 中选型」等规则。
- **MEMORY.md / memory/YYYY-MM-DD.md**：记录已选题、已写标题，配合 `memory_search` 做去重与连续性。
- **TOOLS.md**：如上 Part B，用自然语言描述每个工具在本项目中的用途与路径约定，减少 Agent 误用。

### D.4 定时运行方式

- **方式 1**：系统 Cron 调用 OpenClaw CLI，例如每日 8:00 执行一次「wechat-editor 执行今日任务」。
- **方式 2**：OpenClaw 的 `cron` 工具（若已启用）在网关内配置每日任务，触发对应 Agent。
- **方式 3**：外部调度器（如 GitHub Actions、Jenkins）在指定时间调用 OpenClaw API 或 CLI。

任选其一，确保进程异常退出时有重启（如 Cron 每分钟检查进程是否存在并拉起）。

### D.5 配置与密钥

- **MCP API Keys**（Brave/Google Search、DALL·E 等）：放在 `~/.openclaw/` 或环境变量，不要写入 workspace 或提交到 Git。
- **openclaw.json**：可引用环境变量（若支持），例如 `"args": ["-y", "some-mcp", "--api-key", "${BRAVE_API_KEY}"]`。

---

## Part E: MCP Server 配置示例（openclaw.json 片段）

以下为**示例结构**，实际包名与参数以官方文档为准。请勿将 API Key 写进版本库。

```json
{
  "mcpServers": {
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

- **brave-search**：提供实时搜索，对应 Part B 的 Deep Search。
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
