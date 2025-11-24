# LLMOS Architecture Analysis
## Comprehensive Design Patterns and Dependency Analysis

**Analysis Date**: 2025-11-23
**Version Analyzed**: Phase 2.5
**Analyst**: ArchitectureAnalystAgent

---

## 1. Executive Summary

The **llmos** (LLM Operating System) is an ambitious and well-architected system that treats the Large Language Model as a CPU. The system successfully implements a three-mode execution pattern (Learner/Follower/Orchestrator) with sophisticated memory management and multi-agent orchestration capabilities.

**Key Findings**:
- **Solid Foundation**: The core architecture demonstrates good separation of concerns between cognitive (LLM) and somatic (Python) compute
- **Pattern Opportunities**: Several areas would benefit from formal design pattern application, particularly around dependency injection, configuration management, and mode selection
- **Coupling Hotspots**: Significant coupling exists between Dispatcher, SDK Client, and memory components
- **Extensibility**: The plugin system and agent factory show strong extensibility, but could be enhanced with abstract factories and registry patterns

**Overall Assessment**: The architecture is production-ready but would benefit from targeted refactoring to reduce coupling, improve testability, and formalize pattern usage.

---

## 2. Architecture Map

### 2.1 Component Hierarchy

```
llmos/
├── boot.py (LLMOS main class - Application Entry Point)
│
├── kernel/ (Somatic Compute Layer)
│   ├── bus.py (EventBus - Observer Pattern)
│   ├── scheduler.py (Scheduler - Command Pattern potential)
│   ├── watchdog.py (Watchdog - Observer Pattern)
│   ├── token_economy.py (TokenEconomy - State Pattern potential)
│   ├── agent_factory.py (AgentFactory - Factory Method Pattern ✓)
│   ├── component_registry.py (ComponentRegistry - Registry Pattern ✓)
│   ├── project_manager.py (ProjectManager - Repository Pattern potential)
│   ├── state_manager.py (StateManager - State Pattern ✓)
│   └── hooks.py (Hook System - Observer/Strategy Pattern)
│
├── interfaces/ (Cognitive Compute Layer)
│   ├── dispatcher.py (Dispatcher - Strategy/State Pattern opportunity)
│   ├── sdk_client.py (LLMOSSDKClient - Adapter Pattern ✓)
│   ├── orchestrator.py (SystemAgent - Mediator Pattern ✓)
│   └── cortex.py (Cortex - Fallback implementation)
│
├── memory/ (Storage Layer)
│   ├── traces_sdk.py (TraceManager - Repository Pattern ✓)
│   ├── store_sdk.py (MemoryStore - Repository Pattern ✓)
│   ├── query_sdk.py (MemoryQueryInterface - Facade Pattern ✓)
│   ├── cross_project_sdk.py (CrossProjectLearning - Strategy Pattern potential)
│   ├── sdk_memory.py (SDKMemoryTool - Tool Wrapper)
│   └── trace_analyzer.py (TraceAnalyzer - Strategy Pattern)
│
└── plugins/ (Extension Layer)
    ├── __init__.py (PluginLoader - Registry Pattern ✓)
    ├── example_tools.py
    └── generated/ (Dynamically created tools)
```

### 2.2 Dependency Graph

```
                     ┌─────────────┐
                     │   LLMOS     │
                     │  (boot.py)  │
                     └──────┬──────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                  ▼
    ┌──────────┐    ┌──────────────┐   ┌────────────┐
    │  Kernel  │    │  Interfaces  │   │   Memory   │
    │Components│    │(Dispatcher)  │   │ Components │
    └────┬─────┘    └──────┬───────┘   └─────┬──────┘
         │                 │                   │
         │                 │                   │
         ▼                 ▼                   ▼
    EventBus          SDK Client        TraceManager
    Scheduler         Orchestrator      MemoryStore
    TokenEconomy      Cortex           QueryInterface
    AgentFactory                        CrossProject
    ComponentRegistry
    ProjectManager

    Key Dependencies:
    - Dispatcher → EventBus, TokenEconomy, MemoryStore, TraceManager, ProjectManager
    - Orchestrator → EventBus, ProjectManager, AgentFactory, ComponentRegistry, TokenEconomy, TraceManager
    - SDK Client → TraceManager, TokenEconomy, MemoryQueryInterface
    - LLMOS → ALL kernel, interface, and memory components
```

### 2.3 Data Flow

**Three Execution Modes**:

```
1. FOLLOWER Mode (Zero-Cost Path)
   User Goal → Dispatcher → TraceManager (hash lookup)
            → Cortex (pure Python replay) → Result

2. LEARNER Mode (LLM Path with Hooks)
   User Goal → Dispatcher → MemoryQuery (context injection)
            → SDK Client (with hooks)
            → LLM Execution (tools + hooks)
            → TraceManager (save pattern) → Result

3. ORCHESTRATOR Mode (Multi-Agent Path)
   User Goal → Dispatcher → Orchestrator
            → Planning (LLM decomposition)
            → Agent Registration (AgentDefinition)
            → Multi-Agent Execution (shared SDK client)
            → State Management → Result
```

---

## 3. Current Patterns (Well-Implemented)

### 3.1 Factory Method Pattern ✅

**Location**: `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/kernel/agent_factory.py`

**Implementation**:
```python
class AgentFactory:
    """Creates and manages dynamic agents"""

    def create_agent(
        self,
        name: str,
        agent_type: str,
        category: str,
        description: str,
        system_prompt: str,
        tools: List[str],
        **kwargs
    ) -> AgentSpec:
        """Factory method for creating agents"""
        spec = AgentSpec(...)
        self.save_agent_definition(spec)
        self.agents[spec.name] = spec
        return spec
```

**Strengths**:
- Clean separation of agent creation logic
- Encapsulates agent persistence (YAML frontmatter markdown)
- Supports agent evolution and versioning

**Opportunities**:
- Could benefit from **Abstract Factory** for creating different agent families (research agents, code agents, etc.)
- Consider adding **Builder Pattern** for complex agent configuration

### 3.2 Registry Pattern ✅

**Location**: `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/kernel/component_registry.py`

**Implementation**:
```python
class ComponentRegistry:
    """Central registry for all system and project components"""

    def __init__(self):
        self.agents: Dict[str, AgentSpec] = {}
        self.tools: Dict[str, ToolSpec] = {}

    def register_agent(self, agent: AgentSpec):
        """Register an agent in the registry"""
        self.agents[agent.name] = agent

    def get_agent(self, name: str) -> Optional[AgentSpec]:
        """Get agent by name"""
        return self.agents.get(name)
```

