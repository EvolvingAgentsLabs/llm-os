# Nested Learning Implementation in LLMOS

## Overview

LLMOS now implements **Nested Learning** concepts using LLM-based semantic trace matching instead of traditional embeddings. This provides "soft" associative memory that understands semantic equivalence, not just exact text matching.

## Key Concepts

### From the Nested Learning Paper

The paper describes learning as acquiring effective memory through nested optimization loops:
- **Outer loop (slow):** High-level reasoning and pattern discovery
- **Inner loop (fast):** Rapid execution using compressed associations

### LLMOS Implementation

LLMOS implements this through execution modes:

| Paper Concept | LLMOS Implementation |
|---------------|---------------------|
| Slow optimization | **LEARNER** mode - LLM reasoning ($0.50 cost) |
| Fast execution | **FOLLOWER** mode - Trace replay ($0 cost) |
| Associative memory | **TraceManager** with LLM-based matching |
| Online consolidation | Immediate trace storage after execution |
| Memory compression | Traces store tool sequences, not full context |

## Architecture

### 1. TraceAnalyzer (New)

**File:** `llmos/memory/trace_analyzer.py`

Uses Claude Agent SDK to perform semantic analysis of goal-to-trace matching.

**Key Methods:**
- `analyze_goal_similarity(goal, trace_goal, metadata)` → confidence score (0-1)
- `find_best_matching_trace(goal, traces, min_confidence)` → best match
- `batch_analyze_traces(goal, traces, top_k)` → multiple matches

**Confidence Scoring:**
```
0.95-1.0:  Virtually identical (minor wording differences only)
0.85-0.95: Same core task, slight parameter differences
0.70-0.85: Related tasks, similar approach beneficial
0.50-0.70: Loosely related, different execution needed
0.0-0.50:  Unrelated tasks
```

### 2. Enhanced TraceManager

**File:** `llmos/memory/traces_sdk.py`

**New Methods:**
- `find_trace_with_llm(goal, min_confidence)` → (trace, confidence)
- `find_trace_smart(goal)` → (trace, confidence, recommended_mode)

**Behavior:**
1. Try LLM-based semantic matching first
2. Fallback to hash-based matching if LLM unavailable
3. Return confidence score for intelligent mode selection

### 3. Enhanced Dispatcher

**File:** `llmos/interfaces/dispatcher.py`

**Three Execution Modes Based on Confidence:**

#### High Confidence (≥0.92): FOLLOWER Mode
- Direct trace replay
- $0 cost (no LLM calls)
- Fast execution
- Use when: Goal matches existing trace almost exactly

#### Medium Confidence (0.75-0.92): MIXED Mode ✨ **NEW**
- Uses trace as few-shot guidance for LLM
- ~$0.25 cost (cheaper than LEARNER)
- Adaptive to variations
- Use when: Goal is similar but not identical

#### Low Confidence (<0.75): LEARNER Mode
- Full LLM reasoning
- ~$0.50 cost
- Creative problem-solving
- Use when: Novel task, no similar traces

#### Complex: ORCHESTRATOR Mode
- Multi-agent coordination
- Variable cost
- Use when: Multiple tasks, coordination needed

## Examples

### Example 1: High Confidence Match

**Previous Goal:** "Create a Python file called utils.py"
**Current Goal:** "Create a Python file named helpers.py"
**Confidence:** 0.95
**Mode:** FOLLOWER
**Reasoning:** Same action (create Python file), only filename differs

### Example 2: Medium Confidence Match

**Previous Goal:** "List all files in the project"
**Current Goal:** "Show me all Python files in the project"
**Confidence:** 0.82
**Mode:** MIXED
**Reasoning:** Similar intent (list files), but with filtering requirement. Trace provides structure, LLM adapts for filter.

### Example 3: Low Confidence (New Task)

**Previous Goal:** "Create a Python file"
**Current Goal:** "Analyze the performance metrics of the API"
**Confidence:** 0.15
**Mode:** LEARNER
**Reasoning:** Completely different tasks. No trace match useful.

## Benefits Over Hash-Based Matching

### Hash-Based (Old)
```python
# "create a file" → hash: a1b2c3d4
# "create file"   → hash: e5f6g7h8
# Result: No match ❌
```

