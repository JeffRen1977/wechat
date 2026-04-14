# 发布目标：带图、正确排版、存入公众号草稿箱

## 1. 目标

- **内容**：每篇文章带**封面图**与（可选）正文内**配图**，版式符合公众号规范。
- **排版**：正文为微信公众号支持的 HTML，标题/摘要/正文结构正确，图片来自已上传素材。
- **落点**：自动**存入微信公众平台草稿箱**，可在公众平台后台查看、修改后群发或发布。

## 2. 微信草稿箱 API 要点

- **新增草稿**：`POST https://api.weixin.qq.com/cgi-bin/draft/add?access_token=ACCESS_TOKEN`
- **单篇图文 (news)** 必填：
  - `title`：标题（≤32 字）
  - `content`：正文 HTML（≤2 万字符；文内图片 URL 须来自「上传图文消息内图片」接口）
  - `thumb_media_id`：封面图**永久素材 media_id**（必填）
- **封面图**：须先通过「上传永久素材」得到 `media_id`，再作为 `thumb_media_id` 提交。
- **正文内图片**：须先调用「上传图文消息内的图片获取 URL」，将 HTML 中的图片替换为该接口返回的 URL。
- **凭证**：需公众号的 `access_token`（通过 appid + secret 获取）。

## 3. 与本项目流水线的衔接

| 步骤 | 产出 | 说明 |
|------|------|------|
| 创作层 | `04_output/YYYY-MM-DD/*.md` + `05_assets/images/YYYY-MM-DD_*_cover.png` | 已有；确保每篇有对应封面图 |
| 排版 | 将 Markdown 转为微信合规 HTML，控制字数与标签 | 使用 `scripts/md2wechat.sh` 或增强版，输出带样式的 HTML |
| 上传封面 | 将 `05_assets/images/` 下封面上传为永久素材 → 得到 `thumb_media_id` | 见 `scripts/wechat-draft-upload.sh` 或等价脚本 |
| 上传正文图 | 正文 HTML 中的图片先上传「图文内图片」→ 替换为返回 URL | 同上脚本或单独步骤 |
| 提交草稿 | 调用 `draft/add`，传入 `articles[]`（title、author、digest、content、thumb_media_id 等） | 同上 |

## 4. 凭证与安全

- **access_token**：可临时用 `APPID` + `SECRET` 在服务端换 token，或由外部系统提供 token。
- 勿将 `SECRET` 或长期 token 提交到 Git；使用环境变量或 `~/.openclaw/` 下配置文件（不纳入版本库）。

## 5. 脚本与文档

- **scripts/wechat-draft-upload.sh**（或等价的 Python 脚本）：读 `04_output/YYYY-MM-DD/` 与 `05_assets/images/`，上传封面、组 articles、调用 draft/add。需配置 `WECHAT_APPID`、`WECHAT_SECRET` 或 `WECHAT_ACCESS_TOKEN`。
- **IMPLEMENTATION.md** Phase 4.2 / 4.3：已含 Markdown→HTML；可增加「上传草稿」一步及调用方式。

完成上述后，流水线末端为：**本地 04_output + 05_assets → 转 HTML → 上传图片 → 提交草稿箱**，在公众号后台即可看到带图、正确排版的草稿。

## 6. 为什么会出现「同一篇两份草稿」？

- **`run-daily-wechat.sh`** 在 OpenClaw 写稿结束后会再跑 **`generate-images-and-upload.sh`** → 内部会调用 **`wechat-draft-upload.sh`** 上传**当天文件夹里每一篇** `.md`。
- 若 Agent 在同一轮任务里**又执行了一次** `wechat-draft-upload.sh` 或 `generate-images-and-upload.sh`，同一篇（如 `EDU_article.md`）会被 **`draft/add` 调两次** → 草稿箱里会出现**两条标题几乎一样的草稿**。
- **避免方式**：日更任务里由**宿主机脚本统一上传**；已在 `run-daily-wechat.sh` 的提示词与 `skills/wechat-daily-editor/SKILL.md` 中写明 Agent **不要**在日更流程里再跑上传脚本。

**如何自查是否重复上传过**

```bash
grep 'Draft uploaded' /tmp/wechat-draft-upload.log | tail -30
```

同一天、同一 `base`（如 `EDU_article`）若出现**两行**时间接近的记录，即曾上传两次。

**注意**：`wechat-draft-upload.sh` 会对**该日期目录下所有** `*.md` 各建一条草稿（例如同时存在 `INBOX_article.md`、`INBOX2_article.md` 时会各上传一篇）——这是**多篇不同文件**，不是脚本 bug；若只想上传 EDU/MED/FIN，需把其它 `.md` 移出该日目录或改脚本过滤（未默认实现）。

## 7. Markdown→HTML：`md_to_wechat_html.py` 环境变量

上传草稿前，脚本会对每篇调用 `scripts/md_to_wechat_html.py`。可通过环境变量控制（可写入 `~/.wechat-env`，与 `WECHAT_APPID` 等同源加载时注意只 export 合法 shell变量）：

| 变量 | 含义 | 默认 |
|------|------|------|
| `WECHAT_MD_HTML_THEME` | `minimal`（灰蓝标题）或 `green`（公号绿强调、引用条绿边） | `minimal` |
| `WECHAT_MD_HTML_FOOTNOTES` | `1`：http(s) 链接改为文内 `[n]` + 文末「参考与链接」；`0`：保留 Pandoc 生成的正文内 `<a>` | `1` |
| `WECHAT_MD_HTML_WRAP_SECTION` | `1`：正文外包一层带 padding 的 `<section>` | 关 |

命令行覆盖主题：`python3 scripts/md_to_wechat_html.py file.md --theme green`。
