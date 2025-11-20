# LLM OS Demo Application

A comprehensive demonstration application showcasing all capabilities of the LLM OS (llmos) - Phase 2.5.

## Overview

This demo application demonstrates the full power of llmos through practical, real-world scenarios including:

1. **Three Execution Modes**: Learner, Follower, and Orchestrator
2. **Project Management**: Organizing work into isolated projects
3. **Multi-Agent Orchestration**: Coordinating specialized agents for complex tasks
4. **Dynamic Agent Creation**: Creating agents on-demand for specific needs
5. **Memory System**: Leveraging execution traces and cross-project learning
6. **SDK Hooks**: Budget control, security, and trace capture
7. **Streaming Support**: Real-time feedback during execution
8. **Cost Optimization**: Learning once, executing infinitely at zero cost

## Quick Start

### Prerequisites

- Python 3.11+
- Claude Agent SDK installed
- ANTHROPIC_API_KEY set

### Installation

```bash
# Install dependencies
cd demo-app
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Run the Demo

```bash
# Interactive demo menu
python demo_main.py

# Run specific scenario
python demo_main.py --scenario data-pipeline

# Run all scenarios
python demo_main.py --all
```

## Demo Scenarios

### 1. Data Processing Pipeline
**Scenario**: Build a complete data processing pipeline
- **Mode**: Orchestrator
- **Agents**: Data Collector, Data Processor, Report Generator
- **Features**: Multi-agent coordination, project management, trace capture
- **File**: `scenarios/data_pipeline.py`

### 2. Code Generation Workflow
**Scenario**: Generate, test, and document code
- **Mode**: Learner → Follower
- **Features**: Trace learning, cost optimization, memory reuse
- **File**: `scenarios/code_generation.py`

### 3. Research Assistant
**Scenario**: Research a topic and create a comprehensive report
- **Mode**: Orchestrator
- **Agents**: Research Agent, Synthesis Agent, Technical Writer
- **Features**: Multi-step orchestration, dynamic agent creation
- **File**: `scenarios/research_assistant.py`

### 4. DevOps Automation
**Scenario**: Automate deployment and monitoring tasks
- **Mode**: All three modes
- **Features**: Security hooks, budget control, follower mode efficiency
- **File**: `scenarios/devops_automation.py`

### 5. Cross-Project Learning
**Scenario**: Demonstrate learning insights across multiple projects
- **Mode**: All modes
- **Features**: Cross-project patterns, reusable agents, optimization
- **File**: `scenarios/cross_project_demo.py`

## Architecture

```
demo-app/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── demo_main.py               # Main entry point with interactive menu
├── scenarios/                 # Demo scenarios
│   ├── __init__.py
│   ├── data_pipeline.py       # Data processing pipeline demo
│   ├── code_generation.py     # Code generation with trace learning
│   ├── research_assistant.py  # Research and reporting demo
│   ├── devops_automation.py   # DevOps task automation
│   └── cross_project_demo.py  # Cross-project learning demo
├── agents/                    # Custom agent definitions
│   ├── data_collector.py      # Collects data from sources
│   ├── data_processor.py      # Processes and transforms data
│   ├── report_generator.py    # Generates reports
│   ├── researcher.py          # Research specialist
│   └── technical_writer.py    # Technical documentation writer
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── demo_helpers.py        # Helper functions for demos
│   └── visualization.py       # Visualization utilities
└── output/                    # Demo outputs (generated at runtime)
    ├── projects/              # Project outputs
    ├── reports/               # Generated reports
    └── traces/                # Execution traces
```

## Key Features Demonstrated

### 1. Three Execution Modes

**Learner Mode** - First time execution
```python
result = await os.execute("Create a Python script for data analysis")
# Cost: ~$0.50, learns pattern, creates trace
```

**Follower Mode** - Repeated execution
```python
result = await os.execute("Create a Python script for data analysis")
# Cost: $0.00, replays learned trace
```

**Orchestrator Mode** - Complex multi-step tasks
```python
result = await os.execute(
    "Research AI trends and create a technical report",
    mode="ORCHESTRATOR"
)
# Cost: Variable, coordinates multiple agents
```

### 2. Project Management

```python
# Create isolated project
project = os.create_project("data_analysis", "Analyze customer data")

# Execute in project context
await os.execute(
    "Analyze sales trends",
    project_name="data_analysis"
)

# Project has isolated:
# - Memory traces
# - Agent definitions
# - Output files
# - Execution state
```

### 3. Dynamic Agent Creation

```python
# Create specialized agent on-demand
analyst = os.create_agent(
    name="data-analyst-agent",
    category="data_analysis",
    description="Analyzes CSV data files",
    system_prompt="You are a data analysis specialist...",
    tools=["Read", "Write", "Bash"],
    capabilities=["CSV analysis", "Statistics"],
    constraints=["Max 100MB files"]
)

# Agent is automatically registered and available
```

### 4. Multi-Agent Orchestration

```python
# Orchestrator coordinates multiple agents
result = await os.execute(
    "Collect customer data, process it, and generate report",
    mode="ORCHESTRATOR"
)

# Behind the scenes:
# 1. Creates/selects: DataCollector, DataProcessor, ReportGenerator
# 2. Registers them as AgentDefinitions in SDK
# 3. Coordinates execution via natural language delegation
# 4. Synthesizes final output
```

### 5. SDK Hooks (Phase 2.5)

**Automatic Hook Integration**:
- Budget Control: Prevents runaway costs
- Security: Blocks dangerous commands
- Trace Capture: Records execution for Follower mode
- Cost Tracking: Monitors cumulative costs
- Memory Injection: Provides context from past executions

```python
# Hooks are enabled automatically in Learner mode
result = await os.execute(
    "Create a script",
    max_cost_usd=1.0  # Budget hook ensures cost < limit
)
```

### 6. Cross-Project Learning

```python
# Get common patterns across projects
patterns = await os.get_cross_project_insights()

