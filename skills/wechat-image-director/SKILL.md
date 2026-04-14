---
name: wechat_image_director
description: Map article sections to concrete English image prompts; domain color/style for Gemini cover and fig1/fig2. Complements scripts/gemini-gen-images.py.
---

# WeChat Image Director（视觉导演）

Automated images use `scripts/gemini-gen-images.py` (via `run-gemini-images.sh`). The script reads **H2 sections + first lines** to build prompts. You can improve results **before** generation by:

## 1. 结构配合脚本

- Each **H2** should be followed by **2–4 sentences of concrete nouns**（人、场景、物体、数据关系）—脚本会把 H2 与小节正文拼进配图 prompt。
- Place `![配图](wechat_factory/05_assets/images/YYYY-MM-DD_PREFIX_figN.png)` near the **H2 that best matches** the visual you want for fig1 / fig2.

## 2. 分领域风格（与代码一致，供你写稿时心里有数）

| Prefix | 视觉关键词（英文场景更易出好图） |
|--------|----------------------------------|
| **EDU** | warm learning space, soft daylight, modern edtech, friendly — **not** cluttered text |
| **MED** | clean clinical trust, soft teal/white, wellness — **no** gore, no body horror |
| **FIN** | minimalist business, deep blue/white, abstract charts as shapes — **no** readable numbers/labels on screen |
| **INBOX** | modern editorial, neutral slate + one accent — single clear subject |

## 3. 若用手写英文 prompt（调试用）

- **禁止**在画面里出现可辨认文字（脚本已加 no-text 规则）；用构图、光影、材质表达主题。
- 用**一句具体场景**代替「一张关于教育的图」：例如 *A small group of students around a holographic lesson display, warm rim light, 8k illustration style.*

## 4. 图文相关性

- fig1：优先对应 **第一个实质性 H2**（痛点/情境）。
- fig2：优先对应 **How/方案/总结向 H2**。

When the user says images feel generic: check H2 density, move placeholders, or suggest re-running `./scripts/run-gemini-images.sh <path/to/article.md>` after edits.
