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
from memory.store import MemoryStore
from memory.traces import TraceManager
from interfaces.dispatcher import Dispatcher
from kernel.token_economy import TokenEconomy


class LLMOS:
    """
    The LLM Operating System

    Separates Cognitive Compute (LLM) from Somatic Compute (Python)
    Managed by a strict Token Economy.
    """

    def __init__(self, budget_usd: float = 10.0, workspace: Optional[Path] = None):
        """
        Initialize the LLM OS

        Args:
            budget_usd: Token budget in USD
            workspace: Workspace directory (defaults to ./workspace)
        """
        self.workspace = workspace or Path("./workspace")
        self.workspace.mkdir(exist_ok=True)

        # Initialize components
        self.event_bus = EventBus()
        self.token_economy = TokenEconomy(budget_usd)
        self.scheduler = Scheduler(self.event_bus)
        self.watchdog = Watchdog(self.event_bus)
        self.memory_store = MemoryStore(self.workspace / "memory")
        self.trace_manager = TraceManager(self.workspace / "memory" / "traces")
        self.dispatcher = Dispatcher(
            event_bus=self.event_bus,
            token_economy=self.token_economy,
            memory_store=self.memory_store,
            trace_manager=self.trace_manager
        )

        self._running = False

    async def boot(self):
        """Boot the operating system"""
        print("🚀 Booting LLM OS...")
        print(f"💰 Token Budget: ${self.token_economy.balance:.2f}")
        print(f"📁 Workspace: {self.workspace.absolute()}")
        print()

        # Start kernel components
        await self.scheduler.start()
        await self.watchdog.start()

        self._running = True
        print("✅ LLM OS Ready")
        print()

    async def execute(self, goal: str):
        """
        Execute a goal using the Learner-Follower pattern

        Args:
            goal: Natural language goal to execute
        """
        if not self._running:
            raise RuntimeError("OS not booted. Call boot() first.")

        print(f"🎯 Goal: {goal}")
        print()

        # Dispatch to Learner or Follower mode
        result = await self.dispatcher.dispatch(goal)

        return result

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
