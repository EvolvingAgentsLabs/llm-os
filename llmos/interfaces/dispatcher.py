"""
Dispatcher - The Brain of the LLM OS
Decides between Learner and Follower modes based on token economy
"""

from typing import Dict, Any
from pathlib import Path

from kernel.bus import EventBus
from kernel.token_economy import TokenEconomy, LowBatteryError
from memory.store import MemoryStore
from memory.traces import TraceManager, ExecutionTrace
from interfaces.cortex import Cortex


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
    The Dispatcher - Makes the Learner/Follower decision
    This is the "operating system scheduler" that optimizes for token cost
    """

    def __init__(
        self,
        event_bus: EventBus,
        token_economy: TokenEconomy,
        memory_store: MemoryStore,
        trace_manager: TraceManager
    ):
        self.event_bus = event_bus
        self.token_economy = token_economy
        self.memory_store = memory_store
        self.trace_manager = trace_manager

        # Initialize cortex (will be lazy-loaded)
        self.cortex: Cortex = None

    async def _ensure_cortex(self):
        """Lazy initialization of cortex"""
        if self.cortex is None:
            from pathlib import Path
            workspace = Path("./workspace")
            self.cortex = Cortex(self.event_bus, workspace)
            await self.cortex.initialize()

    async def dispatch(self, goal: str) -> Dict[str, Any]:
        """
        Dispatch a goal to either Learner or Follower mode

        This is the core algorithm that makes LLM OS economical:
        1. Check if we have a proven trace
        2. If yes → Follower Mode (cheap, fast, deterministic)
        3. If no → Learner Mode (expensive, slow, creative)

        Args:
            goal: Natural language goal

        Returns:
            Result dictionary
        """
        print("=" * 60)
        print(f"🎯 Dispatching: {goal}")
        print("=" * 60)

        # Step 1: Query memory for matching trace
        trace = self.trace_manager.find_trace(goal, confidence_threshold=0.9)

        # Step 2: Decide mode
        if trace:
            print(f"📦 Found execution trace (confidence: {trace.success_rating:.2f})")
            print(f"💡 Mode: FOLLOWER (Cost: ~$0, Time: ~{trace.estimated_time_secs:.1f}s)")

            mode = "FOLLOWER"
            estimated_cost = 0.0

        else:
            print("🆕 No matching trace found")
            print("💡 Mode: LEARNER (Cost: ~$0.50, Time: variable)")

            mode = "LEARNER"
            estimated_cost = 0.50  # Rough estimate for Claude API call

            # Check budget
            try:
                self.token_economy.check_budget(estimated_cost)
            except LowBatteryError as e:
                return {
                    "success": False,
                    "error": str(e),
                    "mode": None
                }

        # Step 3: Execute
        await self._ensure_cortex()

        if mode == "FOLLOWER":
            success = await self.cortex.follow(trace)

            # Update trace statistics
            self.trace_manager.update_trace_usage(trace.goal_signature, success)

            return {
                "success": success,
                "mode": mode,
                "trace": trace,
                "cost": 0.0
            }

        else:  # LEARNER
            # Execute with full LLM reasoning
            trace = await self.cortex.learn(goal)

            # Save the new trace for future use
            self.trace_manager.save_trace(trace)

            # Deduct cost
            actual_cost = estimated_cost  # TODO: Get actual cost from Claude SDK
            self.token_economy.deduct(actual_cost, f"Learner: {goal[:50]}...")

            return {
                "success": True,
                "mode": mode,
                "trace": trace,
                "cost": actual_cost
            }
