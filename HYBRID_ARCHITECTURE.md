# Hybrid Architecture: Python Kernel + Markdown Mind

**Status**: ✅ Implemented (2025-11-23)
**Version**: 3.2.0

## Overview

LLMOS now implements a **Hybrid Architecture** that combines the best of both worlds:

- **llmunix philosophy**: Pure Markdown agent definitions (flexibility, self-modification)
- **llmos strength**: Python Kernel with robust tooling (stability, security, performance)

This architecture enables the system to **modify itself** by writing text files, creating new capabilities on demand.

---

## Architecture Components

### 1. The Mind (Cognitive Layer)

**Agents are Markdown files** with YAML frontmatter:

```markdown
---
name: researcher
description: Expert at web research and data synthesis
tools: ["WebFetch", "Read", "Write"]
model: sonnet
---

# Researcher Agent

You are an expert researcher...
[System prompt instructions]
```

**Location**: `workspace/agents/*.md`

**Benefits**:
- Human-readable and editable
- LLM can create/modify agents by writing files
- No restart required (hot-reloading)
- Version control friendly
- Self-documenting

### 2. The Body (Somatic Layer)

**Python Kernel** provides:
- Memory management (L1-L4)
- Token economy and budget control
- Security hooks and validation
- Tool implementations (@llm_tool)
- Runtime and execution

**Location**: `llmos/` directory

**Benefits**:
- Type safety and performance
- Robust error handling
- Secure execution environment
- Production-ready

### 3. The Bridge (Loader)

**AgentLoader** (`llmos/kernel/agent_loader.py`):
- Scans `workspace/agents/*.md`
- Parses YAML frontmatter + Markdown body
- Converts to Claude SDK AgentDefinition
- Injects into runtime dynamically

**Features**:
- File caching for performance
- Hot-reload support
- Validation and error handling

---

## File Structure

```
llm-os/
├── llmos/                           # Python Kernel (Body)
│   ├── kernel/
│   │   ├── agent_loader.py         # NEW: Markdown → Runtime bridge
│   │   └── ...
│   ├── plugins/
│   │   ├── system_tools.py         # NEW: create_agent, list_agents, modify_agent
│   │   └── ...
│   ├── interfaces/
│   │   ├── sdk_client.py           # UPDATED: Uses AgentLoader
│   │   └── ...
│   └── boot.py                      # UPDATED: Imports system tools
│
└── workspace/                       # Markdown Mind (Cognitive)
    └── agents/                      # NEW: Agent definitions
        ├── researcher.md            # Sample: Research agent
        ├── coder.md                 # Sample: Coding agent
        ├── data-analyst.md          # Sample: Data analysis agent
        └── [user-created].md        # System-created agents
```

---

## How It Works

### Agent Loading Flow

1. **Boot Time**:
   ```python
   os = LLMOS(budget_usd=10.0)
   await os.boot()
   ```
   - SDK Client initializes AgentLoader
   - Loader scans `workspace/agents/*.md`
   - Parses each file into AgentDefinition
   - Registers with Claude SDK

2. **Task Execution**:
   ```python
   result = await os.execute(
       goal="Research quantum computing advances",
       mode="ORCHESTRATOR"
   )
   ```
   - Dispatcher selects appropriate agent
   - SDK routes to Markdown-defined agent
   - Agent executes with granted tools
   - Result returned

3. **Self-Modification**:
   ```python
   # System uses create_agent tool
   create_agent(
       name="haiku-poet",
       description="Writes haikus",
       tools=["Write"],
       system_prompt="You are a haiku master..."
   )
   ```
   - Tool writes `workspace/agents/haiku-poet.md`
   - File immediately available (no restart)
   - Next Task execution can use new agent

---

## New Tools

### `create_agent`

Creates a new agent by writing a Markdown file.

**Parameters**:
- `name`: Kebab-case identifier (e.g., "data-analyzer")
- `description`: When to use this agent (1-2 sentences)
- `tools`: List of tool names (e.g., ["Read", "Write", "Bash"])
- `system_prompt`: Detailed agent instructions

**Example**:
```python
create_agent(
    name="security-auditor",
    description="Reviews code for security vulnerabilities",
    tools=["Read", "Grep", "Bash"],
    system_prompt="You are a security expert. Review code for: SQL injection, XSS..."
)
```

**Result**: Creates `workspace/agents/security-auditor.md`

### `list_agents`

Lists all available agents (Markdown + programmatic).

**Example**:
```python
list_agents()
```

**Output**:
```
📋 Available Agents (5):

**deep-researcher**
  📝 Expert at web research, data synthesis, and fact-checking
  🔧 Tools: WebFetch, Read, Write, Bash
  📁 File: researcher.md

**expert-coder**
  📝 Specialized in writing, reviewing, and debugging code
  🔧 Tools: Read, Write, Edit, Bash, Grep, Glob
  📁 File: coder.md

...
```

