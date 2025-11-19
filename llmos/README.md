# LLM OS (llmos) - Generic LLM Operating System

> Evolution of llmunix based on Claude Agent SDK

## Philosophy

LLM OS treats the Large Language Model as the **CPU**:
- **Python Kernel**: Motherboard and peripherals (I/O, storage, execution)
- **LLM**: Processor (logic, planning, reasoning)
- **Tokens**: Energy/Battery (every cognitive cycle costs resources)

## Architecture

### Separation of Concerns

**Somatic Thread (Kernel)**:
- High-speed, deterministic, non-blocking
- Scheduler, Tool Execution, Watchdog, I/O
- Lives in: `kernel/`

**Cognitive Thread (Cortex)**:
- Low-speed, probabilistic, blocking
- Planner, Learner, Follower
- Lives in: `interfaces/cortex.py`

**Memory System (Storage)**:
- L1 Cache: Context Window (in LLM)
- L2 Cache: Short-term memory (session logs)
- L3 Storage: Procedural memory (execution traces)
- L4 Storage: Semantic memory (vector DB)
- Lives in: `memory/`

### Token Economy

The "Battery" of the OS. Manages cost of intelligence:

```python
economy = TokenEconomy(budget_usd=10.0)

# Check if we can afford Learner Mode
economy.check_budget(estimated_cost=0.50)  # Raises LowBatteryError if insufficient

# Deduct actual cost
economy.deduct(actual_cost=0.45, operation="Learn: Create Python script")
```

### Learner-Follower-Orchestrator Pattern

The key innovation that makes the OS economical:

**Learner Mode** (Expensive):
- Uses Claude Sonnet 4.5 for full reasoning
- Creates execution traces for future use
- Cost: ~$0.50 per execution
- Speed: Variable (10-60s)

**Follower Mode** (Free):
- Executes proven traces deterministically
- Cost: $0 (pure Python)
- Speed: Fast (0.1-1s)

**Orchestrator Mode** (Phase 2 NEW):
- Multi-agent coordination for complex tasks
- Dynamic agent creation on-demand
- Project-based organization
- Cost: Variable based on subtasks
- Speed: Variable (depends on complexity)

**Dispatcher Logic**:
```
User Request → Query Trace Memory
  ↓
  Found High-Confidence Trace?
  ↓
  YES → Follower Mode ($0)
  NO  → Check Complexity
        ↓
        Complex (multi-step)? → Orchestrator Mode
        Simple? → Learner Mode ($0.50) → Save New Trace
```

## Installation

```bash
cd llmos
pip install -r requirements.txt
```

**Required Dependencies:**
- `claude-agent-sdk>=0.1.0` - **REQUIRED** for proper Claude integration
- `anyio>=4.0.0` - Async support
- `pyyaml>=6.0` - Configuration
- `numpy>=1.24.0` - Data processing

**Note:** llmos now uses Claude Agent SDK natively. The SDK is required for Learner and Orchestrator modes. Without it, the system falls back to legacy cortex mode with limited functionality.

## Quick Start

### Interactive Mode

```bash
python boot.py interactive
```

```
llmos> Create a Python script to calculate primes
# First time: Learner Mode ($0.50)
# Creates execution trace

llmos> Create a Python script to calculate fibonacci
# Second time: Follower Mode ($0) - reuses learned pattern!
```

### Single Command

```bash
python boot.py "Analyze data in workspace/data.csv"
```

## Project Structure

