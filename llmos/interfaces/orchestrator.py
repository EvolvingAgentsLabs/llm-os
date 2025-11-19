"""
SystemAgent Orchestrator - Multi-agent coordination using Claude Agent SDK
Implements llmunix-style orchestration in llmos
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
except ImportError:
    print("Warning: claude-agent-sdk not installed. Install with: pip install claude-agent-sdk")
    ClaudeSDKClient = None
    ClaudeAgentOptions = None

from kernel.bus import EventBus, Event, EventType
from kernel.project_manager import Project, ProjectManager
from kernel.agent_factory import AgentFactory, AgentSpec
from kernel.component_registry import ComponentRegistry
from kernel.state_manager import StateManager, ExecutionStep
from kernel.token_economy import TokenEconomy
from memory.traces import TraceManager


@dataclass
class OrchestrationResult:
    """Result of orchestrated execution"""
    success: bool
    output: Any
    steps_completed: int
    total_steps: int
    cost_usd: float
    execution_time_secs: float
    state_summary: Dict[str, Any]


class SystemAgent:
    """
    SystemAgent Orchestrator - Master coordinator for multi-agent workflows

    Equivalent to llmunix SystemAgent, but using Claude Agent SDK.
    Coordinates multiple specialized agents to solve complex problems.
    """

    def __init__(
        self,
        event_bus: EventBus,
        project_manager: ProjectManager,
        agent_factory: AgentFactory,
        component_registry: ComponentRegistry,
        token_economy: TokenEconomy,
        trace_manager: TraceManager,
        workspace: Path,
        model: str = "claude-sonnet-4-5-20250929"
    ):
        """
        Initialize SystemAgent

        Args:
            event_bus: Event bus for system events
            project_manager: Project manager
            agent_factory: Agent factory for creating specialized agents
            component_registry: Component registry for discovery
            token_economy: Token economy for budget management
            trace_manager: Trace manager for memory
            workspace: Workspace directory
            model: Claude model to use
        """
        self.event_bus = event_bus
        self.project_manager = project_manager
        self.agent_factory = agent_factory
        self.component_registry = component_registry
        self.token_economy = token_economy
        self.trace_manager = trace_manager
        self.workspace = Path(workspace)
        self.model = model

        # Ensure system agent is registered
        self._ensure_system_agent_registered()

    def _ensure_system_agent_registered(self):
        """Ensure system agent is in registry"""
        from kernel.agent_factory import SYSTEM_AGENT_TEMPLATE

        if not self.component_registry.get_agent("system-agent"):
            self.component_registry.register_agent(SYSTEM_AGENT_TEMPLATE)

    async def orchestrate(
        self,
        goal: str,
        project: Optional[Project] = None,
        max_cost_usd: float = 5.0
    ) -> OrchestrationResult:
        """
        Orchestrate multi-agent execution to achieve goal

        This is the main entry point for complex, multi-step tasks.

        Workflow:
        1. Consult memory for similar tasks
        2. Decompose goal into sub-tasks
        3. Identify required specialized agents
        4. Create agents if needed (via AgentFactory)
        5. Delegate sub-tasks to agents
        6. Coordinate results
        7. Update memory with learnings

        Args:
            goal: Natural language goal to achieve
            project: Optional project context
            max_cost_usd: Maximum cost budget for this orchestration

        Returns:
            OrchestrationResult with execution details
        """
        import time
        start_time = time.time()

        # Create project if not provided
        if project is None:
            # Extract project name from goal (simple heuristic)
            project_name = goal.split()[0:3]
            project_name = "_".join(project_name).lower().replace(" ", "_")
            project = self.project_manager.create_project(
                name=project_name,
                description=f"Auto-created for goal: {goal}"
            )

        # Initialize state manager
        state = StateManager(project.root_path)
        state.initialize_execution(goal)

        # Set budget constraint
        state.update_constraint("max_token_cost", max_cost_usd)

        # Emit orchestration started event
        await self.event_bus.publish(Event(
            type=EventType.TASK_STARTED,
            data={"goal": goal, "project": project.name}
        ))

        # Log event
        state.log_event("ORCHESTRATION_STARTED", {
            "goal": goal,
            "project": project.name,
            "max_cost_usd": max_cost_usd
        })

        try:
            # Step 1: Consult memory
            state.log_event("MEMORY_CONSULTATION", {"phase": "started"})
            memory_insights = await self._consult_memory(goal)
            state.set_variable("memory_insights", memory_insights)

            # Step 2: Decompose goal using Claude Agent SDK
            state.log_event("GOAL_DECOMPOSITION", {"phase": "started"})
            plan = await self._decompose_goal(goal, project, memory_insights)
            state.set_plan(plan)

            # Step 3: Execute plan
            total_cost = 0.0
            for step in plan:
                state.update_step_status(step.step_number, "in_progress")

                # Check budget
                if total_cost >= max_cost_usd:
                    state.log_event("BUDGET_EXCEEDED", {
                        "total_cost": total_cost,
                        "max_cost": max_cost_usd
                    })
                    break

                # Execute step
                step_result = await self._execute_step(step, project, state)

                if step_result["success"]:
                    state.update_step_status(
                        step.step_number,
                        "completed",
                        result=step_result.get("output")
                    )
                    total_cost += step_result.get("cost", 0.0)
                else:
                    state.update_step_status(
                        step.step_number,
                        "failed",
                        error=step_result.get("error")
                    )
                    # Continue or halt based on criticality
                    # For now, continue

            # Step 4: Consolidate results
            execution_summary = state.get_execution_summary()
            state.mark_execution_complete(success=True)

            # Emit completion event
            await self.event_bus.publish(Event(
                type=EventType.TASK_COMPLETED,
                data={"goal": goal, "summary": execution_summary}
            ))

            # Calculate execution time
            execution_time = time.time() - start_time

            return OrchestrationResult(
                success=True,
                output=execution_summary,
                steps_completed=execution_summary["completed_steps"],
                total_steps=execution_summary["total_steps"],
                cost_usd=total_cost,
                execution_time_secs=execution_time,
                state_summary=execution_summary
            )

        except Exception as e:
            state.log_event("ORCHESTRATION_FAILED", {"error": str(e)})
            state.mark_execution_complete(success=False)

            execution_time = time.time() - start_time

            return OrchestrationResult(
                success=False,
                output=str(e),
                steps_completed=0,
                total_steps=len(plan) if 'plan' in locals() else 0,
                cost_usd=0.0,
                execution_time_secs=execution_time,
                state_summary={}
            )

    async def _consult_memory(self, goal: str) -> Dict[str, Any]:
        """
        Consult memory for similar tasks

        Args:
            goal: Goal to search for

        Returns:
            Memory insights
        """
        # Find similar traces
        trace = self.trace_manager.find_trace(goal, confidence_threshold=0.7)

        insights = {
            "similar_trace_found": trace is not None,
            "trace": trace,
            "recommendations": []
        }

        if trace:
            insights["recommendations"].append(
                f"Similar task executed {trace.usage_count} times with "
                f"{trace.success_rating:.0%} success rate"
            )

        return insights

    async def _decompose_goal(
        self,
        goal: str,
        project: Project,
        memory_insights: Dict[str, Any]
    ) -> List[ExecutionStep]:
        """
        Decompose goal into execution steps using Claude Agent SDK

        Args:
            goal: Goal to decompose
            project: Project context
            memory_insights: Insights from memory consultation

        Returns:
            List of ExecutionStep instances
        """
        if ClaudeSDKClient is None:
            raise RuntimeError("Claude Agent SDK not installed")

        # Build planning prompt
        planning_prompt = f"""Decompose this goal into concrete execution steps:

