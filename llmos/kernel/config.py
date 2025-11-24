"""
Configuration Management for LLMOS

Centralized configuration using dataclasses with type safety.
Supports presets for different environments and easy serialization.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
import os


@dataclass
class KernelConfig:
    """Configuration for kernel components"""
    budget_usd: float = 10.0
    enable_scheduling: bool = True
    enable_watchdog: bool = True
    watchdog_timeout_secs: float = 300.0

    def __post_init__(self):
        """Validate configuration"""
        if self.budget_usd < 0:
            raise ValueError("budget_usd must be non-negative")
        if self.watchdog_timeout_secs <= 0:
            raise ValueError("watchdog_timeout_secs must be positive")


@dataclass
class MemoryConfig:
    """Configuration for memory components"""
    enable_llm_matching: bool = True
    trace_confidence_threshold: float = 0.9
    mixed_mode_threshold: float = 0.75
    follower_mode_threshold: float = 0.92
    enable_cross_project_learning: bool = True
    cache_size: int = 100

    def __post_init__(self):
        """Validate configuration"""
        if not 0.0 <= self.trace_confidence_threshold <= 1.0:
            raise ValueError("trace_confidence_threshold must be between 0 and 1")
        if not 0.0 <= self.mixed_mode_threshold <= 1.0:
            raise ValueError("mixed_mode_threshold must be between 0 and 1")
        if not 0.0 <= self.follower_mode_threshold <= 1.0:
            raise ValueError("follower_mode_threshold must be between 0 and 1")


@dataclass
class SDKConfig:
    """Configuration for Claude Agent SDK"""
    model: str = "claude-sonnet-4-5-20250929"
    permission_mode: str = "acceptEdits"
    max_turns: int = 10
    timeout_seconds: float = 300.0
    enable_streaming: bool = False
    enable_hooks: bool = True

    def __post_init__(self):
        """Validate configuration"""
        if self.max_turns <= 0:
            raise ValueError("max_turns must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


@dataclass
class DispatcherConfig:
    """Configuration for dispatcher mode selection"""
    complexity_threshold: int = 2
    auto_crystallization: bool = False
    crystallization_min_usage: int = 5
    crystallization_min_success: float = 0.95

    def __post_init__(self):
        """Validate configuration"""
        if self.complexity_threshold < 0:
            raise ValueError("complexity_threshold must be non-negative")
        if not 0.0 <= self.crystallization_min_success <= 1.0:
            raise ValueError("crystallization_min_success must be between 0 and 1")


@dataclass
class LLMOSConfig:
    """
    Complete LLMOS configuration

    Provides type-safe configuration with validation and presets.

    Example:
        # Use development preset
        config = LLMOSConfig.development()
        os = LLMOS(config=config)

        # Custom configuration
        config = LLMOSConfig(
            workspace=Path("/custom/workspace"),
            kernel=KernelConfig(budget_usd=5.0)
        )
        os = LLMOS(config=config)
    """
    workspace: Path = field(default_factory=lambda: Path("./workspace"))
    kernel: KernelConfig = field(default_factory=KernelConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    sdk: SDKConfig = field(default_factory=SDKConfig)
    dispatcher: DispatcherConfig = field(default_factory=DispatcherConfig)
    project_name: Optional[str] = None

    def __post_init__(self):
        """Ensure workspace is a Path"""
        if not isinstance(self.workspace, Path):
            self.workspace = Path(self.workspace)

    @classmethod
    def from_env(cls) -> 'LLMOSConfig':
        """
        Load configuration from environment variables

        Supported env vars:
        - LLMOS_WORKSPACE: Workspace directory
        - LLMOS_BUDGET: Budget in USD
        - LLMOS_MODEL: Claude model name
        - LLMOS_ENABLE_LLM_MATCHING: Enable LLM-based trace matching
        """
        workspace = os.getenv('LLMOS_WORKSPACE', './workspace')
        budget = float(os.getenv('LLMOS_BUDGET', '10.0'))
        model = os.getenv('LLMOS_MODEL', 'claude-sonnet-4-5-20250929')
        enable_llm = os.getenv('LLMOS_ENABLE_LLM_MATCHING', 'true').lower() == 'true'

        return cls(
            workspace=Path(workspace),
            kernel=KernelConfig(budget_usd=budget),
            sdk=SDKConfig(model=model),
            memory=MemoryConfig(enable_llm_matching=enable_llm)
        )

    @classmethod
    def development(cls) -> 'LLMOSConfig':
        """
        Development configuration preset

        Features:
        - Low budget ($1.00) to prevent expensive mistakes
        - LLM matching disabled for faster iteration
        - Streaming enabled for better UX during development
        """
        return cls(
            workspace=Path("./workspace"),
            kernel=KernelConfig(
                budget_usd=1.0,
                enable_watchdog=False  # Less noise during dev
            ),
            memory=MemoryConfig(
                enable_llm_matching=False,  # Faster
                trace_confidence_threshold=0.8  # More lenient
            ),
            sdk=SDKConfig(
                enable_streaming=True,  # Better dev UX
                timeout_seconds=600.0  # Longer timeout for debugging
            ),
            dispatcher=DispatcherConfig(
                auto_crystallization=False  # Manual control in dev
            )
        )

    @classmethod
    def production(cls) -> 'LLMOSConfig':
        """
        Production configuration preset

        Features:
        - Higher budget ($100.00) for production workloads
        - All features enabled (LLM matching, hooks, etc.)
        - Strict confidence thresholds
        - Auto-crystallization enabled
        """
        return cls(
            workspace=Path("./workspace"),
            kernel=KernelConfig(
                budget_usd=100.0,
                enable_scheduling=True,
                enable_watchdog=True
            ),
            memory=MemoryConfig(
                enable_llm_matching=True,
                trace_confidence_threshold=0.9,
                enable_cross_project_learning=True
            ),
            sdk=SDKConfig(
                enable_hooks=True,
                enable_streaming=False  # More stable in production
            ),
            dispatcher=DispatcherConfig(
                auto_crystallization=True,  # Learn and optimize automatically
                complexity_threshold=2
            )
        )

    @classmethod
    def testing(cls) -> 'LLMOSConfig':
        """
        Testing configuration preset

        Features:
        - Minimal budget ($0.10) for tests
        - All LLM features disabled for fast, deterministic tests
        - Short timeouts
        """
        return cls(
            workspace=Path("./test_workspace"),
            kernel=KernelConfig(
                budget_usd=0.1,
                enable_scheduling=False,
                enable_watchdog=False
            ),
            memory=MemoryConfig(
                enable_llm_matching=False,  # Deterministic tests
                trace_confidence_threshold=1.0,  # Exact matches only
                enable_cross_project_learning=False
            ),
            sdk=SDKConfig(
                timeout_seconds=30.0,  # Fast failures in tests
                enable_streaming=False,
                enable_hooks=False
            ),
            dispatcher=DispatcherConfig(
                auto_crystallization=False
            )
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMOSConfig':
        """Load configuration from dictionary (e.g., from YAML/JSON)"""
        workspace = Path(data.get('workspace', './workspace'))

        kernel_data = data.get('kernel', {})
        memory_data = data.get('memory', {})
        sdk_data = data.get('sdk', {})
        dispatcher_data = data.get('dispatcher', {})

        return cls(
            workspace=workspace,
            kernel=KernelConfig(**kernel_data),
            memory=MemoryConfig(**memory_data),
            sdk=SDKConfig(**sdk_data),
            dispatcher=DispatcherConfig(**dispatcher_data),
            project_name=data.get('project_name')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration to dictionary (for YAML/JSON serialization)"""
        return {
            'workspace': str(self.workspace),
            'kernel': {
                'budget_usd': self.kernel.budget_usd,
                'enable_scheduling': self.kernel.enable_scheduling,
                'enable_watchdog': self.kernel.enable_watchdog,
                'watchdog_timeout_secs': self.kernel.watchdog_timeout_secs
            },
            'memory': {
                'enable_llm_matching': self.memory.enable_llm_matching,
                'trace_confidence_threshold': self.memory.trace_confidence_threshold,
                'mixed_mode_threshold': self.memory.mixed_mode_threshold,
                'follower_mode_threshold': self.memory.follower_mode_threshold,
                'enable_cross_project_learning': self.memory.enable_cross_project_learning,
                'cache_size': self.memory.cache_size
            },
            'sdk': {
                'model': self.sdk.model,
                'permission_mode': self.sdk.permission_mode,
                'max_turns': self.sdk.max_turns,
                'timeout_seconds': self.sdk.timeout_seconds,
                'enable_streaming': self.sdk.enable_streaming,
                'enable_hooks': self.sdk.enable_hooks
            },
            'dispatcher': {
                'complexity_threshold': self.dispatcher.complexity_threshold,
                'auto_crystallization': self.dispatcher.auto_crystallization,
                'crystallization_min_usage': self.dispatcher.crystallization_min_usage,
                'crystallization_min_success': self.dispatcher.crystallization_min_success
            },
            'project_name': self.project_name
        }


