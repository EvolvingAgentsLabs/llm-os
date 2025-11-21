# Testing Instructions for Demo App

## ✅ Your API Key is Already Configured

Your Claude API key has been securely set up in `.env` file and is **excluded from git commits**.

---

## Quick Test (2 minutes)

### 1. Install Dependencies

```bash
cd demo-app
pip install -r requirements.txt
```

This will install:
- `claude-agent-sdk` - Claude integration
- `rich` - Beautiful terminal output
- `python-dotenv` - Load .env files
- Other dependencies

### 2. Verify API Key is Loaded

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key loaded:', 'Yes' if os.getenv('ANTHROPIC_API_KEY') else 'No')"
```

Expected output:
```
API Key loaded: Yes
```

### 3. Run the Demo App

```bash
python demo_main.py
```

You should see:
```
╔══════════════════════════════════════════════════════════════╗
║    LLM OS - Demo Application (Phase 2.5)                     ║
║    Comprehensive showcase of llmos capabilities              ║
╚══════════════════════════════════════════════════════════════╝

Three Execution Modes: Learner | Follower | Orchestrator
Features: Multi-Agent, Projects, Memory, Hooks, Streaming
Budget: $20.00

Select a demo scenario:
...
```

---

## Recommended Test Sequence

### Test 1: Code Generation (Shows Cost Savings) ⭐ **START HERE**

This is the **best first demo** - it clearly shows the Learner → Follower pattern:

```bash
# Option 1: Interactive mode
python demo_main.py
# Then select: 2

# Option 2: Direct command
python demo_main.py --scenario code-generation
```

**What to expect**:
- First run: ~$0.50 (Learner mode - learns the pattern)
- Second run: $0.00 (Follower mode - replays for FREE)
- **100% savings demonstrated!**

**Duration**: ~30 seconds

**Status**: ✅ Fully working as expected

---

### Test 2: Cost Optimization Demo (Dramatic Savings)

Shows savings over 5 repeated executions:

```bash
python demo_main.py --scenario cost-optimization
```

**What to expect**:
- Runs same task 5 times
- First run: ~$0.50 (Learner)
- Runs 2-5: $0.00 (Follower)
- Shows ~80% overall savings

**Duration**: ~1 minute

---

### Test 3: SDK Hooks Demo (Phase 2.5 Features)

Demonstrates automatic hook integration:

```bash
python demo_main.py --scenario hooks
```

**What to expect**:
- Shows all 5 hook types in action:
  - 🔒 Security Hook (blocks dangerous commands)
  - 💰 Budget Control Hook (prevents cost overruns)
  - 📝 Trace Capture Hook (records execution)
  - 💵 Cost Tracking Hook (monitors spending)
  - 🧠 Memory Injection Hook (provides context)

**Duration**: ~20 seconds

---

### Test 4: Research Assistant (Complex Orchestration)

Shows complex multi-step orchestration with research and writing:

```bash
python demo_main.py --scenario research
```

**⚠️ Known Issues**:
- Multiple timeout warnings (300s per delegation) - **This is expected**
- Some delegations may not complete fully
- WebSearch tool may not be available in delegated agents
- Execution may take 10-16 minutes instead of expected 3 minutes
- May show "Success" even with partial completion (2/6 steps)

**What to expect**:
- Creates research and technical-writer agents
- Attempts multi-step research workflow
- Cost: ~$0.30-0.50 (lower than expected $2.50 due to timeouts)
- Some research documents may still be generated in workspace

**Duration**: 10-16 minutes (with timeouts)

**Status**: ⚠️ Partially working - demonstrates multi-agent setup but has delegation timeout issues

**Recommendation**: Try the Data Pipeline scenario instead for a better multi-agent demo.

---

### Test 5: Data Pipeline (Multi-Agent Orchestration)

Shows complex multi-agent coordination:

```bash
python demo_main.py --scenario data-pipeline
```

**What to expect**:
- Creates 3 specialized agents dynamically
- Orchestrates them to work together
- Demonstrates project management
- Cost: ~$1.50

**Duration**: ~2 minutes

**Status**: ✅ Recommended for multi-agent demonstration

---

## Full Test Suite

Run all scenarios:

```bash
python demo_main.py --all
```

**What to expect**:
- Runs all 7 scenarios sequentially
- Total cost: ~$5-8
- Duration: ~10 minutes
- Shows comprehensive cost report at end

---

## Verifying Everything Works

### Check 1: API Key is Secure

```bash
# This should show your .env file is NOT tracked
git status