```
llmos/
├── boot.py                      # Entry point - main OS loop
├── kernel/                      # Somatic layer
│   ├── bus.py                  # Event bus (pub/sub)
│   ├── scheduler.py            # Async scheduler
│   ├── watchdog.py             # LLM monitoring
│   ├── token_economy.py        # Budget management
│   ├── project_manager.py      # Project organization (Phase 2)
│   ├── agent_factory.py        # Dynamic agent creation (Phase 2)
│   ├── component_registry.py   # Agent/component discovery (Phase 2)
│   └── state_manager.py        # Execution state tracking (Phase 2)
├── memory/                      # Storage layer
│   ├── sdk_memory.py           # Claude SDK Memory Tool wrapper
│   ├── store_sdk.py            # File-based memory store (L4)
│   ├── traces_sdk.py           # Execution traces in markdown (L3)
│   ├── query_sdk.py            # Memory query interface (keyword-based)
│   ├── cross_project_sdk.py   # Cross-project insights (file-based)
│   ├── store.py                # Legacy store (backup)
│   └── traces.py               # Legacy traces (backup)
├── interfaces/                  # Cortex layer
│   ├── sdk_client.py           # Claude SDK Client wrapper (Phase 2 - PROPER INTEGRATION)
│   ├── cortex.py               # LLM interface (legacy fallback)
│   ├── dispatcher.py           # 3-mode router (uses SDK)
│   └── orchestrator.py         # Multi-agent coordination (uses SDK)
├── plugins/                     # Extensible tools
│   ├── __init__.py             # Plugin loader
│   └── example_tools.py        # Example tools
├── examples/                    # Usage examples
│   └── multi_agent_example.py  # Phase 2 examples
└── workspace/                   # Runtime workspace
    └── memories/               # Claude SDK memory structure
        ├── traces/            # Execution traces (markdown)
        ├── projects/          # Project-specific memory
        │   └── {project}/
        │       └── traces/    # Project traces
        ├── sessions/          # Session context
        ├── facts/             # Long-term facts
        └── insights/          # Extracted insights
```

## Creating Plugins

Plugins make the OS extensible for any domain (quantum computing, web scraping, etc.):

```python
# plugins/quantum.py
from plugins import llm_tool

@llm_tool(
    "simulate_circuit",
    "Simulate a quantum circuit",
    {"circuit_spec": str, "shots": int}
)
async def simulate_circuit(circuit_spec: str, shots: int):
    # Quantum simulation logic here
    return {"results": {...}}
```

Drop the file in `plugins/` and it's automatically available!

## Example Workflow

```python
from llmos.boot import LLMOS

# Boot the OS
os = LLMOS(budget_usd=10.0)
await os.boot()

# First execution: Learner Mode
await os.execute("Create a CSV parser")
# → Claude learns, creates trace, cost: $0.50

# Second execution: Follower Mode
await os.execute("Create a CSV parser")
# → Executes trace, cost: $0

# Novel task: Learner Mode
await os.execute("Build a quantum circuit")
# → Claude learns, creates trace, cost: $0.50

await os.shutdown()
```

## Key Differences from llmunix

| Feature | llmunix | llmos |
|---------|---------|-------|
| **Foundation** | Custom markdown framework | Claude Agent SDK |
| **Architecture** | Agent-based markdown specs | Kernel-Cortex-Memory layers |
| **Execution** | Multi-agent orchestration | Learner-Follower dispatch |
| **Memory** | File-based logs | Structured traces + vector DB |
| **Extensibility** | Markdown agents/tools | Python plugins |
| **Token Management** | Implicit | Explicit TokenEconomy |
| **Focus** | Project-based CLI/mobile | Generic OS for any domain |

## Use Cases

### Scientific Computing
```python
# plugins/scientific.py with numpy, scipy tools
await os.execute("Solve differential equation: dy/dx = x^2")
```

### Data Processing
```python
# Learn once
await os.execute("Process all CSV files in input/")
# Follower mode handles variations automatically
```

### Code Generation
```python
await os.execute("Create a REST API with FastAPI")
# Trace saved, can repeat for similar APIs
```

### Research
```python
await os.execute("Summarize papers on quantum ML from arxiv")
```

## Phase 2 Features (NEW)

### 1. Native Claude Agent SDK Integration

**Proper SDK Usage:**
llmos now uses Claude Agent SDK correctly via `ClaudeSDKClient` and `ClaudeAgentOptions`:

```python
# Learner Mode (SDK-based)
async with ClaudeSDKClient(
    options=ClaudeAgentOptions(
        system_prompt=agent.system_prompt,
        cwd=str(project.path),
        permission_mode="acceptEdits"
    )
) as client:
    await client.connect(prompt=goal)
    async for message in client.receive_response():
        # Build execution trace from messages
        process_message(message)
```

