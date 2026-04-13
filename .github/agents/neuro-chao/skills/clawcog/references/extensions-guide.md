# OpenCog Extensions / Plugins Guide

## Table of Contents
1. Extension Structure
2. Plugin Manifest
3. Plugin SDK
4. Creating a New Extension
5. Plugin Lifecycle
6. Hook System

## Extension Structure

Extensions live in `extensions/` as pnpm workspace packages:

```
extensions/my-plugin/
├── package.json              # pnpm workspace package
├── openclaw.plugin.json      # Plugin manifest
├── index.ts                  # Main entry point
└── src/                      # Optional source directory
```

### package.json

```json
{
  "name": "@opencog/my-plugin",
  "version": "2026.2.9",
  "private": true,
  "description": "OpenCog my-plugin extension",
  "type": "module",
  "devDependencies": {
    "opencog": "workspace:*"
  },
  "opencog": {
    "extensions": ["./index.ts"]
  }
}
```

### openclaw.plugin.json

```json
{
  "id": "my-plugin",
  "kind": "memory",
  "channels": ["my-channel"],
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": { "type": "string", "description": "API key for the service" }
    }
  }
}
```

| Field | Type | Purpose |
|-------|------|---------|
| `id` | string | Unique plugin identifier |
| `kind` | string | Plugin kind (e.g., `memory`, `channel`) |
| `channels` | string[] | Channel names this plugin provides |
| `configSchema` | object | JSON Schema for plugin config validation |

## Plugin SDK

Import from `opencog/plugin-sdk`. Key exports include:

- Channel adapters (WhatsApp, Telegram, Signal, Discord, Slack, LINE, etc.)
- Account resolution utilities per channel
- Onboarding adapters
- Normalization helpers for messaging targets
- Status issue collectors
- Media utilities (`loadWebMedia`)
- LINE-specific: flex templates, markdown-to-LINE conversion

## Creating a New Extension

1. Create directory under `extensions/`:

```bash
mkdir -p extensions/my-plugin/src
```

2. Create `package.json`:

```json
{
  "name": "@opencog/my-plugin",
  "version": "2026.2.9",
  "private": true,
  "type": "module",
  "devDependencies": { "opencog": "workspace:*" },
  "opencog": { "extensions": ["./index.ts"] }
}
```

3. Create `openclaw.plugin.json` with manifest.

4. Write `index.ts` implementing the plugin interface.

5. Run `pnpm install` from the repo root to link the workspace package.

6. The extension is auto-discovered by the plugin loader.

## Plugin Lifecycle

1. **Discovery**: `discoverOpenCogPlugins()` scans `extensions/` and installed npm packages
2. **Manifest Registry**: `loadPluginManifestRegistry()` loads all `openclaw.plugin.json` files
3. **Config Validation**: `validateJsonSchemaValue()` validates plugin config against schema
4. **Enable Resolution**: `resolveEnableState()` determines if plugin should be active
5. **Runtime Creation**: `createPluginRuntime()` initializes the plugin
6. **Hook Registration**: Plugin registers hooks via the global hook runner

## Hook System

Hooks are event-driven extensions. Built-in hooks live in `src/hooks/bundled/`. Hooks can:

- React to Gmail events (`gmail-watcher`, `gmail-ops`)
- Generate LLM slugs (`llm-slug-generator`)
- Process internal events (`internal-hooks`)
- Run custom logic on agent events

Hook configuration lives in `~/.opencog/opencog.json` under the `hooks` key. Hooks can be installed via `opencog hooks install` or configured manually.

### Hook Frontmatter

Hooks use frontmatter similar to skills, parsed by `src/hooks/frontmatter.ts`. Hook files live in `src/hooks/bundled/*/handler.ts`.

### Plugin-Provided Hooks

Plugins can register hooks via `src/hooks/plugin-hooks.ts`. The hook runner (`src/hooks/hook-runner-global.ts`) dispatches events to all registered hooks.

### Gmail Integration

Gmail hooks provide:
- `gmail-watcher.ts`: Watch for new emails via Gmail push notifications
- `gmail-ops.ts`: Gmail operations (send, reply, label)
- `gmail-setup-utils.ts`: OAuth setup and token management
- `gmail.ts`: Core Gmail integration

Configure Gmail pub/sub in `opencog.json` and set up OAuth credentials. See `docs/automation/gmail-pubsub.md` for full setup.
