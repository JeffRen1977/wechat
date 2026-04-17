<!-- 备选标题：1. 好奇型｜Gemini CLI 里突然多了“子代理”，到底能干嘛？ 2. 收益型｜用 subagents 打造专属 AI 团队，命令行效率起飞 3. 警示型｜多代理并行虽爽，别让自家 CLI 进入“失控编辑模式” 4. 对比型｜CLI 里的多线程 vs. 传统单回话，你更需要哪种 5. 悬念型｜Google 让 Gemini CLI 雇了一支顾问团，你要不要也来一套？｜选用：第2个 -->
# Gemini CLI 上线 subagents：命令行也能“雇一支 AI 团队”

> 以前让模型做大任务，要么拆 prompt，要么被无穷的上下文拖慢。现在 Gemini CLI 直接引入「subagents」，帮你把繁琐步骤外包给小帮手。

## Subagents 到底是什么？

Google 官方给出的定义：subagent = **一个带独立上下文、独立系统指令、独立工具箱的专家代理**。主 CLI 负责战略拆解，具体子任务交由最匹配的 subagent 去执行，再把汇总结果塞回主对话，使主会话保持轻量。

- 每个 subagent 拿到的是自己的 API 密钥/工具清单，不会污染主上下文。
- 它们可以在后台跑几十次工具调用，最后只返回一份摘要或格式化答复。
- 主会话因此更“干净”，成本和延迟也更可控。

换句话说，这是一套「命令行里的微服务编排」。

## 为什么 CLI 需要“多线程团队”？

![配图](wechat_factory/05_assets/images/2026-04-16_INBOX_gemini_fig1.png)

过去我们让 AI 改一整个仓库，往往卡在两件事：

1. **上下文爆炸**：一轮命令塞太多文件，下一轮就忘了前文。
2. **任务串行**：调研、写代码、跑测试都堆在同一上下文，效率被最慢那一步拖住。

Subagents 把这些步骤剥离出去：可以一个 subagent 专做日志分析、一个负责查文档、一个跑批量重构。主 CLI 只收结果，像管理顾问报告一样挑重点。

## 自己写一个“团队成员”也不难

![配图](wechat_factory/05_assets/images/2026-04-16_INBOX_gemini_fig2.png)

子代理是用 **带 YAML frontmatter 的 Markdown** 定义的：

- 放在 `~/.gemini/agents` 可全局复用，放在仓库 `.gemini/agents` 就能随项目共享。
- 你可以限定它能用的工具（read_file、glob、web_fetch…）、模型、语气，比如官方示例里的 frontend specialist。
- 也能随 Gemini CLI 扩展打包；装一个扩展，自动多一名专家。

调用方式也像在群聊里 @ 人：输入 `@frontend-specialist` 或 `@codebase_investigator`，就能让它在隔离上下文里跑完任务，最后回一条长总结。`/agents` 命令能随时查看自己现有的子代理名单。

## 并行=效率，也=风险

> 官方提醒：多个 subagent 并行编辑代码时，**极易互相覆盖**；请求也会成倍叠加，很快打满用量配额。

所以：

- 并行适合调研、分包扫描、批处理，而不是在同一文件里混改。
- 需要写数据的任务可考虑排队或加锁，别让两个代理抢同一资源。
- 主 CLI 仍要当「调度员」，明确谁负责哪一步，返回什么格式。

## 立刻可以做的 3 件事

1. ✅ **梳理团队里最常重复的 CLI 流程**（批量重构、日志排查、翻阅文档），挑出一两件事写成自定义 subagent。
2. ✅ **给 subagent 制定“工具白名单”**，例如只能读文件不能写，降低误操作风险。
3. ✅ **演练一次并行子任务**：比如让 generalist 批量更新 license，codebase_investigator 同时生成依赖图，确认冲突如何解决。

如果你也准备给命令行安上一支 AI 小分队，欢迎点赞、在看并关注我们；哪种专长的 subagent 最值得先写？评论区聊聊。

参考与链接：

1. [Subagents have arrived in Gemini CLI - Google Developers Blog](https://share.google/r1JJhQngwc3I5BCzO)