**Strengths**:
- Central discovery mechanism
- Clean API for registration and retrieval
- Supports filtering and search

**Opportunities**:
- Add **Lazy Loading** for agents (only load when needed)
- Implement **Cache Invalidation** strategy
- Consider **Service Locator** pattern for dependency resolution

### 3.3 Observer Pattern ✅

**Location**: `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/kernel/bus.py`

**Implementation**:
```python
class EventBus:
    """Event Bus for inter-component communication"""

    def __init__(self):
        self._channels: Dict[EventType, tuple] = {}
        self._subscribers: Dict[EventType, List[Callable]] = {}

    async def publish(self, event: Event):
        """Publish an event to all subscribers"""
        if event.type not in self._channels:
            self.create_channel(event.type)
        send_stream, _ = self._channels[event.type]
        await send_stream.send(event)

    async def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to an event type"""
        self._subscribers[event_type].append(callback)
```

**Strengths**:
- Decouples event producers from consumers
- Uses `anyio` for async pub/sub
- Clean event types enumeration

**Opportunities**:
- Add **Event Filtering** at subscription level
- Implement **Priority Queues** for critical events
- Consider **Event Sourcing** for debugging

### 3.4 Repository Pattern ✅

**Location**: `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/memory/traces_sdk.py`

**Implementation**:
```python
class TraceManager:
    """Manages execution traces using SDK memory"""

    def save_trace(self, trace: ExecutionTrace) -> bool:
        """Save execution trace"""
        filename = self._get_trace_filename(...)
        content = trace.to_markdown()
        self.memory_tool.create(file_path, content)
        return True

    def find_trace(self, goal: str, min_confidence: float = 0.9) -> Optional[ExecutionTrace]:
        """Find trace for goal using hash-based exact matching"""
        signature = self._compute_signature(goal)
        traces = self.list_traces()
        for trace in traces:
            if trace.goal_signature == signature:
                return trace
        return None
```

**Strengths**:
- Abstracts storage mechanism (markdown files)
- Clean CRUD operations
- Supports semantic and hash-based search

**Opportunities**:
- Add **Unit of Work** pattern for transactional trace operations
- Implement **Specification Pattern** for complex queries
- Consider **CQRS** for separating read/write models

### 3.5 Adapter Pattern ✅

**Location**: `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/interfaces/sdk_client.py`

**Implementation**:
```python
class LLMOSSDKClient:
    """Adapter for Claude Agent SDK with llmos-specific enhancements"""

    def __init__(
        self,
        workspace: Path,
        trace_manager: TraceManager,
        token_economy: TokenEconomy,
        memory_query: MemoryQueryInterface
    ):
        # Adapts SDK to llmos needs
        self.workspace = workspace
        self.trace_manager = trace_manager
        self.token_economy = token_economy
        self.memory_query = memory_query
```

**Strengths**:
- Clean integration with Claude Agent SDK
- Adds llmos-specific functionality (hooks, tracing)
- Handles SDK availability gracefully

**Opportunities**:
- Add **Decorator Pattern** for enhancing SDK capabilities
- Implement **Proxy Pattern** for lazy SDK initialization

### 3.6 State Pattern ✅

**Location**: `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/kernel/state_manager.py`

**Implementation**:
```python
class StateManager:
    """Manages execution state machine"""

    def __init__(self, project_path: Path):
        self.plan: List[ExecutionStep] = []
        self.context: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}
        self.constraints: Dict[str, Any] = {}

    def update_step_status(
        self,
        step_number: int,
        status: str,  # pending, in_progress, completed, failed
        result: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Update step status"""
        for step in self.plan:
            if step.step_number == step_number:
                step.status = status
                # Update state files
```

**Strengths**:
- Clear state transitions
- Persistent state (markdown + JSON)
- Comprehensive logging

**Opportunities**:
- Formalize state transitions with **State Pattern** classes
- Add **Memento Pattern** for state rollback
- Implement **Command Pattern** for state mutations

### 3.7 Mediator Pattern ✅

**Location**: `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/interfaces/orchestrator.py`

**Implementation**:
```python
class SystemAgent:
    """SystemAgent Orchestrator - Master coordinator for multi-agent workflows"""

    def __init__(
        self,
        event_bus: EventBus,
        project_manager: ProjectManager,
        agent_factory: AgentFactory,
        component_registry: ComponentRegistry,
        token_economy: TokenEconomy,
        trace_manager: TraceManager,
        workspace: Path
    ):
        # Mediates between multiple components

    async def orchestrate(
        self,
        goal: str,
        project: Optional[Project] = None,
        max_cost_usd: float = 5.0
    ) -> OrchestrationResult:
        """Orchestrate multi-agent execution to achieve goal"""
        # Coordinates: memory, planning, agent selection, execution, state
```

**Strengths**:
- Centralizes multi-agent coordination
- Reduces coupling between agents
- Manages complex workflows

**Opportunities**:
- Extract coordination logic to separate **Mediator** classes
- Add **Chain of Responsibility** for step execution

---

## 4. Pattern Opportunities (Top 5 Improvements)

### 4.1 Strategy Pattern for Mode Selection (HIGH PRIORITY)

**Problem**: The Dispatcher currently uses complex conditional logic for mode selection:

```python
# dispatcher.py, lines 167-226
async def _determine_mode(self, goal: str) -> str:
    trace, confidence, recommended_mode = await self.trace_manager.find_trace_smart(goal)

    if trace and confidence >= 0.75:
        if trace.crystallized_into_tool:
            return "CRYSTALLIZED"
        if confidence >= 0.92:
            return "FOLLOWER"
        else:
            return "MIXED"

    # Complex complexity analysis
    complexity_indicators = [...]
    complexity_score = sum(1 for indicator in complexity_indicators if indicator in goal_lower)

    if complexity_score >= 2:
        return "ORCHESTRATOR"

    return "LEARNER"
```

**Solution**: Implement **Strategy Pattern** for mode determination:

