# LLM OS Architecture

## Overview

LLM OS is a **Generic LLM Operating System** that treats the Large Language Model as a CPU. It implements a production-ready architecture using the Claude Agent SDK with three execution modes: Learner, Follower, and Orchestrator.

**Current Version**: Phase 2.5
- ✅ Phase 1: Learner-Follower pattern
- ✅ Phase 2: Multi-agent orchestration, project management
- ✅ Phase 2.5: SDK hooks, streaming, advanced options

## Core Philosophy

### LLM as CPU
- **Python Kernel**: Acts as motherboard - handles I/O, storage, execution, hooks (Somatic)
- **LLM (Claude)**: Acts as processor - handles logic, planning, reasoning (Cognitive)
- **Tokens**: Act as energy/battery - every cognitive cycle consumes resources

### Separation of Compute

**Cognitive Compute** (Reasoning/LLM):
- Slow, probabilistic, expensive
- Handles: Planning, learning, novel problems, orchestration
- Lives in: Cortex (interfaces/cortex.py, interfaces/sdk_client.py)

**Somatic Compute** (Execution/Python):
- Fast, deterministic, free
- Handles: Tool execution, I/O, scheduling, hooks, security
- Lives in: Kernel (kernel/)

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         LLM OS (Phase 2.5)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐         ┌───────────────────────┐          │
│  │  User Input    │────────▶│    Dispatcher         │          │
│  └────────────────┘         │  (The Brain)          │          │
│                             │  + SDK Hooks          │          │
│                             └──────────┬────────────┘          │
│                                        │                        │
│                       ┌────────────────▼──────────────┐        │
│                       │  Query Trace Memory (L3)      │        │
│                       │  + Memory Injection Hook      │        │
│                       └────────────────┬──────────────┘        │
│                                        │                        │
│                   ┌────────────────────┼────────────────┐      │
│                   │                    │                │      │
│           Found Trace?            Complex?             No      │
│                   │                    │                │      │
│                  Yes                   │               Yes     │
│                   │                    │                │      │
│                   ▼                    ▼                ▼      │
│          ┌────────────┐    ┌─────────────────┐  ┌───────────┐│
│          │ Follower   │    │ Orchestrator    │  │ Learner   ││
│          │ Mode       │    │ Mode            │  │ Mode      ││
│          │ Cost: $0   │    │ Multi-Agent     │  │ Claude SDK││
│          │ Pure Python│    │ + SDK Client    │  │ + Hooks   ││
│          └─────┬──────┘    │ + AgentDef      │  │ Cost:~$0.5││
│                │           └────────┬────────┘  └─────┬─────┘│
│                │                    │                  │      │
│                └────────────────────┴──────────────────┘      │
│                                     │                         │
│                          ┌──────────▼──────────┐              │
│                          │  Save/Update Trace  │              │
│                          │  + Cross-Project    │              │
│                          └─────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Three Execution Modes

### 1. Follower Mode (Fast & Free)
**When**: High-confidence trace found (>0.9)
**Cost**: $0.00
**Speed**: 0.1-1s

**Flow**:
```
User Goal → Hash → Find Trace → Execute Steps → Update Stats
```

**Implementation**: Pure Python, deterministic execution

### 2. Learner Mode (Novel & Expensive)
**When**: No trace found, simple novel task
**Cost**: ~$0.50
**Speed**: 10-60s

**Flow**:
```
User Goal → SDK Client → Claude Execution
          ↓
    Hooks (Budget, Security, Trace Capture)
          ↓
    Save Trace → Memory
```

**Key Features** (Phase 2.5):
- Automatic hook integration (budget, security, tracing)
- Memory injection before execution
- Streaming support with callbacks
- Real-time cost tracking

### 3. Orchestrator Mode (Complex & Adaptive) - Phase 2
**When**: Multi-step complex tasks detected
**Cost**: Variable based on subtasks
**Speed**: Variable (depends on complexity)

**Flow**:
```
Complex Goal → Break Down → Create/Select Agents
             ↓
    Register AgentDefinitions in SDK
             ↓
    Shared SDK Client → Natural Language Delegation
             ↓
    Coordinate Results → Synthesize Output
```

