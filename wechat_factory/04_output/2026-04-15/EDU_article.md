# 大学部署 AI 的“施工图”：从 Instructure 的实战学来这 4 步

## 视频要点速览
Craft Conference 发布了《[Transforming Education: Applying AI to Universities](https://www.youtube.com/watch?v=owhWhxXg9JI)》，由 Instructure CTO Zach Pendleton 讲述他们在 Canvas 生态里落地 AI 的全过程：
- **双线教研**：工程团队与教学设计师共建“AI Prompt Library”，让教师可直接调用教案优化、助教机器人，而开发者同步把提示语写成可测试的组件。
- **伦理与可解释**：每个功能上线前都要回答三件事——它如何保护学生数据、是否提供退出机制、能否解释推荐逻辑。
- **迭代节奏**：放弃传统的季度版本，改为“周-月-季”三层循环：快速原型、核心场景试点、再回灌产品路线图。
- **教师成长路径**：把培训分成“AI 增能（怎么省时）”“AI 辨识（怎么防抄袭）”“AI 创新（怎么做跨学科任务）”三层，降低阻力。

> “AI 功能上线前，先问清楚它解决的是谁的痛点，不要把开发团队的兴奋强加给老师。”——Zach Pendleton

![配图](wechat_factory/05_assets/images/2026-04-15_EDU_fig1.png)

## 为什么值得各大高校照抄？
- 这是一个成熟 LMS 厂商交出的“内部维基”，尤其是如何在教师抱怨与工程师冲劲之间找到平衡。
- 视频给出非常具体的组织打法：prompt 模板化、可观测的 A/B 指标、以及面向校董的安全问卷。
- 对刚开始试点 AI 的高校来说，既能学到工具链（Canvas、LLM、内容过滤器），也能学到治理框架。

![配图](wechat_factory/05_assets/images/2026-04-15_EDU_fig2.png)

## Three Action Items
1. **搭建“教学 + 技术”共创室**：仿照 Instructure，把教学设计师、IT、学术诚信办拉到一间线上 war room，先列出 10 个常见课堂痛点，再逐一匹配 AI 解决方案。
2. **制定 Prompt Style Guide**：借鉴视频里“可测试 prompt”理念，要求每个模板都包含输入范围、语气、引用格式，降低教学差异。
3. **发布 AI 使用公约**：把伦理问答（开放/退出、数据用途、人工审阅）写成对外透明的 FAQ，安抚学生与家长。

## 后续可以怎么扩展？
- 结合学校现有 LMS（Canvas、Moodle 或自研），建立“AI 插件白名单”，并配套使用日志与安全审计。
- 让教务处每月发布一次 “AI 课堂案例”，促进跨学院交流，也方便评估哪些功能真正在省时提效。

你们学校在部署 AI 时最大的阻力来自哪里？欢迎在评论区继续讨论。