```python
# Proposed: kernel/mode_strategies.py

from abc import ABC, abstractmethod
from typing import Optional, Tuple

class ModeSelectionStrategy(ABC):
    """Abstract strategy for mode selection"""

    @abstractmethod
    async def determine_mode(
        self,
        goal: str,
        trace_manager: TraceManager,
        complexity_analyzer: ComplexityAnalyzer
    ) -> Tuple[str, float, Optional[ExecutionTrace]]:
        """
        Returns: (mode, confidence, trace)
        """
        pass

class AutoModeStrategy(ModeSelectionStrategy):
    """Automatic mode selection (current logic)"""

    async def determine_mode(self, goal, trace_manager, complexity_analyzer):
        # Smart trace finding
        trace, confidence, _ = await trace_manager.find_trace_smart(goal)

        if trace and confidence >= 0.75:
            return self._select_from_trace(trace, confidence)

        # Complexity analysis
        complexity = await complexity_analyzer.analyze(goal)
        if complexity.score >= 2:
            return ("ORCHESTRATOR", 0.0, None)

        return ("LEARNER", 0.0, None)

    def _select_from_trace(self, trace, confidence):
        if trace.crystallized_into_tool:
            return ("CRYSTALLIZED", 1.0, trace)
        if confidence >= 0.92:
            return ("FOLLOWER", confidence, trace)
        return ("MIXED", confidence, trace)

class ForcedLearnerStrategy(ModeSelectionStrategy):
    """Always use Learner mode (for testing/development)"""

    async def determine_mode(self, goal, trace_manager, complexity_analyzer):
        return ("LEARNER", 1.0, None)

class CostOptimizedStrategy(ModeSelectionStrategy):
    """Prefer cheaper modes when possible"""

    async def determine_mode(self, goal, trace_manager, complexity_analyzer):
        # Always try Follower first, even with lower confidence
        trace, confidence, _ = await trace_manager.find_trace_smart(goal)

        if trace and confidence >= 0.5:  # Lower threshold
            if trace.crystallized_into_tool:
                return ("CRYSTALLIZED", confidence, trace)
            if confidence >= 0.75:  # Lower threshold
                return ("FOLLOWER", confidence, trace)
            return ("MIXED", confidence, trace)

        return ("LEARNER", 0.0, None)

# Modified Dispatcher
class Dispatcher:
    def __init__(self, ..., mode_strategy: ModeSelectionStrategy = None):
        self.mode_strategy = mode_strategy or AutoModeStrategy()
        self.complexity_analyzer = ComplexityAnalyzer()

    async def dispatch(self, goal, mode="AUTO", **kwargs):
        if mode == "AUTO":
            mode, confidence, trace = await self.mode_strategy.determine_mode(
                goal, self.trace_manager, self.complexity_analyzer
            )
        # ... route to appropriate mode
```

**Benefits**:
- **Testability**: Each strategy can be tested independently
- **Flexibility**: Easy to add new mode selection algorithms (e.g., cost-optimized, speed-optimized)
- **Configuration**: Different strategies for different contexts (dev, prod, testing)
- **Reduced Complexity**: 200+ line method becomes manageable strategy classes

**Impact**: HIGH - Improves maintainability and enables A/B testing of mode selection algorithms

---

### 4.2 Dependency Injection Container (HIGH PRIORITY)

**Problem**: The LLMOS class manually constructs ALL dependencies in `__init__`:

```python
# boot.py, lines 44-103
class LLMOS:
    def __init__(self, budget_usd: float = 10.0, workspace: Optional[Path] = None, project_name: Optional[str] = None):
        # Manual construction of 10+ dependencies
        self.event_bus = EventBus()
        self.token_economy = TokenEconomy(budget_usd)
        self.scheduler = Scheduler(self.event_bus)
        self.watchdog = Watchdog(self.event_bus)
        self.memory_store = MemoryStore(self.workspace)
        self.trace_manager = TraceManager(...)
        self.memory_query = MemoryQueryInterface(...)
        self.project_manager = ProjectManager(self.workspace)
        self.agent_factory = AgentFactory(self.workspace)
        self.component_registry = ComponentRegistry()
        self.cross_project_learning = CrossProjectLearning(...)
        self.dispatcher = Dispatcher(...)
```

**Solution**: Implement **Dependency Injection Container**:

```python
# Proposed: kernel/container.py

from typing import Dict, Any, Callable, Type
from dataclasses import dataclass

@dataclass
class ServiceDescriptor:
    """Describes how to construct a service"""
    service_type: Type
    factory: Callable
    singleton: bool = True
    dependencies: list = None

class Container:
    """Simple dependency injection container"""

    def __init__(self):
        self._descriptors: Dict[str, ServiceDescriptor] = {}
        self._singletons: Dict[str, Any] = {}

    def register(
        self,
        name: str,
        service_type: Type,
        factory: Callable,
        singleton: bool = True,
        dependencies: list = None
    ):
        """Register a service"""
        self._descriptors[name] = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            singleton=singleton,
            dependencies=dependencies or []
        )

    def resolve(self, name: str) -> Any:
        """Resolve a service by name"""
        if name not in self._descriptors:
            raise ValueError(f"Service {name} not registered")

        descriptor = self._descriptors[name]

        # Return singleton if already created
        if descriptor.singleton and name in self._singletons:
            return self._singletons[name]

        # Resolve dependencies first
        deps = {dep: self.resolve(dep) for dep in descriptor.dependencies}

        # Create instance
        instance = descriptor.factory(**deps)

        # Cache singleton
        if descriptor.singleton:
            self._singletons[name] = instance

        return instance

# Proposed: kernel/service_configuration.py

def configure_services(container: Container, config: Dict[str, Any]):
    """Configure all llmos services"""

    workspace = config.get('workspace', Path('./workspace'))
    budget_usd = config.get('budget_usd', 10.0)

    # Register kernel services
    container.register(
        'event_bus',
        EventBus,
        factory=lambda: EventBus(),
        singleton=True
    )

    container.register(
        'token_economy',
        TokenEconomy,
        factory=lambda: TokenEconomy(budget_usd),
        singleton=True
    )

    container.register(
        'scheduler',
        Scheduler,
        factory=lambda event_bus: Scheduler(event_bus),
        singleton=True,
        dependencies=['event_bus']
    )

    # Register memory services
    container.register(
        'trace_manager',
        TraceManager,
        factory=lambda: TraceManager(
            memories_dir=workspace / "memories",
            workspace=workspace,
            enable_llm_matching=True
        ),
        singleton=True
    )

    # Register interfaces
    container.register(
        'dispatcher',
        Dispatcher,
        factory=lambda event_bus, token_economy, memory_store, trace_manager, project_manager: Dispatcher(
            event_bus=event_bus,
            token_economy=token_economy,
            memory_store=memory_store,
            trace_manager=trace_manager,
            project_manager=project_manager,
            workspace=workspace
        ),
        singleton=True,
        dependencies=['event_bus', 'token_economy', 'memory_store', 'trace_manager', 'project_manager']
    )

# Modified LLMOS class
class LLMOS:
    def __init__(
        self,
        budget_usd: float = 10.0,
        workspace: Optional[Path] = None,
        project_name: Optional[str] = None,
        container: Optional[Container] = None
    ):
        self.workspace = workspace or Path("./workspace")

        # Use provided container or create default
        if container is None:
            container = Container()
            configure_services(container, {
                'workspace': self.workspace,
                'budget_usd': budget_usd
            })

        self.container = container

        # Resolve services from container
        self.event_bus = container.resolve('event_bus')
        self.token_economy = container.resolve('token_economy')
        self.scheduler = container.resolve('scheduler')
        self.trace_manager = container.resolve('trace_manager')
        self.dispatcher = container.resolve('dispatcher')
        # ... etc
```

