---
name: agent-zero
description: Build and extend Agent Zero autonomous AI agents. Use for creating custom tools, extensions, prompts, instruments, and agent profiles. Covers multi-agent cooperation, code execution, memory systems, MCP integration, and A2A protocol.
---

# Agent Zero Framework

Agent Zero is an organic, self-evolving agentic framework that uses the computer as a tool. Unlike predefined frameworks, it dynamically grows and learns through persistent memory and multi-agent cooperation.

## When to Use This Skill

- Creating custom tools for Agent Zero agents
- Building extensions that hook into agent lifecycle
- Customizing agent behavior through prompts
- Setting up multi-agent hierarchies
- Integrating with MCP servers or A2A protocol
- Developing instruments (callable procedures)
- Creating isolated project workspaces

## Quick Start

```bash
# Docker deployment
docker pull agent0ai/agent-zero
docker run -p 50001:80 agent0ai/agent-zero
# Visit http://localhost:50001
```

## Architecture Overview

```
agent-zero/
├── agent.py              # Core Agent and AgentContext classes
├── models.py             # LLM provider configurations
├── prompts/              # System prompts and templates
├── python/
│   ├── tools/            # Default tools (code_execution, memory, etc.)
│   ├── extensions/       # Lifecycle hooks
│   ├── api/              # REST API endpoints
│   └── helpers/          # Utility modules
├── agents/               # Custom agent profiles
├── instruments/          # Callable procedures
└── knowledge/            # Knowledge base files
```

## Creating Custom Tools

Tools are invoked by agents through JSON tool calls. Create tools in `python/tools/` or agent-specific `agents/{profile}/tools/`.

### Tool Template

```python
# python/tools/my_tool.py
from python.helpers.tool import Tool, Response

class MyTool(Tool):
    async def execute(self, **kwargs) -> Response:
        # Access arguments via self.args
        param = self.args.get("param", "default")
        
        # Perform operation
        result = f"Processed: {param}"
        
        # Return response (break_loop=True ends agent loop)
        return Response(message=result, break_loop=False)
    
    async def before_execution(self, **kwargs):
        # Optional: pre-execution hook
        pass
    
    async def after_execution(self, response, **kwargs):
        # Optional: post-execution hook (e.g., add to history)
        self.agent.hist_add_tool_result(self.name, response.message)
```

### Tool Prompt Definition

Create `prompts/agent.system.tool.my_tool.md`:

```markdown
## my_tool
Use this tool to [description].

**Arguments:**
- `param` (string, required): Description of parameter

**Example:**
~~~json
{
    "thoughts": ["I need to process this data"],
    "tool_name": "my_tool",
    "tool_args": {
        "param": "value"
    }
}
~~~
```

## Creating Extensions

Extensions hook into agent lifecycle at predefined points. See `references/extensions.md` for all extension points.

### Extension Template

```python
# python/extensions/agent_init/my_extension.py
from python.helpers.extension import Extension

class MyExtension(Extension):
    async def execute(self, **kwargs):
        # Access agent via self.agent
        self.agent.agent_name = f"Custom{self.agent.number}"
        
        # Access context via self.agent.context
        self.agent.context.log.log(
            type="info",
            heading="Extension Loaded",
            content="Custom extension initialized"
        )
```

### Extension Points

| Point | Trigger | Use Case |
|-------|---------|----------|
| `agent_init` | Agent creation | Modify agent properties |
| `message_loop_start` | Loop begins | Initialize loop state |
| `before_main_llm_call` | Before LLM | Modify prompts |
| `system_prompt` | Prompt build | Inject system content |
| `response_stream` | LLM streaming | Process responses |
| `monologue_end` | Loop complete | Cleanup/logging |

## Customizing Prompts

Prompts define agent behavior. Override defaults by creating matching files in `agents/{profile}/prompts/`.

### Variable Placeholders

```markdown
# prompts/agent.system.main.environment.md
## Environment
- Current datetime: {{date_time}}
- Working directory: {{cwd}}
```

### Dynamic Variable Loaders

Create `.py` file alongside `.md` to generate variables:

