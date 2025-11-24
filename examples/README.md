# LLM OS - Examples

This directory contains comprehensive examples demonstrating LLM OS capabilities.

## 🆕 NEW: Phase 1 Design Patterns (2025-11-23)

**Start here** to see the latest architecture improvements:

### Phase 1 Patterns Example (`phase1_patterns_example.py`)

**Brand new** interactive example demonstrating Phase 1 design patterns.

**What it demonstrates:**
- ✅ **Configuration Management**: Centralized, type-safe configuration with presets
- ✅ **Strategy Pattern**: Pluggable mode selection algorithms (cost/speed/custom)
- ✅ **Dependency Injection**: Testable component construction
- ✅ **Backward Compatibility**: Old API still works 100%

**Quick Start:**
```bash
python examples/phase1_patterns_example.py
```

**9 Interactive Examples:**
1. Backward Compatibility - Old API still works
2. Configuration Presets - development(), production(), testing()
3. Custom Configuration - Builder pattern
4. Strategy Patterns - cost-optimized, speed-optimized
5. Custom Strategy - Build your own mode selection
6. Dependency Injection - Mock components for testing
7. Complete Integration - All patterns together
8. Environment Variables - 12-factor config
9. Serialization - Save/load configurations

**Impact:**
- **Testability**: +167% improvement (3/10 → 8/10)
- **Configuration**: 20+ scattered values → 1 centralized config
- **Performance**: <3% overhead (negligible)
- **Dependencies**: 0 new frameworks required

**Documentation:** See [../llmos/ARCHITECTURE_PATTERNS.md](../llmos/ARCHITECTURE_PATTERNS.md)

---

## 📚 Available Examples

### 1. Qiskit Studio Backend (`qiskit_studio_backend/`)

**A flagship example** showing LLM OS as a drop-in replacement for complex multi-agent microservice architectures.

**What it demonstrates:**
- 💰 **Cost Reduction**: Learner → Follower caching (100% savings on repeated tasks)
- 🔒 **Enhanced Security**: Multi-layer code execution protection
- 🧠 **Unified Memory**: Cross-project learning and semantic memory
- ⚡ **Simplified Architecture**: Single process replaces 3+ microservices
- 🎨 **API Compatibility**: Works with existing Qiskit Studio frontend

**Quick Start:**
```bash
cd qiskit_studio_backend
./run.sh
```

**Full Documentation:** See [qiskit_studio_backend/README.md](qiskit_studio_backend/README.md)

---

### 2. Q-Kids Studio (`q-kids-studio/`)

**Educational quantum computing platform** for children ages 8-12.

**What it demonstrates:**
- 🎮 **Kid-Friendly Learning**: Block-based programming (like Scratch for quantum!)
- 🦉 **AI Tutoring**: Professor Q agent explains quantum concepts with stories
- 🎯 **Adaptive Difficulty**: Game Master adjusts challenges based on performance
- 💰 **Cost Optimization**: Learner → Follower saves 99%+ on repeated hints
- 🔒 **Safety-First**: Multiple layers protecting kids from dangerous operations
- 📊 **Progress Tracking**: Skill trees, badges, missions, leaderboards
- 🌟 **6 Progressive Missions**: Superposition → Entanglement → VQE algorithms

**Quick Start:**
```bash
cd q-kids-studio
./run.sh
```

**What Kids Learn:**
- Mission 1: Superposition ("Spinning Coin")
- Mission 2: Entanglement ("Magic Twin Telepathy")
- Mission 3: Phase & Interference ("Secret Color Codes")
- Mission 4: Quantum Teleportation ("Teleportation Beam")
- Mission 5: Error Correction ("Noise Monster Shields")
- Mission 6: VQE Algorithm ("Valley Hunter")

**Full Documentation:** See [q-kids-studio/README.md](q-kids-studio/README.md)

---

### 3. RoboOS (`robo-os/`)

**LLM OS as the brain of a robotic arm** - Natural language robot control with multi-layer safety.

**What it demonstrates:**
- 🤖 **Natural Language Control**: Command robots with plain English
- 🛡️ **Multi-Layer Safety**: PreToolUse hook prevents dangerous operations
- 👥 **Multi-Agent Coordination**: Operator + Safety Officer collaboration
- 📹 **State Visualization**: ASCII cockpit view and overhead map
- 💰 **Learner → Follower**: Teach once, replay forever (100% cost savings)
- 🔌 **FastAPI Backend**: Production-ready REST API
- 🌊 **WebSocket Support**: Real-time state updates