**Benefits**:
- **Testability**: Easy to inject mocks for unit testing
- **Configuration**: Different configurations for dev/test/prod
- **Flexibility**: Easy to swap implementations (e.g., different TraceManager)
- **Lifecycle Management**: Centralized control over singleton vs transient services
- **Decoupling**: LLMOS doesn't need to know construction details

**Impact**: HIGH - Dramatically improves testability and configuration management

---

### 4.3 Configuration Management with Builder Pattern (MEDIUM PRIORITY)

**Problem**: Configuration is scattered across multiple initialization parameters:

```python
# Multiple places where configuration is hardcoded
self.trace_manager = TraceManager(
    memories_dir=self.workspace / "memories",
    workspace=self.workspace,
    enable_llm_matching=True  # Hardcoded
)

options = ClaudeAgentOptions(
    model="claude-sonnet-4-5-20250929",  # Hardcoded
    permission_mode="acceptEdits",  # Hardcoded
    ...
)
```

**Solution**: Implement **Builder Pattern** with configuration objects:

```python
# Proposed: kernel/config.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any

@dataclass
class KernelConfig:
    """Configuration for kernel components"""
    budget_usd: float = 10.0
    enable_scheduling: bool = True
    enable_watchdog: bool = True
    watchdog_timeout_secs: float = 300.0

@dataclass
class MemoryConfig:
    """Configuration for memory components"""
    enable_llm_matching: bool = True
    trace_confidence_threshold: float = 0.9
    enable_cross_project_learning: bool = True
    cache_size: int = 100

@dataclass
class SDKConfig:
    """Configuration for Claude Agent SDK"""
    model: str = "claude-sonnet-4-5-20250929"
    permission_mode: str = "acceptEdits"
    max_turns: int = 10
    enable_streaming: bool = False
    enable_hooks: bool = True

@dataclass
class LLMOSConfig:
    """Complete LLMOS configuration"""
    workspace: Path = field(default_factory=lambda: Path("./workspace"))
    kernel: KernelConfig = field(default_factory=KernelConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    sdk: SDKConfig = field(default_factory=SDKConfig)
    project_name: Optional[str] = None

    @classmethod
    def from_file(cls, path: Path) -> 'LLMOSConfig':
        """Load configuration from YAML/JSON file"""
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def development(cls) -> 'LLMOSConfig':
        """Development configuration preset"""
        return cls(
            kernel=KernelConfig(budget_usd=1.0),
            memory=MemoryConfig(enable_llm_matching=False),  # Faster
            sdk=SDKConfig(enable_streaming=True)  # Better UX
        )

    @classmethod
    def production(cls) -> 'LLMOSConfig':
        """Production configuration preset"""
        return cls(
            kernel=KernelConfig(budget_usd=100.0),
            memory=MemoryConfig(enable_llm_matching=True),
            sdk=SDKConfig(enable_hooks=True)
        )

class LLMOSConfigBuilder:
    """Builder for LLMOS configuration"""

    def __init__(self):
        self._config = LLMOSConfig()

    def with_workspace(self, workspace: Path) -> 'LLMOSConfigBuilder':
        self._config.workspace = workspace
        return self

    def with_budget(self, budget_usd: float) -> 'LLMOSConfigBuilder':
        self._config.kernel.budget_usd = budget_usd
        return self

    def with_llm_matching(self, enabled: bool) -> 'LLMOSConfigBuilder':
        self._config.memory.enable_llm_matching = enabled
        return self

    def with_model(self, model: str) -> 'LLMOSConfigBuilder':
        self._config.sdk.model = model
        return self

    def build(self) -> LLMOSConfig:
        return self._config

# Modified LLMOS class
class LLMOS:
    def __init__(self, config: LLMOSConfig = None):
        self.config = config or LLMOSConfig()
        self.workspace = self.config.workspace

        # Use configuration throughout
        self.token_economy = TokenEconomy(self.config.kernel.budget_usd)
        self.trace_manager = TraceManager(
            memories_dir=self.workspace / "memories",
            workspace=self.workspace,
            enable_llm_matching=self.config.memory.enable_llm_matching
        )

# Usage examples
# Development
config = LLMOSConfig.development()
os = LLMOS(config)

# Custom via builder
config = (LLMOSConfigBuilder()
    .with_workspace(Path("/custom/workspace"))
    .with_budget(5.0)
    .with_llm_matching(True)
    .with_model("claude-opus-4")
    .build())
os = LLMOS(config)

# From file
config = LLMOSConfig.from_file(Path("config/production.yaml"))
os = LLMOS(config)
```

**Benefits**:
- **Centralized Configuration**: All settings in one place
- **Type Safety**: Dataclasses provide validation
- **Presets**: Easy to define dev/test/prod configurations
- **Testability**: Easy to create test configurations
- **Documentation**: Configuration is self-documenting

**Impact**: MEDIUM - Improves configuration management and deployment flexibility

---

### 4.4 Abstract Factory for Agent Creation (MEDIUM PRIORITY)

**Problem**: AgentFactory creates all agent types with the same method:

```python
# agent_factory.py
class AgentFactory:
    def create_agent(self, name, agent_type, category, ...):
        """Creates any type of agent with same method"""
        spec = AgentSpec(...)
        return spec
```

**Solution**: Implement **Abstract Factory** for agent families:

