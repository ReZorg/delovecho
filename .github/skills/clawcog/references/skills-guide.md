# OpenCog Skills Guide

## Table of Contents
1. Skill Format
2. Creating a New Skill
3. Skill Gating
4. Skill Configuration
5. ClawHub Registry
6. Slash Commands and Dispatch

## Skill Format

Skills are AgentSkills-compatible directories containing a `SKILL.md` with YAML frontmatter.

```
my-skill/
├── SKILL.md          # Required: frontmatter + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation loaded as needed
└── templates/        # Optional: output assets
```

### SKILL.md Frontmatter

Required fields:

```yaml
---
name: my-skill
description: What the skill does and when to use it.
---
```

Optional fields:

```yaml
---
name: my-skill
description: What the skill does and when to use it.
homepage: https://example.com
user-invocable: true          # Expose as slash command (default: true)
disable-model-invocation: false  # Exclude from model prompt (default: false)
command-dispatch: tool         # Bypass model, dispatch directly to tool
command-tool: my_tool_name     # Tool to invoke for direct dispatch
command-arg-mode: raw          # Forward raw args string
metadata: { "opencog": { "emoji": "🔧", "requires": { "bins": ["curl"], "env": ["API_KEY"] }, "primaryEnv": "API_KEY", "os": ["darwin"], "install": [{ "id": "brew", "kind": "brew", "formula": "curl", "bins": ["curl"] }] } }
---
```

### Metadata Schema

The `metadata.opencog` object controls gating and UI:

| Field | Type | Purpose |
|-------|------|---------|
| `emoji` | string | Display emoji in UI |
| `always` | boolean | Always include regardless of requirements |
| `skillKey` | string | Override config key (default: skill name) |
| `primaryEnv` | string | Primary env var (used with `apiKey` config shorthand) |
| `os` | string[] | OS filter (`darwin`, `linux`, `win32`) |
| `homepage` | string | URL for Skills UI |
| `requires.bins` | string[] | All listed binaries must be present |
| `requires.anyBins` | string[] | At least one binary must be present |
| `requires.env` | string[] | All listed env vars must be set |
| `requires.config` | string[] | All listed config paths must be truthy |
| `install` | array | Install specs for missing dependencies |

### Install Spec

```json
{
  "id": "brew",
  "kind": "brew",        // brew | node | go | uv | download
  "formula": "gh",       // for brew
  "package": "pkg-name", // for node/go/uv
  "bins": ["gh"],
  "label": "Install GitHub CLI (brew)",
  "os": ["darwin"]
}
```

## Creating a New Skill

1. Create the directory in `~/.opencog/workspace/skills/` or the repo's `skills/`:

```bash
mkdir -p skills/my-skill
```

2. Write `SKILL.md` with frontmatter and instructions:

```markdown
---
name: my-skill
description: Do X when user asks for Y.
metadata: { "opencog": { "emoji": "🔧", "requires": { "bins": ["curl"] } } }
---
# My Skill
Instructions for the agent on how to use this skill.
```

3. Refresh skills: ask the agent to "refresh skills" or restart the gateway.

4. Test: `opencog agent --message "use my new skill"`

## Skill Gating

Skills are filtered at load time. A skill is included when ALL conditions pass:

1. Not explicitly disabled via `skills.entries.<key>.enabled: false`
2. Passes `allowBundled` filter (if bundled)
3. OS matches runtime platform (or node reports matching platform)
4. Required binaries found locally or on connected node
5. Required env vars set (in process env, skill config env, or via `apiKey` shorthand)
6. Required config paths are truthy in `opencog.json`

## Skill Configuration

In `~/.opencog/opencog.json`:

```json5
{
  skills: {
    entries: {
      "my-skill": {
        enabled: true,
        apiKey: "sk-...",           // Maps to primaryEnv
        env: { "CUSTOM_VAR": "value" },
      },
    },
    allowBundled: ["weather", "github"],  // Restrict bundled skills
    load: {
      extraDirs: ["/path/to/shared/skills"],
    },
  },
}
```

## ClawHub Registry

ClawHub is the public skills registry at [clawhub.com](https://clawhub.com).

```bash
clawhub install <skill-slug>     # Install to workspace
clawhub update --all             # Update all installed
clawhub sync --all               # Scan + publish updates
```

## Slash Commands and Dispatch

Skills with `user-invocable: true` (default) are exposed as `/skill-name` slash commands.

For direct tool dispatch (bypassing the model):

```yaml
---
name: my-tool-skill
description: Directly invoke my_tool.
command-dispatch: tool
command-tool: my_tool_name
command-arg-mode: raw
---
```

The tool receives: `{ command: "<raw args>", commandName: "<slash command>", skillName: "<skill name>" }`.