Goal: {goal}

Memory Insights:
{json.dumps(memory_insights, indent=2)}

Available Agents:
{self._get_available_agents_summary()}

Create a detailed execution plan with:
1. Clear, actionable steps
2. Agent assignment for each step (or "system-agent" if no specialized agent needed)
3. Expected output for each step

Format your response as JSON:
{{
  "steps": [
    {{
      "number": 1,
      "description": "Step description",
      "agent": "agent-name",
      "expected_output": "What this step should produce"
    }}
  ]
}}
"""

        # Configure agent options
        options = ClaudeAgentOptions(
            model=self.model,
            cwd=str(project.root_path),
            allowed_tools=["Read", "Write", "Grep", "Glob"],
            system_prompt={
                "type": "preset",
                "preset": "claude_code",
                "append": """
You are the planning component of a multi-agent LLM operating system.
Your role is to decompose complex goals into concrete execution steps.

Think systematically:
1. What needs to be done?
2. What's the optimal order?
3. Which specialized agent should handle each step?
4. What are the dependencies between steps?

Be specific and actionable.
"""
            }
        )

        plan_json = None

        async with ClaudeSDKClient(options=options) as client:
            await client.query(planning_prompt)

            async for msg in client.receive_response():
                # Extract plan from response
                if hasattr(msg, "content"):
                    for block in msg.content:
                        if hasattr(block, "text"):
                            text = block.text
                            # Try to parse JSON from response
                            try:
                                # Find JSON in response
                                start = text.find("{")
                                end = text.rfind("}") + 1
                                if start != -1 and end != 0:
                                    plan_json = json.loads(text[start:end])
                            except json.JSONDecodeError:
                                continue

        # Convert to ExecutionStep instances
        steps = []
        if plan_json and "steps" in plan_json:
            for step_data in plan_json["steps"]:
                steps.append(ExecutionStep(
                    step_number=step_data["number"],
                    description=step_data["description"],
                    agent=step_data.get("agent", "system-agent"),
                    status="pending"
                ))

        # If no plan generated, create simple fallback
        if not steps:
            steps = [
                ExecutionStep(
                    step_number=1,
                    description=goal,
                    agent="system-agent",
                    status="pending"
                )
            ]

        return steps

    async def _execute_step(
        self,
        step: ExecutionStep,
        project: Project,
        state: StateManager
    ) -> Dict[str, Any]:
        """
        Execute a single step, potentially delegating to specialized agent

        Args:
            step: ExecutionStep to execute
            project: Project context
            state: State manager

        Returns:
            Result dictionary with success, output, cost
        """
        state.log_event("STEP_EXECUTION_STARTED", {
            "step": step.step_number,
            "description": step.description,
            "agent": step.agent
        })

        # Get agent spec
        agent_spec = self.component_registry.get_agent(step.agent)

        if agent_spec is None:
            # Try to create agent on-demand
            state.log_event("AGENT_NOT_FOUND", {
                "agent": step.agent,
                "action": "attempting to create"
            })

            # For now, use system-agent as fallback
            agent_spec = self.component_registry.get_agent("system-agent")

        # Delegate to agent using Claude Agent SDK
        result = await self._delegate_to_agent(
            agent_spec,
            step.description,
            project,
            state
        )

        state.log_event("STEP_EXECUTION_COMPLETED", {
            "step": step.step_number,
            "success": result["success"],
            "cost": result.get("cost", 0.0)
        })

        return result

    async def _delegate_to_agent(
        self,
        agent_spec: AgentSpec,
        task: str,
        project: Project,
        state: StateManager
    ) -> Dict[str, Any]:
        """
        Delegate task to specialized agent using Claude Agent SDK

        This follows the pattern from the chief_of_staff example.

        Args:
            agent_spec: Agent specification
            task: Task description
            project: Project context
            state: State manager

        Returns:
            Result dictionary
        """
        if ClaudeSDKClient is None:
            raise RuntimeError("Claude Agent SDK not installed")

        # Configure agent options
        options = ClaudeAgentOptions(
            model=self.model,
            cwd=str(project.root_path),
            allowed_tools=agent_spec.tools,
            system_prompt={
                "type": "text",
                "text": agent_spec.system_prompt
            },
            permission_mode="acceptEdits"  # Auto-accept tool executions
        )

        result_text = None
        cost_estimate = 0.0

        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.query(task)

                async for msg in client.receive_response():
                    # Emit activity event
                    activity = self._get_activity_text(msg)
                    if activity:
                        state.log_event("AGENT_ACTIVITY", {
                            "agent": agent_spec.name,
                            "activity": activity
                        })

                    # Extract result
                    if hasattr(msg, "result"):
                        result_text = msg.result

                    # Estimate cost (rough approximation)
                    # TODO: Get actual cost from SDK if available
                    cost_estimate += 0.001  # Small cost per message

            return {
                "success": True,
                "output": result_text,
                "cost": cost_estimate
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "cost": cost_estimate
            }

    def _get_activity_text(self, msg) -> Optional[str]:
        """Extract activity text from a message (from chief_of_staff example)"""
        try:
            if "Assistant" in msg.__class__.__name__:
                if hasattr(msg, "content") and msg.content:
                    first_content = msg.content[0] if isinstance(msg.content, list) else msg.content
                    if hasattr(first_content, "name"):
                        return f"Using: {first_content.name}()"
                return "Thinking..."
            elif "User" in msg.__class__.__name__:
                return "Tool completed"
        except (AttributeError, IndexError):
            pass
        return None

    def _get_available_agents_summary(self) -> str:
        """Get summary of available agents for planning"""
        agents = self.component_registry.list_agents(status="production")

        summary_parts = []
        for agent in agents:
            summary_parts.append(
                f"- {agent.name}: {agent.description} (Tools: {', '.join(agent.tools)})"
            )

        return "\n".join(summary_parts) if summary_parts else "No specialized agents available"

    async def create_agent_on_demand(
        self,
        capability: str,
        project: Project
    ) -> Optional[AgentSpec]:
        """
        Create a specialized agent on-demand for a capability

        Args:
            capability: Capability description
            project: Project context

        Returns:
            Created AgentSpec or None
        """
        # Use Claude to design the agent
        if ClaudeSDKClient is None:
            return None

        design_prompt = f"""Design a specialized agent for this capability: {capability}