```python
# Proposed: kernel/agent_factories.py

from abc import ABC, abstractmethod

class AbstractAgentFactory(ABC):
    """Abstract factory for creating agent families"""

    @abstractmethod
    def create_agent(self, **kwargs) -> AgentSpec:
        """Create an agent"""
        pass

    @abstractmethod
    def get_default_tools(self) -> List[str]:
        """Get default tools for this agent family"""
        pass

    @abstractmethod
    def get_category(self) -> str:
        """Get agent category"""
        pass

class ResearchAgentFactory(AbstractAgentFactory):
    """Factory for research agents"""

    def create_agent(self, name: str, description: str, **kwargs) -> AgentSpec:
        return AgentSpec(
            name=name,
            agent_type="specialized",
            category="research",
            description=description,
            tools=self.get_default_tools(),
            capabilities=[
                "Web search and analysis",
                "Document summarization",
                "Information extraction",
                "Cross-reference validation"
            ],
            constraints=[
                "Must cite sources",
                "Must validate information",
                "Must avoid speculation"
            ],
            system_prompt=self._get_research_prompt(),
            **kwargs
        )

    def get_default_tools(self) -> List[str]:
        return ["Read", "WebFetch", "Grep", "Write"]

    def get_category(self) -> str:
        return "research"

    def _get_research_prompt(self) -> str:
        return """You are a research specialist agent..."""

class CodeAgentFactory(AbstractAgentFactory):
    """Factory for code-related agents"""

    def create_agent(self, name: str, description: str, **kwargs) -> AgentSpec:
        return AgentSpec(
            name=name,
            agent_type="specialized",
            category="code_generation",
            description=description,
            tools=self.get_default_tools(),
            capabilities=[
                "Code generation",
                "Code review",
                "Testing",
                "Debugging"
            ],
            constraints=[
                "Must include type hints",
                "Must include docstrings",
                "Must follow PEP 8",
                "Must include error handling"
            ],
            system_prompt=self._get_code_prompt(),
            **kwargs
        )

    def get_default_tools(self) -> List[str]:
        return ["Read", "Write", "Bash", "Grep", "Glob"]

    def get_category(self) -> str:
        return "code_generation"

    def _get_code_prompt(self) -> str:
        return """You are a code generation specialist agent..."""

class DataAnalysisAgentFactory(AbstractAgentFactory):
    """Factory for data analysis agents"""

    def create_agent(self, name: str, description: str, **kwargs) -> AgentSpec:
        return AgentSpec(
            name=name,
            agent_type="specialized",
            category="data_analysis",
            description=description,
            tools=self.get_default_tools(),
            capabilities=[
                "Statistical analysis",
                "Data visualization",
                "Pattern recognition",
                "Report generation"
            ],
            constraints=[
                "Must validate data quality",
                "Must explain methodology",
                "Must include visualizations",
                "Must summarize findings"
            ],
            system_prompt=self._get_analysis_prompt(),
            **kwargs
        )

    def get_default_tools(self) -> List[str]:
        return ["Read", "Write", "Bash"]  # Could execute Python scripts

    def get_category(self) -> str:
        return "data_analysis"

    def _get_analysis_prompt(self) -> str:
        return """You are a data analysis specialist agent..."""

# Agent factory selector
class AgentFactoryRegistry:
    """Registry of agent factories by category"""

    def __init__(self):
        self._factories: Dict[str, AbstractAgentFactory] = {
            "research": ResearchAgentFactory(),
            "code_generation": CodeAgentFactory(),
            "data_analysis": DataAnalysisAgentFactory(),
        }

    def register_factory(self, category: str, factory: AbstractAgentFactory):
        """Register a new agent factory"""
        self._factories[category] = factory

    def get_factory(self, category: str) -> AbstractAgentFactory:
        """Get factory by category"""
        if category not in self._factories:
            raise ValueError(f"No factory registered for category: {category}")
        return self._factories[category]

    def create_agent(self, category: str, **kwargs) -> AgentSpec:
        """Create agent using appropriate factory"""
        factory = self.get_factory(category)
        return factory.create_agent(**kwargs)

# Modified AgentFactory (now coordinator)
class AgentFactory:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.agents_dir = self.workspace / "agents"
        self.agents: Dict[str, AgentSpec] = {}
        self.factory_registry = AgentFactoryRegistry()

    def create_agent(
        self,
        name: str,
        category: str,
        description: str,
        **kwargs
    ) -> AgentSpec:
        """Create agent using appropriate factory"""
        spec = self.factory_registry.create_agent(
            category=category,
            name=name,
            description=description,
            **kwargs
        )

        self.save_agent_definition(spec)
        self.agents[spec.name] = spec
        return spec

# Usage
factory = AgentFactory(workspace)

# Create research agent with research-specific defaults
research_agent = factory.create_agent(
    name="web-researcher",
    category="research",
    description="Researches web content"
)

# Create code agent with code-specific defaults
code_agent = factory.create_agent(
    name="python-generator",
    category="code_generation",
    description="Generates Python code"
)
```

**Benefits**:
- **Consistency**: Each agent family has consistent defaults
- **Extensibility**: Easy to add new agent families
- **Reduced Errors**: Less chance of misconfiguration
- **Domain Knowledge**: Factory encapsulates domain-specific knowledge

**Impact**: MEDIUM - Improves agent creation consistency and reduces configuration errors

---

### 4.5 Command Pattern for State Mutations (LOW-MEDIUM PRIORITY)

**Problem**: State mutations in StateManager are direct method calls without undo/redo capability:

```python
# state_manager.py
class StateManager:
    def update_step_status(self, step_number, status, result=None, error=None):
        """Direct mutation - no history"""
        for step in self.plan:
            if step.step_number == step_number:
                step.status = status
                step.result = result
                step.error = error
        self._save_plan()
```

**Solution**: Implement **Command Pattern** for state changes:

