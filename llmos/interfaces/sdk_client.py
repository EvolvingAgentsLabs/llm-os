"""
Claude SDK Client Integration for llmos
Proper integration with Claude Agent SDK for Learner and Orchestrator modes
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from claude_agent_sdk import ClaudeSDKClient, query as sdk_query
    from claude_agent_sdk.types import ClaudeAgentOptions, HookEvent, HookMatcher, Message
    from claude_agent_sdk.types import AssistantMessage, ResultMessage, TextBlock, ToolUseBlock
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    print("Warning: claude-agent-sdk not installed. Install with: pip install claude-agent-sdk")

from memory.traces_sdk import ExecutionTrace
from kernel.project_manager import Project
from kernel.agent_factory import AgentSpec


class TraceBuilder:
    """
    Builds execution traces from SDK messages

    Captures tool usage, outputs, and metadata during execution
    to create replayable traces for Follower mode.
    """

    def __init__(self, goal: str):
        self.goal = goal
        self.tools_used: List[str] = []
        self.output_parts: List[str] = []
        self.error_notes: List[str] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.cost_usd: float = 0.0
        self.success: bool = True

    def add_message(self, message: 'Message'):
        """Process message and extract trace information"""
        if not SDK_AVAILABLE:
            return

        # Extract from AssistantMessage
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    self.output_parts.append(block.text)
                elif isinstance(block, ToolUseBlock):
                    if block.name not in self.tools_used:
                        self.tools_used.append(block.name)

        # Extract from ResultMessage
        elif isinstance(message, ResultMessage):
            self.end_time = datetime.now()
            self.cost_usd = message.total_cost_usd
            # Consider it successful if no error in result
            self.success = not hasattr(message, 'error') or message.error is None

    def add_error(self, error: str):
        """Add error note"""
        self.error_notes.append(error)
        self.success = False

    def to_trace(self, goal_signature: str) -> ExecutionTrace:
        """Convert to ExecutionTrace"""
        execution_time = (
            (self.end_time - self.start_time).total_seconds()
            if self.end_time else 0.0
        )

        return ExecutionTrace(
            goal_signature=goal_signature,
            goal_text=self.goal,
            success_rating=1.0 if self.success else 0.5,
            usage_count=1,
            created_at=self.start_time,
            last_used=None,
            estimated_cost_usd=self.cost_usd,
            estimated_time_secs=execution_time,
            mode="LEARNER",
            tools_used=self.tools_used if self.tools_used else None,
            output_summary="\n".join(self.output_parts[:5]) if self.output_parts else "",
            error_notes="\n".join(self.error_notes) if self.error_notes else ""
        )


class LLMOSSDKClient:
    """
    Wrapper around Claude Agent SDK for llmos integration

    Provides proper integration between llmos architecture and
    Claude Agent SDK, handling:
    - Learner mode execution with trace capture
    - Orchestrator mode with multi-agent coordination
    - Hook-based trace building
    - Project-aware execution
    """

    def __init__(
        self,
        workspace: Path,
        trace_manager: Optional[Any] = None
    ):
        """
        Initialize SDK client wrapper

        Args:
            workspace: Workspace directory
            trace_manager: Optional trace manager for saving traces
        """
        if not SDK_AVAILABLE:
            raise RuntimeError(
                "Claude Agent SDK not installed. "
                "Install with: pip install claude-agent-sdk"
            )

        self.workspace = Path(workspace)
        self.trace_manager = trace_manager

    def _build_agent_options(
        self,
        agent_spec: Optional[AgentSpec] = None,
        project: Optional[Project] = None,
        permission_mode: str = "default",
        hooks: Optional[Dict[HookEvent, List[HookMatcher]]] = None
    ) -> ClaudeAgentOptions:
        """
        Build ClaudeAgentOptions from agent spec and project

        Args:
            agent_spec: Agent specification
            project: Project context
            permission_mode: Permission mode for tools
            hooks: Optional hooks for events

        Returns:
            ClaudeAgentOptions configured for llmos
        """
        # Determine working directory
        cwd = str(project.path) if project else str(self.workspace)

        # Build system prompt
        system_prompt = None
        if agent_spec:
            system_prompt = agent_spec.system_prompt

        return ClaudeAgentOptions(
            system_prompt=system_prompt,
            cwd=cwd,
            permission_mode=permission_mode,
            hooks=hooks or {}
        )

    async def execute_learner_mode(
        self,
        goal: str,
        goal_signature: str,
        agent_spec: Optional[AgentSpec] = None,
        project: Optional[Project] = None,
        max_cost_usd: float = 5.0
    ) -> Dict[str, Any]:
        """
        Execute goal in Learner mode using Claude SDK

        This is the proper way to use the SDK - it handles all
        communication with Claude and returns structured messages.

        Args:
            goal: Goal to execute
            goal_signature: Signature for trace storage
            agent_spec: Optional agent specification
            project: Optional project context
            max_cost_usd: Maximum cost budget

        Returns:
            Result dictionary with trace and execution details
        """
        trace_builder = TraceBuilder(goal)

        # Build SDK options
        options = self._build_agent_options(
            agent_spec=agent_spec,
            project=project,
            permission_mode="acceptEdits"  # Auto-accept edits in Learner mode
        )

        result = {
            "success": False,
            "mode": "LEARNER",
            "trace": None,
            "cost": 0.0,
            "output": ""
        }

        try:
            # Use SDK client
            async with ClaudeSDKClient(options=options) as client:
                # Connect and send goal
                await client.connect(prompt=goal)

                # Receive all messages
                async for message in client.receive_response():
                    trace_builder.add_message(message)

                    # Check cost budget
                    if isinstance(message, ResultMessage):
                        if message.total_cost_usd > max_cost_usd:
                            print(f"⚠️  Cost ${message.total_cost_usd:.2f} exceeded budget ${max_cost_usd:.2f}")

                        result["cost"] = message.total_cost_usd
                        result["success"] = True

            # Build trace
            trace = trace_builder.to_trace(goal_signature)
            result["trace"] = trace
            result["output"] = trace.output_summary

            # Save trace to memory
            if self.trace_manager:
                self.trace_manager.save_trace(trace)

        except Exception as e:
            trace_builder.add_error(str(e))
            result["error"] = str(e)

            # Still save failed trace for learning
            trace = trace_builder.to_trace(goal_signature)
            result["trace"] = trace

            if self.trace_manager:
                self.trace_manager.save_trace(trace)

        return result

    async def execute_one_shot_query(
        self,
        goal: str,
        agent_spec: Optional[AgentSpec] = None,
        project: Optional[Project] = None
    ) -> Dict[str, Any]:
        """
        Execute simple one-shot query using SDK query function

        Use this for simple, stateless queries where you don't need
        trace capture or complex interaction.

        Args:
            goal: Goal to execute
            agent_spec: Optional agent specification
            project: Optional project context

        Returns:
            Result dictionary
        """
        options = self._build_agent_options(
            agent_spec=agent_spec,
            project=project
        )

        result = {
            "success": False,
            "output": "",
            "cost": 0.0
        }

        output_parts = []

        try:
            async for message in sdk_query(prompt=goal, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            output_parts.append(block.text)

                if isinstance(message, ResultMessage):
                    result["cost"] = message.total_cost_usd
                    result["success"] = True

            result["output"] = "\n".join(output_parts)

        except Exception as e:
            result["error"] = str(e)

        return result

    async def execute_with_streaming(
        self,
        goal: str,
        on_message_callback,
        agent_spec: Optional[AgentSpec] = None,
        project: Optional[Project] = None
    ) -> Dict[str, Any]:
        """
        Execute with streaming callback for real-time updates

        Args:
            goal: Goal to execute
            on_message_callback: Async callback called for each message
            agent_spec: Optional agent specification
            project: Optional project context

        Returns:
            Result dictionary
        """
        options = self._build_agent_options(
            agent_spec=agent_spec,
            project=project
        )

        result = {
            "success": False,
            "cost": 0.0
        }

        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.connect(prompt=goal)

                async for message in client.receive_response():
                    # Call user callback
                    await on_message_callback(message)

                    if isinstance(message, ResultMessage):
                        result["cost"] = message.total_cost_usd
                        result["success"] = True

        except Exception as e:
            result["error"] = str(e)

        return result


def is_sdk_available() -> bool:
    """Check if Claude Agent SDK is available"""
    return SDK_AVAILABLE


def get_sdk_version() -> Optional[str]:
    """Get installed SDK version"""
    if not SDK_AVAILABLE:
        return None

    try:
        import claude_agent_sdk
        return getattr(claude_agent_sdk, '__version__', 'unknown')
    except:
        return None