**Key Features**:
- Multi-agent coordination
- Dynamic agent creation
- Project-based organization
- AgentDefinition support (Phase 2)

## Three-Tier Event Loop

### 1. Kernel (Somatic Thread)
**Role**: High-speed, deterministic, non-blocking

**Components**:
- **Event Bus** (`kernel/bus.py`): Pub/Sub communication
- **Scheduler** (`kernel/scheduler.py`): Cron-like task scheduling
- **Watchdog** (`kernel/watchdog.py`): LLM timeout monitoring
- **Token Economy** (`kernel/token_economy.py`): Budget management
- **Hooks** (`kernel/hooks.py`): Event-based control flow (Phase 2.5)
- **Project Manager** (`kernel/project_manager.py`): Project organization
- **Agent Factory** (`kernel/agent_factory.py`): Dynamic agent creation
- **Component Registry** (`kernel/component_registry.py`): Agent discovery

**Operations**:
- Tool execution (Read, Write, Bash)
- Event dispatch
- Timer management
- Cost tracking
- Hook callbacks (PreToolUse, PostToolUse)

### 2. Cortex (Cognitive Thread)
**Role**: Low-speed, probabilistic, blocking

**Components**:
- **SDK Client** (`interfaces/sdk_client.py`): Claude Agent SDK wrapper (Phase 2/2.5)
- **Dispatcher** (`interfaces/dispatcher.py`): 3-mode router (Learner/Follower/Orchestrator)
- **Orchestrator** (`interfaces/orchestrator.py`): Multi-agent coordinator (Phase 2)
- **Cortex** (`interfaces/cortex.py`): Legacy fallback (if SDK unavailable)

**Modes**:
- **Planner**: Decomposes goals into steps (Orchestrator)
- **Learner**: Solves novel problems (SDK-based)
- **Follower**: Replays learned patterns (Pure Python)
- **Orchestrator**: Coordinates multiple agents (SDK-based)

**Operations**:
- LLM queries via SDK
- Plan generation and execution
- Trace creation and replay
- Agent delegation
- Hook management

### 3. Memory (Storage System)
**Role**: Persistent knowledge and patterns

**Components** (SDK-aligned):
- **Trace Manager** (`memory/traces_sdk.py`): L3 Procedural Memory (Markdown)
- **Memory Store** (`memory/store_sdk.py`): L4 File-based storage
- **Memory Query** (`memory/query_sdk.py`): Keyword-based search
- **Cross-Project** (`memory/cross_project_sdk.py`): Learning insights (Phase 2)
- **SDK Memory** (`memory/sdk_memory.py`): Memory Tool wrapper

**Tiers**:
```
L1 Cache (Context Window)
    ↓ Active conversation state
    ↓ Held in LLM memory

L2 Cache (Short-Term)
    ↓ Session logs
    ↓ workspace/memories/sessions/

L3 Storage (Procedural/Trace)
    ↓ Execution patterns (Markdown)
    ↓ workspace/memories/traces/

L4 Storage (Semantic/Facts)
    ↓ Long-term knowledge (Markdown)
    ↓ workspace/memories/facts/
    ↓ workspace/memories/insights/
```

## Phase 2.5: SDK Hooks System

Event-based control flow for budget, security, and tracing.

### Available Hooks

**PreToolUse Hooks** (Before tool execution):
```python
# BudgetControlHook
- Estimates cost per operation
- Denies expensive ops if budget low
- Prevents runaway costs

# SecurityHook
- Blocks dangerous bash commands (rm -rf /, curl | bash)
- Prevents file operations outside workspace
- Enforces security policies
```

**PostToolUse Hooks** (After tool execution):
```python
# TraceCaptureHook
- Records tool usage automatically
- Builds execution traces for Follower mode
- Captures outputs and errors

# CostTrackingHook
- Monitors cumulative cost
- Stops execution if budget exceeded
```

**UserPromptSubmit Hooks** (Before prompt submission):
```python
# MemoryInjectionHook
- Injects relevant past experiences
- Finds similar tasks from memory
- Provides context for better results
```

### Hook Integration

Hooks are automatically created and registered:

```python
# In LLMOSSDKClient.execute_learner_mode()
if enable_hooks:
    hook_registry = create_default_hooks(
        token_economy=self.token_economy,
        workspace=self.workspace,
        trace_builder=trace_builder,
        memory_query=self.memory_query,
        max_cost_usd=max_cost_usd
    )
    sdk_hooks = hook_registry.to_sdk_hooks()
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
    mode: str = "AUTO"        # AUTO, LEARNER, FOLLOWER, ORCHESTRATOR
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
- Learner Mode = "High Performance Mode" (drains battery, but hooks control it)
- Follower Mode = "Power Saving Mode" (no battery drain)
- Orchestrator Mode = "Variable Performance" (controlled by budget hooks)

## The Dispatcher: 3-Mode Router

The critical optimization logic (Phase 2.5):

```python
async def dispatch(goal: str, mode: str = "AUTO") -> Result:
    # Step 1: Determine mode
    if mode == "AUTO":
        # Check for trace
        trace = trace_manager.find_trace(goal, confidence_threshold=0.9)

        if trace:
            mode = "FOLLOWER"
        else:
            # Check complexity
            complexity_score = analyze_complexity(goal)
            if complexity_score >= 2:
                mode = "ORCHESTRATOR"
            else:
                mode = "LEARNER"

    # Step 2: Route to appropriate mode
    if mode == "FOLLOWER":
        return await _dispatch_follower(goal)
    elif mode == "ORCHESTRATOR":
        return await _dispatch_orchestrator(goal, project, max_cost_usd)
    else:  # LEARNER
        return await _dispatch_learner(goal, project, max_cost_usd)
```

### Learner Mode Dispatch (Phase 2.5)

```python
async def _dispatch_learner(goal, project, max_cost_usd):
    # Use SDK client with hooks
    result = await self.sdk_client.execute_learner_mode(
        goal=goal,
        goal_signature=hash(goal),
        project=project,
        available_agents=all_agents,  # Pass all registered agents
        max_cost_usd=max_cost_usd,
        enable_hooks=True,           # Automatic budget/security/tracing
        enable_streaming=False       # Optional real-time feedback
    )

    # Deduct actual cost from token economy
    if result["success"]:
        self.token_economy.deduct(result["cost"], f"Learner: {goal}")

    return result
```

### Orchestrator Mode Dispatch (Phase 2)

```python
async def _dispatch_orchestrator(goal, project, max_cost_usd):
    # Initialize orchestrator with all agents
    await self._ensure_orchestrator()

    # Execute multi-agent orchestration
    result = await self.orchestrator.orchestrate(
        goal=goal,
        project=project,
        max_cost_usd=max_cost_usd
    )

    # Deduct cost
    if result.success:
        self.token_economy.deduct(result.cost_usd, f"Orchestrator: {goal}")

    return result
```

## Phase 2: Multi-Agent Orchestration

### Agent Architecture

**AgentSpec** (llmos internal representation):
```python
@dataclass
class AgentSpec:
    name: str
    category: str
    description: str
    system_prompt: str
    tools: List[str]
    capabilities: List[str]
    constraints: List[str]
```

**AgentDefinition** (Claude SDK representation):
```python
# Converted via agent_spec_to_definition()
AgentDefinition(
    description=spec.description,
    prompt=spec.system_prompt,
    tools=spec.tools,
    model="sonnet"
)
```

### Orchestration Flow

```python
# 1. Register all agents as AgentDefinitions
agents_dict = {
    agent.name: agent_spec_to_definition(agent)
    for agent in all_agents
}

# 2. Create shared SDK client
options = ClaudeAgentOptions(
    agents=agents_dict,  # All agents registered!
    cwd=str(project.path),
    permission_mode="acceptEdits",
    hooks=sdk_hooks
)

# 3. Execute plan with shared client
async with ClaudeSDKClient(options=options) as client:
    for step in plan:
        # Natural language delegation
        await client.query(f"Use the {agent_name} agent to {task}")

        # Or direct step execution
        result = await execute_step(client, step, state)
```

### Project Management

**Project Structure**:
```
workspace/projects/
  my_project/
    components/      # Project-specific agents
    memory/          # Project memory traces
    output/          # Generated files
    state/           # Execution state
```

**API**:
```python
# Create project
project = os.create_project("data_analysis", "Analyze customer data")

