---
name: clawcog
description: Develop, configure, extend, and operate OpenCog (clawcog) — a personal AI assistant gateway with multi-channel messaging, cognitive architecture, skills, plugins, and multi-agent routing. Use when working on the cogpy/clawcog repository, building OpenCog extensions or skills, configuring the gateway, debugging channel integrations, or contributing to the codebase.
---

# OpenCog (clawcog)

OpenCog is a personal AI assistant gateway you run on your own devices. It connects to channels (WhatsApp, Telegram, Slack, Discord, Signal, iMessage, Google Chat, MS Teams, WebChat, and more), runs an embedded agent runtime, and exposes a WebSocket control plane.

**Repository**: `cogpy/clawcog` — MIT license, TypeScript/pnpm monorepo, Node ≥22.

## Architecture Overview

```
┌──────────────┐   WS    ┌──────────────┐   WS    ┌─────────────┐
│  CLI / App   │────────▶│   Gateway    │◀────────│   Nodes     │
│  (clients)   │         │  :18789 WS   │         │ (mac/ios/   │
└──────────────┘         │  :18790 TCP  │         │  android)   │
                         │  :18793 HTTP │         └─────────────┘
                         └──────┬───────┘
                                │
          ┌─────────┬───────────┼───────────┬──────────┐
          ▼         ▼           ▼           ▼          ▼
      WhatsApp  Telegram    Discord     Signal    iMessage ...
```

**Gateway** (daemon): owns all channel connections, exposes typed WS API, validates frames against JSON Schema, emits events (`agent`, `chat`, `presence`, `health`, `cron`).

**Nodes**: connect with `role: node`, provide device capabilities (`canvas.*`, `camera.*`, `screen.record`, `location.get`).

**Agent Runtime**: embedded pi-mono with workspace files (`AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `IDENTITY.md`).

## Repository Layout

| Path | Purpose |
|------|---------|
| `src/` | Core TypeScript source — agents, gateway, channels, CLI, cognitive, plugins, cron, hooks |
| `extensions/` | 34 channel/feature plugins (slack, discord, whatsapp, memory-core, voice-call, etc.) |
| `skills/` | 52 bundled AgentSkills (weather, github, slack, canvas, coding-agent, etc.) |
| `packages/` | Sub-packages (clawdbot, moltbot) |
| `apps/` | Native apps (macOS Swift, iOS Swift, Android Kotlin) |
| `ui/` | Web control UI |
| `docs/` | Comprehensive documentation site |
| `scripts/` | Build, release, and dev scripts |
| `Swabble/` | Swift wake-word daemon for macOS |

## Development Workflow

### Setup from source

```bash
git clone https://github.com/cogpy/clawcog.git && cd clawcog
pnpm install
pnpm ui:build    # auto-installs UI deps on first run
pnpm build       # tsdown bundler
pnpm opencog onboard --install-daemon
```

### Key commands

```bash
pnpm dev                    # Run in dev mode
pnpm build                  # Production build (tsdown)
pnpm check                  # format:check + tsgo + lint
pnpm test                   # vitest unit tests
pnpm test:e2e               # end-to-end tests
pnpm check:loc              # enforce max 500 LOC per file
```

### Build system

Bundler is tsdown with multiple entry points (`src/index.ts`, `src/entry.ts`, `src/plugin-sdk/index.ts`). Testing uses vitest with separate configs for unit, e2e, extensions, gateway, and live tests. Formatting uses oxfmt. TypeScript targets ES2023 with NodeNext modules.

## Configuration

Config lives at `~/.opencog/opencog.json` (JSON5). Key sections:

```json5
{
  agents: {
    defaults: { workspace: "~/.opencog/workspace", models: ["opencode/claude-opus-4-6"] },
    list: [/* multi-agent definitions */],
  },
  channels: {
    whatsapp: { allowFrom: ["+1234567890"] },
    telegram: { allowFrom: ["username"] },
  },
  session: { dmScope: "per-channel-peer" },
  skills: { entries: { "skill-name": { enabled: true, apiKey: "..." } } },
  plugins: { /* extension enable/disable */ },
}
```

Strict validation — unknown keys block startup. Run `opencog doctor --fix` to repair.

## Task Decision Tree

**Creating a new skill?** → Read `{baseDir}/references/skills-guide.md`

**Writing an extension/plugin?** → Read `{baseDir}/references/extensions-guide.md`

**Working with the cognitive architecture?** → Read `{baseDir}/references/cognitive-arch.md`

**Configuring channels or gateway?** → Read `{baseDir}/references/channels-config.md`

**Contributing to the core codebase?** → Follow the development workflow above, enforce `pnpm check` and `pnpm check:loc` (max 500 LOC per file).

## CLI Quick Reference

```bash
opencog onboard [--install-daemon]   # Guided setup wizard
opencog gateway [--port 18789]       # Start the gateway daemon
opencog agent --message "prompt"     # Send agent prompt
opencog message send --to +1234567890 --message "text"
opencog status                       # Gateway status
opencog doctor [--fix]               # Diagnose and repair
opencog config set <key> <value>     # Update config
opencog models list                  # List available models
opencog skills list [--eligible]     # List skills
opencog cron list                    # List scheduled jobs
opencog update [--channel stable|beta|dev]
```

## Multi-Agent Routing

Each agent is fully scoped with its own workspace, state directory (`agentDir`), session store, and auth profiles under `~/.opencog/agents/<agentId>/`. Bindings route inbound messages to agents. Single-agent mode is default; multi-agent requires `agents.list[]` in config.

## Docker Deployment

```bash
# docker-compose.yml uses OPENCOG_IMAGE, OPENCOG_GATEWAY_TOKEN, etc.
docker compose up -d opencog-gateway
```

Gateway binds to `0.0.0.0:18789` inside container. Set `OPENCOG_GATEWAY_BIND=lan` for LAN access.

## Troubleshooting

- `opencog doctor` — diagnose config, auth, channel issues
- `opencog doctor --fix` — auto-apply migrations and repairs
- `opencog logs` — view gateway logs
- `opencog health` — check gateway health
- Config validation is strict: unknown keys block startup
- Git hooks path: `git-hooks/` (set via `core.hooksPath` on install)
