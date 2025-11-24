# Qiskit Studio Backend - Quick Start Guide

## ✅ Status: Ready to Use!

All issues have been fixed and the implementation is fully functional.

---

## Prerequisites

- Python 3.10+
- Anthropic API key (for Claude)
- (Optional) IBM Quantum API token for real quantum hardware

---

## Installation

### 1. Navigate to the project directory
```bash
cd /Users/agustinazwiener/evolving-agents-labs/llm-os/examples/qiskit_studio_backend
```

### 2. Create and configure environment file
```bash
cp .env.template .env
```

Edit `.env` and add your API key:
```bash
ANTHROPIC_API_KEY=your-api-key-here
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

Or if you want to install in a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Running the Backend

### Method 1: Using the run script (recommended)
```bash
chmod +x run.sh  # Make executable (first time only)
./run.sh
```

### Method 2: Direct Python execution
```bash
python server.py
```

### Method 3: With custom settings
```bash
python server.py --port 8000 --host 0.0.0.0
```

The server will start on `http://localhost:8000`

---

## Testing the Implementation

### 1. Run the demo suite
```bash
# In a new terminal (while server is running)
python demo.py
```

This will run 5 demonstrations:
1. Code generation via chat
2. Direct code execution
3. Learner → Follower cost savings
4. Security hooks
5. Backend statistics

### 2. Test individual endpoints

**Health check:**
```bash
curl http://localhost:8000/
```

**Chat endpoint (code generation):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Create a Bell state"}
    ]
  }'
```

**Run endpoint (code execution):**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "input_value": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0,1)\nprint(qc)"
  }'
```

**Statistics endpoint:**
```bash
curl http://localhost:8000/stats | jq
```

---

## Connecting to Qiskit Studio Frontend

### 1. Navigate to the frontend directory
```bash
cd /Users/agustinazwiener/evolving-agents-labs/qiskit-studio
```

### 2. Install frontend dependencies (first time only)
```bash
npm install
```

### 3. Configure frontend to use LLM OS backend
```bash
cp .env.local.template .env.local
```

Edit `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/chat
NEXT_PUBLIC_PARAMETER_UPDATE_API_URL=http://127.0.0.1:8000/chat
NEXT_PUBLIC_RUNCODE_URL=http://127.0.0.1:8000/run
```

### 4. Start the frontend
```bash
npm run dev
```

### 5. Open in browser
```
http://localhost:3000
```

---

## What Was Fixed

### 1. Path Resolution Issues ✅
- Fixed hardcoded path traversal in all Python files
- Now works regardless of execution context

### 2. Dependencies ✅
- Uncommented required packages in requirements.txt
- Added httpx for demo script

### 3. Circular Import ✅
- Fixed circular import in plugins/__init__.py
- Changed import to use `llmos.plugins` directly

### 4. Module Exports ✅
- Added proper __all__ exports in plugins/__init__.py

---

## Verification Checklist

Run these commands to verify everything is working:

```bash
# 1. Test Python syntax
python -m py_compile server.py agents/*.py plugins/*.py config.py demo.py
# Expected: No errors

# 2. Test config import
python -c "import config; print('✓ Config OK')"
# Expected: ✓ Config OK

# 3. Start server
./run.sh &
# Wait 5 seconds for startup

# 4. Test health endpoint
curl http://localhost:8000/
# Expected: {"status":"healthy",...}

# 5. Run demos
python demo.py
# Expected: All demos pass

# 6. Stop server
pkill -f "python server.py"
```

---

## Architecture Overview

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
│  │  • Analyzes intent                                   │  │
│  │  • Routes: LEARNER / FOLLOWER / ORCHESTRATOR         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────┐          ┌──────────────────┐       │
│  │ Quantum Architect│          │  Quantum Tutor   │       │
│  │ (Code Generator) │          │  (Q&A Expert)    │       │
│  └──────────────────┘          └──────────────────┘       │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Qiskit Tools (Somatic Layer)               │  │
│  │  • execute_qiskit_code (with security)               │  │
│  │  • validate_qiskit_code                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 🎯 Drop-in Replacement
- Same API endpoints as original Qiskit Studio
- No frontend changes required
- Compatible with existing workflows

### 💰 Cost Optimization
- Learner mode: First request (learns pattern)
- Follower mode: Subsequent requests (FREE!)
- Budget tracking and enforcement

### 🔒 Enhanced Security
- Multi-layer validation
- Restricted execution environment
- Dangerous import blocking

### 🧠 Unified Memory
- L4 semantic memory integration
- Cross-project learning
- High-confidence pattern caching

### ⚡ Simplified Architecture
- Single process vs. 3 microservices
- One port (8000) vs. multiple
- Easier deployment and debugging

---

## Troubleshooting

### Server won't start
```bash
# Check if ANTHROPIC_API_KEY is set
cat .env | grep ANTHROPIC_API_KEY

# Check if port 8000 is available
lsof -i :8000

# Check logs
python server.py
```

### Import errors
```bash
# Ensure you're in the correct directory
pwd
# Should be: .../llm-os/examples/qiskit_studio_backend

# Check if llmos module is accessible
python -c "import sys; sys.path.insert(0, '../..'); import llmos; print('OK')"
```

### Demo fails
```bash
# Ensure server is running
curl http://localhost:8000/

# Check dependencies
pip install -r requirements.txt

# Run with verbose output
python demo.py
```

### Frontend can't connect
```bash
# 1. Check backend is running
curl http://localhost:8000/

# 2. Check .env.local in frontend
cat ../../../qiskit-studio/.env.local

# 3. Check browser console for CORS errors

# 4. Verify ports
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
```

---

## Next Steps

1. **Explore the API**: Try different quantum circuits and algorithms
2. **Monitor costs**: Check `/stats` endpoint to see savings
3. **Test security**: Try malicious code to see it blocked
4. **Frontend integration**: Connect the visual circuit builder
5. **Customize agents**: Modify agent prompts for your use case

---

## Documentation

- [README.md](README.md) - Comprehensive documentation
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation details
- [ANALYSIS_AND_FIXES.md](ANALYSIS_AND_FIXES.md) - Analysis and fixes applied

---

## Support

For issues or questions:
1. Check [ANALYSIS_AND_FIXES.md](ANALYSIS_AND_FIXES.md) for known issues
2. Review server logs for error messages
3. Test individual components using the verification checklist above

---

**Status**: ✅ Ready for production use (with recommended enhancements)

**Last Updated**: 2025-11-23