# Execute in project context
result = await os.execute(
    "Analyze sales trends",
    project_name="data_analysis"
)
```

## Memory Flow

### Write Path (Learning - Phase 2.5)

```
User Goal
  ↓
Memory Injection Hook (finds similar tasks)
  ↓
Learner Mode (Claude SDK)
  ↓
PreToolUse Hooks (budget, security)
  ↓
Execute with tools
  ↓
PostToolUse Hooks (trace capture, cost tracking)
  ↓
Extract execution sequence
  ↓
Create ExecutionTrace (Markdown)
  ↓
Save to L3 (workspace/memories/traces/)
  ↓
Update trace index
```

### Read Path (Following)

```
User Goal
  ↓
Hash goal → goal_signature
  ↓
Query L3 index (keyword-based)
  ↓
Found trace with confidence > 0.9?
  ↓
Load ExecutionTrace (from Markdown)
  ↓
Execute steps deterministically (Pure Python)
  ↓
Update usage stats
```

## Execution Trace Format (Phase 2.5)

Traces are now stored as **Markdown** (SDK-aligned):

```markdown
---
goal_signature: a3f7c9e1b2d4f8a6
goal_text: Create a Python script to calculate primes
success_rating: 0.92
usage_count: 15
last_used: 2025-01-19T10:30:00
created_at: 2025-01-15T14:20:00
estimated_cost_usd: 0.45
estimated_time_secs: 12.5
mode: LEARNER
tools_used:
  - Write
  - Bash
---

## Execution Steps

### Step 1: Write primes.py
Tool: Write
File: primes.py

```python
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
```

### Step 2: Test script
Tool: Bash
Command: python primes.py

Output: Success
```

## Phase 2.5: Advanced SDK Options

Full control over Claude Agent SDK behavior:

```python
options = ClaudeAgentOptions(
    # System prompt (string or preset)
    system_prompt="...",
    # OR use preset:
    # system_prompt={"type": "preset", "preset": "claude_code", "append": "..."},

    # Working directory
    cwd="/path/to/workspace",

    # Multi-agent support
    agents={
        "researcher": AgentDefinition(...),
        "writer": AgentDefinition(...),
    },

    # Permission mode
    permission_mode="acceptEdits",  # "default", "acceptEdits", etc.

    # Hooks for control flow
    hooks={
        HookEvent.PRE_TOOL_USE: [budget_hook, security_hook],
        HookEvent.POST_TOOL_USE: [trace_hook, cost_hook],
        HookEvent.USER_PROMPT_SUBMIT: [memory_hook]
    },

    # Model selection
    model="sonnet",  # "sonnet", "opus", "haiku"

    # Conversation limits
    max_turns=10,

    # Environment variables
    env={"KEY": "value"},

    # Streaming support
    include_partial_messages=True  # Enable real-time progress
)
```

## Phase 2.5: Streaming Support

Real-time feedback during execution:

```python
# Define streaming callback
async def on_stream(event: StreamEvent):
    if hasattr(event, 'content'):
        print(".", end="", flush=True)

# Execute with streaming
result = await sdk_client.execute_learner_mode(
    goal="Write a long document",
    enable_streaming=True,
    streaming_callback=on_stream
)
```

**Benefits**:
- Real-time progress updates
- Non-blocking execution feedback
- User experience improvement

## Event Flow (Phase 2.5)

```
User Input
  ↓
EventBus.publish(Event.USER_INPUT)
  ↓
Dispatcher.dispatch()
  ↓
  ├─ Learner Mode
  │   ↓
  │   Create SDK Hooks
  │   ↓
  │   Memory Injection (UserPromptSubmit)
  │   ↓
  │   ClaudeSDKClient.connect()
  │   ↓
  │   Tool Execution
  │   ├─ PreToolUse Hooks (Budget, Security)
  │   ├─ Tool Call
  │   └─ PostToolUse Hooks (Trace, Cost)
  │   ↓
  │   EventBus.publish(Event.LLM_OUTPUT)
  │
  ├─ Follower Mode
  │   ↓
  │   Load Trace
  │   ↓
  │   Direct Tool Execution (Pure Python)
  │   ↓
  │   EventBus.publish(Event.TOOL_OUTPUT)
  │
  └─ Orchestrator Mode
      ↓
      Register AgentDefinitions
      ↓
      Create Shared SDK Client
      ↓
      Execute Plan Steps
      ├─ Natural Language Delegation
      └─ Direct Step Execution
      ↓
      Synthesize Results
  ↓
