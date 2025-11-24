# LLM OS - Evolution of llmunix

> A Self-Modifying LLM Operating System with Hybrid Architecture

**Current Version**: 3.2.0 (Hybrid Architecture)
- ✅ **Phase 3.2**: Hybrid Architecture - Markdown agents + Python kernel
- ✅ Phase 3.0: HOPE - Self-modifying kernel with crystallization
- ✅ Phase 2.5: SDK hooks, streaming, nested learning
- ✅ Phase 2: Multi-agent orchestration, project management
- ✅ Phase 1: Learner-Follower pattern (cost optimization)

## 🌟 The Hybrid Architecture

**The future of LLM OS**: Agents are defined in **Markdown files** that the system can create and modify on the fly!

### Three-Layer Stack

```
┌─────────────────────────────────────────┐
│   Markdown Mind (Cognitive Layer)       │
│   workspace/agents/*.md                 │
│   - Self-modifiable by the LLM          │
│   - Hot-reloadable (no restart)         │
│   - Human-readable, version-controllable│
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│   Python Kernel (Somatic Layer)         │
│   llmos/                                │
│   - Type-safe, performant               │
│   - Security hooks, token economy       │
│   - Production-ready runtime            │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│   Crystallized Intelligence (HOPE)      │
│   llmos/plugins/generated/              │
│   - Auto-generated Python tools         │
│   - Instant, zero-cost execution        │
│   - System self-optimization            │
└─────────────────────────────────────────┘
```

### Key Innovation: Self-Modification

The system can **create new agents** by writing Markdown files:

```python
# System uses create_agent tool
await os.execute("Create a haiku-poet agent that writes beautiful haikus")

# Result: workspace/agents/haiku-poet.md is created
# Agent is immediately available, no restart needed!
```

**Why This Matters:**
- 📝 **Just-in-Time Agents**: System creates specialists on demand
- 🔄 **Hot Reload**: Changes take effect instantly
- 🧠 **LLM-Friendly**: System can read/write its own definitions
- 🎯 **Self-Evolution**: System improves itself over time
- 📚 **Version Control**: Track agent evolution in git

See **[HYBRID_ARCHITECTURE.md](HYBRID_ARCHITECTURE.md)** for full documentation.

## Overview

This repository contains **llmos** (LLM OS), the evolved version of [llmunix](../llmunix) based on the Claude Agent SDK. Starting with v3.2.0, llmos implements a **Hybrid Architecture** combining llmunix's markdown philosophy (flexibility, self-modification) with llmos's Python kernel (stability, security, performance).

## Project Structure

```
llm-os/
├── llmos/                          # Python Kernel (Somatic Layer)
│   ├── boot.py                     # Entry point
│   ├── kernel/                     # Core OS components
│   │   ├── agent_loader.py         # 🆕 Markdown → Runtime bridge
│   │   └── ...                     # Scheduler, Watchdog, Event Bus
│   ├── memory/                     # Storage layer (Traces, Memory)
│   ├── interfaces/                 # Execution layer (Dispatcher, Orchestrator)
│   └── plugins/                    # Tools
│       ├── system_tools.py         # 🆕 create_agent, list_agents, modify_agent
│       └── generated/              # 🆕 Auto-generated crystallized tools
│
├── workspace/                      # 🆕 Markdown Mind (Cognitive Layer)
│   └── agents/                     # 🆕 Agent definitions (.md files)
│       ├── researcher.md           # Sample: Web research specialist
│       ├── coder.md                # Sample: Expert coder
│       └── data-analyst.md         # Sample: Data analysis specialist
│
├── examples/                       # Production-ready examples
│   ├── hybrid_architecture_demo.py # ⭐ NEW: Self-modification demo
│   ├── qiskit_studio_backend/      # Quantum computing backend
│   ├── q-kids-studio/              # Educational quantum (ages 8-12)
│   ├── robo-os/                    # Robot control with LLM brain
│   ├── demo-app/                   # Rich TUI with 7 scenarios
│   └── multi_agent_example.py      # Phase 2/2.5 feature showcase
│
└── HYBRID_ARCHITECTURE.md          # 🆕 Full documentation (531 lines)
```

## Key Differences

| Feature | llmunix | llmos (Phase 2.5) |
|---------|---------|-------|
| **Foundation** | Custom markdown framework | Claude Agent SDK |
| **Architecture** | Agent-based orchestration | Kernel-Cortex-Memory OS |
| **Execution** | Multi-agent pipelines | 3-mode dispatch (Learner/Follower/Orchestrator) |
| **Memory** | File-based logs | SDK-aligned traces (Markdown) + file-based storage |
| **Extensibility** | Markdown agents/tools | Python plugins + AgentDefinitions |
| **Token Management** | Implicit cost tracking | Explicit TokenEconomy + SDK hooks |
| **Focus** | Project-based CLI/mobile | Generic OS for any domain |
| **Philosophy** | Markdown-driven | CPU analogy (LLM as processor) |
| **Control Flow** | Linear | Event-driven with hooks (budget, security) |
| **Multi-Agent** | Markdown orchestration | AgentDefinition + shared SDK client |
| **Security** | N/A | PreToolUse hooks (dangerous command blocking) |
| **Streaming** | N/A | Real-time feedback with partial messages |