# This should confirm .env is ignored
git check-ignore .env
# Expected output: .env
```

### Check 2: Environment Loading

```bash
# Check if dotenv is installed
pip show python-dotenv

# Verify API key loads
python -c "from dotenv import load_dotenv; import os; load_dotenv(); key = os.getenv('ANTHROPIC_API_KEY'); print(f'Key found: {len(key)} characters') if key else print('No key')"
```

Expected output:
```
Key found: 108 characters
```

### Check 3: Demo App Boots

```bash
python demo_main.py --help
```

Should show:
```
usage: demo_main.py [-h] [--budget BUDGET] [--verbose] [--scenario SCENARIO] [--all]

LLM OS Demo Application

options:
  -h, --help           show this help message and exit
  --budget BUDGET      Budget in USD
  --verbose            Enable verbose output
  --scenario SCENARIO  Run specific scenario
  --all               Run all scenarios
```

---

## Command Line Options

### Set Custom Budget

```bash
python demo_main.py --budget 50.0
```

### Enable Verbose Output

```bash
python demo_main.py --verbose
```

### Run Specific Scenarios

```bash
# Code generation (best first demo)
python demo_main.py --scenario code-generation

# Cost optimization
python demo_main.py --scenario cost-optimization

# SDK hooks
python demo_main.py --scenario hooks

# Data pipeline
python demo_main.py --scenario data-pipeline

# DevOps automation
python demo_main.py --scenario devops

# Research assistant
python demo_main.py --scenario research

# Cross-project learning
python demo_main.py --scenario cross-project
```

---

## Understanding the Output

### Successful Execution

```
╔══════════════════════════════════════════════════════════════╗
║ 📊 Code Generation Results                                   ║
╠══════════════════════════════════════════════════════════════╣
║ ✅ Success                                                   ║
║                                                              ║
║ Mode: FOLLOWER                                               ║
║ Cost: $0.0000                                                ║
║ Steps: 3/3                                                   ║
║ Time: 0.5s                                                   ║
╚══════════════════════════════════════════════════════════════╝
```

**What this means**:
- ✅ = Execution succeeded
- FOLLOWER = Used free trace replay (no LLM needed)
- $0.0000 = Zero cost
- 3/3 = All steps completed
- 0.5s = Near-instant execution

### Cost Summary

After running scenarios:

```
╔══════════════════════════════════════════════════════════════╗
║ Cost Summary                                                 ║
╠══════════════════════════════════════════════════════════════╣
║ Scenario                    Cost                             ║
║ ────────────────────────────────────────────────────────     ║
║ Code Generation             $0.5000                          ║
║ Cost Optimization           $0.5000                          ║
║ Sdk Hooks                   $0.3000                          ║
║ ────────────────────────────────────────────────────────     ║
║ Total                       $1.3000                          ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Troubleshooting

### Problem: "ANTHROPIC_API_KEY not found"

