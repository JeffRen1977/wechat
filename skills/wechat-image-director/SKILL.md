---
name: wechat_image_director
description: Emotion-first image briefs — subject + composition + style + light; domain palettes; complements gemini-gen-images.py.
---

# WeChat Image Director（视觉导演 / Image_Gen_Master）

自动化仍走 `scripts/gemini-gen-images.py`（`run-gemini-images.sh`）。**在调用脚本之前**，先在稿子里定调，可显著提升质感。

## 1. 先定「情绪」，再写画面（不要只丢一句「配张图」）

对当前文章用 **一句话**写清 **Emotional_Goal**（与 `article_style.md` 一致）：

- **EDU：** 缓解焦虑 / 点亮方法感  
- **MED：** 踏实、可信、不恐吓  
- **FIN：** 冷静、清晰、有掌控感  

然后为 **封面** 与 **fig1 / fig2** 各写一句英文 brief，结构固定为：

**`主体 (subject) + 构图 (composition) + 风格 (style) + 光影 (light)`**

示例（教育）：  
*One focused student at a desk, soft side light through window, rule-of-thirds, 3D high-quality illustration, warm rim light, minimalist color.*

## 2. 风格关键词池（可混用，每次选 2～4 个）

- `3D high-quality illustration` / `minimalist flat design`
- `editorial magazine cover`
- `soft natural daylight` / `cinematic rim light`
- `leica photography style`（偏纪实、克制）
- `shot on iPhone 15 Pro`（生活感、真实焦段）
- 领域色：EDU 暖色、MED 青白信任感、FIN 深蓝极简（与脚本默认一致）

画面 **禁止** 出现可读文字（脚本已加规则）。

## 3. 结构配合脚本

- 每个 **H2** 下先有 **带具象名词** 的 2～4 句，再插 `![配图](wechat_factory/05_assets/images/YYYY-MM-DD_PREFIX_figN.png)`。
- fig1：痛点 / 情境向 H2；fig2：How / 方案 / 总结向 H2。

## 4. 与代码的衔接

- 脚本会读取 **标题 + H2 段落文字** 拼 prompt；你在 brief 里想的 **情绪与关键词** 应体现在 **H2 行文** 中，脚本才能对齐。

When images feel generic: refine H2 concrete nouns, re-run `./scripts/run-gemini-images.sh <article.md>`, or set `GEMINI_IMAGE_MODEL` env if needed.