```python
# Proposed: kernel/state_commands.py

from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime

class Command(ABC):
    """Abstract command for state mutations"""

    def __init__(self):
        self.executed_at: Optional[datetime] = None

    @abstractmethod
    def execute(self, state: StateManager) -> Any:
        """Execute the command"""
        pass

    @abstractmethod
    def undo(self, state: StateManager) -> None:
        """Undo the command"""
        pass

    @abstractmethod
    def describe(self) -> str:
        """Describe what this command does"""
        pass

class UpdateStepStatusCommand(Command):
    """Command to update step status"""

    def __init__(
        self,
        step_number: int,
        new_status: str,
        result: Optional[str] = None,
        error: Optional[str] = None
    ):
        super().__init__()
        self.step_number = step_number
        self.new_status = new_status
        self.new_result = result
        self.new_error = error

        # Store previous state for undo
        self.previous_status: Optional[str] = None
        self.previous_result: Optional[str] = None
        self.previous_error: Optional[str] = None

    def execute(self, state: StateManager) -> None:
        """Execute status update"""
        self.executed_at = datetime.now()

        # Find step and save previous state
        for step in state.plan:
            if step.step_number == self.step_number:
                self.previous_status = step.status
                self.previous_result = step.result
                self.previous_error = step.error

                # Update to new state
                step.status = self.new_status
                step.result = self.new_result
                step.error = self.new_error
                break

        state._save_plan()
        state.log_event("STEP_UPDATED", {
            "step": self.step_number,
            "status": self.new_status
        })

    def undo(self, state: StateManager) -> None:
        """Undo status update"""
        for step in state.plan:
            if step.step_number == self.step_number:
                step.status = self.previous_status
                step.result = self.previous_result
                step.error = self.previous_error
                break

        state._save_plan()
        state.log_event("STEP_REVERTED", {
            "step": self.step_number,
            "status": self.previous_status
        })

    def describe(self) -> str:
        return f"Update step {self.step_number} to {self.new_status}"

class SetVariableCommand(Command):
    """Command to set a variable"""

    def __init__(self, key: str, value: Any):
        super().__init__()
        self.key = key
        self.new_value = value
        self.previous_value: Optional[Any] = None
        self.had_previous: bool = False

    def execute(self, state: StateManager) -> None:
        self.executed_at = datetime.now()

        # Save previous value
        if self.key in state.variables:
            self.previous_value = state.variables[self.key]
            self.had_previous = True

        # Set new value
        state.variables[self.key] = self.new_value
        state._save_variables()

    def undo(self, state: StateManager) -> None:
        if self.had_previous:
            state.variables[self.key] = self.previous_value
        else:
            del state.variables[self.key]
        state._save_variables()

    def describe(self) -> str:
        return f"Set variable {self.key} = {self.new_value}"

class CommandHistory:
    """Manages command history for undo/redo"""

    def __init__(self):
        self._executed: List[Command] = []
        self._undone: List[Command] = []

    def execute(self, command: Command, state: StateManager) -> None:
        """Execute a command and add to history"""
        command.execute(state)
        self._executed.append(command)
        self._undone.clear()  # Clear redo stack

    def undo(self, state: StateManager) -> bool:
        """Undo last command"""
        if not self._executed:
            return False

        command = self._executed.pop()
        command.undo(state)
        self._undone.append(command)
        return True

    def redo(self, state: StateManager) -> bool:
        """Redo last undone command"""
        if not self._undone:
            return False

        command = self._undone.pop()
        command.execute(state)
        self._executed.append(command)
        return True

    def get_history(self) -> List[str]:
        """Get command history descriptions"""
        return [cmd.describe() for cmd in self._executed]

# Modified StateManager
class StateManager:
    def __init__(self, project_path: Path):
        # ... existing initialization ...
        self.command_history = CommandHistory()

    def update_step_status(
        self,
        step_number: int,
        status: str,
        result: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Update step status using command pattern"""
        command = UpdateStepStatusCommand(step_number, status, result, error)
        self.command_history.execute(command, self)

    def set_variable(self, key: str, value: Any):
        """Set variable using command pattern"""
        command = SetVariableCommand(key, value)
        self.command_history.execute(command, self)

    def undo_last_action(self) -> bool:
        """Undo the last state change"""
        return self.command_history.undo(self)

    def redo_last_action(self) -> bool:
        """Redo the last undone action"""
        return self.command_history.redo(self)

    def get_action_history(self) -> List[str]:
        """Get history of all actions"""
        return self.command_history.get_history()

# Usage
state = StateManager(project_path)

# Execute commands
state.update_step_status(1, "in_progress")
state.update_step_status(1, "completed", result="Success!")
state.set_variable("attempt_count", 1)

# Undo last action
state.undo_last_action()  # attempt_count removed

# Redo
state.redo_last_action()  # attempt_count restored

# View history
history = state.get_action_history()
# ["Update step 1 to in_progress", "Update step 1 to completed", "Set variable attempt_count = 1"]
```

**Benefits**:
- **Undo/Redo**: Full undo/redo capability for debugging
- **Auditing**: Complete history of state changes
- **Debugging**: Can replay state mutations
- **Testing**: Commands can be tested independently
- **Macro Commands**: Can group multiple commands

**Impact**: LOW-MEDIUM - Improves debugging and enables advanced state management features

---

## 5. Dependency Analysis

### 5.1 Coupling Hotspots

#### High Coupling: Dispatcher ↔ Multiple Components

**Location**: `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/interfaces/dispatcher.py`

**Dependencies** (7 direct dependencies):
- `EventBus` (kernel)
- `TokenEconomy` (kernel)
- `MemoryStore` (memory)
- `TraceManager` (memory)
- `MemoryQueryInterface` (memory)
- `ProjectManager` (kernel)
- `LLMOSSDKClient` (interfaces)

**Issues**:
- Constructor takes 6+ parameters
- Hard to test (requires mocking 6+ dependencies)
- Changes to any dependency require Dispatcher changes
- Difficult to reconfigure

**Recommendation**: Apply **Dependency Injection Container** (see 4.2)

---

#### High Coupling: Orchestrator ↔ Multiple Components

**Location**: `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/interfaces/orchestrator.py`

**Dependencies** (7 direct dependencies):
- `EventBus`
- `ProjectManager`
- `AgentFactory`
- `ComponentRegistry`
- `TokenEconomy`
- `TraceManager`
- `StateManager`

**Issues**:
- Similar to Dispatcher - too many dependencies
- Complex initialization in `__init__` (lines 48-90)
- Difficult to unit test

**Recommendation**: Apply **Dependency Injection Container** + **Facade Pattern** to simplify interface

---

#### Medium Coupling: LLMOS ↔ All Subsystems

**Location**: `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/boot.py`

**Dependencies**: Creates instances of 12+ components

**Issues**:
- God object anti-pattern
- Exposes all internal components as public attributes
- No encapsulation

**Recommendation**:
- Use **Facade Pattern** to hide internal components
- Apply **Dependency Injection Container**
- Provide minimal public API

---

### 5.2 Configuration Coupling

**Problem**: Configuration values scattered throughout codebase:

```python
# Hardcoded in multiple places:
enable_llm_matching=True  # traces_sdk.py line 172
model="claude-sonnet-4-5-20250929"  # orchestrator.py line 58
permission_mode="acceptEdits"  # orchestrator.py line 186
min_confidence=0.9  # dispatcher.py line 290
complexity_score >= 2  # dispatcher.py line 220
```

