"""
Dispatcher - The Brain of the LLM OS
Decides between Learner, Follower, and Orchestration modes based on token economy
"""

from typing import Dict, Any, Optional
from pathlib import Path

from kernel.bus import EventBus
from kernel.token_economy import TokenEconomy, LowBatteryError
from kernel.project_manager import ProjectManager, Project
from kernel.config import LLMOSConfig
from kernel.mode_strategies import (
    ModeSelectionStrategy,
    ModeContext,
    get_strategy
)
from memory.store_sdk import MemoryStore
from memory.traces_sdk import TraceManager, ExecutionTrace
from memory.query_sdk import MemoryQueryInterface
from interfaces.cortex import Cortex
from interfaces.sdk_client import LLMOSSDKClient, is_sdk_available


class TaskBlock:
    """
    A TaskBlock is a "Program" in the LLM OS
    Not a compiled binary, but a natural language intent
    """

    def __init__(
        self,
        goal: str,
        inputs: Dict[str, Any] = None,
        constraints: list = None,
        priority: int = 50,
        mode: str = "AUTO"
    ):
        self.goal = goal
        self.inputs = inputs or {}
        self.constraints = constraints or []
        self.priority = priority
        self.mode = mode  # AUTO, LEARNER, or FOLLOWER


class Dispatcher:
    """
    The Dispatcher - Makes the Learner/Follower/Orchestration decision
    This is the "operating system scheduler" that optimizes for token cost

    Now supports three modes:
    1. FOLLOWER: Execute proven trace (fast, cheap, deterministic)
    2. LEARNER: Learn new pattern (slow, expensive, creative)
    3. ORCHESTRATOR: Multi-agent coordination (complex, adaptive, powerful)
    """

    def __init__(
        self,
        event_bus: EventBus,
        token_economy: TokenEconomy,
        memory_store: MemoryStore,
        trace_manager: TraceManager,
        project_manager: Optional[ProjectManager] = None,
        workspace: Optional[Path] = None,
        config: Optional[LLMOSConfig] = None,
        strategy: Optional[ModeSelectionStrategy] = None
    ):
        self.event_bus = event_bus
        self.token_economy = token_economy
        self.memory_store = memory_store
        self.trace_manager = trace_manager
        self.project_manager = project_manager
        self.workspace = workspace or Path("./workspace")

        # Configuration and strategy
        self.config = config or LLMOSConfig()
        self.strategy = strategy or get_strategy("auto")

        # Initialize cortex (will be lazy-loaded)
        self.cortex: Cortex = None

        # Initialize orchestrator (will be lazy-loaded)
        self.orchestrator = None

        # Initialize memory query interface
        self.memory_query = MemoryQueryInterface(trace_manager, memory_store)

        # Initialize SDK client (if available)
        self.sdk_client: Optional[LLMOSSDKClient] = None
        if is_sdk_available():
            self.sdk_client = LLMOSSDKClient(
                workspace=self.workspace,
                trace_manager=self.trace_manager,
                token_economy=self.token_economy,  # For budget control hooks
                memory_query=self.memory_query  # For context injection hooks
            )
        else:
            print("⚠️  Claude Agent SDK not available - using fallback cortex mode")
            print("   Install with: pip install claude-agent-sdk")

    async def _ensure_cortex(self):
        """Lazy initialization of cortex"""
        if self.cortex is None:
            self.cortex = Cortex(self.event_bus, self.workspace)
            await self.cortex.initialize()

    async def _ensure_orchestrator(self):
        """Lazy initialization of orchestrator"""
        if self.orchestrator is None:
            from kernel.agent_factory import AgentFactory
            from kernel.component_registry import ComponentRegistry
            from interfaces.orchestrator import SystemAgent

            # Initialize dependencies
            agent_factory = AgentFactory(self.workspace)
            component_registry = ComponentRegistry()

            # Register built-in agents
            for agent in agent_factory.list_agents():
                component_registry.register_agent(agent)

            self.orchestrator = SystemAgent(
                event_bus=self.event_bus,
                project_manager=self.project_manager,
                agent_factory=agent_factory,
                component_registry=component_registry,
                token_economy=self.token_economy,
                trace_manager=self.trace_manager,
                workspace=self.workspace
            )

    async def dispatch(
        self,
        goal: str,
        mode: str = "AUTO",
        project: Optional[Project] = None,
        max_cost_usd: float = 5.0
    ) -> Dict[str, Any]:
        """
        Dispatch a goal to appropriate execution mode

        This is the core algorithm that makes LLM OS economical:
        1. Check complexity (simple vs complex)
        2. Check if we have a proven trace
        3. Route to: FOLLOWER (proven) / LEARNER (novel) / ORCHESTRATOR (complex)

        Args:
            goal: Natural language goal
            mode: "AUTO" (auto-detect), "LEARNER", "FOLLOWER", or "ORCHESTRATOR"
            project: Optional project context for orchestration
            max_cost_usd: Maximum cost budget

        Returns:
            Result dictionary
        """
        print("=" * 60)
        print(f"🎯 Dispatching: {goal}")
        print("=" * 60)

        # Determine execution mode
        if mode == "AUTO":
            mode = await self._determine_mode(goal)

        print(f"📋 Selected Mode: {mode}")
        print("=" * 60)

        # Route to appropriate mode
        if mode == "CRYSTALLIZED":
            return await self._dispatch_crystallized(goal)
        elif mode == "ORCHESTRATOR":
            return await self._dispatch_orchestrator(goal, project, max_cost_usd)
        elif mode == "FOLLOWER":
            return await self._dispatch_follower(goal)
        elif mode == "MIXED":
            return await self._dispatch_mixed(goal, project, max_cost_usd)
        else:  # LEARNER
            return await self._dispatch_learner(goal, project, max_cost_usd)

    async def _determine_mode(self, goal: str) -> str:
        """
        Automatically determine the best execution mode using Strategy pattern

        Uses the configured mode selection strategy to determine the optimal
        execution mode based on available traces, complexity, and configuration.

        Execution modes:
        - CRYSTALLIZED: Trace has been converted to tool - Execute tool directly
        - FOLLOWER: High confidence - Execute proven trace directly
        - MIXED: Medium confidence - Use trace as few-shot guidance
        - LEARNER: Low confidence - Full LLM reasoning
        - ORCHESTRATOR: Complex multi-agent task

        Args:
            goal: Natural language goal

        Returns:
            Mode string: "CRYSTALLIZED", "FOLLOWER", "MIXED", "LEARNER", or "ORCHESTRATOR"
        """
        # Use strategy pattern for mode selection
        context = ModeContext(
            goal=goal,
            trace_manager=self.trace_manager,
            config=self.config
        )

        decision = await self.strategy.determine_mode(context)

        # Log decision
        if decision.trace:
            if decision.mode == "CRYSTALLIZED":
                print(f"💎 Crystallized tool: {decision.trace.crystallized_into_tool}")
                print(f"   {decision.reasoning}")
            elif decision.mode == "FOLLOWER":
                print(f"📦 Trace replay (confidence: {decision.confidence:.0%})")
                print(f"   Success: {decision.trace.success_rating:.0%}, "
                      f"Used: {decision.trace.usage_count}x")
                print(f"   {decision.reasoning}")
            elif decision.mode == "MIXED":
                print(f"📝 Trace-guided (confidence: {decision.confidence:.0%})")
                print(f"   {decision.reasoning}")
        else:
            if decision.mode == "ORCHESTRATOR":
                print(f"🔀 {decision.reasoning}")
            else:
                print(f"🆕 {decision.reasoning}")

        return decision.mode

    async def _dispatch_crystallized(self, goal: str) -> Dict[str, Any]:
        """
        Dispatch to Crystallized mode (execute generated tool directly)

        This is the final form of the HOPE architecture - instant, free execution
        of a crystallized pattern via Python code.

        Args:
            goal: Natural language goal

        Returns:
            Result dictionary
        """
        # Find the trace with crystallized tool
        result = await self.trace_manager.find_trace_with_llm(goal, min_confidence=0.75)

        if not result:
            return {
                "success": False,
                "error": "No crystallized trace found",
                "mode": "CRYSTALLIZED"
            }

        trace, confidence = result

        if not trace.crystallized_into_tool:
            return {
                "success": False,
                "error": "Trace not crystallized",
                "mode": "CRYSTALLIZED"
            }

        print(f"💡 Cost: $0.00 (crystallized tool)")
        print(f"💡 Time: ~instant")

        # Execute the crystallized tool
        # Note: Tool execution would be handled by the plugin system
        # For now, we return success with metadata

        # Update trace statistics
        self.trace_manager.update_usage(trace.goal_signature)

        return {
            "success": True,
            "mode": "CRYSTALLIZED",
            "tool_name": trace.crystallized_into_tool,
            "trace": trace,
            "cost": 0.0,
            "message": f"Executed crystallized tool: {trace.crystallized_into_tool}"
        }

    async def _dispatch_follower(self, goal: str) -> Dict[str, Any]:
        """
        Dispatch to Follower mode (direct trace replay)

        Used when confidence ≥0.92 (virtually identical to previous execution)
        """
        # Try to find trace with LLM matching
        result = await self.trace_manager.find_trace_with_llm(goal, min_confidence=0.92)

        if not result:
            # Fallback to hash matching
            trace = self.trace_manager.find_trace(goal, min_confidence=0.9)
            if not trace:
                return {
                    "success": False,
                    "error": "No trace found for Follower mode",
                    "mode": "FOLLOWER"
                }
        else:
            trace, confidence = result

        print(f"💡 Cost: ~$0, Time: ~{trace.estimated_time_secs:.1f}s")

        await self._ensure_cortex()
        success = await self.cortex.follow(trace)

        # Update trace statistics
        self.trace_manager.update_usage(trace.goal_signature)

        return {
            "success": success,
            "mode": "FOLLOWER",
            "trace": trace,
            "cost": 0.0
        }

    async def _dispatch_mixed(
        self,
        goal: str,
        project: Optional[Project] = None,
        max_cost_usd: float = 5.0
    ) -> Dict[str, Any]:
        """
        Dispatch to Mixed mode (trace-guided LLM execution)

        Used when confidence is 0.75-0.92 (similar but not identical).
        The trace is provided as few-shot guidance to the LLM.

        This is cheaper than full LEARNER mode but more adaptive than FOLLOWER.
        """
        # Find matching trace
        result = await self.trace_manager.find_trace_with_llm(goal, min_confidence=0.75)

        if not result:
            print("[WARNING] MIXED mode requested but no trace found - falling back to LEARNER")
            return await self._dispatch_learner(goal, project, max_cost_usd)

        trace, confidence = result

        estimated_cost = 0.25  # Cheaper than LEARNER ($0.50) but not free

        print(f"💡 Cost: ~${estimated_cost:.2f}, Time: variable")
        print(f"💡 Using trace as guidance (confidence: {confidence:.0%})")

        # Check budget
        try:
            self.token_economy.check_budget(max_cost_usd)
        except LowBatteryError as e:
            return {
                "success": False,
                "error": str(e),
                "mode": "MIXED"
            }

        # Use SDK client if available
        if self.sdk_client:
            print("🔌 Using Claude Agent SDK with trace guidance")

            # Build few-shot prompt with trace
            few_shot_context = f"""
# Similar Task Example

I have executed a similar task before. Here's what I did:

**Previous Goal:** {trace.goal_text}
**Success Rate:** {trace.success_rating:.0%}
**Tools Used:** {', '.join(trace.tools_used) if trace.tools_used else 'N/A'}

**Output Summary:**
{trace.output_summary if trace.output_summary else 'No summary available'}

---

**Current Goal (may differ slightly):** {goal}

Use the above as guidance, but adapt as needed for the current goal.
"""

            # Execute with few-shot context
            import hashlib
            goal_signature = hashlib.sha256(goal.encode()).hexdigest()[:16]

            result = await self.sdk_client.execute_learner_mode(
                goal=few_shot_context,
                goal_signature=goal_signature,
                project=project,
                max_cost_usd=max_cost_usd
            )

            # Deduct cost
            if result["success"]:
                self.token_economy.deduct(
                    result["cost"],
                    f"Mixed: {goal[:50]}..."
                )

            result["mode"] = "MIXED"
            result["guidance_trace"] = trace
            result["confidence"] = confidence
            return result

        # Fallback to cortex
        else:
            print("⚠️  Using fallback cortex mode (SDK not available)")

            await self._ensure_cortex()

            # Execute with trace as context
            new_trace = await self.cortex.learn(goal, guidance_trace=trace)

            # Save the new trace
            self.trace_manager.save_trace(new_trace)

            # Deduct cost
            self.token_economy.deduct(estimated_cost, f"Mixed: {goal[:50]}...")

            return {
                "success": True,
                "mode": "MIXED",
                "trace": new_trace,
                "guidance_trace": trace,
                "confidence": confidence,
                "cost": estimated_cost
            }

    async def _dispatch_learner(
        self,
        goal: str,
        project: Optional[Project] = None,
        max_cost_usd: float = 5.0
    ) -> Dict[str, Any]:
        """
        Dispatch to Learner mode

        Uses Claude Agent SDK when available for proper integration.
        Falls back to cortex if SDK not installed.
        """
        estimated_cost = 0.50

        print(f"💡 Cost: ~${estimated_cost:.2f}, Time: variable")

        # Check budget
        try:
            self.token_economy.check_budget(max_cost_usd)
        except LowBatteryError as e:
            return {
                "success": False,
                "error": str(e),
                "mode": "LEARNER"
            }

        # Use SDK client if available (PROPER WAY)
        if self.sdk_client:
            print("🔌 Using Claude Agent SDK (proper integration)")

            # Compute goal signature for trace storage
            import hashlib
            goal_signature = hashlib.sha256(goal.encode()).hexdigest()[:16]

            # Get available agents to register in SDK
            available_agents = None
            if hasattr(self, 'orchestrator') and self.orchestrator:
                available_agents = self.orchestrator.component_registry.list_agents()

            # Execute with SDK
            result = await self.sdk_client.execute_learner_mode(
                goal=goal,
                goal_signature=goal_signature,
                project=project,
                available_agents=available_agents,  # Pass all agents!
                max_cost_usd=max_cost_usd
            )

            # Deduct actual cost
            if result["success"]:
                self.token_economy.deduct(
                    result["cost"],
                    f"Learner: {goal[:50]}..."
                )

            return result

        # Fallback to cortex (if SDK not available)
        else:
            print("⚠️  Using fallback cortex mode (SDK not available)")

            await self._ensure_cortex()

            # Execute with full LLM reasoning
            trace = await self.cortex.learn(goal)

            # Save the new trace for future use
            self.trace_manager.save_trace(trace)

            # Deduct cost
            actual_cost = estimated_cost
            self.token_economy.deduct(actual_cost, f"Learner: {goal[:50]}...")

            return {
                "success": True,
                "mode": "LEARNER",
                "trace": trace,
                "cost": actual_cost
            }

    async def _dispatch_orchestrator(
        self,
        goal: str,
        project: Optional[Project],
        max_cost_usd: float
    ) -> Dict[str, Any]:
        """Dispatch to Orchestrator mode (multi-agent)"""
        print(f"💡 Multi-agent orchestration")
        print(f"💡 Max Cost: ${max_cost_usd:.2f}")

        # Check budget
        try:
            self.token_economy.check_budget(max_cost_usd)
        except LowBatteryError as e:
            return {
                "success": False,
                "error": str(e),
                "mode": "ORCHESTRATOR"
            }

        await self._ensure_orchestrator()

        # Execute orchestration
        result = await self.orchestrator.orchestrate(
            goal=goal,
            project=project,
            max_cost_usd=max_cost_usd
        )

        # Deduct actual cost
        if result.success:
            self.token_economy.deduct(
                result.cost_usd,
                f"Orchestrator: {goal[:50]}..."
            )

        return {
            "success": result.success,
            "mode": "ORCHESTRATOR",
            "output": result.output,
            "steps_completed": result.steps_completed,
            "total_steps": result.total_steps,
            "cost": result.cost_usd,
            "execution_time": result.execution_time_secs,
            "state_summary": result.state_summary
        }