**Quick Start:**
```bash
cd robo-os
./run.sh
```

**Key Features:**
- **Somatic Layer**: Robot controller plugin with 7 control tools
- **Cognitive Layer**: Operator agent (control) + Safety Officer (monitoring)
- **Safety Hook**: Validates workspace bounds, prohibited zones, speed limits
- **Camera Feeds**: Cockpit HUD and overhead map views
- **Emergency Systems**: Instant halt with system lock-out

**Example Commands:**
```
"Move 30cm to the right"
"Pick up object at (1.5, 1.0, 0.5)"
"Show me the cockpit view"
"Return to home position"
```

**Safety Demonstrations:**
- Workspace boundary enforcement (-2 to 2m in X/Y, 0 to 3m in Z)
- Prohibited zone avoidance (0.5m safety radius)
- Speed limiting (max 0.5m per command)
- Emergency stop with violation logging

**Full Documentation:** See [robo-os/README.md](robo-os/README.md)

---

### 4. Multi-Agent Example (`multi_agent_example.py`)

**Interactive Python script** demonstrating Phase 2 and Phase 2.5 features.

**What it demonstrates:**
- 🤖 **Dynamic Agent Creation**: Create specialized agents on-demand
- 📂 **Project Management**: Organize work into isolated projects
- 🔄 **Multi-Agent Orchestration**: Coordinate multiple agents
- 💾 **Memory System**: Claude SDK file-based memory with high-confidence traces
- 🌐 **Cross-Project Learning**: Learn patterns across different projects
- 🔌 **SDK Hooks**: Budget control, security, trace capture, memory injection
- 📡 **Streaming Support**: Real-time feedback during execution
- ⚙️  **Advanced Options**: System prompts, permissions, environment config

**Quick Start:**
```bash
cd ..  # Navigate to llm-os root
python examples/multi_agent_example.py
```

**Select from 12 examples:**
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

---

### 5. Demo App (`demo-app/`)

**Rich interactive terminal application** with menu-driven scenarios.

**What it demonstrates:**
- 📊 **7 Real-World Scenarios**: Data pipelines, code generation, research, DevOps, etc.
- 💡 **Cost Analysis**: Detailed cost tracking and savings demonstrations
- 📈 **Visual Feedback**: Beautiful terminal UI using Rich library
- ⏱️  **Performance Metrics**: Execution time, steps completed, success rates
- 🎯 **Targeted Demos**: Each scenario highlights specific LLM OS features

**Quick Start:**
```bash
cd demo-app
python demo_main.py
```

**Available Scenarios:**
1. **Data Processing Pipeline** - Multi-agent orchestration (3 agents)
2. **Code Generation Workflow** - Learner → Follower savings demo
3. **Research Assistant** - Complex orchestration (⚠️ has timeouts)
4. **DevOps Automation** - Security hooks in action
5. **Cross-Project Learning** - Pattern detection across projects
6. **Cost Optimization** - Run same task 5x, show savings
7. **SDK Hooks** - All Phase 2.5 hooks demonstrated

**Command-line options:**
```bash
python demo_main.py --budget 50.0          # Set budget
python demo_main.py --scenario devops      # Run specific scenario
python demo_main.py --all                  # Run all scenarios
```

**Full Documentation:** See [demo-app/README.md](demo-app/README.md)

---

## 🎯 Which Example Should I Use?

| If you want to... | Use | Why |
|------------------|-----|-----|
| See a production-ready architecture | **Qiskit Studio Backend** | Full backend replacement with FastAPI |
| Build educational tools for kids | **Q-Kids Studio** | Kid-safe, gamified, block-based learning |
| Control robots with natural language | **RoboOS** | LLM as robot brain, multi-layer safety |
| Explore all Phase 2/2.5 features interactively | **Multi-Agent Example** | 12 focused examples, easy to navigate |
| Run impressive demos with visual feedback | **Demo App** | Rich UI, scenario-based, great for presentations |
| Learn about quantum computing integration | **Qiskit Studio Backend** or **Q-Kids Studio** | Domain-specific agents, Qiskit tools |
| Understand Learner/Follower cost savings | **Q-Kids Studio** or **Demo App (Scenario 6)** | Clear cost breakdown, multiple runs |
| See multi-agent orchestration | **Demo App (Scenario 1)** | 3 agents working together |
| Test security hooks | **Demo App (Scenario 4 or 7)** | Security and budget control demos |
| Adaptive AI tutoring systems | **Q-Kids Studio** | Professor Q agent, context-aware hints |
| Robot safety and control systems | **RoboOS** | Safety hook, prohibited zones, emergency stop |
| Natural language hardware interfaces | **RoboOS** | Translate NL to precise actions |

