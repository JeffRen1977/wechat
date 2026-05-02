<!-- 备选标题：1.悬念型｜AI 代理全面入侵，安全部门该先盯哪一层？ 2.收益型｜微软 Agent 365 上线：三步控制企业里所有 AI 助手 3.对比型｜别只盯 Copilot，Agent 365 把影子 AI 一网打尽 4.警示型｜没有治理的 AI 代理=下一个数据泄露入口 5.好奇型｜Windows 365 for Agents 到底给企业什么安全缓冲？ 选用：第2个 -->
# 微软 Agent 365 上线：三步控制企业里所有 AI 助手

## 影子 AI 爆炸，真正的风险不是「有没有 Copilot」
微软安全博客 5 月 1 日官宣：Agent 365 正式 GA，并同步推出一系列预览功能。微软的判断很直接——**AI 代理已经无处不在**：从 Teams、Copilot 到员工私装的 OpenClaw、Claude Code，再加上层出不穷的 SaaS 助手。问题不在于它们出现，而是它们扩散极快、跨端运行、权限边界模糊，安全团队根本看不见、管不了。

> ⚠️ 当一个代理可以串联工具、调用数据并与别的代理对话时，「好心的自动化」随时可能演变成数据外泄、越权操作。

## Agent 365 给出的 7 件「治乱」新武器
微软把 Agent 365 定位为企业的「AI 代理控制平面」，此次发布涵盖：

1. **观察、治理、安控三合一**：无论代理是代人执行（delegated access）还是自带账号，都能接入同一管控视图。
2. **发现影子 AI**：借助 Microsoft Defender + Intune，在 Windows 终端上侦测本地代理（首批支持 OpenClaw，后续推 GitHub Copilot CLI、Claude Code），还能直接下达阻断策略。
3. **SaaS 代理登记册**：把微软及生态伙伴的云端代理纳入统一清单，标注权限范围、调用 API、合规状态。
4. **Windows 365 for Agents**：给自治代理配置受管虚拟工作站，限定可用工具、网络出口，强制开启 DLP 与审计日志。
5. **策略模板**：按场景（如邮件分拣、开发助手）预置分级管控，快速落地「只读 vs. 可写」等权限差异。
6. **合作伙伴生态**：开放 Copilot Partner Directory，方便企业挑选深度安全分析、合规自动化或托管服务商协同。
7. **全球支持计划**：微软联合 SDC（软件开发商）共建集成，让第三方代理默认兼容 Agent 365 的治理流程。

![配图](wechat_factory/05_assets/images/2026-05-01_INBOX_fig1.png)

## 三步落地：先看见，再圈住，最后审计
微软在文中给出的落地建议，其实可以转成任何安全团队的「三步走」：

1. **端点普查**：利用 Defender + Intune 打开 Shadow AI 页面，列出所有本地代理、运行方式、设备归属。先做只读监控，再决定封堵策略。
2. **云端登记**：把所有 SaaS 代理纳入 Agent 365 registry，统一查看它们请求的作用域，结合合规策略自动审批/拒绝。
3. **沙箱运行 + 日志**：对高权限或自治代理，迁入 Windows 365 for Agents，限制联网、工具集并强制留痕。**没有日志的自动化就是黑箱**。

> 💡 先用「只读」确保可见性，等抓住运行规律后再给写权限，是避免大嘴巴代理泄密的安全底线。

![配图](wechat_factory/05_assets/images/2026-05-01_INBOX_fig2.png)

## 谁最该关注？
- **安全团队**：终于有办法把所有代理拉到同一仪表板，联合 DLP、SIEM、SOAR 做闭环。
- **IT / 终端管理**：Intune 策略可以直接阻断常见的 OpenClaw 启动方式，或按设备群组下发白名单。
- **业务负责人**：借策略模板快速评估一个代理的风险级别，避免试点项目失控。
- **生态伙伴 / SDC**：尽快把自家代理接入 registry，才能在大企业招标中「开箱即管」。

## Action Items
1. ✅ 立即盘点公司里正在跑的所有 AI 代理（含本地、SaaS），并标记数据触达范围。
2. ✅ 对高权限代理启用 Windows 365 for Agents 或等效沙箱，强制开启 DLP 和操作日志。
3. ✅ 选用微软或伙伴提供的策略模板，把代理按风险分级管理，明确「只读」「可写」「可联动」差异。

如果这篇内容对你有用，欢迎点赞、在看，也别忘了关注公号获取更多企业级 AI 安全策略。你的团队目前最头疼的「影子 AI」是哪一种？评论区聊聊。

来源：[Microsoft Security Blog｜Microsoft Agent 365, now generally available, expands capabilities and integrations](https://www.microsoft.com/en-us/security/blog/2026/05/01/microsoft-agent-365-now-generally-available-expands-capabilities-and-integrations/)