# Identify reusable agents
reusable = await os.get_reusable_agents()

# Get project-specific summary
summary = await os.get_project_summary("my_project")
```

### 7. Streaming Support

```python
# Define streaming callback
async def on_stream(event):
    print(".", end="", flush=True)

# Execute with real-time feedback
result = await os.sdk_client.execute_learner_mode(
    goal="Write a long document",
    enable_streaming=True,
    streaming_callback=on_stream
)
```

## Cost Analysis

The demo tracks costs across scenarios:

| Scenario | First Run (Learner) | Repeat (Follower) | Savings |
|----------|---------------------|-------------------|---------|
| Simple Code Gen | $0.50 | $0.00 | 100% |
| Data Pipeline | $1.20 | $0.00 | 100% |
| Research Task | $2.50 | $0.50 | 80% |
| DevOps Task | $0.30 | $0.00 | 100% |

**Total savings after trace library built**: ~90-100%

## Memory and Learning

### Trace Evolution

```
Initial execution:
  confidence: 0.75
  cost: $0.50
  time: 15s

After 5 successful uses:
  confidence: 0.95
  cost: $0.00 (Follower mode)
  time: 0.5s
```

### Cross-Project Patterns

The demo shows how patterns learned in one project can benefit others:
- Reusable agent templates
- Common task patterns
- Optimization insights
- Anti-pattern detection

## Running the Demo

### Interactive Menu

```bash
python demo_main.py
```

You'll see:
```
╔══════════════════════════════════════════╗
║   LLM OS - Demo Application (Phase 2.5)  ║
╚══════════════════════════════════════════╝

Select a demo scenario:
1. Data Processing Pipeline
2. Code Generation Workflow
3. Research Assistant
4. DevOps Automation
5. Cross-Project Learning Demo
6. Run All Scenarios
7. Exit

Choice (1-7):
```

### Command Line Options

```bash
# Run specific scenario
python demo_main.py --scenario data-pipeline

# Run all scenarios
python demo_main.py --all

# Set custom budget
python demo_main.py --budget 20.0

# Enable verbose mode
python demo_main.py --verbose

# Use specific project
python demo_main.py --project my_project
```

## Expected Outputs

After running demos, you'll find:

```
output/
├── projects/
│   ├── data_pipeline_demo/
│   │   ├── components/         # Project agents
│   │   ├── memory/            # Project traces
│   │   ├── output/            # Generated files
│   │   └── state/             # Execution state
│   └── research_demo/
│       └── ...
├── reports/
│   ├── data_analysis_report.md
│   ├── research_summary.md
│   └── cost_analysis.md
└── traces/
    └── trace_*.md             # Execution traces
```

## Key Concepts Demonstrated

### 1. Token Economy
Every demo shows:
- Initial budget allocation
- Cost per execution
- Budget monitoring
- Savings via Follower mode

### 2. Memory Hierarchy
- **L1**: Context window (active conversation)
- **L2**: Short-term memory (session logs)
- **L3**: Procedural memory (execution traces - Markdown)
- **L4**: Semantic memory (facts and insights - files)

### 3. Plugin Architecture
Custom tools can be added to any demo:
```python
@llm_tool("analyze_csv", "Analyze CSV file", {"path": str})
async def analyze_csv(path: str):
    # Custom analysis logic
    return {"insights": [...]}
```

### 4. Event-Driven Architecture
All demos use the event bus:
- Tool execution events
- LLM output events
- Budget events
- State change events

## Troubleshooting

### "Claude Agent SDK not installed"
```bash
pip install claude-agent-sdk
```

### "ANTHROPIC_API_KEY not found"
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### "Low battery error"
Increase budget:
```bash
python demo_main.py --budget 50.0
```

### "Permission denied on workspace"
```bash
chmod -R 755 ../llmos/workspace/
```

## Next Steps

After running the demo:

1. **Explore the Traces**: Check `output/traces/` to see captured execution patterns
2. **Modify Scenarios**: Edit scenarios in `scenarios/` to customize for your use case
3. **Create Custom Agents**: Add new agents in `agents/`
4. **Add Custom Tools**: Create plugins for domain-specific functionality
5. **Run Real Workflows**: Apply llmos to your actual projects

## Documentation

- Main docs: `../llmos/README.md`
- Architecture: `../llmos/ARCHITECTURE.md`
- Getting Started: `../llmos/GETTING_STARTED.md`
- Examples: `../llmos/examples/multi_agent_example.py`

## Philosophy

This demo embodies the llmos philosophy:

1. **Learn Once, Execute Infinitely**: First run is expensive, repeats are free
2. **Token-Aware**: Every decision considers cost
3. **Memory as Code**: Execution traces are executable knowledge
4. **Event-Driven**: Async, non-blocking architecture
5. **Plugin-Based**: Domain-agnostic core
6. **Multi-Agent Ready**: Orchestration for complex tasks

## Contributing

To add new scenarios:

1. Create file in `scenarios/`
2. Implement scenario class with `run()` method
3. Add to menu in `demo_main.py`
4. Document in this README

## License

Apache 2.0 (same as llmos)

---

Built with LLM OS - The Generic LLM Operating System
Phase 2.5: Multi-Agent + SDK Hooks + Streaming + Advanced Options
