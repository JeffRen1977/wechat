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
