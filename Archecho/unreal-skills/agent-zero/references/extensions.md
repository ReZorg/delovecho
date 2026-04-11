# Agent Zero Extensions Reference

## Table of Contents

1. [Extension Architecture](#extension-architecture)
2. [Extension Points](#extension-points)
3. [Creating Extensions](#creating-extensions)
4. [Extension Override Logic](#extension-override-logic)
5. [Complete Examples](#complete-examples)

## Extension Architecture

Extensions hook into specific points in the agent's lifecycle, allowing modification or enhancement of behavior. The framework uses plugin-like architecture where extensions are automatically discovered and loaded.

### Discovery Order

1. Load default extensions from `/python/extensions/{extension_point}/`
2. Load agent-specific extensions from `/agents/{agent_profile}/extensions/{extension_point}/`
3. Merge with agent-specific overriding defaults (by filename)
4. Execute each extension in alphabetical order

### Naming Convention

Use numeric prefixes to control execution order:
- `_10_first_extension.py` - Runs first
- `_20_second_extension.py` - Runs second
- `_99_last_extension.py` - Runs last

## Extension Points

### agent_init

**Trigger**: When an agent is initialized  
**Use Cases**: Modify agent properties, set initial state, configure logging

```python
from python.helpers.extension import Extension

class AgentInitExtension(Extension):
    async def execute(self, **kwargs):
        self.agent.agent_name = f"CustomAgent{self.agent.number}"
        self.agent.set_data("custom_flag", True)
```

### message_loop_start

**Trigger**: At the start of the message processing loop  
**Use Cases**: Initialize loop state, reset counters, prepare resources

```python
class LoopStartExtension(Extension):
    async def execute(self, loop_data, **kwargs):
        loop_data.extras_temporary["session_start"] = datetime.now().isoformat()
```

### message_loop_prompts_before

**Trigger**: Before prompts are processed in the message loop  
**Use Cases**: Modify prompts before processing, inject context

```python
class PromptsBeforeExtension(Extension):
    async def execute(self, loop_data, **kwargs):
        # Add custom context to prompts
        loop_data.system.append("Additional context here")
```

### message_loop_prompts_after

**Trigger**: After prompts are processed in the message loop  
**Use Cases**: Post-process prompts, add final modifications

```python
class PromptsAfterExtension(Extension):
    async def execute(self, loop_data, **kwargs):
        # Finalize prompt modifications
        pass
```

### before_main_llm_call

**Trigger**: Before the main LLM call is made  
**Use Cases**: Modify messages, add system content, log requests

```python
class BeforeLLMExtension(Extension):
    async def execute(self, messages, **kwargs):
        # Inspect or modify messages before LLM call
        self.agent.context.log.log(
            type="info",
            heading="LLM Call",
            content=f"Sending {len(messages)} messages"
        )
```

### system_prompt

**Trigger**: When system prompts are processed  
**Use Cases**: Inject dynamic system content, add capabilities

```python
class SystemPromptExtension(Extension):
    async def execute(self, system_prompt, loop_data, **kwargs):
        # Append to system prompt list
        system_prompt.append("## Custom Instructions\nFollow these rules...")
```

### reasoning_stream

**Trigger**: When reasoning stream data is received (for models with reasoning)  
**Use Cases**: Process reasoning tokens, log thinking process

```python
class ReasoningStreamExtension(Extension):
    async def execute(self, chunk, total, **kwargs):
        # Process reasoning stream
        if "error" in chunk.lower():
            self.agent.context.log.log(type="warning", content=chunk)
```

### response_stream

**Trigger**: When response stream data is received  
**Use Cases**: Process response tokens, detect patterns, trigger actions

```python
class ResponseStreamExtension(Extension):
    async def execute(self, chunk, total, **kwargs):
        # Process response stream in real-time
        pass
```

### monologue_start

**Trigger**: At the start of agent monologue  
**Use Cases**: Initialize monologue state, start timers

```python
class MonologueStartExtension(Extension):
    async def execute(self, **kwargs):
        self.agent.set_data("monologue_start_time", time.time())
```

### monologue_end

**Trigger**: At the end of agent monologue  
**Use Cases**: Cleanup, logging, metrics collection

```python
class MonologueEndExtension(Extension):
    async def execute(self, **kwargs):
        start = self.agent.get_data("monologue_start_time")
        if start:
            duration = time.time() - start
            self.agent.context.log.log(
                type="info",
                heading="Monologue Complete",
                content=f"Duration: {duration:.2f}s"
            )
```

### hist_add_before

**Trigger**: Before adding message to history  
**Use Cases**: Modify content, add metadata, filter messages

```python
class HistAddBeforeExtension(Extension):
    async def execute(self, content_data, ai, **kwargs):
        # Modify content before adding to history
        if isinstance(content_data["content"], str):
            content_data["content"] = content_data["content"].strip()
```

### hist_add_tool_result

**Trigger**: When adding tool result to history  
**Use Cases**: Process tool results, add metadata

```python
class HistToolResultExtension(Extension):
    async def execute(self, data, **kwargs):
        # Add timestamp to tool results
        data["timestamp"] = datetime.now().isoformat()
```

### util_model_call_before

**Trigger**: Before utility model calls  
**Use Cases**: Modify utility model parameters, log calls

```python
class UtilModelExtension(Extension):
    async def execute(self, call_data, **kwargs):
        # Modify utility model call parameters
        call_data["system"] += "\nBe concise."
```

## Extension Override Logic

When an extension with the same filename exists in both locations, the agent-specific version takes precedence:

```
/python/extensions/agent_init/example.py        # Default
/agents/my_agent/extensions/agent_init/example.py  # Overrides default
```

This allows selective overriding while inheriting other default behaviors.

## Complete Examples

### Custom Logging Extension

```python
# /python/extensions/message_loop_end/_50_custom_logger.py
from python.helpers.extension import Extension
import json

class CustomLogger(Extension):
    async def execute(self, loop_data, **kwargs):
        # Log loop statistics
        stats = {
            "iteration": loop_data.iteration,
            "history_length": len(loop_data.history_output),
            "extras_count": len(loop_data.extras_persistent)
        }
        
        self.agent.context.log.log(
            type="info",
            heading="Loop Statistics",
            content=json.dumps(stats, indent=2)
        )
```

### Rate Limiting Extension

```python
# /python/extensions/before_main_llm_call/_10_rate_limiter.py
from python.helpers.extension import Extension
import asyncio
import time

class RateLimiter(Extension):
    async def execute(self, **kwargs):
        last_call = self.agent.get_data("last_llm_call") or 0
        min_interval = 1.0  # Minimum 1 second between calls
        
        elapsed = time.time() - last_call
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)
        
        self.agent.set_data("last_llm_call", time.time())
```

### Context Injection Extension

```python
# /agents/researcher/extensions/system_prompt/_20_research_context.py
from python.helpers.extension import Extension

class ResearchContext(Extension):
    async def execute(self, system_prompt, loop_data, **kwargs):
        research_guidelines = """
## Research Guidelines
- Always cite sources
- Verify information from multiple sources
- Distinguish between facts and opinions
- Note publication dates for time-sensitive information
"""
        system_prompt.append(research_guidelines)
```
