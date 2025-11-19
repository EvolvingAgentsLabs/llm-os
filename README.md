# LLM OS - Evolution of llmunix

> A Generic LLM Operating System built on Claude Agent SDK

**Current Version**: Phase 2.5
- ✅ Phase 1: Learner-Follower pattern (cost optimization)
- ✅ Phase 2: Multi-agent orchestration, project management
- ✅ Phase 2.5: SDK hooks, streaming, advanced options

## Overview

This repository contains **llmos** (LLM OS), the evolved version of [llmunix](../llmunix) based on the Claude Agent SDK. While llmunix is a markdown-driven framework focused on project-based agent orchestration, llmos is a **generic operating system** that treats the LLM as a CPU with three execution modes: Learner, Follower, and Orchestrator.

## Project Structure

```
llm-os/
├── llmos/              # The new LLM OS implementation
│   ├── boot.py         # Entry point
│   ├── kernel/         # Somatic layer (Scheduler, Watchdog, Event Bus)
│   ├── memory/         # Storage layer (Traces, Semantic memory)
│   ├── interfaces/     # Cognitive layer (Cortex, Dispatcher)
│   └── plugins/        # Extensible tools
│
└── llmunix/           # Original llmunix (in parent directory)
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

- **[llmos/README.md](llmos/README.md)** - LLM OS overview and usage
- **[llmos/ARCHITECTURE.md](llmos/ARCHITECTURE.md)** - System architecture design
- **[llmos/GETTING_STARTED.md](llmos/GETTING_STARTED.md)** - Installation and first steps
- **[llmos/DEPLOYMENT_CHECKLIST.md](llmos/DEPLOYMENT_CHECKLIST.md)** - Implementation checklist

## Architecture Highlights

### LLM as CPU

llmos treats the LLM as a **Central Processing Unit**:

- **Python Kernel**: Motherboard (I/O, scheduling, monitoring, hooks)
- **LLM**: Processor (planning, reasoning, learning, orchestration)
- **Tokens**: Battery (energy for cognitive cycles, controlled by hooks)

### Three Execution Modes (Phase 2.5)

**1. Follower Mode** (Fast & Free)
```
Repeat Task: "Create Python calculator"
  → Finds matching trace (confidence > 0.9)
  → Pure Python execution
  → Cost: $0.00
```

**2. Learner Mode** (Novel & Controlled)
```
New Task: "Create Python calculator"
  → No trace found
  → Claude SDK with hooks (budget, security, tracing)
  → Saves execution trace (Markdown)
  → Cost: ~$0.50 (controlled by hooks)
```

**3. Orchestrator Mode** (Complex & Multi-Agent) - Phase 2
```
Complex Task: "Research AI trends and write report"
  → Detects complexity (keywords: "and", "research")
  → Breaks down into subtasks
  → Creates/selects agents (researcher, writer)
  → Coordinates via AgentDefinitions
  → Cost: Variable (~$1-2, hook-controlled)
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

## Use Cases

### Code Generation
```
llmos> Create a REST API with FastAPI
# First time: $0.50 (Learner)
# Repeat: $0 (Follower)
```

### Data Processing
```
llmos> Parse CSV files and create summary
# Pattern saved, reusable
```

### Research
```
llmos> Summarize latest AI papers
# Learns research pattern
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

## License

Apache 2.0

---

**llmunix**: Markdown Operating System for agentic workflows
**llmos** (Phase 2.5): Generic LLM Operating System with:
- Three execution modes (Learner/Follower/Orchestrator)
- SDK hooks (budget, security, tracing)
- Multi-agent orchestration (AgentDefinition)
- Streaming support
- Token economy

Both are part of the Evolving Agents Labs ecosystem.

**Latest**: Phase 2.5 adds comprehensive SDK integration with hooks, streaming, and advanced options for production-ready LLM OS deployments.
