# Getting Started with LLM OS

**Version**: Phase 2.5 (Multi-Agent + SDK Hooks + Streaming)

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Anthropic API key (for Claude Agent SDK)
- **Claude Agent SDK** 0.1.0+ (required)

## Installation

### 1. Install Dependencies

```bash
cd llmos
pip install -r requirements.txt
```

This installs:
- `claude-agent-sdk` - Claude Agent SDK for LLM integration
- `anyio` - Async I/O for event bus and scheduler
- `pyyaml` - YAML support for execution traces
- `numpy` - For semantic memory embeddings

### 2. Set Up Environment

Create a `.env` file or set environment variable:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Get your API key from: https://console.anthropic.com/

### 3. Verify Installation

```bash
python boot.py
```

You should see:
```
Usage:
  python boot.py interactive        # Interactive mode
  python boot.py <goal>            # Execute single goal
```

## First Steps

### Interactive Mode

Start the OS in interactive mode:

```bash
python boot.py interactive
```

You'll see the boot sequence:
```
🚀 Booting LLM OS...
💰 Token Budget: $10.00
📁 Workspace: /path/to/llmos/workspace

✅ LLM OS Ready

📝 Interactive Mode (type 'exit' to quit)

llmos>
```

### Execute Your First Goal

Try a simple task:

```
llmos> Create a Python script that prints hello world
```

**What happens**:
1. Dispatcher checks for existing trace (none found)
2. Enters Learner Mode (uses Claude SDK)
3. Claude creates the script
4. Execution trace is saved
5. Cost: ~$0.50

### Execute the Same Goal Again

```
llmos> Create a Python script that prints hello world
```

**What happens**:
1. Dispatcher finds existing trace (confidence > 0.9)
2. Enters Follower Mode (pure Python)
3. Executes saved trace deterministically
4. Cost: $0.00

**Savings**: 100% cost reduction!

### Try a Complex Goal (Orchestrator Mode - Phase 2)

```
llmos> Research Python best practices and create a style guide
```

**What happens**:
1. Dispatcher detects complexity (keywords: "and", "research")
2. Enters Orchestrator Mode (multi-agent)
3. Creates/selects specialized agents (researcher, writer)
4. Coordinates execution via AgentDefinitions
5. Synthesizes results
6. Cost: Variable (~$1-2)

**This demonstrates the three execution modes**: Follower (free), Learner (novel), Orchestrator (complex).

## Single Command Mode

Execute a goal directly:

```bash
python boot.py "Analyze the data in workspace/data.csv"
```

The OS will:
- Boot
- Execute the goal
- Shutdown
- Display budget report

## Understanding the Output

### Learner Mode Output

```
🎯 Dispatching: Create a Python calculator
====================================
🆕 No matching trace found
💡 Mode: LEARNER (Cost: ~$0.50, Time: variable)

🧠 Learner Mode: Solving novel problem...
✅ Learner Mode Complete: 3 steps, 12.5s

💾 Final Balance: $9.50
📊 Total Spent: $0.50
```

### Follower Mode Output

```
🎯 Dispatching: Create a Python calculator
====================================
📦 Found execution trace (confidence: 0.92)
💡 Mode: FOLLOWER (Cost: ~$0, Time: ~0.5s)

⚡ Follower Mode: Executing 3 steps...
  → Write
  → Bash
  → Read
✅ Follower Mode Complete

💾 Final Balance: $9.50
📊 Total Spent: $0.50
```

## Workspace Structure (Phase 2.5)

After running, check the workspace:

```bash
ls -R workspace/
```

```
workspace/
├── memories/                    # SDK-aligned memory structure
│   ├── traces/                 # Execution traces (Markdown)
│   │   ├── trace_a3f7c9e1.md
│   │   └── trace_b8d2f4a6.md
│   ├── projects/               # Project-specific memory
│   │   └── my_project/
│   │       └── traces/
│   ├── sessions/               # Session context
│   ├── facts/                  # Long-term facts
│   └── insights/               # Extracted insights
├── projects/                    # Project workspaces (Phase 2)
│   └── my_project/
│       ├── components/         # Project agents
│       ├── memory/            # Project memory
│       ├── output/            # Generated files
│       └── state/             # Execution state
└── [output files from your tasks]
```

**Note**: Memory structure is now SDK-aligned (Markdown format instead of YAML).

## Common Use Cases

### 1. Code Generation

