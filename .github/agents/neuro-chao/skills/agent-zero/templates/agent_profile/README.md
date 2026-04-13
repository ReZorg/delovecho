# Agent Profile Template

This directory contains a template for creating custom Agent Zero profiles.

## Directory Structure

```
agents/{profile_name}/
├── _context.md           # Agent description (shown in UI)
├── settings.json         # Override global settings
├── prompts/              # Custom prompts
│   ├── agent.system.main.role.md
│   └── agent.system.tool.*.md
├── tools/                # Custom tools
│   └── my_tool.py
└── extensions/           # Custom extensions
    └── agent_init/
        └── _10_custom.py
```

## Usage

1. Copy this template to `agents/{your_profile_name}/`
2. Customize files as needed
3. Select profile in Agent Zero settings

## Files

### _context.md

Agent description shown in the UI profile selector.

### settings.json

Override any global settings. Only include fields you want to change:

```json
{
    "chat_model": {
        "provider": "anthropic",
        "name": "claude-3-opus"
    }
}
```

### prompts/

Custom prompts override defaults. Only create files you need to change.

### tools/

Custom tools specific to this profile. Override default tools by using the same filename.

### extensions/

Custom extensions for this profile. Organize by extension point.
