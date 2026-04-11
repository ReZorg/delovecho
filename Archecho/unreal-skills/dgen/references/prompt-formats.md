# DreamGen Prompt Formats

## ChatML+Text Format

DreamGen uses ChatML format with an extended `text` role for creative writing.

### Basic Structure

```
<|im_start|>system
{system prompt}
<|im_end|>
<|im_start|>user
{user message}
<|im_end|>
<|im_start|>assistant
{assistant response}
<|im_end|>
```

### Text Role for Creative Writing

The `text` role enables character-based generation:

```
<|im_start|>text name=Alice
Hello, how are you today?
<|im_end|>
<|im_start|>text name=Bob
I'm doing well, thanks for asking!
<|im_end|>
```

### Narrator Mode

Empty name for narrator/third-person prose:

```
<|im_start|>text name=
The sun dipped below the horizon, casting long shadows across the valley.
<|im_end|>
```

## OpenAI API Role Mapping

When using the OpenAI-compatible API:

| OpenAI Role | DreamGen Interpretation |
|-------------|------------------------|
| `system` | System prompt |
| `user` | User message OR text role (if `name` is set) |
| `assistant` | Assistant OR text role (via `role_config`) |

### Using Names for Text Role

```python
messages = [
    {"role": "system", "content": "A fantasy story..."},
    {"role": "user", "name": "Gandalf", "content": "You shall not pass!"},
    {"role": "user", "name": "Frodo", "content": "But we must cross!"},
    {"role": "user", "name": "", "content": "The bridge crumbled beneath them."}
]
```

Messages with `name` field are interpreted as `text` role.

## Role Configuration

Control response role via `role_config`:

```python
role_config = {
    "assistant": {
        "role": "text",      # or "assistant"
        "name": "Character", # optional, for text role
        "open": True         # True for text role continuations
    },
    "user": {
        "role": "text",      # interpret user messages as text
        "name": "UserChar"   # optional character name
    }
}
```

### Model Path Shorthand

Alternative to `role_config` in request body:

- `lucid-v1-extra-large/text` → `{"assistant": {"role": "text", "open": true}}`
- `lucid-v1-extra-large/assistant` → `{"assistant": {"role": "assistant", "open": false}}`

## Example: Multi-Character Scene

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DGEN_API_KEY"],
    base_url="https://dreamgen.com/api/openai/v1"
)

messages = [
    {"role": "system", "content": "A detective noir story set in 1940s Chicago."},
    {"role": "user", "name": "", "content": "Rain hammered the office window."},
    {"role": "user", "name": "Detective", "content": "Another night, another case."},
    {"role": "user", "name": "Femme Fatale", "content": "I need your help, detective."}
]

response = client.chat.completions.create(
    model="lucid-v1-extra-large",
    messages=messages,
    max_tokens=300,
    extra_body={
        "role_config": {
            "assistant": {"role": "text", "name": "Detective"}
        }
    }
)
```

## System Prompt Best Practices

1. **Setting first**: Establish world, time period, genre
2. **Character descriptions**: Include personality, speech patterns
3. **Style guidance**: Prose style, POV, tone
4. **Constraints**: Content boundaries, themes to explore

Example:
```
A dark fantasy adventure set in a dying world. 

Characters:
- Kira: A cynical mercenary with a hidden heart of gold
- Vex: An enigmatic mage seeking forbidden knowledge

Style: Third-person limited, atmospheric prose, morally gray themes.
```
