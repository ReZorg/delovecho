---
name: dgen
description: Integrates with the DreamGen (dgen) API for advanced creative writing and role-playing. Use for story generation, character-based dialogue, interactive fiction, and fine-tuned control over DreamGen's `lucid-v1` models. Supports both native and OpenAI-compatible APIs.
---

# DreamGen (dgen) API Skill

This skill provides tools and workflows to interact with the DreamGen API, which is specialized for high-quality creative writing, role-playing, and story generation using the `lucid-v1` family of models.

## Core Concepts

DreamGen extends standard chat formats with features designed for narrative control:

- **`text` Role**: The primary role for story content. It allows assigning content to specific characters or a narrator.
- **Character Generation**: By assigning a `name` to a `text` role message, you can create dialogue and actions for specific characters.
- **Narrator Mode**: A `text` role with an empty `name` (`name=""`) is used for third-person narration, scene descriptions, and actions.

## Primary Workflow: Story Generation

For most creative writing tasks, use the `dgen_story.py` script. It manages the scene, characters, and history for you.

**Process:**

1.  **Create a `scenario.json` file**: This file defines the story's context, characters, and existing history.
2.  **Run `dgen_story.py`**: Use the script to generate the next part of the story, either as a character or as the narrator.
3.  **Append to History**: Use the `--append` flag to automatically save the generated content back to your `scenario.json` file, maintaining the story's continuity.

### `scenario.json` Structure

```json
{
    "system": "A high-fantasy adventure story. The party is exploring an ancient, forgotten library.",
    "characters": {
        "Kaelen": "A stoic elven ranger, wise and cautious.",
        "Lyra": "A hot-headed human sorceress, powerful but reckless."
    },
    "history": [
        {
            "role": "text",
            "name": "",
            "content": "Dust motes danced in the single beam of light piercing the gloom of the grand library. Shelves overflowed with decaying books, their pages whispering secrets to the silence."
        },
        {
            "role": "text",
            "name": "Lyra",
            "content": "I can feel immense power here. Let's see what's hidden in the restricted section."
        }
    ]
}
```

### Example Usage

To continue the story as Kaelen:

```bash
python /home/ubuntu/skills/dgen/scripts/dgen_story.py \
    --scenario path/to/your/scenario.json \
    --continue-as "Kaelen" \
    --append
```

## Available Scripts

This skill provides three Python scripts for different levels of control.

| Script | Purpose | When to Use |
| --- | --- | --- |
| `dgen_story.py` | High-level story and role-play management | **Default choice.** For most creative writing tasks involving characters and a continuing narrative. |
| `dgen_chat.py` | General-purpose chat completions | For simpler, non-narrative tasks, or when you need to use the assistant role. Works like a standard OpenAI chat client. |
| `dgen_text.py` | Low-level native API access | For advanced use cases requiring precise control over the raw ChatML prompt and sampling parameters not exposed in the other scripts. |

## Reference Guides

For detailed information, consult the reference files:

- **Prompting**: To understand the ChatML+Text format, roles, and character naming conventions, read `/home/ubuntu/skills/dgen/references/prompt-formats.md`.
- **Sampling**: To fine-tune the model's output with parameters like `temperature`, `minP`, and the `DRY` sampler, read `/home/ubuntu/skills/dgen/references/sampling-params.md`.

## Quick Start Examples

### Simple Chat Completion

Generate a simple completion using the `dgen_chat.py` script.

```bash
python /home/ubuntu/skills/dgen/scripts/dgen_chat.py \
    --system "You are a helpful assistant." \
    --user "Explain the concept of nucleus sampling."
```

### New Story from Scratch

1.  Create a `my_story.json` file with a system prompt and character definitions.
2.  Run `dgen_story.py` to generate the first block of narration.

```bash
# Create my_story.json
cat <<EOF > my_story.json
{
  "system": "A cyberpunk detective story on the rain-slicked streets of Neo-Kyoto.",
  "characters": {
    "Jax": "A grizzled cyber-detective with a robotic arm and a drinking problem."
  },
  "history": []
}
EOF

# Generate the opening narration
python /home/ubuntu/skills/dgen/scripts/dgen_story.py \
    --scenario my_story.json \
    --narrator \
    --append
```