### `modify_agent`

Modifies an existing agent's definition.

**Parameters**:
- `name`: Agent name
- `field`: "description", "tools", or "prompt"
- `value`: New value

**Example**:
```python
modify_agent(
    name="coder",
    field="tools",
    value=["Read", "Write", "Edit", "Bash", "Grep", "Glob", "WebFetch"]
)
```

---

## The HOPE Pattern

**HOPE**: Higher-Order Programming Evolution

The system can evolve itself through two levels:

### Level 1: Fluid Evolution (Markdown)
- **Action**: Rewrite agent Markdown files
- **Cost**: Cheap, fast, low risk
- **Use Case**: Improve prompts, adjust tools

**Example**: System realizes researcher needs Bash for curl, adds it to tools list.

### Level 2: Crystallized Evolution (Python)
- **Action**: Write new Python tools
- **Cost**: Higher risk, needs validation
- **Use Case**: Frequently-used tool chains

**Example**: System notices it always runs the same 5 Bash commands, creates `@llm_tool("scan_network")`.

---

## HOPE Implementation (Phase 3.0)

**HOPE** (Higher-Order Programming Evolution) takes the Hybrid Architecture to the next level through **crystallization** - converting frequently-used LLM patterns into permanent Python tools.

### The Crystallization Process

The system monitors execution traces and identifies patterns ready for crystallization:

**Criteria**:
- **Usage Count**: ≥ 5 uses (frequently needed)
- **Success Rate**: ≥ 95% (stable and proven)
- **Not Already Crystallized**: Prevents duplicate work

**Priority Calculation**:
```python
priority = (
    usage_count * 10 * 0.5 +       # 50% weight on frequency
    cost_savings * 100 * 0.3 +     # 30% weight on cost savings
    success_rate * 100 * 0.2       # 20% weight on reliability
)
```

### Architecture Components

#### 1. ExecutionTrace Enhancement

**Location**: `llmos/memory/traces_sdk.py`

```python
crystallized_into_tool: Optional[str] = None  # Name of generated tool
```

When a trace is crystallized, this field stores the generated Python tool name.

#### 2. Crystallization Candidate Identification

**Location**: `llmos/memory/cross_project_sdk.py`

**Method**: `identify_crystallization_candidates()`

```python
candidates = await cross_project.identify_crystallization_candidates(
    min_usage=5,
    min_success=0.95
)

for candidate in candidates:
    print(f"Goal: {candidate['goal']}")
    print(f"Usage: {candidate['usage_count']} times")
    print(f"Priority: {candidate['crystallization_priority']:.1f}")
```

#### 3. Hot-Reload Plugin System

**Location**: `llmos/plugins/__init__.py`

**Methods**:
- `load_plugin_dynamically(file_path)` - Load new plugin without restart
- `reload_plugin(module_name)` - Reload existing plugin

**Benefits**:
- No system restart required
- Instant tool availability
- Seamless integration

#### 4. Toolsmith Agent

**Location**: `llmos/kernel/agent_factory.py`

A specialized agent that generates Python plugin code:
- Analyzes execution traces
- Generates `@llm_tool` decorated functions
- Includes error handling and type hints
- Validates syntax using AST parsing
- Saves to `llmos/plugins/generated/`

**Safety Constraints**:
- No dangerous imports (os.system, subprocess)
- Input validation required
- Exception handling mandatory
- Workspace-scoped operations only

#### 5. Crystallization Workflow

**Location**: `llmos/interfaces/orchestrator.py`

```
1. Retrieve trace from memory
   ↓
2. Register Toolsmith agent
   ↓
3. Build crystallization prompt
   ↓
4. Delegate to Toolsmith via SDK
   ↓
5. Validate generated code (AST)
   ↓
6. Hot-load new tool
   ↓
7. Mark trace as crystallized
```

**Usage**:
```python
tool_name = await orchestrator.crystallize_pattern(
    trace_signature="abc123def456",
    plugin_loader=plugin_loader
)
# Result: llmos/plugins/generated/tool_abc123def456.py
```

#### 6. Execution Mode Hierarchy

**Location**: `llmos/interfaces/dispatcher.py`

The dispatcher now supports five execution modes:

| Mode | Cost | Latency | Intelligence | Use Case |
|------|------|---------|--------------|----------|
| **CRYSTALLIZED** | **$0.00** | **<1s** | **Crystallized** | Frequent, proven patterns |
| FOLLOWER | $0.00 | 2-5s | Replay | High-confidence traces |
| MIXED | ~$0.25 | 5-15s | Guided | Medium-confidence traces |
| LEARNER | ~$0.50 | 10-30s | Full LLM | New tasks |
| ORCHESTRATOR | Variable | Variable | Multi-agent | Complex workflows |