Create an agent specification in JSON format:
{{
  "name": "kebab-case-name",
  "type": "specialized",
  "category": "domain_category",
  "description": "When to use this agent",
  "tools": ["Read", "Write", "Bash"],
  "capabilities": ["capability 1", "capability 2"],
  "constraints": ["constraint 1", "constraint 2"],
  "system_prompt": "Detailed agent instructions..."
}}
"""

        options = ClaudeAgentOptions(
            model=self.model,
            cwd=str(project.root_path),
            allowed_tools=[],
            system_prompt={
                "type": "text",
                "text": "You are an agent designer. Create detailed agent specifications."
            }
        )

        agent_json = None

        async with ClaudeSDKClient(options=options) as client:
            await client.query(design_prompt)

            async for msg in client.receive_response():
                if hasattr(msg, "content"):
                    for block in msg.content:
                        if hasattr(block, "text"):
                            text = block.text
                            try:
                                start = text.find("{")
                                end = text.rfind("}") + 1
                                if start != -1 and end != 0:
                                    agent_json = json.loads(text[start:end])
                            except json.JSONDecodeError:
                                continue

        if agent_json:
            # Create agent using factory
            agent = self.agent_factory.create_agent(**agent_json)
            self.component_registry.register_agent(agent)
            return agent

        return None