---

## 🚀 General Setup

All examples require:

1. **Python 3.10+**
2. **Anthropic API Key**:
   ```bash
   export ANTHROPIC_API_KEY=your-key-here
   ```
3. **Install LLM OS** (if running from repository root):
   ```bash
   # From llm-os root directory
   pip install -e .
   ```

---

## 📖 Learn More

- **LLM OS Documentation**: See [../README.md](../README.md) for architecture overview
- **Phase 1 Patterns**: Configuration, Strategy, Dependency Injection (NEW 2025-11-23)
- **Phase 2 Features**: Multi-agent orchestration, project management, memory query
- **Phase 2.5 Features**: SDK hooks, streaming, advanced options, system prompts
- **Phase 3 Features**: HOPE architecture (self-modifying kernel, crystallization)

### Version History

| Version | Date | Key Features |
|---------|------|--------------|
| **3.1.0** | 2025-11-23 | Phase 1 Patterns: Config, Strategy, DI |
| 3.0.0 | 2025-11-22 | Phase 3.0: HOPE Architecture (Crystallization) |
| 2.5.0 | 2025-11-21 | Phase 2.5: Nested Learning (Semantic Matching) |
| 2.0.0 | 2025-11-20 | Phase 2.0: Multi-Agent Orchestration |
| 1.0.0 | 2025-11-19 | Phase 1.0: Learner/Follower Pattern |

**All examples maintain backward compatibility** - examples from v1.0.0 still work in v3.1.0!

---

## 🤝 Contributing Examples

Want to add your own example? Great! Follow this structure:

```
examples/
└── your-example/
    ├── README.md           # Usage instructions
    ├── requirements.txt    # Dependencies
    ├── .env.template      # Environment variables template
    └── main.py            # Entry point
```

Make sure to:
- ✅ Include comprehensive README
- ✅ Add requirements.txt with all dependencies
- ✅ Provide .env.template for configuration
- ✅ Include error handling and helpful messages
- ✅ Document what the example demonstrates
- ✅ Add to this main examples/README.md

---

## 📊 Example Comparison

| Feature | Qiskit Studio | Q-Kids Studio | RoboOS | Multi-Agent Example | Demo App |
|---------|--------------|---------------|---------|---------------------|----------|
| **Type** | Full backend application | Educational platform | Robot control system | Interactive Python script | Rich TUI application |
| **Complexity** | High (production-ready) | High (kid-safe) | High (safety-critical) | Medium (educational) | Medium (demo-focused) |
| **Use Case** | Backend replacement | STEM education | Robot control | Feature exploration | Presentations, demos |
| **Documentation** | Extensive (700+ lines) | Extensive (900+ lines) | Extensive (800+ lines) | Code comments | Inline help |
| **UI** | REST API | REST API + Block UI | REST API + WebSocket | Text prompts | Rich terminal UI |
| **Lines of Code** | ~3,000 | ~2,500 | ~2,000 | ~500 | ~700 |
| **Best For** | Production deployment | Educational apps | Robotics applications | Learning LLM OS | Showcasing features |
| **Agents** | 2 quantum specialists | 2 tutors (Q + Master) | 2 (Operator + Safety) | System agent (dynamic) | 3-7 per scenario |
| **Tools** | 2 Qiskit tools | 3 kid-safe tools | 7 robot control tools | Standard toolkit | Standard toolkit |
| **Cost Tracking** | Per-request metadata | Learner/Follower demo | Learner/Follower demo | Not emphasized | Detailed cost analysis |
| **Target Audience** | Quantum developers | Kids ages 8-12 | Roboticists | Developers | Stakeholders |
| **Safety Features** | Code validation | Multi-layer kid protection | Multi-layer safety hook | Standard | Standard |

---

## 🆘 Troubleshooting

**Import errors:**
```
ModuleNotFoundError: No module named 'boot'
```
Solution: Make sure you're running from the correct directory or llmos is in your Python path.

**API Key errors:**
```
Error: ANTHROPIC_API_KEY not set
```
Solution: Export your API key or add it to .env file.

**Permission errors:**
```
Permission denied: ./run.sh
```
Solution: Make script executable with `chmod +x run.sh`

**Budget exceeded:**
```
BudgetExceededError: Remaining budget $0.00
```
Solution: Increase budget when initializing LLMOS or in example configuration.

---

**Happy exploring! 🚀**

For questions or issues, please open a GitHub issue or check the main LLM OS documentation.