**Recommendation**: Apply **Configuration Management** pattern (see 4.3)

---

### 5.3 Circular Dependencies

**Found**: None (Good!)

The architecture avoids circular dependencies through careful layering:
- Kernel layer (no dependencies on interfaces/memory)
- Memory layer (depends on kernel for events)
- Interfaces layer (depends on kernel and memory)

---

### 5.4 Hard-to-Test Components

**Highly Coupled Components** (difficult to unit test):

1. **Dispatcher** (7 dependencies)
   - Solution: Dependency injection, interface segregation

2. **Orchestrator** (7 dependencies)
   - Solution: Dependency injection, extract coordination logic

3. **LLMOS** (12+ dependencies)
   - Solution: Facade pattern, minimal public API

4. **LLMOSSDKClient** (4 dependencies + SDK)
   - Solution: Mock SDK with adapter pattern

**Components with External Dependencies**:

1. **TraceAnalyzer** (depends on Claude SDK)
   - Solution: Interface abstraction for LLM calls

2. **All SDK-dependent code**
   - Solution: Adapter pattern with mock implementations

---

### 5.5 Dependency Inversion Violations

**Problem**: Concrete dependencies instead of abstractions:

```python
# dispatcher.py - depends on concrete classes
from kernel.bus import EventBus  # Concrete
from kernel.token_economy import TokenEconomy  # Concrete
from memory.traces_sdk import TraceManager  # Concrete
```

**Recommendation**: Define interfaces/protocols:

```python
# Proposed: kernel/interfaces.py

from typing import Protocol

class IEventBus(Protocol):
    """Interface for event bus"""
    async def publish(self, event: Event) -> None: ...
    async def subscribe(self, event_type: EventType, callback: Callable) -> None: ...

class ITokenEconomy(Protocol):
    """Interface for token economy"""
    def check_budget(self, cost: float) -> bool: ...
    def deduct(self, cost: float, operation: str) -> None: ...

class ITraceManager(Protocol):
    """Interface for trace management"""
    def save_trace(self, trace: ExecutionTrace) -> bool: ...
    def find_trace(self, goal: str, min_confidence: float) -> Optional[ExecutionTrace]: ...

# Dispatcher now depends on interfaces
class Dispatcher:
    def __init__(
        self,
        event_bus: IEventBus,
        token_economy: ITokenEconomy,
        trace_manager: ITraceManager,
        ...
    ):
        # Now depends on abstractions, not concrete classes
```

**Benefits**:
- Easier to mock for testing
- Can swap implementations without changing Dispatcher
- Better adherence to SOLID principles

---

## 6. Recommendations (Prioritized by Impact)

### Priority 1: Critical (Implement First)

#### 6.1 Implement Dependency Injection Container
**Effort**: HIGH
**Impact**: HIGH
**Benefit**: Dramatically improves testability, configuration, and maintainability

**Action Items**:
1. Create `kernel/container.py` with basic DI container
2. Create `kernel/service_configuration.py` with service registrations
3. Refactor `LLMOS.__init__()` to use container
4. Add unit tests with mocked dependencies
5. Document DI usage patterns

**Files to Modify**:
- `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/boot.py`
- Create `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/kernel/container.py`
- Create `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/kernel/service_configuration.py`

---

#### 6.2 Apply Strategy Pattern to Mode Selection
**Effort**: MEDIUM
**Impact**: HIGH
**Benefit**: Enables A/B testing of mode selection algorithms, improves testability

**Action Items**:
1. Create `kernel/mode_strategies.py` with strategy interface
2. Implement `AutoModeStrategy`, `CostOptimizedStrategy`, `ForcedLearnerStrategy`
3. Refactor `Dispatcher._determine_mode()` to use strategy
4. Add configuration option for strategy selection
5. Add unit tests for each strategy

**Files to Modify**:
- `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/interfaces/dispatcher.py`
- Create `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/kernel/mode_strategies.py`

---

### Priority 2: Important (Implement Second)

#### 6.3 Implement Configuration Management
**Effort**: MEDIUM
**Impact**: MEDIUM-HIGH
**Benefit**: Centralized configuration, easier deployment, better testability

**Action Items**:
1. Create `kernel/config.py` with configuration dataclasses
2. Add YAML/JSON configuration file support
3. Create preset configurations (dev, test, prod)
4. Refactor all hardcoded configuration values
5. Add configuration validation

**Files to Modify**:
- Create `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/kernel/config.py`
- Modify all files with hardcoded configuration
- Add `config/` directory with preset files

---

#### 6.4 Apply Abstract Factory to Agent Creation
**Effort**: MEDIUM
**Impact**: MEDIUM
**Benefit**: Consistent agent creation, reduced errors, better domain knowledge encapsulation

**Action Items**:
1. Create `kernel/agent_factories.py` with abstract factory
2. Implement factories for research, code, data analysis agents
3. Create `AgentFactoryRegistry`
4. Refactor `AgentFactory` to use registry
5. Add unit tests for each factory

**Files to Modify**:
- `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/kernel/agent_factory.py`
- Create `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/kernel/agent_factories.py`

---

### Priority 3: Nice to Have (Implement Third)

#### 6.5 Add Command Pattern to State Management
**Effort**: MEDIUM
**Impact**: LOW-MEDIUM
**Benefit**: Undo/redo capability, better debugging, audit trail

**Action Items**:
1. Create `kernel/state_commands.py` with command interface
2. Implement commands for common state mutations
3. Add `CommandHistory` class
4. Refactor `StateManager` to use commands
5. Add undo/redo API methods

**Files to Modify**:
- `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/kernel/state_manager.py`
- Create `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/kernel/state_commands.py`

---

#### 6.6 Apply Facade Pattern to LLMOS
**Effort**: LOW-MEDIUM
**Impact**: MEDIUM
**Benefit**: Simpler public API, better encapsulation

**Action Items**:
1. Identify minimal public API surface
2. Create facade methods that hide internal components
3. Mark internal components as private (`_component`)
4. Update documentation with simplified API
5. Add deprecation warnings for direct component access

**Files to Modify**:
- `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/boot.py`

---

#### 6.7 Define Protocol Interfaces (Dependency Inversion)
**Effort**: LOW-MEDIUM
**Impact**: MEDIUM
**Benefit**: Better testability, clearer contracts, easier mocking

