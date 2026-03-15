# Step-by-Step Implementation Guide — WeChat 公众号自动化

本文档基于 [DESIGN.md](./DESIGN.md)，给出**分阶段实现步骤**、**OpenClaw 技能与工具说明**、**测试方案**以及**与 OpenClaw 的协作方式**。每个 Skill/工具都会说明其在 OpenClaw 中的**功能与用途**。

---

## Part A: Implementation Phases (Step-by-Step)

### Phase 0: Prerequisites

| Step | Action | Purpose |
|------|--------|---------|
| 0.1 | 安装并配置 OpenClaw（Gateway + 至少一个 Agent） | 多智能体运行环境 |
| 0.2 | 准备 Claude API（或兼容端点）与 Ollama 本地 | 认知/创作用云端模型 + 初筛/翻译用本地模型 |
| 0.3 | 初始化 Git 仓库于 `wechat/` 或 `~/.openclaw/workspace`（若 workspace 指向此处） | 版本控制与回滚 |

### Phase 1: Workspace & wechat_factory 对接

| Step | Action | Purpose |
|------|--------|---------|
| 1.1 | 确定 workspace 根目录：`~/.openclaw/workspace` 或项目内 `wechat/` | 所有文件类工具的相对路径以此为基准 |
| 1.2 | 若 workspace 在 `~/.openclaw/workspace`：将 `wechat_factory` 复制或软链到 `~/.openclaw/workspace/wechat_factory` | 让 Agent 能通过相对路径访问 01_sources～05_assets |
| 1.3 | 若 workspace 即 `wechat/`：则 `wechat_factory/` 已在项目内，无需迁移 | 开发与生产可共用同一目录 |
| 1.4 | 在 workspace 根目录确保存在 `AGENTS.md`、`SOUL.md`、`TOOLS.md`（OpenClaw 约定） | 会话加载与工具可见性 |

### Phase 2: MCP Skills & Tools 配置

| Step | Action | Purpose |
|------|--------|---------|
| 2.1 | 在 `~/.openclaw/openclaw.json` 中配置 `mcpServers`（见 Part B） | 为 Agent 提供搜索、浏览器、PDF、文件、图像等能力 |
| 2.2 | 在 workspace 的 `TOOLS.md` 中列出本项目会用到的工具及用途（给 Agent 看的说明） | 引导 Agent 在正确场景调用正确工具 |
| 2.3 | 可选：在 `workspace/skills/` 下为 wechat 流水线写专用 Skill（如 `wechat-daily-editor`），在 SKILL.md 中引用 MCP 工具与步骤 | 把「每日 5 篇」流程固化为可复用技能 |
| 2.4 | 重启 Gateway，执行 `openclaw mcp list` 校验 MCP 连接 | 确保工具在运行时可用 |

### Phase 3: Agent 指令与每日流程

| Step | Action | Purpose |
|------|--------|---------|
| 3.1 | 为负责「公众号内容」的 Agent 创建或指定目录（如 `~/.openclaw/agents/wechat-editor/`） | 独立身份、workspace、记忆 |
| 3.2 | 在该 Agent 的 `INSTRUCTIONS.md`（或等价指令文件）中写入 DESIGN.md 第 6 节的「每日动作清单」 | 驱动扫描→研读→拟题→撰稿→归档→配图 |
| 3.3 | 将该 Agent 的 `workspace` 指向包含 `wechat_factory` 的目录 | 保证读写路径一致 |
| 3.4 | 配置 Cron 或 OpenClaw 内置调度，每日定时触发该 Agent 的「执行今日任务」 | 自动化日更 |

### Phase 4: 外部工具与发布链

| Step | Action | Purpose |
|------|--------|---------|
| 4.1 | 安装并配置 Ollama，拉取 Qwen2.5 / Llama3.3，用于初筛、翻译、去重 | 降低成本，减少 Claude 调用量 |
| 4.2 | 安装 Pandoc 或 Markdown-to-WeChat，编写脚本将 `04_output/YYYY-MM-DD/*.md` 转为公众号 HTML | 完成发布前格式转换 |
| 4.3 | 配置系统 Cron：定时运行 OpenClaw 任务 + 可选 Git 提交（如每日 23:00 提交 04_output） | 稳定性与可回滚 |
| 4.4 | 在 02_knowledge_base 与 03_templates 中逐步填充领域知识与标题句式 | 提高选题与文案质量 |

### Phase 5: 测试与上线

| Step | Action | Purpose |
|------|--------|---------|
| 5.1 | 单链路测试：手动触发一次「单领域单篇」（见 Part C） | 验证 感知→认知→创作→存储 全链路 |
| 5.2 | 工具级测试：分别验证搜索、抓取、PDF 解析、写文件、图像生成 | 快速定位故障点 |
| 5.3 | 日产出测试：连续 2～3 天跑满 5 篇，检查 04_output 与 05_assets | 验证产能与稳定性 |
| 5.4 | 发布链测试：Markdown → HTML → 公众号后台粘贴（或 API） | 验证最后一公里 |

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