```python
# prompts/agent.system.tools.py
from python.helpers.files import VariablesPlugin

class Tools(VariablesPlugin):
    def get_variables(self, file, backup_dirs=None):
        # Dynamically collect tool instructions
        tools = self.collect_tool_prompts()
        return {"tools": "\n\n".join(tools)}
```

### File Includes

```markdown
# prompts/agent.system.main.md
{{ include "agent.system.main.role.md" }}
{{ include "agent.system.main.environment.md" }}
```

## Creating Agent Profiles

Agent profiles customize behavior without modifying defaults.

```
agents/my_agent/
├── _context.md           # Agent description
├── settings.json         # Override global settings
├── prompts/              # Custom prompts
├── tools/                # Custom tools
└── extensions/           # Custom extensions
```

### Profile Settings Override

```json
// agents/my_agent/settings.json
{
    "chat_model": {
        "provider": "anthropic",
        "name": "claude-3-opus"
    },
    "context_window": 128000
}
```

## Creating Instruments

Instruments are callable procedures in `instruments/default/` or `instruments/custom/`.

```
instruments/custom/my_instrument/
├── instrument.json       # Metadata and schema
└── my_script.py          # Implementation
```

### Instrument Definition

```json
// instruments/custom/my_instrument/instrument.json
{
    "name": "my_instrument",
    "description": "Performs custom operation",
    "parameters": {
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "Input data"}
        },
        "required": ["input"]
    }
}
```

## Projects System

Projects provide isolated workspaces with dedicated memory, knowledge, and secrets.

```
usr/projects/{project_name}/
└── .a0proj/
    ├── project.json      # Project metadata
    ├── instructions/     # Auto-injected prompts
    ├── knowledge/        # Project knowledge base
    ├── memory/           # Isolated memory storage
    ├── secrets.env       # API keys, passwords
    └── variables.env     # Configuration flags
```

## Multi-Agent Cooperation

Agents form hierarchies with superior/subordinate relationships.

```python
# Subordinate creation via call_subordinate tool
{
    "tool_name": "call_subordinate",
    "tool_args": {
        "message": "Research topic X and summarize",
        "reset": false
    }
}
```

Key behaviors:
- Agent 0's superior is the human user
- Subordinates report back to their superior
- Each agent maintains clean, focused context
- Subordinates can override parent settings

## External Connectivity

### REST API

```javascript
// POST /api_message
const response = await fetch('http://localhost:50001/api_message', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-API-KEY': 'YOUR_API_KEY'
    },
    body: JSON.stringify({
        message: "Your task",
        context_id: "optional_existing_context"
    })
});
```

### MCP Server

Agent Zero can act as MCP server. Configure in settings and connect via:
- `send_message` - Send messages to agent
- `get_response` - Get agent response
- `finish_chat` - Terminate context

### A2A Protocol

Agent-to-agent communication via `a2a_chat` tool:

```json
{
    "tool_name": "a2a_chat",
    "tool_args": {
        "url": "http://other-agent:50001",
        "message": "Collaborate on task"
    }
}
```

## Development Setup

For local development with debugging:

1. Clone repository and create Python environment
2. Install dependencies: `pip install -r requirements.txt`
3. Run Docker instance for code execution
4. Configure RFC connection between local and Docker
5. Debug in VS Code with provided launch configurations

See `references/development.md` for detailed setup guide.

## Default Tools Reference

| Tool | Purpose |
|------|---------|
| `code_execution` | Run Python, Node.js, terminal commands |
| `memory_save/load/delete` | Persistent memory operations |
| `call_subordinate` | Create/communicate with sub-agents |
| `response` | Send final response to user |
| `search_engine` | Web search |
| `browser_agent` | Browser automation |
| `document_query` | Query documents with LLM |
| `scheduler` | Schedule future tasks |
| `notify_user` | Send notifications |

## Resources

- **Extensions Reference**: See `references/extensions.md` for all extension points and examples
- **API Reference**: See `references/api.md` for complete REST API documentation
- **Tool Examples**: See `templates/tool_template.py` for annotated tool template