```
llmos> Create a FastAPI REST API with user authentication
```

First time: Learner Mode (~$0.50)
Repeat: Follower Mode ($0)

### 2. Data Processing

```
llmos> Parse all CSV files in input/ and create summary report
```

Creates a reusable pattern for CSV processing.

### 3. Research & Analysis

```
llmos> Summarize the latest AI papers from arxiv
```

Learns the pattern, can repeat cheaply.

### 4. File Operations

```
llmos> Organize files in downloads/ by type
```

Pattern saved, applicable to any directory.

## Phase 2 Features: Projects and Multi-Agent

### Creating a Project

```python
# In boot.py or via API
os = LLMOS(budget_usd=10.0, project_name="my_project")
await os.boot()

# Or create dynamically
project = os.create_project("data_analysis", "Analyze customer data")
```

**Benefits**:
- Isolated memory per project
- Project-specific agents
- Organized workspace
- Cross-project learning

### Creating Specialized Agents

```python
# Create a data analyst agent
analyst = os.create_agent(
    name="data-analyst-agent",
    agent_type="specialized",
    category="data_analysis",
    description="Analyzes CSV data files",
    system_prompt="You are a data analysis specialist...",
    tools=["Read", "Write", "Bash"],
    capabilities=["CSV analysis", "Statistics"],
    constraints=["Max 100MB files"]
)

# List all agents
agents = os.list_agents()
for agent in agents:
    print(f"{agent.name}: {agent.description}")
```

### Running Multi-Agent Orchestration

```
llmos> Research latest AI developments and create a technical report
```

The Orchestrator will:
1. Detect this is a complex multi-step task
2. Break it down into subtasks
3. Create/select appropriate agents (researcher, writer)
4. Register agents as AgentDefinitions in SDK
5. Coordinate execution with natural language delegation
6. Synthesize final report

### Working with Projects

```
llmos> [In project context] Analyze sales data for Q4
```

The system:
- Uses project-specific memory
- Can access project-specific agents
- Saves traces to project memory
- Maintains project state

## Phase 2.5 Features: Hooks and Streaming

### SDK Hooks (Automatic)

Hooks are **automatically enabled** in Learner mode:

**Budget Control Hook** (PreToolUse):
- Estimates cost before each operation
- Denies expensive operations if budget low
- Prevents runaway costs

**Security Hook** (PreToolUse):
- Blocks dangerous bash commands (`rm -rf /`, `curl | bash`, etc.)
- Prevents file writes outside workspace
- Enforces security policies

**Trace Capture Hook** (PostToolUse):
- Records tool usage automatically
- Builds execution traces for Follower mode
- Captures outputs and errors

**Cost Tracking Hook** (PostToolUse):
- Monitors cumulative cost
- Stops execution if budget exceeded

**Memory Injection Hook** (UserPromptSubmit):
- Finds similar past tasks
- Injects relevant context before execution
- Improves results with historical knowledge

**You'll see hooks in action**:
```
🔌 Enabled 3 hook types
💰 Budget OK for Write (~$0.001)
🔒 Security: Allowed operation
📝 Captured: Write
```

### Streaming (Optional)

For long-running tasks, enable streaming for real-time feedback:

```python
# Via SDK client (advanced usage)
async def on_stream(event):
    print(".", end="", flush=True)

result = await os.sdk_client.execute_learner_mode(
    goal="Write a comprehensive report",
    enable_streaming=True,
    streaming_callback=on_stream
)
```

Output:
```
📡 Executing with streaming enabled...
Progress: ....................
✅ Complete!
```

## Customizing the OS

### Adjust Token Budget

```python
# boot.py
os = LLMOS(budget_usd=100.0)  # Increase budget
```

### Change Workspace Location

```python
from pathlib import Path

os = LLMOS(
    budget_usd=10.0,
    workspace=Path("/custom/workspace")
)
```

### Use Different Model

Edit `interfaces/cortex.py`:

```python
self.model = "claude-opus-4-20250514"  # Use Opus instead
```

## Creating Plugins

### Step 1: Create Plugin File

Create `plugins/my_tools.py`:

```python
from plugins import llm_tool

@llm_tool(
    "greet",
    "Greet a person",
    {"name": str, "formal": bool}
)
async def greet(name: str, formal: bool = False):
    if formal:
        return f"Good day, {name}."
    else:
        return f"Hey {name}!"
```

### Step 2: Boot the OS