Result to User
```

## Comparison to Traditional OS

| Traditional OS | LLM OS |
|----------------|--------|
| **CPU** | Hardware processor | LLM (Claude) |
| **RAM** | Physical memory | Context window + trace cache |
| **Disk** | Hard drive | L3/L4 memory stores (Markdown/files) |
| **Programs** | Compiled binaries | Natural language goals |
| **Instructions** | Assembly/bytecode | Tool call sequences |
| **I/O** | Hardware drivers | Claude Code tools |
| **Scheduler** | Process scheduling | 3-mode dispatch (L/F/O) |
| **Security** | Kernel mode/user mode | SDK hooks (PreToolUse) |
| **Cost** | Fixed hardware cost | Variable token cost (with hooks) |
| **Extensions** | Kernel modules | Python plugins + AgentDefinitions |

## Key Innovations

1. **Token-Aware Architecture**: Every decision considers cost (with hook controls)
2. **Three-Mode Pattern**: Learner/Follower/Orchestrator dispatch
3. **Execution Traces as "Bytecode"**: Reusable patterns in Markdown
4. **Event-Driven Kernel**: Async throughout with hook integration
5. **Plugin-Based Extensibility**: No hardcoded tools
6. **Memory Hierarchy**: L1-L4 for different access patterns
7. **SDK Hooks System**: Budget, security, tracing via events (Phase 2.5)
8. **Multi-Agent Orchestration**: AgentDefinition support (Phase 2)
9. **Streaming Support**: Real-time feedback (Phase 2.5)
10. **System Prompt Presets**: Leverage Claude's optimized prompts (Phase 2.5)

## Cross-Project Learning (Phase 2)

Extract insights across project boundaries:

```python
# Analyze patterns across all projects
patterns = await os.get_cross_project_insights(
    min_projects=2,
    min_confidence=0.7
)

# Identify reusable agent patterns
reusable_agents = await os.get_reusable_agents(
    min_success_rate=0.8,
    min_usage_count=3
)

# Get project-specific summary
summary = await os.get_project_summary("my_project")
```

**Benefits**:
- Learn from past projects
- Identify reusable patterns
- Optimize agent selection
- Avoid anti-patterns

## Future Enhancements

### Short-Term
- [ ] Trace evolution with feedback loops
- [ ] Advanced semantic matching (embeddings)
- [ ] Parallel agent execution in Orchestrator
- [ ] Custom hook creation API

### Medium-Term
- [ ] Multi-model support (Opus, Haiku, local models)
- [ ] Distributed execution across machines
- [ ] Web UI for OS control
- [ ] Export/import trace libraries
- [ ] Agent marketplace

### Long-Term
- [ ] Self-modifying traces (meta-learning)
- [ ] Cross-domain transfer learning
- [ ] Formal verification of traces
- [ ] Trace compression and optimization
- [ ] Autonomous agent evolution

## Design Principles

1. **Separation of Concerns**: Cognitive (LLM) vs Somatic (Python)
2. **Economy First**: Optimize for token cost with hooks
3. **Memory as Code**: Traces are executable knowledge
4. **Event-Driven**: Async, non-blocking kernel
5. **Plugin Architecture**: Domain-agnostic core
6. **Learn Once, Execute Infinitely**: Core value proposition
7. **Hook-Based Control**: Budget, security, tracing via events
8. **SDK-Native**: Proper Claude Agent SDK integration
9. **Multi-Agent Ready**: Orchestration for complex tasks
10. **Streaming-Capable**: Real-time feedback for UX

---

This architecture enables:
- **Novel problem solving** via Learner Mode (with hooks)
- **Cheap repetition** via Follower Mode
- **Complex orchestration** via Orchestrator Mode
- **Budget control** via SDK hooks
- **Security enforcement** via PreToolUse hooks
- **Continuous learning** via trace accumulation
- **Domain flexibility** via plugins and agents
- **Cost efficiency** via token economy and hooks

**The result**: An LLM operating system that gets **smarter, cheaper, and safer over time**.
