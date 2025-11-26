# Qiskit Studio Backend - LLM OS Edition

> **A flagship example of LLM OS as a drop-in replacement for complex multi-agent microservice architectures.**

This project reimplements the [Qiskit Studio](https://github.com/AI4quantum/qiskit-studio) backend using **LLM OS**, demonstrating how a unified operating system for LLMs can replace multiple specialized microservices while providing superior memory management, cost efficiency, and security.

## 🎯 What This Demonstrates

The original Qiskit Studio uses **Maestro** to orchestrate three distinct microservices:

| Original Service | Purpose | LLM OS Replacement |
|-----------------|---------|-------------------|
| `chat-agent` | RAG-based Q&A about quantum computing | **Quantum Tutor** agent with L4 semantic memory |
| `codegen-agent` | Generate/update Qiskit quantum code | **Quantum Architect** agent with Learner/Follower modes |
| `coderun-agent` | Execute Python/Qiskit code securely | **Qiskit Tools** plugin with security hooks |

**Key Improvements:**

1. **💰 Cost Reduction**: Learner → Follower mode caches repeated patterns (e.g., "Create a Bell state") - second request is **FREE**
2. **🔒 Enhanced Security**: Built-in security hooks prevent malicious code execution
3. **🧠 Unified Memory**: Cross-project learning and semantic memory across all interactions
4. **⚡ Simplified Architecture**: Single LLM OS instance replaces 3+ microservices
5. **🎨 Same Frontend**: Drop-in API compatibility with existing Qiskit Studio UI

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Qiskit Studio Frontend                    │
│                    (Next.js - Unchanged)                     │
└────────────────┬─────────────────────────────────┬───────────┘
                 │                                 │
        POST /chat                         POST /run
                 │                                 │
                 ▼                                 ▼
┌────────────────────────────────────────────────────────────┐
│              FastAPI Bridge Server (server.py)              │
│  • Intent analysis (coding vs. question)                    │
│  • Session management                                       │
│  • API compatibility layer                                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────┐
│                        LLM OS Kernel                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Dispatcher (AUTO Mode Detection)                    │  │
│  │  • Analyzes intent hash                              │  │
│  │  • Routes: LEARNER / FOLLOWER / ORCHESTRATOR         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────┐          ┌──────────────────┐       │
│  │ Quantum Architect│          │  Quantum Tutor   │       │
│  │ (Code Generator) │          │  (Q&A Expert)    │       │
│  │ Mode: LEARNER    │          │ Mode: ORCHESTRATOR│      │
│  └────────┬─────────┘          └──────────────────┘       │
│           │                                                 │
│           ▼                                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Qiskit Tools (Somatic Layer)               │  │
│  │  • execute_qiskit_code (with security hooks)         │  │
│  │  • validate_qiskit_code                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        L4 Semantic Memory + Cross-Project Learning   │  │
│  │  • Quantum patterns cached                           │  │
│  │  • High-confidence traces stored                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- Anthropic API key (for Claude)
- (Optional) IBM Quantum API token for real quantum hardware

### Installation

1. **Navigate to the project**:
   ```bash
   cd llm-os/examples/qiskit_studio_backend
   ```

2. **Set up backend environment**:
   ```bash
   # Create .env from template
   cp .env.template .env

   # Edit .env and add your Anthropic API key
   # ANTHROPIC_API_KEY=your-api-key-here
   ```

3. **Run the backend**:
   ```bash
   # Make run script executable (if not already)
   chmod +x run.sh

   # Start the server
   ./run.sh
   ```

   Or manually:
   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Run server
   python server.py
   ```

The backend will start on `http://localhost:8000`

### Run the Included Frontend

This project includes a complete Next.js frontend (copied from qiskit-studio):

1. **Set up frontend**:
   ```bash
   cd frontend

   # Create .env.local from template
   cp .env.local.template .env.local

   # Install dependencies
   npm install
   ```

2. **Run the frontend**:
   ```bash
   npm run dev
   ```

3. **Open in browser**: `http://localhost:3000`

### Alternative: Connect to External Qiskit Studio Frontend

If you prefer to use a separate qiskit-studio installation:

1. **Clone Qiskit Studio frontend** (in a separate directory):
   ```bash
   cd ../qiskit-studio
   npm install
   ```

2. **Configure frontend** to point to LLM OS backend:

   Edit `qiskit-studio/.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/chat
   NEXT_PUBLIC_PARAMETER_UPDATE_API_URL=http://127.0.0.1:8000/chat
   NEXT_PUBLIC_RUNCODE_URL=http://127.0.0.1:8000/run
   ```

3. **Run the frontend**:
   ```bash
   npm run dev
   ```

4. **Open in browser**: `http://localhost:3000`

---

## 💡 Key Features Showcase

### 1. Learner → Follower Cost Savings

**Scenario**: User asks "Create a GHZ state circuit" via the UI

**First Request (LEARNER mode)**:
- LLM reasons about GHZ states
- Generates Qiskit code
- Tests and validates
- **Cost: ~$0.05**
- Execution time: ~5 seconds

**Second Request (FOLLOWER mode)**:
- LLM OS recognizes the intent hash
- Replays cached tool sequence
- **Cost: $0.00 (FREE!)**
- Execution time: <1 second

Check the response metadata to see when FOLLOWER mode activates:
```json
{
  "metadata": {
    "mode": "FOLLOWER",
    "cost": 0.0,
    "cached": true
  }
}
```

### 2. Security Hooks

The `execute_qiskit_code` tool includes automatic security validation:

**Try injecting malicious code** (via the UI or API):
```python
import os
os.system("rm -rf /")
```

**LLM OS Response**:
```
Security Error: Potentially dangerous operation 'import os' not allowed.
```

The code is blocked **before** reaching the Python interpreter.

### 3. Unified Memory & Cross-Project Learning

**Memory Persistence**:
- Learn about "Grover's Algorithm" in Project A
- Knowledge automatically available in Project B
- High-confidence patterns cached across sessions

**View statistics**:
```bash
curl http://localhost:8000/stats
```

Response shows:
- Token economy (budget, spent, remaining)
- Memory traces (total, high-confidence, facts)
- Active agents
- Session statistics

### 4. Intelligent Agent Routing

The bridge server automatically routes requests:

| User Input | Detected Agent | Mode | Why? |
|-----------|----------------|------|------|
| "Create a Bell state circuit" | Quantum Architect | AUTO | Code generation task |
| "What is quantum entanglement?" | Quantum Tutor | ORCHESTRATOR | Conceptual question |
| "How do I use Sampler?" | Quantum Tutor | ORCHESTRATOR | API question |
| "Implement Grover's algorithm" | Quantum Architect | AUTO | Algorithm implementation |

---

## 📡 API Reference

### POST `/chat`

**Purpose**: Chat and code generation (replaces both `chat-agent` and `codegen-agent`)

**Request formats** (both are supported):
```json
// Standard format
{
  "messages": [
    {"role": "user", "content": "Create a 3-qubit GHZ state"}
  ],
  "session_id": "optional-session-id"
}

// Maestro format (compatible with original qiskit-studio)
{
  "input_value": "Create a 3-qubit GHZ state",
  "prompt": "Create a 3-qubit GHZ state",
  "session_id": "optional-session-id"
}
```

**Response** (Maestro-compatible format):
```json
{
  "response": "{\"final_prompt\": \"...\", \"agent\": \"quantum-architect\", \"mode\": \"AUTO\", \"cost\": 0.0234, \"cached\": false}",
  "output": "```python\nfrom qiskit import QuantumCircuit\n...\n```"
}
```

### POST `/chat/stream`

**Purpose**: Streaming chat using Server-Sent Events (SSE)

**Request**: Same format as `/chat`

**Response**: SSE stream
```
data: {"step_name": "llm_step", "step_result": "Here is your quantum circuit..."}

data: [DONE]
```

### POST `/run`

**Purpose**: Execute Qiskit code (replaces `coderun-agent`)

**Request**:
```json
{
  "input_value": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nprint(qc)",
  "ibm_token": "optional-ibm-quantum-token",
  "channel": "ibm_quantum",
  "instance": "optional-crn",
  "region": "optional-region"
}
```

**Response**:
```json
{
  "output": "     ┌───┐\nq_0: ┤ H ├\n     └───┘\nq_1: ─────\n"
}
```

### GET `/stats`

**Purpose**: View LLM OS performance metrics

**Response**:
```json
{
  "token_economy": {
    "budget_usd": 50.0,
    "spent_usd": 2.34,
    "remaining_usd": 47.66,
    "transactions": 15
  },
  "memory": {
    "total_traces": 42,
    "high_confidence_traces": 12,
    "facts": 8
  },
  "agents": {
    "registered": 4,
    "available": ["quantum-architect", "quantum-tutor", "system-agent"]
  },
  "sessions": {
    "active": 2,
    "total_messages": 34
  }
}
```

### POST `/clear_session`

**Purpose**: Clear chat history for a session

**Request**:
```json
{
  "session_id": "session-to-clear"
}
```

---

## 🧪 Testing

### Test the Backend Directly

```bash
# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Create a Bell state"}
    ]
  }'

# Test code execution
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "input_value": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0,1)\nprint(qc)"
  }'

# View statistics
curl http://localhost:8000/stats | jq
```

### Example Test Cases

**1. Cost Savings Demo**:
```bash
# First request (LEARNER - costs money)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Create a 3-qubit GHZ state"}]}'

# Second request (FOLLOWER - FREE!)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Create a 3-qubit GHZ state"}]}'

# Check metadata.cached field in response
```

**2. Security Test**:
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "input_value": "import os; os.system(\"ls -la\")"
  }'