**Key Integration Points:**
- ✅ `LLMOSSDKClient` wrapper in `interfaces/sdk_client.py`
- ✅ Dispatcher uses SDK for Learner mode
- ✅ Orchestrator uses SDK for multi-agent coordination
- ✅ Automatic trace building from SDK messages
- ✅ Project-aware execution with `cwd` setting
- ✅ Permission modes for tool execution
- ✅ Fallback to legacy cortex if SDK unavailable

### 2. Claude SDK Memory Integration

File-based memory system aligned with Claude Agent SDK conventions:

```python
# Memory stored in /memories directory with SDK structure
similar_tasks = await os.memory_query.find_similar_tasks(
    goal="analyze CSV data",
    limit=5,
    min_confidence=0.7
)
```

**Memory Structure**:
```
/memories/
    traces/         # Execution traces (markdown)
    projects/       # Project-specific memory
    sessions/       # Session context
    facts/          # Long-term facts
    insights/       # Extracted insights
```

**Benefits**:
- Fast keyword-based search (no dependencies)
- Human-readable markdown format
- Compatible with Claude Agent SDK conventions
- Easy to inspect and edit manually
- Simple file-based architecture

### 2. Cross-Project Learning

Extract insights across project boundaries:

```python
# Analyze patterns across all projects
patterns = await os.get_cross_project_insights()

# Identify reusable agent patterns
reusable_agents = await os.get_reusable_agents()

# Get project-specific summary
summary = await os.get_project_summary("my_project")
```

**Features**:
- Common pattern detection across projects
- Reusable agent identification
- Success strategy extraction
- Cost optimization insights
- Anti-pattern detection

### 3. Project Management

Organize work into projects with isolated memory and agents:

```python
# Create a project
project = os.create_project("data_analysis", "Analyze customer data")

# Execute within project context
await os.execute(
    "Analyze sales trends",
    project_name="data_analysis"
)

# List all projects
projects = os.list_projects()
```

**Structure**:
```
workspace/
  projects/
    my_project/
      components/    # Project-specific agents
      memory/        # Project memory traces
      output/        # Generated files
      state/         # Execution state
```

### 4. Dynamic Agent Creation

Create specialized agents on-demand:

```python
# Create a specialized agent
analyst = os.create_agent(
    name="data-analyst-agent",
    category="data_analysis",
    description="Analyzes CSV data files",
    system_prompt="You are a data analysis specialist...",
    tools=["Read", "Write", "Bash"],
    capabilities=["CSV analysis", "Statistics"],
    constraints=["Max 100MB files"]
)

# List all agents
agents = os.list_agents()
```

### 5. Multi-Agent Orchestration

Coordinate multiple agents for complex tasks:

```python
# Complex goal triggers orchestration
await os.execute(
    "Research quantum computing trends and create a summary report",
    mode="ORCHESTRATOR"
)

# Orchestrator will:
# 1. Break down into subtasks
# 2. Create/select specialized agents
# 3. Coordinate execution
# 4. Synthesize results
```

## Future Enhancements

1. **Trace Evolution**: Traces improve over time with feedback
2. **Multi-Model**: Support multiple LLMs (Opus, Haiku, local models)
3. **Distributed**: Run on multiple machines
4. **GUI**: Web interface for OS control
5. **Agent Marketplace**: Share and discover reusable agents
6. **Advanced Orchestration**: Parallel agent execution, dependencies

## Design Principles

1. **Generic by Design**: No hardcoded domain logic
2. **Plugin-Based**: Everything is a plugin
3. **Token-Aware**: Always optimize for cost
4. **Learner-Follower**: Learn expensive, execute cheap
5. **Event-Driven**: Async all the way down
6. **Memory-First**: Past informs future

## Comparison to Traditional OS

| Traditional OS | LLM OS |
|----------------|--------|
| Programs are binaries | Programs are natural language goals |
| CPU executes instructions | LLM interprets goals |
| RAM stores data | Memory stores traces & knowledge |
| I/O via drivers | I/O via tools (Read, Write, Bash) |
| Process scheduling | Task dispatching (Learner/Follower) |
| Limited by hardware | Limited by token budget |

## License

Apache 2.0

---

Built with the Claude Agent SDK by Evolving Agents Labs
