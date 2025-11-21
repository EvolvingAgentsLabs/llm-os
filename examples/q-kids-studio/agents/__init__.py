"""
Q-Kids Studio Agents

Educational agents for teaching quantum computing to children ages 8-12.
"""

from pathlib import Path
import sys

# Add llmos to path
sys.path.insert(0, str(Path(__file__).parents[3] / "llmos"))

from kernel.agent_factory import AgentSpec

# Import the agent specs
from .professor_q import PROFESSOR_Q
from .game_master import GAME_MASTER

# Export all agents
__all__ = ["PROFESSOR_Q", "GAME_MASTER"]
