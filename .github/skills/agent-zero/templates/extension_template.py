"""
Agent Zero Extension Template

Extensions hook into specific points in the agent's lifecycle.
Copy this file to the appropriate extension point directory:
- Default: python/extensions/{extension_point}/
- Agent-specific: agents/{profile}/extensions/{extension_point}/

Extension Points:
- agent_init: Agent creation
- message_loop_start: Loop begins
- message_loop_prompts_before: Before prompts processed
- message_loop_prompts_after: After prompts processed
- before_main_llm_call: Before LLM call
- system_prompt: System prompt building
- reasoning_stream: Reasoning tokens received
- response_stream: Response tokens received
- monologue_start: Monologue begins
- monologue_end: Monologue ends
- hist_add_before: Before adding to history
- hist_add_tool_result: Tool result added
- util_model_call_before: Before utility model call

Naming Convention:
Use numeric prefixes for execution order:
- _10_first.py (runs first)
- _20_second.py (runs second)
- _99_last.py (runs last)
"""

from python.helpers.extension import Extension
from datetime import datetime
import asyncio


class MyExtension(Extension):
    """
    Example extension that demonstrates available features.
    
    Available Properties:
    - self.agent: The Agent instance
    - self.agent.context: The AgentContext
    - self.agent.config: Agent configuration
    - self.agent.history: Message history
    """

    async def execute(self, **kwargs):
        """
        Main extension logic.
        
        kwargs vary by extension point. See examples below.
        """
        # Access agent properties
        agent_name = self.agent.agent_name
        agent_number = self.agent.number
        
        # Access context
        context_id = self.agent.context.id
        
        # Log to UI
        self.agent.context.log.log(
            type="info",
            heading="Extension Executed",
            content=f"Agent {agent_name} (#{agent_number})"
        )
        
        # Store/retrieve persistent data
        self.agent.set_data("my_extension_ran", True)
        previous_value = self.agent.get_data("my_extension_ran")
        
        # Access configuration
        model_name = self.agent.config.chat_model.name


# Extension Point Examples

class AgentInitExtension(Extension):
    """
    Extension point: agent_init
    Triggered when agent is created.
    """
    async def execute(self, **kwargs):
        # Customize agent name
        self.agent.agent_name = f"CustomAgent{self.agent.number}"
        
        # Initialize custom data
        self.agent.set_data("initialized_at", datetime.now().isoformat())


class MessageLoopStartExtension(Extension):
    """
    Extension point: message_loop_start
    Triggered at start of message processing loop.
    """
    async def execute(self, loop_data, **kwargs):
        # loop_data contains:
        # - iteration: Current loop iteration
        # - system: System prompt parts
        # - history_output: Formatted history
        # - extras_temporary: Temporary context
        # - extras_persistent: Persistent context
        
        loop_data.extras_temporary["loop_start"] = datetime.now().isoformat()


class SystemPromptExtension(Extension):
    """
    Extension point: system_prompt
    Triggered when building system prompt.
    """
    async def execute(self, system_prompt, loop_data, **kwargs):
        # system_prompt is a list of strings
        # Append custom instructions
        system_prompt.append("""
## Custom Instructions
- Follow these additional guidelines
- Be extra careful with X
""")


class BeforeLLMCallExtension(Extension):
    """
    Extension point: before_main_llm_call
    Triggered before calling the LLM.
    """
    async def execute(self, messages, **kwargs):
        # messages is list of LangChain messages
        # Can inspect or modify before sending
        
        # Log message count
        self.agent.context.log.log(
            type="info",
            heading="LLM Call",
            content=f"Sending {len(messages)} messages"
        )


class ResponseStreamExtension(Extension):
    """
    Extension point: response_stream
    Triggered for each response token.
    """
    async def execute(self, chunk, total, **kwargs):
        # chunk: Current token/chunk
        # total: Accumulated response so far
        
        # Example: Detect specific patterns
        if "ERROR" in chunk.upper():
            self.agent.context.log.log(
                type="warning",
                heading="Error Detected",
                content=chunk
            )


class MonologueEndExtension(Extension):
    """
    Extension point: monologue_end
    Triggered when agent monologue completes.
    """
    async def execute(self, **kwargs):
        # Cleanup, logging, metrics
        
        start_time = self.agent.get_data("monologue_start")
        if start_time:
            import time
            duration = time.time() - start_time
            self.agent.context.log.log(
                type="info",
                heading="Monologue Complete",
                content=f"Duration: {duration:.2f}s"
            )


class HistAddBeforeExtension(Extension):
    """
    Extension point: hist_add_before
    Triggered before adding message to history.
    """
    async def execute(self, content_data, ai, **kwargs):
        # content_data["content"]: Message content
        # ai: True if AI message, False if user/system
        
        # Example: Add timestamp to all messages
        if isinstance(content_data["content"], dict):
            content_data["content"]["timestamp"] = datetime.now().isoformat()


class RateLimitingExtension(Extension):
    """
    Example: Rate limiting extension for before_main_llm_call
    """
    async def execute(self, **kwargs):
        import time
        
        last_call = self.agent.get_data("last_llm_call_time") or 0
        min_interval = 1.0  # Minimum 1 second between calls
        
        elapsed = time.time() - last_call
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)
        
        self.agent.set_data("last_llm_call_time", time.time())


class ContextInjectionExtension(Extension):
    """
    Example: Inject dynamic context into system prompt
    """
    async def execute(self, system_prompt, loop_data, **kwargs):
        # Get external data
        import os
        
        # Example: Inject environment info
        env_info = f"""
## Environment Context
- Working Directory: {os.getcwd()}
- User: {os.getenv('USER', 'unknown')}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        system_prompt.append(env_info)