# Expected: Security error response
```

**3. Multi-Session Memory**:
```bash
# Session 1
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is quantum entanglement?"}],
    "session_id": "session-1"
  }'

# Session 2 (different session, should have separate history)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Create a Bell state"}],
    "session_id": "session-2"
  }'
```

---

## 🎓 Educational Value

This example teaches:

1. **LLM OS Architecture**: How to structure a production-grade LLM application
2. **Agent Specialization**: Creating domain-specific agents (quantum computing)
3. **Tool Integration**: Building custom tools for domain tasks
4. **API Bridging**: Making LLM OS compatible with existing frontends
5. **Cost Optimization**: Leveraging Learner/Follower patterns
6. **Security**: Implementing safe code execution
7. **Memory Management**: Cross-project learning and caching

---

## 🔧 Configuration

### Environment Variables

See `.env.template` for all available options:

```bash
# Required
ANTHROPIC_API_KEY=your-api-key

# Optional - IBM Quantum
IBM_QUANTUM_TOKEN=your-token
IBM_QUANTUM_CHANNEL=ibm_quantum
IBM_QUANTUM_INSTANCE=crn:...
IBM_QUANTUM_REGION=us-east

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# LLM OS
LLMOS_BUDGET_USD=50.0
LLMOS_PROJECT_NAME=qiskit_studio_session

