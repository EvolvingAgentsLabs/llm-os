#!/usr/bin/env python3
"""
LLM OS (llmos) - Boot Entry Point
Based on Claude Agent SDK

This is the main entry point for the LLM Operating System.
Treats the LLM as the CPU, Python as the motherboard, and tokens as energy.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from kernel.bus import EventBus
from kernel.scheduler import Scheduler
from kernel.watchdog import Watchdog
from kernel.project_manager import ProjectManager, Project
from kernel.agent_factory import AgentFactory
from kernel.component_registry import ComponentRegistry
from memory.store_sdk import MemoryStore
from memory.traces_sdk import TraceManager
from memory.query_sdk import MemoryQueryInterface
from memory.cross_project_sdk import CrossProjectLearning
from interfaces.dispatcher import Dispatcher
from kernel.token_economy import TokenEconomy


class LLMOS:
    """
    The LLM Operating System

    Separates Cognitive Compute (LLM) from Somatic Compute (Python)
    Managed by a strict Token Economy.

    Now with Phase 2 capabilities:
    - Project management (llmunix-style)
    - Dynamic agent creation
    - Multi-agent orchestration
    - Component registry
    - Memory query interface
    """

    def __init__(
        self,
        budget_usd: float = 10.0,
        workspace: Optional[Path] = None,
        project_name: Optional[str] = None
    ):
        """
        Initialize the LLM OS

        Args:
            budget_usd: Token budget in USD
            workspace: Workspace directory (defaults to ./workspace)
            project_name: Optional project name (creates/loads project)
        """
        self.workspace = workspace or Path("./workspace")
        self.workspace.mkdir(exist_ok=True)

        # Initialize kernel components
        self.event_bus = EventBus()
        self.token_economy = TokenEconomy(budget_usd)
        self.scheduler = Scheduler(self.event_bus)
        self.watchdog = Watchdog(self.event_bus)

        # Initialize memory components (SDK-based, using /memories directory)
        self.memory_store = MemoryStore(self.workspace)
        self.trace_manager = TraceManager(self.workspace / "memories")
        self.memory_query = MemoryQueryInterface(self.trace_manager, self.memory_store)

        # Initialize Phase 2 components
        self.project_manager = ProjectManager(self.workspace)
        self.agent_factory = AgentFactory(self.workspace)
        self.component_registry = ComponentRegistry()

        # Initialize cross-project learning (Phase 2 enhancement)
        self.cross_project_learning = CrossProjectLearning(
            project_manager=self.project_manager,
            workspace=self.workspace
        )

        # Register built-in agents
        self._register_builtin_agents()

        # Create/load project if specified
        self.current_project: Optional[Project] = None
        if project_name:
            self.current_project = self.project_manager.create_project(project_name)

        # Initialize dispatcher with all components
        self.dispatcher = Dispatcher(
            event_bus=self.event_bus,
            token_economy=self.token_economy,
            memory_store=self.memory_store,
            trace_manager=self.trace_manager,
            project_manager=self.project_manager,
            workspace=self.workspace
        )

        self._running = False

    def _register_builtin_agents(self):
        """Register built-in system agents"""
        from kernel.agent_factory import SYSTEM_AGENT_TEMPLATE

        # Register system agent
        self.component_registry.register_agent(SYSTEM_AGENT_TEMPLATE)

        # Register any custom agents from agents/ directory
        for agent_spec in self.agent_factory.list_agents():
            self.component_registry.register_agent(agent_spec)

    async def boot(self):
        """Boot the operating system"""
        print("🚀 Booting LLM OS (Phase 2 - Claude SDK Memory)...")
        print(f"💰 Token Budget: ${self.token_economy.balance:.2f}")
        print(f"📁 Workspace: {self.workspace.absolute()}")
        print(f"💾 Memory: /memories (Claude SDK file-based)")

        if self.current_project:
            print(f"📂 Current Project: {self.current_project.name}")

        # Show memory stats
        mem_stats = self.memory_query.get_memory_statistics()
        print(f"🧠 Traces: {mem_stats.get('total_traces', 0)} traces, "
              f"{mem_stats.get('high_confidence_count', 0)} high-confidence, "
              f"{mem_stats.get('facts_count', 0)} facts")

        # Show available agents
        agents = self.component_registry.list_agents()
        print(f"🤖 Agents: {len(agents)} registered")

        print()

        # Start kernel components
        await self.scheduler.start()
        await self.watchdog.start()

        self._running = True
        print("✅ LLM OS Ready (Learner | Follower | Orchestrator modes available)")
        print()

    async def execute(
        self,
        goal: str,
        mode: str = "AUTO",
        project_name: Optional[str] = None,
        max_cost_usd: float = 5.0
    ):
        """
        Execute a goal using Learner/Follower/Orchestrator pattern

        Args:
            goal: Natural language goal to execute
            mode: "AUTO" (auto-detect), "LEARNER", "FOLLOWER", or "ORCHESTRATOR"
            project_name: Optional project name (creates if doesn't exist)
            max_cost_usd: Maximum cost budget for execution

        Returns:
            Result dictionary
        """
        if not self._running:
            raise RuntimeError("OS not booted. Call boot() first.")

        print(f"🎯 Goal: {goal}")

        # Get/create project if specified
        project = None
        if project_name:
            project = self.project_manager.get_project(project_name)
            if not project:
                project = self.project_manager.create_project(project_name)
                print(f"📂 Created project: {project.name}")
        elif self.current_project:
            project = self.current_project

        # Get memory insights
        recommendations = await self.memory_query.get_recommendations(goal)
        if recommendations:
            print("\n💡 Memory Recommendations:")
            for rec in recommendations[:3]:  # Show top 3
                print(f"   - {rec}")

        # Get cross-project insights
        cross_project_recs = await self.cross_project_learning.get_cross_project_recommendations(
            current_project=project,
            goal=goal
        )
        if cross_project_recs:
            print("\n🌐 Cross-Project Insights:")
            for rec in cross_project_recs[:3]:  # Show top 3
                print(f"   - {rec}")

        print()

        # Dispatch to appropriate mode
        result = await self.dispatcher.dispatch(
            goal=goal,
            mode=mode,
            project=project,
            max_cost_usd=max_cost_usd
        )

        return result

    def create_project(self, name: str, description: str = "") -> Project:
        """
        Create a new project

        Args:
            name: Project name
            description: Project description

        Returns:
            Project instance
        """
        project = self.project_manager.create_project(name, description)
        self.current_project = project
        return project

    def set_project(self, name: str):
        """
        Set current project

        Args:
            name: Project name
        """
        project = self.project_manager.get_project(name)
        if project:
            self.current_project = project
        else:
            raise ValueError(f"Project {name} not found")

    def list_projects(self):
        """List all projects"""
        return self.project_manager.list_projects()

    def create_agent(self, **kwargs):
        """
        Create a new agent

        Args:
            **kwargs: Agent specification parameters

        Returns:
            AgentSpec instance
        """
        agent = self.agent_factory.create_agent(**kwargs)
        self.component_registry.register_agent(agent)
        return agent

    def list_agents(self, **kwargs):
        """
        List registered agents

        Args:
            **kwargs: Filter parameters

        Returns:
            List of AgentSpec instances
        """
        return self.component_registry.list_agents(**kwargs)

    async def get_cross_project_insights(self, **kwargs):
        """
        Get cross-project insights

        Args:
            **kwargs: Filter parameters for insights

        Returns:
            List of CrossProjectInsight instances
        """
        return await self.cross_project_learning.analyze_common_patterns(**kwargs)

    async def get_reusable_agents(self, **kwargs):
        """
        Get reusable agent patterns from cross-project analysis

        Args:
            **kwargs: Filter parameters

        Returns:
            List of ReusableAgent instances
        """
        return await self.cross_project_learning.identify_reusable_agents(**kwargs)

    async def get_project_summary(self, project_name: str):
        """
        Get learning summary for a project

        Args:
            project_name: Project name

        Returns:
            Dictionary with project insights
        """
        project = self.project_manager.get_project(project_name)
        if not project:
            raise ValueError(f"Project {project_name} not found")

        return await self.cross_project_learning.get_project_learning_summary(project)

    async def shutdown(self):
        """Shutdown the operating system"""
        print()
        print("🛑 Shutting down LLM OS...")

        self._running = False

        # Stop kernel components
        await self.scheduler.stop()
        await self.watchdog.stop()

        # Save state
        print(f"💾 Final Balance: ${self.token_economy.balance:.2f}")
        print(f"📊 Total Spent: ${sum(log['cost'] for log in self.token_economy.spend_log):.2f}")

        print("✅ Shutdown complete")


async def main():
    """Main entry point"""
    # Create and boot the OS
    os = LLMOS(budget_usd=10.0)
    await os.boot()

    try:
        # Interactive mode
        if len(sys.argv) > 1 and sys.argv[1] == "interactive":
            print("📝 Interactive Mode (type 'exit' to quit)")
            print()

            while True:
                try:
                    goal = input("llmos> ")
                    if goal.lower() in ["exit", "quit"]:
                        break
                    if goal.strip():
                        await os.execute(goal)
                except KeyboardInterrupt:
                    break

        # Single command mode
        elif len(sys.argv) > 1:
            goal = " ".join(sys.argv[1:])
            await os.execute(goal)

        else:
            print("Usage:")
            print("  python boot.py interactive        # Interactive mode")
            print("  python boot.py <goal>            # Execute single goal")

    finally:
        await os.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
