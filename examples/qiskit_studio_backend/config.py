"""
Configuration module for Qiskit Studio Backend

Loads environment variables and provides configuration settings.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


class Config:
    """Configuration settings for Qiskit Studio Backend"""

    # Anthropic API
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # IBM Quantum (optional)
    IBM_QUANTUM_TOKEN: Optional[str] = os.getenv("IBM_QUANTUM_TOKEN")
    IBM_QUANTUM_CHANNEL: str = os.getenv("IBM_QUANTUM_CHANNEL", "ibm_quantum")
    IBM_QUANTUM_INSTANCE: Optional[str] = os.getenv("IBM_QUANTUM_INSTANCE")
    IBM_QUANTUM_REGION: Optional[str] = os.getenv("IBM_QUANTUM_REGION")

    # Server settings
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))

    # LLM OS settings
    LLMOS_BUDGET_USD: float = float(os.getenv("LLMOS_BUDGET_USD", "50.0"))
    LLMOS_PROJECT_NAME: str = os.getenv("LLMOS_PROJECT_NAME", "qiskit_studio_session")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required. Please set it in .env file")
        return True


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️  Configuration Warning: {e}")
    print("   Create a .env file from .env.template and add your API key")