### LLM-Based (New)
```python
# "create a file" vs "create file"
# Analysis: Semantically identical
# Confidence: 0.98
# Result: FOLLOWER mode ✅
```

## Integration with Nested Learning Theory

### 1. Associative Memory (M: K → V)

**Paper:** Memory maps keys to values via learned associations

**LLMOS:**
- **Keys (K):** Goal semantic embedding (via LLM analysis)
- **Values (V):** Tool execution sequences (traces)
- **Mapping:** Confidence-scored similarity, not exact hash

### 2. Update Frequencies (f_slow, f_fast)

**Paper:** Different learning rates for different time scales

**LLMOS:**
- **f_slow (LEARNER):** Full LLM reasoning, creates new traces
- **f_medium (MIXED):** Guided by trace, adapted by LLM
- **f_fast (FOLLOWER):** Direct trace replay, no learning

### 3. Online Consolidation

**Paper:** Rapidly stabilize memory during task execution

**LLMOS:** Every LEARNER execution immediately creates a trace file, consolidating the "memory" to disk for future reuse

### 4. Continuum Memory System

**Paper:** Memory should operate on a continuum, not binary

**LLMOS:** Three modes (FOLLOWER/MIXED/LEARNER) create a continuum based on confidence scores, not a binary Learner/Follower choice

## Cost Optimization

| Mode | Cost | When Used | Example |
|------|------|-----------|---------|
| FOLLOWER | $0.00 | Confidence ≥ 0.92 | "List files" → "List files" |
| MIXED | $0.25 | 0.75 ≤ Confidence < 0.92 | "List files" → "List Python files" |
| LEARNER | $0.50 | Confidence < 0.75 | Novel task |
| ORCHESTRATOR | Variable | Complex multi-step | Research + Analysis + Report |

**Savings Example:**
- Old system: 100 similar tasks × $0.50 = **$50**
- New system: 1 LEARNER ($0.50) + 99 FOLLOWER ($0) = **$0.50**
- **Savings: 99%**

With MIXED mode:
- 1 LEARNER ($0.50) + 30 MIXED ($7.50) + 69 FOLLOWER ($0) = **$8.00**
- Still **84% savings** while handling variations!

## Configuration

### Enable/Disable LLM Matching

```python
# Enable LLM matching (default)
trace_manager = TraceManager(
    memories_dir=workspace / "memories",
    workspace=workspace,
    enable_llm_matching=True
)

# Disable (fallback to hash matching only)
trace_manager = TraceManager(
    memories_dir=workspace / "memories",
    workspace=workspace,
    enable_llm_matching=False
)
```

### Adjust Confidence Thresholds

In `llmos/memory/trace_analyzer.py`:

```python
def _determine_mode(self, confidence: float) -> str:
    if confidence >= 0.92:  # Adjust for stricter FOLLOWER
        return "FOLLOWER"
    elif confidence >= 0.75:  # Adjust for wider MIXED range
        return "MIXED"
    else:
        return "LEARNER"
```

## Future Enhancements

### 1. Self-Modifying Kernel (HOPE Implementation)
Allow LLMOS to write its own Python plugins (not just traces) based on frequent patterns.

### 2. Sleep Mode (Offline Consolidation)
- Scheduled task to analyze traces during idle time
- Merge similar traces into generalized patterns
- Delete low-confidence/unused traces (forgetting)

### 3. Dynamic Update Frequency
Automatically adjust confidence thresholds based on execution success rates.

### 4. Multi-Trace Blending
For complex tasks, blend insights from multiple similar traces rather than using just the best match.

## Testing

See `examples/test_nested_learning.py` for integration tests.

## References

- **Nested Learning Paper:** [Link to paper when available]
- **Claude Agent SDK:** https://github.com/anthropics/claude-agent-sdk
- **LLMOS Documentation:** `/docs/`

## Summary

LLMOS now implements the "Illusion of Depth" concept from Nested Learning:

Instead of a single deep LLM context window, we create **nested loops**:
1. **LLM (Cognitive):** Slow, expensive, creative
2. **Traces (Somatic):** Fast, free, deterministic
3. **Semantic Matching:** Soft associations, not brittle hashes

This creates an **economical**, **scalable**, and **adaptive** system that learns from experience while maintaining budget control.
