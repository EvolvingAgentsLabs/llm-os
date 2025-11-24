"""
Qiskit Studio Specialized Agents

This module contains agent definitions for the Qiskit Studio backend,
specialized for quantum computing tasks.
"""

from pathlib import Path
import sys

# Add llmos to path - support both standalone and in-tree execution
LLMOS_ROOT = Path(__file__).parents[3]  # Go up to llm-os root
if (LLMOS_ROOT / "llmos").exists():
    sys.path.insert(0, str(LLMOS_ROOT))  # Add llm-os root to path

# Import the agent specs
from .quantum_architect import QUANTUM_ARCHITECT
from .quantum_tutor import QUANTUM_TUTOR

# Export all agents
__all__ = ["QUANTUM_ARCHITECT", "QUANTUM_TUTOR"]
