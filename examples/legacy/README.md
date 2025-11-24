# Legacy Examples

This directory contains examples from earlier versions of LLM OS that demonstrate concepts now superseded by the **Hybrid Architecture (v3.2.0)**.

## Why These Are Archived

With the introduction of v3.2.0, LLM OS now features **Markdown-defined agents** that can be created and modified by the system itself. This represents a paradigm shift from programmatic agent creation.

## Available Legacy Examples

### `multi_agent_example.py` (Phase 2/2.5)

**Original Purpose**: Demonstrate programmatic agent creation using Python `AgentSpec` classes.

**12 Interactive Examples:**
1. Simple Learner Mode
2. Project Management
3. Multi-Agent Orchestration
4. Dynamic Agent Creation
5. Memory Query Interface
6. Complete Workflow
7. Claude SDK Memory
8. Cross-Project Learning
9. SDK Hooks System (Phase 2.5)
10. Streaming Support (Phase 2.5)
11. System Prompt Presets (Phase 2.5)
12. Advanced SDK Options (Phase 2.5)

**Why Archived:**
- v3.2.0 promotes **Markdown agents** (`workspace/agents/*.md`) as the primary approach
- Programmatic agents (Python) are still supported but no longer the recommended path
- The Hybrid Architecture demo (`../hybrid_architecture_demo.py`) shows the new philosophy

**Still Useful For:**
- Understanding the underlying Python API
- Building custom integrations that need programmatic control
- Seeing how Phase 2/2.5 features work under the hood

**Quick Start:**
```bash
cd examples/legacy
python multi_agent_example.py
```

Select from 12 examples or run all with `all`.

## Modern Alternatives

For current best practices, see:

| Legacy Example | Modern Alternative |
|---------------|-------------------|
| **Multi-Agent Example** | **`../hybrid_architecture_demo.py`** ⭐ |
| Programmatic agent creation | System creates agents via `create_agent` tool |
| Python AgentSpec classes | Markdown files in `workspace/agents/*.md` |
| Manual agent registration | Hot-reload with AgentLoader |

## When to Use Legacy Examples

Use these examples if you need to:
- Understand the Python API for custom integrations
- Build tools that programmatically manage agents
- Learn about the Phase 2/2.5 internal architecture
- See comprehensive feature coverage in one place

For **new projects**, start with:
1. **`../hybrid_architecture_demo.py`** - See self-modification in action
2. **`../demo-app/`** - Comprehensive feature tour
3. **Domain examples** - `qiskit_studio_backend/`, `robo-os/`, `q-kids-studio/`

## Compatibility Note

All legacy examples are **fully compatible** with v3.2.0. The Python API has not changed - we've simply added Markdown agents on top. You can mix both approaches in the same project.

---

**Version**: Archived from v3.1.0 and earlier
**Last Updated**: 2025-11-23
**Status**: Maintained for reference, not actively promoted