# Logging
LOG_LEVEL=INFO
```

### Adjusting Token Budget

Edit `server.py` startup:
```python
os_instance = LLMOS(
    budget_usd=100.0,  # Increase budget
    project_name="my_quantum_project"
)
```

Or use environment variable:
```bash
LLMOS_BUDGET_USD=100.0 python server.py
```

---

## 📊 Performance Comparison

| Metric | Original (Maestro) | LLM OS Edition | Improvement |
|--------|-------------------|----------------|-------------|
| **Microservices** | 3 (chat, codegen, coderun) | 1 (unified) | **67% reduction** |
| **Repeated Pattern Cost** | Full LLM call each time | $0.00 (cached) | **~100% savings** |
| **Memory Sharing** | None (isolated services) | Cross-project | **Unlimited context** |
| **Security** | Per-service validation | Unified hooks | **Consistent enforcement** |
| **Deployment Complexity** | Docker Compose + K8s | Single process | **90% simpler** |

---

## 🛠️ Development

### Project Structure

```
qiskit_studio_backend/
├── server.py              # FastAPI bridge server (unified backend)
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── run.sh                # Startup script
├── .env.template         # Backend environment template
│
├── agents/               # Specialized quantum agents
│   ├── __init__.py
│   ├── quantum_architect.py    # Code generation agent
│   └── quantum_tutor.py        # Q&A agent
│
├── plugins/              # Qiskit tools
│   ├── __init__.py
│   └── qiskit_tools.py         # execute_qiskit_code, validate
│
├── memory/               # Knowledge base (optional)
│   └── qiskit_docs/            # Qiskit documentation for RAG
│
└── frontend/             # Next.js Qiskit Studio UI
    ├── app/                    # Next.js app directory
    ├── components/             # React components
    │   ├── nodes/             # Quantum computing nodes
    │   └── ui/                # UI components
    ├── hooks/                  # React hooks (AI code generation)
    ├── lib/                    # Utility functions & API service
    ├── public/                 # Static assets
    ├── .env.local.template    # Frontend environment template
    ├── package.json           # Node dependencies
    └── tsconfig.json          # TypeScript config