**Solution**:
```bash
# Check .env file exists
ls -la .env

# Verify content
cat .env

# Should show:
# ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Problem: "Claude Agent SDK not installed"

**Solution**:
```bash
pip install claude-agent-sdk
```

### Problem: "python-dotenv not found"

**Solution**:
```bash
pip install python-dotenv
```

### Problem: "Low battery error"

**Solution**: Increase budget
```bash
python demo_main.py --budget 50.0
```

### Problem: "Permission denied"

**Solution**:
```bash
chmod +x demo_main.py
```

### Problem: Import errors

**Solution**: Make sure you're in the right directory
```bash
cd demo-app
python demo_main.py
```

### Problem: "Delegation timed out after 300.0s"

This is a **known issue** with the Research Assistant scenario (Scenario 3).

**What's happening**:
- The system delegates tasks to specialized agents
- Some delegations timeout after 300 seconds (5 minutes)
- This is expected behavior for the current implementation

**Solution**: This is not a critical error. The system will:
- Show timeout warnings in debug output
- Continue with remaining steps
- Generate partial research results
- Still mark as "Success" even with incomplete execution

**Workaround**:
- Use the Data Pipeline scenario instead for reliable multi-agent demonstration
- Check `workspace/projects/Project_research_demo/` for any generated research documents

### Problem: "No messages for 60s - stopping delegation"

This warning appears when a delegated agent takes too long to respond.

**Solution**: This is informational and part of the Research scenario's known issues. The system will:
- Automatically stop waiting after timeout
- Move to the next step
- Continue execution where possible

### Problem: WebSearch not working in delegated agents

**What's happening**: When agents are delegated through the orchestrator, some tools (like WebSearch) may not be available.

**Solution**: This is a current limitation of the multi-agent delegation system. The research scenario demonstrates the orchestration pattern, even though tool delegation has limitations.

**Status**: Under investigation for future Phase 2.6 improvements.

---

## Output Files

After running demos, check generated files:

```bash
# View output structure
ls -R output/

# Should show:
# output/
# ├── projects/
# ├── reports/
# └── traces/
```

### View Generated Reports

```bash
ls output/reports/
cat output/reports/cost_analysis.md
```

### View Execution Traces

```bash
ls ../llmos/workspace/memories/traces/
cat ../llmos/workspace/memories/traces/trace_*.md
```

---

## Expected Costs

| Test | Estimated Cost | Duration | Status |
|------|---------------|----------|--------|
| Code Generation | $0.50 | 30s | ✅ Working |
| Cost Optimization | $0.50 | 1min | ✅ Working |
| SDK Hooks | $0.30 | 20s | ✅ Working |
| Data Pipeline | $1.50 | 2min | ✅ Working |
| DevOps | $0.30 | 20s | ✅ Working |
| Research | $0.30-0.50 | 10-16min | ⚠️ Partial (timeouts) |
| Cross-Project | $0.00 | 10s | ✅ Working |
| **All Scenarios** | **$3-6** | **15-25min** | ⚠️ Research has issues |

**Note**: Costs may vary. First-time executions are more expensive (Learner mode). Repeated executions are cheaper or free (Follower mode).

**Important**: Research Assistant scenario has known timeout issues. The system will show multiple timeout warnings, which is expected behavior. Generated research documents can still be found in `workspace/projects/`.

---

## Quick Reference

### Most Important Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run interactive demo
python demo_main.py

# 3. Run best first demo (code generation)
python demo_main.py --scenario code-generation

# 4. Run all demos
python demo_main.py --all
```

### File Locations

- **API Key**: `.env` (git-ignored)
- **Demo App**: `demo_main.py`
- **Generated Output**: `output/`
- **Execution Traces**: `../llmos/workspace/memories/traces/`
- **Documentation**: `README.md`, `ANALYSIS.md`, `QUICKSTART.md`

---

## Security Check ✅

Your API key is secure:

1. ✅ Stored in `.env` file
2. ✅ `.env` is in `.gitignore`
3. ✅ Will NOT be committed to git
4. ✅ Loaded automatically by `python-dotenv`

Verify:
```bash
git status  # Should NOT show .env
git check-ignore .env  # Should output: .env
```

---

## Next Steps After Testing

1. **Read the docs**: `cat README.md`
2. **View detailed analysis**: `cat ANALYSIS.md`
3. **Check traces**: `ls ../llmos/workspace/memories/traces/`
4. **Try custom scenarios**: Modify `demo_main.py`
5. **Explore llmos**: `cd ../llmos && python boot.py interactive`

---

## Need Help?

1. **Quick Start Guide**: `cat QUICKSTART.md`
2. **Full README**: `cat README.md`
3. **Technical Analysis**: `cat ANALYSIS.md`
4. **llmos Documentation**: `cat ../llmos/README.md`

---

**You're all set!** Start with:

```bash
python demo_main.py --scenario code-generation
```

This will show you the core value proposition (Learner → Follower savings) in ~30 seconds.
