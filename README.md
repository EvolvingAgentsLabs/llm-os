# LLM OS - Evolution of llmunix

> A Generic LLM Operating System built on Claude Agent SDK

## Overview

This repository contains **llmos** (LLM OS), the evolved version of [llmunix](../llmunix) based on the Claude Agent SDK. While llmunix is a markdown-driven framework focused on project-based agent orchestration, llmos is a **generic operating system** that treats the LLM as a CPU.

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

| Feature | llmunix | llmos |
|---------|---------|-------|
| **Foundation** | Custom markdown framework | Claude Agent SDK |
| **Architecture** | Agent-based orchestration | Kernel-Cortex-Memory OS |
| **Execution** | Multi-agent pipelines | Learner-Follower dispatch |
| **Memory** | File-based logs | Structured traces + vector DB |
| **Extensibility** | Markdown agents/tools | Python plugins |
| **Token Management** | Implicit cost tracking | Explicit TokenEconomy |
| **Focus** | Project-based CLI/mobile | Generic OS for any domain |
| **Philosophy** | Markdown-driven | CPU analogy (LLM as processor) |

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

- **Python Kernel**: Motherboard (I/O, scheduling, monitoring)
- **LLM**: Processor (planning, reasoning, learning)
- **Tokens**: Battery (energy for cognitive cycles)

### Learner-Follower Pattern

The core innovation that makes llmos economical:

```
First Execution (Learner Mode)
  User: "Create Python calculator"
  → Claude SDK executes ($0.50)
  → Saves execution trace
  → Cost: $0.50

Second Execution (Follower Mode)
  User: "Create Python calculator"
  → Finds matching trace
  → Executes deterministically
  → Cost: $0.00
```

### Token Economy

Explicit budget management:

```python
economy = TokenEconomy(budget_usd=10.0)
economy.check_budget(0.50)  # Learner Mode
economy.deduct(0.45, "Learn: Create script")
```

### Memory Hierarchy

- **L1**: Context window (in LLM)
- **L2**: Short-term memory (session logs)
- **L3**: Procedural memory (execution traces - YAML)
- **L4**: Semantic memory (vector DB - JSON)

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

1. **Adopting Claude Agent SDK** as the foundation
2. **Implementing OS-like architecture** (Kernel-Cortex-Memory)
3. **Adding explicit token economy** for cost optimization
4. **Using execution traces** as "compiled bytecode"
5. **Plugin-based extensibility** instead of markdown specs
6. **Generic design** applicable to any domain

## When to Use Each

**Use llmunix when**:
- You need project-based organization
- Markdown-driven configuration is preferred
- Multi-agent orchestration fits your workflow
- Mobile app generation is needed
- You want Claude Code-native integration

**Use llmos when**:
- You need a generic LLM operating system
- Cost optimization is critical
- You want to build up a trace library
- Plugin-based extensibility is preferred
- You're building custom tooling on Claude Agent SDK

## License

Apache 2.0

---

**llmunix**: Markdown Operating System for agentic workflows
**llmos**: Generic LLM Operating System with token economy

Both are part of the Evolving Agents Labs ecosystem.