```

### Adding New Agents

1. Create agent spec in `agents/`:
```python
# agents/quantum_optimizer.py
from kernel.agent_factory import AgentSpec

QUANTUM_OPTIMIZER = AgentSpec(
    name="quantum-optimizer",
    category="optimization",
    agent_type="specialized",
    description="Optimizes quantum circuits for depth and gate count",
    system_prompt="You are an expert in quantum circuit optimization...",
    tools=["execute_qiskit_code"],
    capabilities=["circuit optimization", "transpilation"]
)
```

2. Register in `agents/__init__.py`:
```python
from .quantum_optimizer import QUANTUM_OPTIMIZER
__all__ = ["QUANTUM_ARCHITECT", "QUANTUM_TUTOR", "QUANTUM_OPTIMIZER"]
```

3. Register in `server.py`:
```python
from agents import QUANTUM_OPTIMIZER
# In startup():
os_instance.component_registry.register_agent(QUANTUM_OPTIMIZER)
```

### Adding New Tools

1. Create tool in `plugins/qiskit_tools.py`:
```python
@llm_tool(
    "optimize_circuit",
    "Optimizes a quantum circuit using Qiskit transpiler",
    {"circuit_code": "str", "optimization_level": "int"}
)
async def optimize_circuit(circuit_code: str, optimization_level: int = 3) -> str:
    # Implementation
    pass
```

2. Register in `server.py`:
```python
from plugins.qiskit_tools import optimize_circuit
# In startup():
os_instance.component_registry.register_tool(optimize_circuit)
```

---

## 🤝 Contributing

This is a reference implementation. Contributions welcome:

1. Additional quantum algorithms
2. Enhanced RAG knowledge base
3. More sophisticated intent analysis
4. Performance optimizations
5. Testing suite

---

## 📝 License

Same as parent LLM OS project (see root LICENSE)

---

## 🙏 Acknowledgments

- **Original Qiskit Studio**: [AI4quantum/qiskit-studio](https://github.com/AI4quantum/qiskit-studio)
- **Qiskit**: IBM Quantum team
- **LLM OS**: Evolving Agents Labs

---

## 📚 Further Reading

- [LLM OS Documentation](../../README.md)
- [Qiskit Documentation](https://docs.quantum.ibm.com/)
- [Claude Agent SDK](https://github.com/anthropics/anthropic-sdk-python)

---

## 🆘 Troubleshooting

**Server won't start**:
- Check `.env` file has valid `ANTHROPIC_API_KEY`
- Ensure port 8000 is available
- Check logs in console output

**Frontend can't connect**:
- Verify server is running on correct port
- Check CORS settings in `server.py`
- Confirm `.env.local` in frontend has correct URLs

**Code execution fails**:
- Ensure Qiskit is installed: `pip install qiskit qiskit-aer`
- Check if code contains restricted operations
- Review logs for detailed error messages

**High costs**:
- Check if FOLLOWER mode is activating (metadata.cached field)
- Reduce `LLMOS_BUDGET_USD` to enforce stricter limits
- Review `/stats` endpoint to monitor spending

---

**Made with ❤️ by Evolving Agents Labs**

**Star ⭐ the repo if this helped you understand LLM OS architecture!**
