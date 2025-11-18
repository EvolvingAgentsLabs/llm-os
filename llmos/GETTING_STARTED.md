# Getting Started with LLM OS

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Anthropic API key (for Claude Agent SDK)

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

## Workspace Structure

After running, check the workspace:

```bash
ls -R workspace/
```

```
workspace/
├── memory/
│   ├── traces/
│   │   ├── trace_a3f7c9e1_20250115_103000.yaml
│   │   └── trace_b8d2f4a6_20250115_104500.yaml
│   └── semantic_memory.json
└── [output files from your tasks]
```

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

## Inspecting Traces

View saved execution traces:

```bash
cat workspace/memory/traces/trace_*.yaml
```

Example trace:
```yaml
goal_signature: "a3f7c9e1b2d4f8a6"
goal_text: "Create a Python script to calculate primes"
success_rating: 0.92
usage_count: 15
steps:
  - tool: Write
    input:
      file_path: "primes.py"
      content: "def is_prime(n): ..."
  - tool: Bash
    input:
      command: "python primes.py"
```

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

## Philosophy Reminder

LLM OS optimizes for:
1. **Learn expensive, execute cheap** - Learner/Follower pattern
2. **Token economy** - Every decision considers cost
3. **Memory as code** - Traces are executable knowledge
4. **Plugin extensibility** - Domain-agnostic core

The OS gets **smarter and cheaper** over time as your trace library grows.

---

**Ready to start?**

```bash
python boot.py interactive
llmos> Hello, LLM OS!
```
