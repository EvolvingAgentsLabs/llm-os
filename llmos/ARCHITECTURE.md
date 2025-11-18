# LLM OS Architecture

## Overview

LLM OS is a **Generic LLM Operating System** that treats the Large Language Model as a CPU. It implements the architecture design from "LLMunix Gen-1" specification using the Claude Agent SDK.

## Core Philosophy

### LLM as CPU
- **Python Kernel**: Acts as motherboard - handles I/O, storage, execution (Somatic)
- **LLM (Claude)**: Acts as processor - handles logic, planning, reasoning (Cognitive)
- **Tokens**: Act as energy/battery - every cognitive cycle consumes resources

### Separation of Compute

**Cognitive Compute** (Reasoning/LLM):
- Slow, probabilistic, expensive
- Handles: Planning, learning, novel problems
- Lives in: Cortex (interfaces/cortex.py)

**Somatic Compute** (Execution/Python):
- Fast, deterministic, free
- Handles: Tool execution, I/O, scheduling
- Lives in: Kernel (kernel/)

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        LLM OS                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────┐         ┌──────────────────┐       │
│  │  User Input    │────────▶│   Dispatcher     │       │
│  └────────────────┘         │   (The Brain)    │       │
│                             └─────────┬────────┘       │
│                                       │                 │
│                          ┌────────────▼───────────┐    │
│                          │  Query Trace Memory    │    │
│                          └────────────┬───────────┘    │
│                                       │                 │
│                    ┌──────────────────┼─────────────┐  │
│                    │                  │             │  │
│            Found Trace?              No          Yes   │
│                    │                  │             │  │
│                    ▼                  ▼             ▼  │
│          ┌─────────────────┐  ┌──────────┐  ┌────────┐│
│          │  Learner Mode   │  │ Create   │  │Follower││
│          │  (Claude SDK)   │  │  New     │  │ Mode   ││
│          │  Cost: ~$0.50   │  │ Trace    │  │Cost: $0││
│          └────────┬────────┘  └────┬─────┘  └───┬────┘│
│                   │                │             │     │
│                   └────────────────┴─────────────┘     │
│                                    │                   │
│                          ┌─────────▼────────┐          │
│                          │   Save Trace     │          │
│                          │  Update Stats    │          │
│                          └──────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

## Three-Tier Event Loop

### 1. Kernel (Somatic Thread)
**Role**: High-speed, deterministic, non-blocking

**Components**:
- **Event Bus** (`kernel/bus.py`): Pub/Sub communication
- **Scheduler** (`kernel/scheduler.py`): Cron-like task scheduling
- **Watchdog** (`kernel/watchdog.py`): LLM timeout monitoring
- **Token Economy** (`kernel/token_economy.py`): Budget management

**Operations**:
- Tool execution (Read, Write, Bash)
- Event dispatch
- Timer management
- Cost tracking

### 2. Cortex (Cognitive Thread)
**Role**: Low-speed, probabilistic, blocking

**Components**:
- **Cortex** (`interfaces/cortex.py`): Claude Agent SDK wrapper
- **Dispatcher** (`interfaces/dispatcher.py`): Learner/Follower router

**Modes**:
- **Planner**: Decomposes goals into steps
- **Learner**: Solves novel problems
- **Follower**: Replays learned patterns

**Operations**:
- LLM queries
- Plan generation
- Trace creation
- Deterministic execution

### 3. Memory (Storage System)
**Role**: Persistent knowledge and patterns

**Components**:
- **Trace Manager** (`memory/traces.py`): L3 Procedural Memory
- **Memory Store** (`memory/store.py`): L4 Semantic Memory

**Tiers**:
```
L1 Cache (Context Window)
    ↓ Active conversation state
    ↓ Held in LLM memory

L2 Cache (Short-Term)
    ↓ Session logs
    ↓ workspace/memory/short_term/

L3 Storage (Procedural/Trace)
    ↓ Execution patterns (YAML)
    ↓ workspace/memory/traces/

L4 Storage (Semantic)
    ↓ Vector database (JSON)
    ↓ workspace/memory/semantic_memory.json
```

## The TaskBlock: The "Program"

In LLM OS, a "program" is not a compiled binary, but a **TaskBlock**:

```python
@dataclass
class TaskBlock:
    goal: str                 # Natural language intent
    inputs: Dict[str, Any]    # Data context
    constraints: List[str]    # "Must be Python", "Max cost $0.10"
    priority: int             # 0-100
    tools_required: List[str] # ["fs_tools", "web_tools"]
    mode: str = "AUTO"        # AUTO, LEARNER, or FOLLOWER
```

## The Token Economy: The "Battery"

Manages the cost of intelligence:

```python
class TokenEconomy:
    balance: float              # Current budget in USD
    spend_log: List[SpendLog]   # History of spending

    def check_budget(cost: float) -> bool:
        """Raises LowBatteryError if insufficient"""

    def deduct(cost: float, operation: str):
        """Deduct cost and log"""
```

**Philosophy**:
- Learner Mode = "High Performance Mode" (drains battery)
- Follower Mode = "Power Saving Mode" (no battery drain)

## The Learner-Follower Dispatcher

