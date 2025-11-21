"""
Qiskit Studio Specialized Agents

This module contains agent definitions for the Qiskit Studio backend,
specialized for quantum computing tasks.
"""

from pathlib import Path
import sys

# Add llmos to path
sys.path.insert(0, str(Path(__file__).parents[3] / "llmos"))

from kernel.agent_factory import AgentSpec

# Import the agent specs
from .quantum_architect import QUANTUM_ARCHITECT
from .quantum_tutor import QUANTUM_TUTOR

# Export all agents
__all__ = ["QUANTUM_ARCHITECT", "QUANTUM_TUTOR"]