## Quick Start

See [llmos/GETTING_STARTED.md](llmos/GETTING_STARTED.md) for detailed instructions.

```bash
cd llmos
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
python boot.py interactive
```

## Documentation

### Core Documentation
- **[llmos/README.md](llmos/README.md)** - LLM OS overview and usage
- **[llmos/ARCHITECTURE.md](llmos/ARCHITECTURE.md)** - System architecture design
- **[llmos/GETTING_STARTED.md](llmos/GETTING_STARTED.md)** - Installation and first steps
- **[llmos/DEPLOYMENT_CHECKLIST.md](llmos/DEPLOYMENT_CHECKLIST.md)** - Implementation checklist

### Examples
- **[examples/README.md](examples/README.md)** - Examples overview and navigation guide
- **[examples/qiskit_studio_backend/](examples/qiskit_studio_backend/)** - Flagship: Quantum computing backend
  - Drop-in replacement for [Qiskit Studio](https://github.com/AI4quantum/qiskit-studio) backend
  - Demonstrates production-grade LLM OS architecture
  - 100% cost savings on repeated tasks via Learner→Follower
- **[examples/q-kids-studio/](examples/q-kids-studio/)** - Educational quantum platform (ages 8-12)
  - Block-based quantum programming with gamification
  - Multi-layer safety for kids
  - 99%+ cost savings via Learner→Follower caching
- **[examples/robo-os/](examples/robo-os/)** - Robot control with LLM as brain
  - Natural language robot control
  - Multi-layer safety hooks (PreToolUse validation)
  - Operator + Safety Officer multi-agent coordination
- **[examples/demo-app/](examples/demo-app/)** - Rich terminal UI with 7 demo scenarios
- **[examples/multi_agent_example.py](examples/multi_agent_example.py)** - 12 interactive examples of Phase 2/2.5 features

## Architecture Highlights

### LLM as CPU

llmos treats the LLM as a **Central Processing Unit**:

- **Python Kernel**: Motherboard (I/O, scheduling, monitoring, hooks)
- **LLM**: Processor (planning, reasoning, learning, orchestration)
- **Tokens**: Battery (energy for cognitive cycles, controlled by hooks)

### Five Execution Modes (v3.2.0)

**1. CRYSTALLIZED Mode** (Instant & Free) - 🆕 HOPE Phase 3.0
```
Frequent Task: "Create API endpoint"
  → Pattern used 5+ times (95%+ success)
  → Execute auto-generated Python tool
  → Cost: $0.00, Time: <1s
```

**2. FOLLOWER Mode** (Fast & Free)
```
Repeat Task: "Create Python calculator"
  → Finds matching trace (confidence > 0.9)
  → Pure Python execution
  → Cost: $0.00, Time: 2-5s
```

**3. MIXED Mode** (Guided & Efficient) - Phase 2.5
```
Similar Task: "Create calculator with GUI"
  → Found similar trace (confidence 0.75-0.92)
  → Few-shot LLM guidance
  → Cost: ~$0.25, Time: 5-15s
```

**4. LEARNER Mode** (Novel & Controlled)
```
New Task: "Create Python calculator"
  → No trace found
  → Claude SDK with hooks (budget, security, tracing)
  → Saves execution trace (Markdown)
  → Cost: ~$0.50, Time: 10-30s
```

**5. ORCHESTRATOR Mode** (Complex & Multi-Agent) - Phase 2
```
Complex Task: "Research AI trends and write report"
  → Detects complexity (keywords: "and", "research")
  → Breaks down into subtasks
  → Creates/selects agents (researcher, writer)
  → Coordinates via AgentDefinitions
  → Cost: Variable (~$1-2)
```

### Token Economy

Explicit budget management:

```python
economy = TokenEconomy(budget_usd=10.0)
economy.check_budget(0.50)  # Learner Mode
economy.deduct(0.45, "Learn: Create script")
```

### Memory Hierarchy (SDK-Aligned)

- **L1**: Context window (in LLM)
- **L2**: Short-term memory (session logs)
- **L3**: Procedural memory (execution traces - **Markdown**)
- **L4**: Semantic memory (facts, insights - **file-based**)

**Phase 2.5 Update**: Memory now uses SDK-aligned structure with Markdown traces instead of YAML.

### Phase 2.5 Highlights

**SDK Hooks System** (Automatic):
- 🔒 **Security Hook**: Blocks dangerous commands (`rm -rf /`, `curl | bash`)
- 💰 **Budget Hook**: Prevents runaway costs, estimates before execution
- 📝 **Trace Hook**: Automatic execution trace capture
- 💵 **Cost Hook**: Real-time cost monitoring
- 🧠 **Memory Hook**: Injects relevant past experiences

**Streaming Support**:
- Real-time progress updates
- Partial message streaming
- Non-blocking execution feedback

**Advanced SDK Integration**:
- System prompt presets (leverage Claude's optimized prompts)
- Full ClaudeAgentOptions support (model, max_turns, env, etc.)
- AgentDefinition support for multi-agent orchestration
- Shared SDK client for efficient agent coordination

## Examples & Use Cases

### 🌟 Flagship Example: Qiskit Studio Backend

**LLM OS as a drop-in replacement for complex microservice architectures**

We've reimplemented the [Qiskit Studio](https://github.com/AI4quantum/qiskit-studio) backend using LLM OS, replacing 3 separate Maestro-orchestrated microservices with a single unified backend:

**Original Architecture (Maestro):**
- `chat-agent` - RAG-based Q&A (separate microservice)
- `codegen-agent` - Quantum code generation (separate microservice)
- `coderun-agent` - Code execution (separate microservice)

**LLM OS Architecture:**
- **Quantum Tutor** agent - Chat & education (ORCHESTRATOR mode)
- **Quantum Architect** agent - Code generation (LEARNER/FOLLOWER modes)
- **Qiskit Tools** plugin - Secure code execution (Somatic Layer)

**Key Improvements:**
- 💰 **100% cost savings** on repeated tasks (Learner → Follower caching)
- 🔒 **Enhanced security** with multi-layer protection hooks
- 🧠 **Unified memory** across all interactions (L4 semantic memory)
- ⚡ **90% simpler deployment** (single process vs. Docker Compose)
- 🎨 **API compatible** with existing Next.js frontend

**Try it:**
```bash
cd examples/qiskit_studio_backend
./run.sh
# Backend runs on http://localhost:8000
# Compatible with Qiskit Studio frontend
```

See [examples/qiskit_studio_backend/README.md](examples/qiskit_studio_backend/README.md) for full documentation.

---

### Other Use Cases

#### Code Generation
```
llmos> Create a REST API with FastAPI
# First time: $0.50 (Learner)
# Repeat: $0 (Follower)
```

#### Data Processing
```
llmos> Parse CSV files and create summary
# Pattern saved, reusable
```

#### Research
```
llmos> Summarize latest AI papers
# Learns research pattern
```

#### Quantum Computing
```
llmos> Create a 3-qubit GHZ state circuit
# First time: $0.05 (Learner)
# Second time: $0.00 (Follower - cached!)
```

#### Robotics Control
```
llmos> Move the robot arm 30cm to the right
# Operator Agent → move_relative(dx=0.3)
# Safety Hook validates position
# Robot executes safely
```

## Evolution from llmunix

llmos **evolves** from llmunix by:

1. **Adopting Claude Agent SDK** as the foundation (proper integration)
2. **Implementing OS-like architecture** (Kernel-Cortex-Memory)
3. **Adding three execution modes** (Learner/Follower/Orchestrator)
4. **Explicit token economy** with SDK hooks for control
5. **Using execution traces** as "compiled bytecode" (Markdown format)
6. **Plugin-based extensibility** + AgentDefinition support
7. **Generic design** applicable to any domain
8. **Hook-based security** and budget control (Phase 2.5)
9. **Multi-agent orchestration** with natural language delegation (Phase 2)
10. **Streaming support** for real-time feedback (Phase 2.5)

## When to Use Each

**Use llmunix when**:
- You need project-based organization with markdown configs
- Markdown-driven workflow is preferred
- Mobile app generation is needed
- You want Claude Code-native integration out of the box

**Use llmos when**:
- You need a **generic LLM operating system** with three execution modes
- **Cost optimization is critical** (hooks prevent runaway costs)
- **Security is important** (dangerous command blocking)
- You want to build up a **trace library** (Markdown format)
- **Multi-agent orchestration** is needed (AgentDefinition support)
- Plugin-based extensibility is preferred
- You're building custom tooling on **Claude Agent SDK**
- You need **streaming** for real-time feedback
- You want **proper SDK integration** with hooks
- **Replacing microservice architectures** with a unified backend (see [Qiskit Studio example](examples/qiskit_studio_backend/))

## License

Apache 2.0

---

**llmunix**: Markdown Operating System for agentic workflows
**llmos** (v3.2.0): Self-Modifying LLM Operating System with:
- **Hybrid Architecture**: Markdown Mind + Python Kernel + Crystallization
- Five execution modes (CRYSTALLIZED/FOLLOWER/MIXED/LEARNER/ORCHESTRATOR)
- Self-modification: System creates and evolves its own agents
- Hot-reload: Changes take effect instantly
- SDK hooks (budget, security, tracing)
- Multi-agent orchestration
- Token economy

Both are part of the Evolving Agents Labs ecosystem.

**Latest**: v3.2.0 introduces the **Hybrid Architecture**, combining llmunix's markdown flexibility with llmos's Python stability. The system can now create and modify agents by writing Markdown files, achieving true self-modification. See **[HYBRID_ARCHITECTURE.md](HYBRID_ARCHITECTURE.md)** for details.
