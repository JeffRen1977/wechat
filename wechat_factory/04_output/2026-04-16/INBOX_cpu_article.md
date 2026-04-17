<!-- 备选标题：1. 悬念型｜Nuvia 原班人马再出山，为何又要重做 CPU？ 2. 警示型｜还在等 GPU？别忽视这支要“重写硅片规则”的 CPU 创业队 3. 对比型｜与其等巨头迭代，Nuvacore 想直接跳到 AI 时代底座 4. 收益型｜读懂 Nuvacore 的野心，提前想好 AI 服务器的新分工 5. 好奇型｜Sequoia 押注的 Nuvacore，究竟要造一颗怎样的芯片｜选用：第2个 -->
# Nuvacore 再次喊话要“重写硅片规则”，靠谱还是噱头？

> 当年把 Apple A 系列推上巅峰、又创办 Nuvia 的那拨人，再次离开 Qualcomm，带着一家公司叫 Nuvacore 回来了。

## 谁在 Nuvacore 下注？

创始三人——Gerard Williams III、John Bruno、Ram Srinivasan——履历堪称 Arm 阵营天花板：

- Williams 是 iPhone 从 A7 到 M1 的 CPU 架构“总工”，后在 Nuvia、Qualcomm 掌舵高性能核心。
- Bruno 管过苹果和 Qualcomm 的系统架构，擅长把算力、功耗和 IO 拉到平衡点。
- Srinivasan 则是 SoC 流程里最懂“怎么把理念落成芯片”的那类设计师。

Sequoia Capital 直接领投，让这支团队在离开 Qualcomm 几个月后就启动了 Nuvacore，官方口号写着「Engineered for Altitude」。翻译一下：目标锁在数据中心、AI 基础设施，并不是消费级晶片的“再就业”。

## 他们想解决什么瓶颈？

Nuvacore 的宣言直指“旧势力只会在既有架构上打补丁”。现实是，AI 时代的通用 CPU 任务确实发生了变化：

![配图](wechat_factory/05_assets/images/2026-04-16_INBOX_cpu_fig1.png)

- **全天候 AI 服务**：推理、Agent、搜索编排越来越像“长跑”，CPU 要给 GPU、加速卡喂数据，同时保证延迟稳定。
- **功耗与面积**：数据中心里每 1 瓦都要算入 TCO，靠堆核心的传统做法很难持续。
- **数据搬运**：AI 工程不再是“算完就走”，而是持续吸入海量上下文。CPU 是否优化了大带宽缓存、IO 通道，直接决定整体效率。

Nuvacore 说自己要做“高通量、高效能、能维持长时间饱和负载”的新一代核心，听上去既像 marketing，也确实击中了云厂商这两年的焦虑。

## 新公司能带来哪些变量？

> “为 AI 和基础设施而生的清洁纸（clean-sheet）设计。”——Nuvacore 官网

![配图](wechat_factory/05_assets/images/2026-04-16_INBOX_cpu_fig2.png)

我们可以从他们过往的打法推测几个方向：

1. **架构很可能仍是 Arm**：客户都有 Arm 定制经验，生态成熟，不必从零教育开发者。
2. **与 AI 加速器“互补”**：既然目标是 agentic computing，他们可能在链路上加速指令调度、内存一致性，甚至为多沙箱 Agent 做线程级 QoS。
3. **面积/功耗比**：Williams 多次强调“性能每平方毫米”，意味着不会盲目追求超大核，而是把 IPC 和缓存策略做到极致。

如果这些都成立，Nuvacore 可能成为云厂商“自研之外”的第三条路径：买现成 IP，却能拿到为 AI 调过的底座。

## 到底要等多久？

Nuvia 的历史提醒我们：

- 设计期至少 18–24 个月；
- 还要找代工、流片、认证，量产更久；
- 前一家公司最终被 Qualcomm 收购，路线又转回客户端。

所以 Nuvacore 想真正“改写硅片规则”，最快也要 2028 年后才看得到产品。期间它得穿过三道坎：

1. **资金 vs. 研发周期**：Sequoia 可以让它活下来，但数据中心客制芯片的烧钱速度已完全不同于 10 年前。
2. **生态信任**：云巨头已经有自研计划，要说服他们再买一颗第三方 CPU，必须拿出被验证的性能指标。
3. **并发竞争**：Arm 自己也下场做数据中心芯片，RISC-V 社区同样在提速，窗口期并不宽。

## 现在可以先做什么？

1. ✅ **复盘你家 AI 工作负载里 CPU 真实瓶颈**：IO？内存带宽？还是调度？以后跟 Nuvacore 或其他新架构谈合作时，才知道要什么。
2. ✅ **提前规划“CPU+加速卡”分工**：无论 Nuvacore 成不成，AI 数据中心都会走向专业化分层，流程和软件栈要提前适配。
3. ✅ **关注 Arm 与开源 ISA 的政策/授权变化**：新创和大厂都在抢定制权，合同条款可能影响你的部署路线。

如果这次的新创让你对 AI 服务器的底层分工有新想法，欢迎点赞、在看，也别忘了关注我们；你最希望下一代 CPU 提供什么“AI 原生”能力？评论区聊聊。

参考与链接：

1. [Legendary Qualcomm, Apple, and Nuvia alumni form new CPU startup — Nuvacore promises to 'rewrite the rules of silicon' | Tom's Hardware](https://share.google/0OsZYFzjJ0P73OtZH)
