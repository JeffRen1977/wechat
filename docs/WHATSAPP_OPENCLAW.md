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
