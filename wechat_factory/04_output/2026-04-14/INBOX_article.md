<!-- 备选标题：1. 把 Claude Code 用在非技术岗位的 3 秘诀 2. 别只让 Claude Code 写代码：它还能做销售、PPT、搜资料 3. 非技术团队也能用 Claude Code？三步套公式 4. Claude Code + 非技术任务：演示、知识库、销售三合一 5. 用 Claude Code 做 PPT 找客户，真的靠谱吗？ 选用：第2个 -->
# 别只让 Claude Code 写代码：它还能做销售、PPT、搜资料

身边很多团队已经把 Claude Code 当成写 Bug 的「万能键」，可 Towards Data Science 最新的一篇实践稿提醒我们：这个工具真正的红利可能在非技术侧。作者 Eivind Kjosbakken 把日常的演示制作、知识检索、销售拓客全部交给 Claude Code，效率直接翻倍。与其守着 IDE 等工位，不如把这套流程搬到业务场景里。

## 为什么非技术任务更需要 AI 代理

营销、客服、产品经理看似「不用写代码」，但 90% 的时间都在电脑前重复搬运信息——排 PPT、找旧资料、回 CRM。Claude Code 的价值不是让人人学编程，而是让它在本地/云端帮你批量写文档、调用 API、整理目录。

> **作者的第一反应已经变成：「接到任务先问——Claude Code 能帮我做吗？」**

具体来说：
- 做演示不用重搭模板，直接让 Claude 用 LaTeX 生成 PDF 幻灯，统一品牌色；
- 找资料不用来回切换 Notion、邮件、Drive，只要开放 API key 就能一次搜遍；
- 销售拓客也能让它自动找 ICP、写脚本、更新 CRM。

![配图](wechat_factory/05_assets/images/2026-04-14_INBOX_fig1.png)

## Claude Code 的三个非技术场景

### 1. 演示/提案

作者把所有演示素材放在同一个文件夹，让 Claude 读取旧 deck，继承常用的色板、图表、段落结构。命令很简单：「用 LaTeX 生成一份 X 主题的演示，保留公司模板，并安装所需包。」生成的 PDF 每页就是一张幻灯，大纲、图示、图例都能复用，后续只需微调。

### 2. 知识库秒搜

把邮箱、Notion、Google Drive、Slack 的 API key 配好后，Claude Code 就能像内部 Google 一样调取资料。它可以批量搜索关键词、串联上下文、甚至把相关文件复制到临时文件夹，这比人工先猜在哪个应用里高效太多。作者说光这一招每周至少省掉数小时。

### 3. 销售拓客

Claude Code 可以：
- 根据 ICP 条件去网页上找潜在客户；
- 为每个客户生成定制化文案（职位、痛点、地区一个不落）；
- 把名单、沟通记录同步回 CRM，自动清理旧数据。

作者还维护了一个「Sales with Claude」文件夹，里面放公司简介、客群画像、话术示例。这样 Claude 每次开工都有上下文，不需要重新培训。

![配图](wechat_factory/05_assets/images/2026-04-14_INBOX_fig2.png)

## 如何把经验落到团队里

1. **任务拆解表**：列出团队里最费时的 5 个非技术任务，标注输入文件夹、输出格式、评估标准，再交给 Claude 去跑第一版。
2. **资料接入清单**：整理所有常用 SaaS 的 API key / 导出权限，用 `.env` 或保险箱规范管理，确保 Claude 有合法访问而且可撤销。
3. **成果库**：演示、邮件、销售脚本都存进固定目录，并写一份 `README` 教 Claude 如何继承旧作品，避免每次从零开始。

---

### Action Items

1. **挑一项非技术任务做试点**：比如本周的市场周会演示，全程交给 Claude Code + LaTeX 生成，再人工校对。
2. **接入统一检索**：为邮箱、Notion、Drive、Slack 配好只读 API key，写一个提示词模板让 Claude 一次搜全。
3. **打造业务资料夹**：建立「Claude_Sales」或「Claude_Operations」文件夹，内含 ICP、品牌语气、常用 KPI，供后续任务复用。

如果这篇对你有帮助，欢迎点赞、在看；想持续追踪「AI 工具如何落地业务」，点个关注不走失。你最想先让 Claude Code 接管哪项琐碎任务？评论区一起出题。

**参考与链接**

- [How to Apply Claude Code to Non-technical Tasks（Towards Data Science）](https://towardsdatascience.com/how-to-apply-claude-code-to-non-technical-tasks/)