**Mode Selection**:
```python
if trace.crystallized_into_tool:
    return "CRYSTALLIZED"  # Instant, free
elif confidence >= 0.92:
    return "FOLLOWER"      # Zero-cost replay
elif confidence >= 0.75:
    return "MIXED"         # Few-shot guidance
else:
    return "LEARNER"       # Full reasoning
```

### The Evolution Timeline

#### Before Crystallization
```
User: "Create API endpoint"
  ↓
Dispatcher → LEARNER mode
  ↓
LLM reasons through steps (cost: $0.50, time: 15s)
  ↓
Trace saved to memory
  ↓
Usage: 1, Success: 100%
```

#### After 5 Uses
```
User: "Create API endpoint"
  ↓
Dispatcher → FOLLOWER mode
  ↓
Replay trace (cost: $0.00, time: 3s)
  ↓
Usage: 5, Success: 100%
  ↓
Candidate for crystallization!
```

#### After Crystallization
```
User: "Create API endpoint"
  ↓
Dispatcher → CRYSTALLIZED mode
  ↓
Execute tool_abc123.py (cost: $0.00, time: <1s)
  ↓
Pure Python execution - instant, free, permanent
```

### Benefits

**1. Performance**
- 10-30x faster than LLM reasoning
- Sub-second execution for common tasks
- No API latency

**2. Cost Savings**
- $0.00 for crystallized tasks
- Break-even after ~2 uses
- Example: 10 uses × $0.50 = $5.00 saved

**3. System Evolution**
- System writes its own code
- Automatic optimization over time
- Permanent knowledge capture

### The Complete Hybrid Stack

```
┌─────────────────────────────────────────┐
│   Markdown Mind (Cognitive Layer)       │
│   workspace/agents/*.md                 │
│   - Flexible, self-modifiable           │
│   - Hot-reloadable                      │
│   - Human-readable                      │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│   Python Kernel (Somatic Layer)         │
│   llmos/                                │
│   - Type-safe, performant               │
│   - Secure execution                    │
│   - Production-ready                    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│   Crystallized Intelligence             │
│   llmos/plugins/generated/              │
│   - Instant execution                   │
│   - Zero cost                           │
│   - Self-generated                      │
└─────────────────────────────────────────┘
```

### Future Enhancements

**1. Automatic Crystallization**
```python
# Background job in Scheduler
async def auto_crystallize():
    candidates = await identify_crystallization_candidates()
    for candidate in candidates[:3]:  # Top 3
        await orchestrator.crystallize_pattern(candidate['signature'])
```

**2. Tool Evolution**
```python
if trace.success_rating > crystallized_tool.version_rating + 0.05:
    # Re-crystallize with improved pattern
    await orchestrator.crystallize_pattern(trace.signature)
```

**3. Cross-Project Tool Sharing**
```python
# Export tool to shared library
await export_tool(tool_name, target_project="all")
```

---

## Example Scenarios

### Scenario 1: Create Specialized Agent

**User Goal**: "I need an agent that can analyze network security"

**System Response**:
1. Uses `create_agent` tool
2. Writes `workspace/agents/network-analyzer.md`
3. Agent immediately available

**Markdown Created**:
```markdown
---
name: network-analyzer
description: Analyzes network security, detects vulnerabilities
tools: ["Bash", "Read", "Write"]
---

# Network Security Analyzer

You are an expert in network security...
```

### Scenario 2: Self-Improvement

**Observation**: Researcher agent frequently needs to parse HTML

**System Action**:
1. Uses `modify_agent` tool
2. Adds "BeautifulSoup" to tools list (if available)
3. Updates system prompt with HTML parsing instructions

**Result**: Agent capabilities enhanced without human intervention

### Scenario 3: Agent Specialization

**Task**: "Analyze this quantum algorithm paper"

**System Reasoning**:
1. Checks available agents
2. Finds "researcher" (too general) and "expert-coder" (wrong domain)
3. Uses `create_agent` to make "quantum-research-specialist"
4. Delegates task to new specialist

**Benefit**: Just-in-time agent creation

---

## Backward Compatibility

### Old Code (Still Works)

```python
# Python-defined agents
agent_spec = AgentSpec(
    name="my-agent",
    system_prompt="...",
    tools=[...]
)
os.component_registry.register_agent(agent_spec)
```

### New Code (Hybrid)

```python
# Markdown-defined agents loaded automatically
# Python agents still work and take precedence
os = LLMOS(budget_usd=10.0)
await os.boot()  # Loads both Markdown and Python agents
```

**Rule**: If a Python-defined agent has the same name as a Markdown agent, Python wins.

---

## Security Considerations

### Tool Granting

Agents can only use tools explicitly granted in their YAML frontmatter:

```yaml
tools: ["Read", "Write"]  # Cannot use Bash, Delete, etc.
```

The Python Kernel enforces this restriction.

### File Validation

AgentLoader validates:
- YAML syntax
- Required fields (name, description)
- Malformed frontmatter rejected

### Sandboxing

Python execution environment restricts:
- Dangerous imports (os, subprocess, etc.)
- File system access (via tools only)
- Network access (via tools only)

---

## Performance

### Caching

AgentLoader caches parsed definitions:
- Checks file modification time
- Only reloads if file changed
- Speeds up repeated loads

### Memory

Markdown parsing is lightweight:
- ~1ms per agent file
- Minimal memory overhead
- Scales to hundreds of agents

---

## Best Practices

### Agent Naming

- Use kebab-case: `quantum-researcher`
- Be specific: `security-auditor` not `checker`
- Indicate domain: `data-analyst`, `code-reviewer`

### Descriptions

- **Good**: "Reviews Python code for bugs, style issues, and performance"
- **Bad**: "Helps with code" (too vague)

### System Prompts

Structure your prompts:

```markdown
---
name: agent-name
---

# Agent Title

You are [role description].

## Core Capabilities
- Capability 1
- Capability 2

## Protocol
1. Step 1
2. Step 2

## Constraints
- Don't do X
- Always do Y

## Example
[Show example interaction]
```

### Tool Selection

- **Principle of Least Privilege**: Only grant tools the agent needs
- **Common Tools**: Read, Write, Bash (most agents need these)
- **Specialized Tools**: WebFetch (research), Grep (search), Edit (code modification)

---

## Troubleshooting

### Agent Not Found

**Symptom**: "Agent 'my-agent' not found"

**Solutions**:
1. Check file exists: `ls workspace/agents/my-agent.md`
2. Check YAML syntax
3. Check 'name' field matches filename (without .md)

### Agent Not Loading

**Symptom**: Agent file exists but not available

**Solutions**:
1. Check file has YAML frontmatter (starts with `---`)
2. Check YAML is valid: `python -c "import yaml; yaml.safe_load(open('file.md').read().split('---')[1])"`
3. Check logs for parsing errors

### Tool Not Available

**Symptom**: Agent tries to use tool but fails

**Solutions**:
1. Check tool is in agent's `tools` list
2. Check tool is registered: `os.component_registry.list_tools()`
3. Check tool is imported in boot.py

---

## Testing

Run the demo:

```bash
python examples/hybrid_architecture_demo.py
```

**Demonstrates**:
1. Listing Markdown agents
2. Creating new agent via system tool
3. Using newly created agent
4. Modifying existing agent
5. Inspecting Markdown files

---

## Migration Guide

### From llmunix

**You had**: Shell scripts in `agents/`
**You get**: Markdown files in `workspace/agents/`

**Convert**:
```bash
# Old llmunix agent (shell)
agents/researcher.sh

# New llmos agent (Markdown)
workspace/agents/researcher.md
```

### From Old llmos

**You had**: Python AgentSpec classes
**You get**: Both Python and Markdown (choose what fits)

**When to use Markdown**:
- Agent is simple (system prompt + tools)
- You want system to create/modify it
- You want hot-reloading

**When to use Python**:
- Complex initialization logic
- Dynamic tool generation
- Integration testing

---

## Future Enhancements

### Planned

1. **Agent Templates**: Pre-built agent templates in `llmos/system/agents/templates/`
2. **Version Control**: Track agent evolution over time
3. **Agent Marketplace**: Share agents across projects
4. **Semantic Search**: Find agents by capability description
5. **Agent Composition**: Combine multiple agents into workflows

### Experimental

1. **LLM-Generated Tools**: System writes Python tools
2. **Agent Learning**: Agents improve from feedback
3. **Agent Collaboration**: Agents that spawn sub-agents

---

## Resources

- **Example Agents**: `workspace/agents/*.md`
- **Demo Script**: `examples/hybrid_architecture_demo.py`
- **AgentLoader Code**: `llmos/kernel/agent_loader.py`
- **System Tools**: `llmos/plugins/system_tools.py`

---

## Contributing

To add a new system agent:

1. Create `workspace/agents/my-agent.md`
2. Follow the template structure
3. Test with demo script
4. Submit PR with example usage

---

**Version**: 3.2.0 (includes HOPE Phase 3.0)
**Last Updated**: 2025-11-23
**Status**: Production Ready ✅

## Architecture Evolution

- **Phase 1**: Hash-based exact matching
- **Phase 2**: Claude SDK integration, projects, cross-project learning
- **Phase 2.5**: Semantic matching, SDK hooks, streaming
- **Phase 3.0**: HOPE - Self-modifying kernel with crystallization
- **Current**: Hybrid Architecture - Markdown Mind + Python Kernel + Crystallization
