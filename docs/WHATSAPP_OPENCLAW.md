# WhatsApp + OpenClaw — pairing (QR code)

The WhatsApp QR code **does not** appear when you run `openclaw gateway start`. You need to **link the channel** separately.

## Show the QR code

1. **Start the gateway** (in one terminal):
   ```bash
   openclaw gateway start
   ```
   Or run it in the foreground: `openclaw gateway run`

2. **In another terminal**, link WhatsApp (this is when the QR appears):
   ```bash
   openclaw channels login --channel whatsapp --verbose
   ```

3. On your phone: **WhatsApp** → **Settings** → **Linked devices** → **Link a device** → scan the QR code.

4. After scanning, the channel is linked. You can keep using `openclaw gateway start` (or your usual way of running the gateway); WhatsApp will reconnect using the stored session.

## Your config

- Number in allowlist: `+18586039367` (in `~/.openclaw/openclaw.json` under `channels.whatsapp.allowFrom`).
- Only messages from that number (or numbers you add) will be handled when `dmPolicy` is `allowlist`.

## If no QR appears

- Ensure the **gateway is running** before running `channels login`.
- Try: `openclaw channels login --channel whatsapp --verbose` and watch for errors or a QR in the output.
- Check: `openclaw channels status` to see if WhatsApp is configured and what state it’s in.

---

## Inbox pipeline: link or content → one WeChat draft

When you send **one link** or **pasted content** in WhatsApp, the agent should:

1. **Fetch** the link (or use the pasted text).
2. **Write** one article to `wechat_factory/04_output/YYYY-MM-DD/INBOX_article.md`.
3. **Generate** 1 cover + 2 figures via `./scripts/run-gemini-images.sh .../INBOX_article.md`.
4. **Upload** to the WeChat draft box via `./scripts/wechat-draft-upload.sh YYYY-MM-DD`.

The agent follows **skills/wechat-from-inbox/SKILL.md**. Ensure `~/.gemini-env` (GEMINI_API_KEY) and `~/.wechat-env` (WeChat credentials) are set.

### Test without WhatsApp

From the repo root, with the **gateway running**:

```bash
# From a URL
./scripts/run-inbox-wechat.sh "https://example.com/some-article"

# From a file (pasted content)
./scripts/run-inbox-wechat.sh wechat_factory/01_sources/web_snapshots/paste.txt
```

Log: `/tmp/wechat-inbox.log`. Then check 微信公众平台 → 草稿箱 for the new draft.