The plugin is auto-discovered and loaded:

```bash
python boot.py interactive
```

Output:
```
  ✓ Loaded tool: greet
```

### Step 3: Use the Tool

```
llmos> Use the greet tool to say hello to Alice
```

## Inspecting Traces (Phase 2.5 - Markdown Format)

View saved execution traces:

```bash
cat workspace/memories/traces/trace_*.md
```

Example trace (Markdown format):
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

**Note**: Traces are now in Markdown format (SDK-aligned) instead of YAML.

## Monitoring Budget

### Check Current Budget

The OS shows budget on boot and shutdown:

```
💰 Token Budget: $10.00    # On boot
💾 Final Balance: $8.50    # On shutdown
📊 Total Spent: $1.50
```

### View Spend Log

Modify `boot.py` to print detailed log:

```python
# In shutdown()
for log in self.token_economy.spend_log:
    print(f"{log.timestamp}: {log.operation} - ${log.cost:.4f}")
```

## Troubleshooting

### "Claude Agent SDK not installed"

```bash
pip install claude-agent-sdk
```

### "ANTHROPIC_API_KEY not found"

Set the environment variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### "Permission denied" on workspace

```bash
chmod -R 755 workspace/
```

### "Low battery error"

Increase budget:

```python
os = LLMOS(budget_usd=50.0)
```

## Next Steps

1. **Read ARCHITECTURE.md** - Understand the system design
2. **Create custom plugins** - Add domain-specific tools
3. **Experiment with goals** - Build up your trace library
4. **Monitor costs** - Track token usage patterns
5. **Optimize workflows** - Identify reusable patterns

## Advanced Topics

### Trace Evolution

Traces improve with usage:
- Initial confidence: 0.75
- After successful execution: +0.1
- After failed execution: -0.2

View trace evolution:

```bash
grep "success_rating" workspace/memory/traces/*.yaml
```

### Semantic Memory

Add knowledge to semantic memory:

```python
from memory.store import MemoryStore

store = MemoryStore(Path("workspace/memory"))
store.add_memory(
    "Python best practice: Use type hints",
    metadata={"category": "python"}
)
```

Search semantic memory:

```python
results = store.search("How to write good Python code")
for entry, score in results:
    print(f"{score:.2f}: {entry.text}")
```

### Custom Scheduling

Add background tasks:

```python
from kernel.scheduler import Scheduler

async def daily_cleanup():
    # Cleanup logic
    return "Cleanup complete"

scheduler.register_task(
    "cleanup",
    daily_cleanup,
    interval_seconds=86400  # 24 hours
)
```

## Community & Support

- **Documentation**: See README.md, ARCHITECTURE.md
- **Issues**: Report bugs on GitHub
- **Examples**: Check `plugins/example_tools.py`

## Running Examples

Check out comprehensive examples for all features:

```bash
python examples/multi_agent_example.py
```

**Available examples** (12 total):
1. Simple Learner Mode
2. Project Management
3. Multi-Agent Orchestration
4. Dynamic Agent Creation
5. Memory Query Interface
6. Complete Workflow
7. Claude SDK Memory
8. Cross-Project Learning
9. **SDK Hooks System** (NEW Phase 2.5)
10. **Streaming Support** (NEW Phase 2.5)
11. **System Prompt Presets** (NEW Phase 2.5)
12. **Advanced SDK Options** (NEW Phase 2.5)

Each example demonstrates specific features with detailed output.

## Philosophy Reminder

LLM OS optimizes for:
1. **Three execution modes** - Learner (novel), Follower (free), Orchestrator (complex)
2. **Token economy** - Every decision considers cost (with hook controls)
3. **Memory as code** - Traces are executable knowledge (Markdown format)
4. **Plugin extensibility** - Domain-agnostic core
5. **Multi-agent orchestration** - AgentDefinition support (Phase 2)
6. **Hook-based control** - Budget, security, tracing (Phase 2.5)
7. **SDK-native integration** - Proper Claude Agent SDK usage

The OS gets **smarter, cheaper, and safer** over time as your trace library grows.

---

**Ready to start?**

```bash
python boot.py interactive
llmos> Hello, LLM OS!
```

**Try all three modes**:
```
llmos> Create a Python calculator           # Learner (first time)
llmos> Create a Python calculator           # Follower (second time)
llmos> Research AI trends and write report  # Orchestrator (complex)
```
