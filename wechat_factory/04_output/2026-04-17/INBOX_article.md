<!-- 备选标题：1.为什么谷歌要让任何 Agent 3 倍速写 Android App？ 2.用 Android CLI+Skills，搭建 AI 代工流水线最快 3X 3.传统 Android Studio vs 新 Agent 工具箱：效率差在哪 4.别让你的 Agent 乱改 SDK：Android 官方技能库来了 5.一篇看懂 Android CLI、Skills、Knowledge Base 怎么串｜选用：第2个 -->
# 用 Android CLI+Skills，搭建 AI 代工流水线最快 3X

还在为「让 AI 写 Android App 结果越帮越忙」而抓狂吗？谷歌刚把 agent 专用的 CLI、技能库和知识库打包上线，官方实测可以让 LLM 代工流程节省 70% token、提速 3 倍，这可是难得的「把内部自用工具全放出来」。

## 为什么谷歌突然把 agent 工具箱公开

过去一年大家都想让大模型写 App，可是**环境配置、依赖安装、模拟器连接**这些「看似简单」的机械活总是把自动化流程卡死。Gemini、Claude、Codex 等 agent 被迫靠搜索旧文档来补课，结果不是装错 SDK 就是跑旧模板。

> 谷歌这次给出的答案是：直接把「应该怎么做」写成 CLI 指令和技能卡，让任何代理都能照着执行。

这波发布集中在三个组件：全新的 Android CLI、Android Skills 仓库，以及实时更新的 Android Knowledge Base。组合拳的核心，就是把「指令 + 最佳实践 + 最新文档」绑定在一起，避免 agent 乱猜。

## Android CLI 如何把 token 浪费砍掉 70%

先看 CLI。本质上它是一个面向 agent 的轻量入口：`android create` 几秒钟就生成官方模板，默认把推荐架构、Compose 配置、Gradle 版本一次带齐；`android sdk install` 只下必要组件，不再让 LLM 反复问「要不要装 platform-tools」。

更关键的是设备和运行命令：`android emulator`、`android run` 能直接创建虚拟机、安装 APK、回传日志。Agent 不用再摸索 GUI，脚本里就能搞定 build→deploy 全链路。

![配图](wechat_factory/05_assets/images/2026-04-17_INBOX_fig1.png)

谷歌内部测试显示，有了这些命令，agent 完成「搭环境+起项目」的 token 消耗比传统方式少了 70%，时间缩短到原来的三分之一，还顺便解决了多人协作时「谁的 SDK 是最新的」这种经典问题。

## Skills + Knowledge Base 让 LLM 不跑偏

CLI 管住了动作，但 LLM 仍需要任务书。为此，谷歌把技能写成了类似我们熟悉的 `SKILL.md`：当你触发「Navigation 3 迁移」「Edge-to-edge 适配」等需求时，agent 自动读到分步指令、风险提示和最佳依赖版本。开发者也能把自家规范塞进同一个仓库，让自定义技能和官方技能共存。

另一个重要拼图是 Android Knowledge Base。它是一个可被 CLI、Android Studio 甚至独立 agent 调用的检索接口，涵盖 Android Docs、Firebase、Google Developers、Kotlin 最新文章。**哪怕 LLM 的训练数据已经停在去年，也能即时查到本周更新的指导**。

> 简单理解：Skills 解决「怎么做」，Knowledge Base 解决「查什么」，两者叠加，agent 才不会胡乱引用旧方案。

## 最终目的：把草稿带回 Android Studio 精修

谷歌没打算让你永远离开 IDE。官方流程是：用 agent + CLI 快速搭建原型、跑通 CI，再把工程无缝拉进 Android Studio。新版 Studio 里自带 Agent 与 Planning Mode，可以在了解项目上下文的情况下继续写 UI、调试性能，还能通过 AI 驱动的 New Project Flow 快速生成新想法的脚手架。

![配图](wechat_factory/05_assets/images/2026-04-17_INBOX_fig2.png)

这意味着真实团队可以把「重复性劳动」交给 agent，把「体验打磨、跨设备适配」交回给开发者。最终产物依然是多端统一的高质量应用，而不是一次性 Demo。

---

## Action Items

1. ✅ 立即访问 [d.android.com/tools/agents](https://d.android.com/tools/agents) 下载 Android CLI，并在脚本里测试 `android create`、`android run` 的串联效果。
2. ✅ 克隆 [Android Skills 仓库](https://github.com/android/skills)，挑一两个与你团队痛点相符的技能，按模板写成自定义指令，让 agent 能执行公司规范。
3. ✅ 在代理或 CI 流程里接入 Android Knowledge Base 检索，确保每次引用的 API/架构建议都是最新版本。

如果这篇对你有用，欢迎点赞、在看；想持续收到类似的 AI 工具解读，点个关注不迷路。你最想先让 agent 接管哪段 Android 流程？评论区聊聊看。

**来源**：[Android Developers Blog｜Build Android apps 3x faster using any agent](https://android-developers.googleblog.com/2026/04/build-android-apps-3x-faster-using-any-agent.html)
