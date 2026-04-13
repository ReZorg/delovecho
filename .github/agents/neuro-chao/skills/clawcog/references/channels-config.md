# OpenCog Channels & Gateway Configuration

## Table of Contents
1. Supported Channels
2. Channel Configuration
3. Gateway Configuration
4. Session Management
5. Model Configuration
6. Deployment Options

## Supported Channels

| Channel | Type | Extension | Key Config Path |
|---------|------|-----------|-----------------|
| WhatsApp | Built-in (Baileys) | — | `channels.whatsapp` |
| Telegram | Built-in (grammY) | — | `channels.telegram` |
| Discord | Extension | `extensions/discord` | `channels.discord` |
| Slack | Extension | `extensions/slack` | `channels.slack` |
| Signal | Built-in | — | `channels.signal` |
| iMessage | Extension | `extensions/imessage` | macOS only |
| Google Chat | Extension | `extensions/googlechat` | `channels.googlechat` |
| MS Teams | Extension | `extensions/msteams` | `channels.msteams` |
| Matrix | Extension | `extensions/matrix` | `channels.matrix` |
| BlueBubbles | Extension | `extensions/bluebubbles` | `channels.bluebubbles` |
| LINE | Extension | `extensions/line` | `channels.line` |
| Nostr | Extension | `extensions/nostr` | `channels.nostr` |
| Zalo | Extension | `extensions/zalo` | `channels.zalo` |
| Zalo Personal | Extension | `extensions/zalouser` | `channels.zalouser` |
| Twitch | Extension | `extensions/twitch` | `channels.twitch` |
| Mattermost | Extension | `extensions/mattermost` | `channels.mattermost` |
| Nextcloud Talk | Extension | `extensions/nextcloud-talk` | `channels.nextcloudTalk` |
| Tlon | Extension | `extensions/tlon` | `channels.tlon` |
| Feishu | Extension | `extensions/feishu` | `channels.feishu` |
| WebChat | Built-in | — | Gateway WS API |

## Channel Configuration

### WhatsApp

```json5
{
  channels: {
    whatsapp: {
      allowFrom: ["+1234567890", "+0987654321"],
      groups: {
        allowAll: false,
        allow: ["group-jid@g.us"],
        mentionOnly: true,
      },
    },
  },
}
```

### Telegram

```json5
{
  channels: {
    telegram: {
      allowFrom: ["username1", "username2"],
      groups: {
        allowAll: false,
        allow: [-1001234567890],
        mentionOnly: true,
      },
    },
  },
}
```

### Discord

```json5
{
  channels: {
    discord: {
      guilds: {
        "guild-id": {
          channels: ["channel-id"],
          mentionOnly: true,
        },
      },
    },
  },
}
```

### Slack

Configured via the Slack extension. Requires bot token setup through `opencog onboard`.

## Gateway Configuration

### Bind modes

| Mode | Binds To | Use Case |
|------|----------|----------|
| `loopback` | 127.0.0.1 | Local only (default) |
| `lan` | LAN interface | Local network access |
| `tailnet` | Tailscale interface | Remote access via Tailscale |
| `auto` | Best available | Tailscale > LAN > loopback |

### Gateway start

```bash
opencog gateway --port 18789 --bind loopback --verbose
```

### Gateway token

Set `OPENCOG_GATEWAY_TOKEN` for authenticated access. Required for remote connections.

### Config apply (RPC)

```bash
# Read current config
opencog gateway call config.get --params '{}'

# Apply full config (replaces entire config)
opencog gateway call config.apply --params '{"raw": "...", "baseHash": "..."}'

# Partial update (merge patch)
opencog gateway call config.patch --params '{"patch": {"session": {"dmScope": "per-peer"}}}'
```

## Session Management

```json5
{
  session: {
    dmScope: "main",                    // main | per-peer | per-channel-peer | per-account-channel-peer
    mainKey: "main",                    // Default main session key
    identityLinks: {                    // Map cross-channel identities
      "whatsapp:+1234567890": "alice",
      "telegram:alice_user": "alice",
    },
  },
}
```

**DM scope options**:
- `main`: All DMs share one session (default, simple but leaks context)
- `per-peer`: Isolate by sender ID across channels
- `per-channel-peer`: Isolate by channel + sender (recommended for multi-user)
- `per-account-channel-peer`: Isolate by account + channel + sender (multi-account)

## Model Configuration

```json5
{
  agents: {
    defaults: {
      models: ["opencode/claude-opus-4-6", "openai/gpt-5.1-codex"],
    },
  },
}
```

Built-in providers: OpenAI, Anthropic (Claude), Google (Gemini), and more via pi-ai catalog.

Auth methods:
- API keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.
- OAuth subscriptions: Claude Pro/Max, ChatGPT Plus
- CLI: `opencog onboard --auth-choice openai-api-key`

Model failover: configure multiple models for automatic fallback. See `docs/concepts/model-failover.md`.

## Deployment Options

### Docker

```bash
docker compose up -d opencog-gateway
```

Environment variables: `OPENCOG_IMAGE`, `OPENCOG_GATEWAY_TOKEN`, `OPENCOG_GATEWAY_PORT`, `OPENCOG_GATEWAY_BIND`, `CLAUDE_AI_SESSION_KEY`.

### Fly.io

Use `fly.toml` or `fly.private.toml` in repo root. See `docs/install/fly.md`.

### Render

Use `render.yaml` in repo root. See `docs/install/render.mdx`.

### Systemd / launchd

`opencog onboard --install-daemon` installs a user service. Scripts in `scripts/systemd/`.

### Nix

Community Nix flake at `github:cogpy/nix-opencog`.