**Action Items**:
1. Create `kernel/protocols.py` with protocol interfaces
2. Define protocols for: EventBus, TokenEconomy, TraceManager, etc.
3. Update type hints to use protocols instead of concrete classes
4. Create mock implementations for testing
5. Update documentation with interface contracts

**Files to Modify**:
- Create `/Users/agustinazwiener/evolving-agents-labs/llm-os/llmos/kernel/protocols.py`
- Update type hints in all files

---

### Priority 4: Future Enhancements

#### 6.8 Implement Specification Pattern for Trace Queries
**Effort**: MEDIUM
**Impact**: LOW-MEDIUM
**Benefit**: More flexible trace querying, composable search criteria

**Action Items**:
1. Create specification interface
2. Implement common specifications (ByGoal, ByConfidence, ByUsage, etc.)
3. Add AND/OR/NOT combinators
4. Refactor TraceManager to use specifications
5. Add query builder API

---

#### 6.9 Add Chain of Responsibility for Step Execution
**Effort**: MEDIUM
**Impact**: LOW
**Benefit**: More flexible step execution, easier to add pre/post processors

**Action Items**:
1. Create step executor chain
2. Implement handlers for validation, execution, logging
3. Refactor orchestrator to use chain
4. Add handler registration API

---

#### 6.10 Implement Memento Pattern for State Snapshots
**Effort**: LOW
**Impact**: LOW
**Benefit**: Easy state rollback, better debugging

**Action Items**:
1. Create memento class for state snapshots
2. Add snapshot/restore methods to StateManager
3. Implement snapshot storage
4. Add API for state rollback

---

## 7. Testing Strategy

### 7.1 Current Testing Gaps

Based on the architecture analysis, these components need comprehensive unit tests:

1. **Dispatcher** - Mode selection logic, routing
2. **Orchestrator** - Multi-agent coordination
3. **TraceManager** - Trace finding and matching
4. **AgentFactory** - Agent creation and evolution
5. **StateManager** - State transitions

### 7.2 Recommended Test Structure

```
tests/
├── unit/
│   ├── kernel/
│   │   ├── test_bus.py
│   │   ├── test_scheduler.py
│   │   ├── test_agent_factory.py
│   │   ├── test_component_registry.py
│   │   ├── test_project_manager.py
│   │   ├── test_state_manager.py
│   │   └── test_token_economy.py
│   ├── interfaces/
│   │   ├── test_dispatcher.py
│   │   ├── test_orchestrator.py
│   │   └── test_sdk_client.py
│   └── memory/
│       ├── test_traces_sdk.py
│       ├── test_store_sdk.py
│       ├── test_query_sdk.py
│       └── test_cross_project_sdk.py
├── integration/
│   ├── test_learner_mode.py
│   ├── test_follower_mode.py
│   ├── test_orchestrator_mode.py
│   └── test_end_to_end.py
└── fixtures/
    ├── mock_traces.py
    ├── mock_agents.py
    └── test_configs.py
```

### 7.3 Testing with Dependency Injection

After implementing DI container:

```python
# tests/unit/interfaces/test_dispatcher.py

import pytest
from kernel.container import Container
from interfaces.dispatcher import Dispatcher
from tests.fixtures.mocks import (
    MockEventBus,
    MockTokenEconomy,
    MockTraceManager,
    MockMemoryStore,
    MockProjectManager
)

@pytest.fixture
def test_container():
    """Create container with mock dependencies"""
    container = Container()

    container.register('event_bus', MockEventBus, factory=MockEventBus)
    container.register('token_economy', MockTokenEconomy, factory=lambda: MockTokenEconomy(10.0))
    container.register('trace_manager', MockTraceManager, factory=MockTraceManager)
    container.register('memory_store', MockMemoryStore, factory=MockMemoryStore)
    container.register('project_manager', MockProjectManager, factory=MockProjectManager)

    container.register(
        'dispatcher',
        Dispatcher,
        factory=lambda event_bus, token_economy, memory_store, trace_manager, project_manager: Dispatcher(
            event_bus=event_bus,
            token_economy=token_economy,
            memory_store=memory_store,
            trace_manager=trace_manager,
            project_manager=project_manager
        ),
        dependencies=['event_bus', 'token_economy', 'memory_store', 'trace_manager', 'project_manager']
    )

    return container

@pytest.mark.asyncio
async def test_dispatcher_learner_mode(test_container):
    """Test dispatcher routes to learner mode"""
    dispatcher = test_container.resolve('dispatcher')
    trace_manager = test_container.resolve('trace_manager')

    # Mock: no trace found
    trace_manager.mock_find_trace_result = None

    result = await dispatcher.dispatch("Novel task", mode="AUTO")

    assert result["mode"] == "LEARNER"

@pytest.mark.asyncio
async def test_dispatcher_follower_mode(test_container):
    """Test dispatcher routes to follower mode"""
    dispatcher = test_container.resolve('dispatcher')
    trace_manager = test_container.resolve('trace_manager')

    # Mock: high confidence trace found
    trace_manager.mock_find_trace_result = (MockTrace(), 0.95, "FOLLOWER")

    result = await dispatcher.dispatch("Known task", mode="AUTO")

    assert result["mode"] == "FOLLOWER"
```

---

## 8. Conclusion

The **llmos** architecture demonstrates sophisticated design with clear separation of concerns and strong extensibility. However, there are significant opportunities for improvement through formal design pattern application.

**Key Strengths**:
- Clean three-tier architecture (kernel, interfaces, memory)
- Excellent plugin system with hot-reload
- Smart multi-mode execution strategy
- Good use of Repository and Factory patterns

**Key Weaknesses**:
- High coupling in Dispatcher and Orchestrator
- Scattered configuration management
- Limited testability due to concrete dependencies
- Missing formal patterns for mode selection and state management

**Recommended Implementation Order**:
1. **Dependency Injection Container** (Weeks 1-2)
2. **Strategy Pattern for Mode Selection** (Week 3)
3. **Configuration Management** (Week 4)
4. **Abstract Factory for Agents** (Week 5)
5. **Protocol Interfaces** (Week 6)
6. **Command Pattern for State** (Week 7)

Implementing these patterns will transform llmos from a working system to a highly maintainable, testable, and extensible LLM operating system that can scale to production deployments.

---

**Next Steps**:
1. Review this analysis with the development team
2. Prioritize pattern implementations based on current project needs
3. Create implementation tickets for each pattern
4. Set up comprehensive test suite
5. Document patterns in architecture guide

**Estimated Timeline**: 6-8 weeks for Priority 1-2 implementations
