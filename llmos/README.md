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

### Learner-Follower Pattern

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

**Dispatcher Logic**:
```
User Request → Query Trace Memory
  ↓
  Found High-Confidence Trace?
  ↓
  YES → Follower Mode ($0)
  NO  → Learner Mode ($0.50) → Save New Trace
```

## Installation

```bash
cd llmos
pip install -r requirements.txt
```

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
├── boot.py                  # Entry point - main OS loop
├── kernel/                  # Somatic layer
│   ├── bus.py              # Event bus (pub/sub)
│   ├── scheduler.py        # Async scheduler
│   ├── watchdog.py         # LLM monitoring
│   └── token_economy.py    # Budget management
├── memory/                  # Storage layer
│   ├── store.py            # Semantic memory (L4)
│   └── traces.py           # Execution traces (L3)
├── interfaces/              # Cortex layer
│   ├── cortex.py           # LLM interface (Claude Agent SDK)
│   └── dispatcher.py       # Learner/Follower router
├── plugins/                 # Extensible tools
│   ├── __init__.py         # Plugin loader
│   └── example_tools.py    # Example tools
└── workspace/              # Runtime workspace
    └── memory/             # Persistent memory
        └── traces/         # Execution trace storage
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

## Future Enhancements

1. **Better Embeddings**: Replace simple hash with sentence-transformers
2. **Semantic Trace Matching**: Fuzzy goal matching, not just exact
3. **Trace Evolution**: Traces improve over time with feedback
4. **Multi-Model**: Support multiple LLMs (Opus, Haiku, local models)
5. **Distributed**: Run on multiple machines
6. **GUI**: Web interface for OS control

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
