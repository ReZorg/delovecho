"""
Agent Zero Custom Tool Template

This template provides a complete example of a custom tool for Agent Zero.
Copy this file to python/tools/ or agents/{profile}/tools/ and customize.

Tool Lifecycle:
1. Tool initialization (constructor)
2. before_execution() - Optional pre-execution hook
3. execute() - Main tool logic
4. after_execution() - Optional post-execution hook

Available Properties:
- self.agent: The Agent instance
- self.name: Tool name (from tool call)
- self.args: Tool arguments (from tool call)
- self.progress: Progress text for streaming output
"""

from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from typing import Any


class MyCustomTool(Tool):
    """
    Custom tool description.
    
    This tool demonstrates all available features and patterns
    for creating Agent Zero tools.
    """

    async def execute(self, **kwargs) -> Response:
        """
        Main tool execution logic.
        
        Returns:
            Response object with message and optional flags
        """
        # Handle intervention (pause/resume)
        await self.agent.handle_intervention()
        
        # Get arguments with defaults
        param1 = self.args.get("param1", "default_value")
        param2 = self.args.get("param2", 0)
        optional_flag = self.args.get("optional_flag", False)
        
        # Validate required arguments
        if not param1:
            return Response(
                message="Error: param1 is required",
                break_loop=False
            )
        
        # Log to UI
        self.agent.context.log.log(
            type="info",
            heading=f"icon://tool {self.name}",
            content=f"Processing with param1={param1}"
        )
        
        # Print to terminal (for debugging)
        PrintStyle(font_color="cyan").print(f"Executing {self.name}")
        
        # Update progress (visible in streaming output)
        self.set_progress(f"Processing {param1}...")
        
        # Perform main operation
        try:
            result = await self._process_data(param1, param2)
        except Exception as e:
            return Response(
                message=f"Error: {str(e)}",
                break_loop=False
            )
        
        # Clear progress
        self.set_progress(None)
        
        # Return response
        # break_loop=True ends the agent's message loop
        # break_loop=False allows agent to continue processing
        return Response(
            message=result,
            break_loop=False,
            additional={"custom_data": "value"}  # Optional extra data
        )

    async def _process_data(self, param1: str, param2: int) -> str:
        """
        Internal processing method.
        
        Separate business logic from tool interface for cleaner code.
        """
        # Access agent's persistent data
        previous_result = self.agent.get_data("my_tool_last_result")
        
        # Perform operation
        result = f"Processed: {param1} with {param2}"
        
        # Store data for future use
        self.agent.set_data("my_tool_last_result", result)
        
        return result

    async def before_execution(self, **kwargs):
        """
        Optional hook called before execute().
        
        Use for:
        - Validation
        - Resource acquisition
        - Logging
        """
        PrintStyle(font_color="gray").print(f"Preparing {self.name}...")

    async def after_execution(self, response: Response, **kwargs):
        """
        Optional hook called after execute().
        
        Use for:
        - Adding results to history
        - Cleanup
        - Metrics collection
        
        Default behavior adds tool result to agent history.
        Override to customize or extend.
        """
        # Add to agent history (standard pattern)
        self.agent.hist_add_tool_result(
            self.name,
            response.message,
            **(response.additional or {})
        )
        
        # Custom logging
        self.agent.context.log.log(
            type="info",
            heading=f"icon://check {self.name} complete",
            content=f"Result length: {len(response.message)}"
        )

    def get_log_object(self):
        """
        Optional: Customize log appearance in UI.
        
        Returns a log object for streaming output display.
        """
        return self.agent.context.log.log(
            type="tool",
            heading=self.get_heading(),
            content="",
            kvps=self.args,
        )

    def get_heading(self, text: str = "") -> str:
        """
        Optional: Customize log heading.
        """
        if not text:
            text = f"{self.name}"
        return f"icon://tool {text}"


# Alternative: Simple tool without hooks
class SimpleCustomTool(Tool):
    """
    Minimal tool implementation.
    
    For simple tools, only execute() is required.
    """

    async def execute(self, **kwargs) -> Response:
        value = self.args.get("value", "")
        result = f"Simple result: {value}"
        return Response(message=result, break_loop=False)


# Alternative: Tool with state management
class StatefulTool(Tool):
    """
    Tool that maintains state across calls.
    
    Uses agent.get_data/set_data for persistence.
    """

    STATE_KEY = "_stateful_tool_state"

    async def execute(self, **kwargs) -> Response:
        # Get or initialize state
        state = self.agent.get_data(self.STATE_KEY) or {"counter": 0, "history": []}
        
        # Update state
        state["counter"] += 1
        state["history"].append(self.args.get("input", ""))
        
        # Save state
        self.agent.set_data(self.STATE_KEY, state)
        
        return Response(
            message=f"Call #{state['counter']}, history: {len(state['history'])} items",
            break_loop=False
        )