The critical optimization logic:

```python
async def dispatch(goal: str) -> Result:
    # Step 1: Query L3 Storage (Traces)
    trace = trace_manager.find_trace(goal)

    # Step 2: Decision
    if trace and trace.confidence > 0.9:
        # Follower Mode (Deterministic/Fast)
        result = await cortex.follow(trace)
        cost = 0.0
    else:
        # Learner Mode (Claude/Expensive)
        check_budget(estimated_cost=0.50)
        result = await cortex.learn(goal)
        trace = result.trace
        trace_manager.save_trace(trace)
        cost = 0.50

    # Step 3: Update trace stats
    trace_manager.update_usage(trace, success=result.success)

    return result
```

## Memory Flow

### Write Path (Learning)
```
User Goal
  ↓
Learner Mode (Claude)
  ↓
Execute with tools
  ↓
Extract execution sequence
  ↓
Create ExecutionTrace
  ↓
Save to L3 (YAML file)
  ↓
Index goal signature
```

### Read Path (Following)
```
User Goal
  ↓
Hash goal → goal_signature
  ↓
Query L3 index
  ↓
Found trace with confidence > 0.9?
  ↓
Load ExecutionTrace
  ↓
Execute steps deterministically
  ↓
Update usage stats
```

## Execution Trace Format

```yaml
---
goal_signature: "a3f7c9e1b2d4f8a6"
goal_text: "Create a Python script to calculate primes"
success_rating: 0.92
usage_count: 15
last_used: "2025-01-15T10:30:00"
created_at: "2025-01-10T14:20:00"
estimated_cost_usd: 0.0
estimated_time_secs: 0.5
---

steps:
  - tool: Write
    input:
      file_path: "primes.py"
      content: |
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True

  - tool: Bash
    input:
      command: "python primes.py"
```

## Plugin System

Makes the OS extensible without hardcoding domain logic:

```python
# Drop a file in plugins/
@llm_tool("simulate_quantum", "Run quantum simulation", {...})
async def simulate_quantum(circuit: str):
    # Quantum logic here
    return result
```

**Auto-Discovery**:
1. Boot scans `plugins/` directory
2. Imports all `.py` files
3. Finds functions with `@llm_tool` decorator
4. Registers in tool registry
5. Available to LLM immediately

## Event Flow

```
User Input
  ↓
EventBus.publish(Event.USER_INPUT)
  ↓
Dispatcher.dispatch()
  ↓
  ├─ Learner Mode
  │   ↓
  │   EventBus.publish(Event.LLM_OUTPUT)
  │   ↓
  │   Tool Execution
  │   ↓
  │   EventBus.publish(Event.TOOL_OUTPUT)
  │
  └─ Follower Mode
      ↓
      Direct Tool Execution
      ↓
      EventBus.publish(Event.TOOL_OUTPUT)
  ↓
Result to User
```

## Comparison to Traditional OS

| Traditional OS | LLM OS |
|----------------|--------|
| **CPU** | Hardware processor | LLM (Claude) |
| **RAM** | Physical memory | Context window + trace cache |
| **Disk** | Hard drive | L3/L4 memory stores |
| **Programs** | Compiled binaries | Natural language goals |
| **Instructions** | Assembly/bytecode | Tool call sequences |
| **I/O** | Hardware drivers | Claude Code tools |
| **Scheduler** | Process scheduling | Learner/Follower dispatch |
| **Cost** | Fixed hardware cost | Variable token cost |

## Key Innovations

1. **Token-Aware Architecture**: Every decision considers cost
2. **Learner-Follower Pattern**: Learn expensive, execute cheap
3. **Execution Traces as "Bytecode"**: Reusable patterns
4. **Event-Driven Kernel**: Async throughout
5. **Plugin-Based Extensibility**: No hardcoded tools
6. **Memory Hierarchy**: L1-L4 for different access patterns

## Future Enhancements

### Short-Term
- [ ] Semantic trace matching (fuzzy goal matching)
- [ ] Real embedding models (sentence-transformers)
- [ ] Trace evolution (improve with feedback)
- [ ] Better tool execution in Follower Mode

### Medium-Term
- [ ] Multi-model support (Opus, Haiku, local models)
- [ ] Distributed execution across machines
- [ ] Web UI for OS control
- [ ] Export/import trace libraries

### Long-Term
- [ ] Self-modifying traces (meta-learning)
- [ ] Cross-domain transfer learning
- [ ] Formal verification of traces
- [ ] Trace compression and optimization

## Design Principles

1. **Separation of Concerns**: Cognitive vs Somatic
2. **Economy First**: Optimize for token cost
3. **Memory as Code**: Traces are executable knowledge
4. **Event-Driven**: Async, non-blocking kernel
5. **Plugin Architecture**: Domain-agnostic core
6. **Learn Once, Execute Infinitely**: Core value proposition

---

This architecture enables:
- **Novel problem solving** via Learner Mode
- **Cheap repetition** via Follower Mode
- **Continuous learning** via trace accumulation
- **Domain flexibility** via plugins
- **Cost efficiency** via token economy

The result: An LLM operating system that gets **smarter and cheaper over time**.