class ConfigBuilder:
    """
    Fluent builder for LLMOS configuration

    Example:
        config = (ConfigBuilder()
            .with_workspace(Path("/custom"))
            .with_budget(5.0)
            .with_llm_matching(True)
            .with_model("claude-opus-4")
            .build())
    """

    def __init__(self):
        self._config = LLMOSConfig()

    def with_workspace(self, workspace: Path) -> 'ConfigBuilder':
        """Set workspace directory"""
        self._config.workspace = workspace
        return self

    def with_budget(self, budget_usd: float) -> 'ConfigBuilder':
        """Set token budget"""
        self._config.kernel.budget_usd = budget_usd
        return self

    def with_llm_matching(self, enabled: bool) -> 'ConfigBuilder':
        """Enable/disable LLM-based trace matching"""
        self._config.memory.enable_llm_matching = enabled
        return self

    def with_model(self, model: str) -> 'ConfigBuilder':
        """Set Claude model"""
        self._config.sdk.model = model
        return self

    def with_streaming(self, enabled: bool) -> 'ConfigBuilder':
        """Enable/disable streaming"""
        self._config.sdk.enable_streaming = enabled
        return self

    def with_project(self, project_name: str) -> 'ConfigBuilder':
        """Set project name"""
        self._config.project_name = project_name
        return self

    def with_auto_crystallization(self, enabled: bool) -> 'ConfigBuilder':
        """Enable/disable automatic crystallization"""
        self._config.dispatcher.auto_crystallization = enabled
        return self

    def build(self) -> LLMOSConfig:
        """Build the configuration"""
        return self._config
