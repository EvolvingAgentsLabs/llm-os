# Advanced Tool Use Implementation Plan

## Executive Summary

This document outlines the integration of Anthropic's new **Advanced Tool Use** features (announced Nov 24, 2025) into LLM OS. The key insight is that these features are **complementary** to our existing architecture, not replacements.

**Two Distinct Layers:**
1. **Learning/Evolution Layer** (existing) - Understands execution history, learns patterns, decides what to do
2. **Execution Efficiency Layer** (new) - Once we know what to do, execute it efficiently

```
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 1: LEARNING / EVOLUTION                      │
│              (LLM OS's TraceManager & Mode Strategies)          │
│                                                                 │
│  Purpose: INTELLIGENCE & ADAPTATION                             │
│  - Analyzes execution history (traces)                          │
│  - Learns which patterns work best for which scenarios          │
│  - Evolves system by tracking success/failure rates             │
│  - Semantic matching to find relevant past experiences          │
│  - Decides: "What's the BEST approach for this scenario?"       │
│                                                                 │
│  Components: TraceManager, ExecutionTrace, ModeSelectionStrategy│
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Decision: "Use Pattern X"
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 2: EXECUTION EFFICIENCY                      │
│              (Anthropic's Advanced Tool Use Features)           │
│                                                                 │
│  Purpose: EFFICIENT EXECUTION                                   │
│  - Once we know WHAT to do, do it with minimal tokens/cost      │
│  - PTC: Execute tool sequences outside context window           │
│  - Tool Search: Load only needed tools on-demand                │
│  - Tool Examples: Help LLM use tools correctly first time       │
│  - Question: "How to execute this pattern CHEAPLY?"             │
│                                                                 │
│  Components: PTC Container, Tool Search Engine, Tool Examples   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Current LLM OS Architecture

### The Learning Layer (Preserved & Enhanced)

| Component | Purpose | Status |
|-----------|---------|--------|
| **TraceManager** | Store & retrieve execution patterns | Keep - adds learning |
| **ExecutionTrace** | Record of successful executions | Keep - enables evolution |
| **ModeSelectionStrategy** | Decide best approach for scenario | Keep - the brain |
| **Semantic Matching** | Find similar past experiences | Keep - enables generalization |

### Execution Modes (Enhanced with PTC)

| Mode | Cost | Learning Layer Decision | Execution Layer |
|------|------|------------------------|-----------------|
| **CRYSTALLIZED** | $0.00 | "We've done this exact thing many times" | → PTC (code execution) |
| **FOLLOWER** | ~$0.00 | "We've seen something very similar" | → PTC (tool replay) |
| **MIXED** | ~$0.25 | "We've seen something related" | → Tool Examples + LLM |
| **LEARNER** | ~$0.50 | "This is novel, need to learn" | → Tool Search + Full LLM |
| **ORCHESTRATOR** | Variable | "This needs multiple agents" | → Tool Search + Multi-agent |

### Key Files
- `llmos/kernel/mode_strategies.py` - Strategy pattern for mode selection
- `llmos/memory/traces_sdk.py` - Trace storage and semantic matching
- `llmos/interfaces/dispatcher.py` - Mode routing and execution
- `llmos/interfaces/sdk_client.py` - Claude SDK integration
- `llmos/kernel/component_registry.py` - Agent/tool registry

---

## Anthropic's Advanced Tool Use Features (Nov 2025)

### 1. Programmatic Tool Calling (PTC)
**The Game Changer for FOLLOWER Mode**

```python
# NEW: Tools can be called from code execution
tool_definition = {
    "name": "write_file",
    "allowed_callers": ["code_execution_20250825"],  # KEY FIELD
    "input_schema": {...}
}
```

**Benefits:**
- Tool results stay OUT of context window
- 85%+ token reduction in tests
- Perfect for repetitive tool sequences (our FOLLOWER use case)

### 2. Tool Search Tool
**On-Demand Tool Discovery**

```python
# NEW: Tools can be deferred until needed
tool_definition = {
    "name": "rare_tool",
    "defer_loading": true,  # KEY FIELD
    "input_schema": {...}
}
```

**Benefits:**
- Start with minimal tools (save context)
- Claude searches for tools when needed
- 85-90% context reduction for large toolsets

### 3. Tool Use Examples
**Better Tool Usage via Examples**

```python
# NEW: Show Claude how to use tools correctly
tool_definition = {
    "name": "complex_tool",
    "input_examples": [  # KEY FIELD
        {
            "description": "Example: Create a user",
            "arguments": {"name": "John", "role": "admin"}
        }
    ]
}
```

**Benefits:**
- Better tool usage patterns
- Fewer errors in tool calls
- Useful for complex tools

---

## Feature Mapping: Complementary Integration

### The Key Insight: Two Different Problems

| Problem | LLM OS Solution | Anthropic Solution | Relationship |
|---------|-----------------|-------------------|--------------|
| "What pattern to use?" | TraceManager + Mode Strategies | N/A | **LLM OS only** |
| "Execute pattern efficiently" | FOLLOWER mode replay | PTC | **Complementary** |
| "Find right tools" | ComponentRegistry | Tool Search | **Complementary** |
| "Use tools correctly" | Trace examples | Tool Examples | **Complementary** |

### Integration Strategy

```
                     LEARNING LAYER (LLM OS - Keep)
                     =============================
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   TraceManager         Mode Strategy        Semantic Match
   (history)            (decisions)          (generalization)
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                     Decision Made: Mode X
                              │
                              ▼
                   EXECUTION LAYER (Anthropic - Add)
                   ==================================
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
      PTC               Tool Search          Tool Examples
   (CRYSTALLIZED/       (LEARNER/            (All modes
    FOLLOWER)           ORCHESTRATOR)         need help)
```

### How They Work Together

1. **CRYSTALLIZED Mode Flow:**
   - Learning Layer: "We've seen this exact pattern 10+ times with 95% success"
   - Execution Layer: Use **PTC** to replay tool sequence in code container

2. **FOLLOWER Mode Flow:**
   - Learning Layer: "Very similar to trace X (92% confidence)"
   - Execution Layer: Use **PTC** to replay trace X's tool sequence

3. **MIXED Mode Flow:**
   - Learning Layer: "Related to trace X (78% confidence), need some adaptation"
   - Execution Layer: Use **Tool Examples** from trace X to guide LLM

4. **LEARNER Mode Flow:**
   - Learning Layer: "Novel scenario, no relevant traces"
   - Execution Layer: Use **Tool Search** to discover needed tools on-demand

5. **ORCHESTRATOR Mode Flow:**
   - Learning Layer: "Complex task requiring multiple agents"
   - Execution Layer: Use **Tool Search** for each agent's tool discovery

---

## Implementation Plan

### Phase 1: PTC Integration (Priority: HIGH)
**Upgrade CRYSTALLIZED and FOLLOWER modes**

#### 1.1 Add PTC Support to SDK Client
```python
# llmos/interfaces/sdk_client.py

class LLMOSSDKClient:
    def __init__(self, ...):
        # NEW: Beta header for PTC
        self.beta_headers = {
            "advanced-tool-use-2025-11-20": True
        }

    async def execute_ptc_mode(
        self,
        tool_sequence: List[Dict],  # From trace
        container_id: str = None
    ) -> Dict[str, Any]:
        """Execute tool sequence in code execution container"""
        # Tools called from code, results don't hit context
        pass
```

#### 1.2 New PTC Mode Strategy
```python
# llmos/kernel/mode_strategies.py

class PTCModeStrategy(ModeSelectionStrategy):
    """
    Programmatic Tool Calling mode selection

    Uses code execution for trace replay, dramatically reducing tokens.
    """

    async def determine_mode(self, context: ModeContext) -> ModeDecision:
        trace, confidence = await self._find_trace(context)

        if trace and trace.tools_used:
            # CAN we use PTC? (tools support it)
            if self._tools_support_ptc(trace.tools_used):
                return ModeDecision(
                    mode="PTC",
                    confidence=confidence,
                    trace=trace,
                    reasoning="Trace available, executing via PTC (zero-context replay)"
                )

        # Fall back to existing logic
        return await super().determine_mode(context)
```

#### 1.3 PTC Dispatcher Method
```python
# llmos/interfaces/dispatcher.py

async def _dispatch_ptc(self, goal: str, trace: ExecutionTrace) -> Dict[str, Any]:
    """
    Dispatch to PTC mode (tool sequence replay in code execution)

    This is the OFFICIAL Anthropic way to do FOLLOWER mode.
    Tool results don't hit context window = massive token savings.
    """
    # Generate Python code from trace's tool sequence
    code = self._trace_to_python_code(trace)

    # Execute in container with allowed_callers
    result = await self.sdk_client.execute_ptc_mode(
        code=code,
        tools=trace.tools_used,
        container_id=self._get_or_create_container()
    )

    return {
        "success": result["success"],
        "mode": "PTC",
        "cost": 0.0,  # Tool results didn't hit context
        "trace": trace
    }
```

### Phase 2: Tool Search Integration (Priority: MEDIUM)
**Upgrade ComponentRegistry for on-demand tool discovery**

#### 2.1 Deferred Tool Loading
```python
# llmos/kernel/component_registry.py

@dataclass
class ToolSpec:
    name: str
    description: str
    category: str
    defer_loading: bool = True  # NEW: Default to deferred
    embedding: Optional[List[float]] = None  # NEW: For semantic search
```

#### 2.2 Tool Search Implementation
```python
# llmos/kernel/tool_search.py (NEW FILE)

class ToolSearchEngine:
    """
    Implements Anthropic's Tool Search pattern with embeddings

    Uses sentence-transformers for semantic search over tools.
    """

    def __init__(self, registry: ComponentRegistry):
        self.registry = registry
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self._build_tool_index()

    def search_tools(self, query: str, top_k: int = 5) -> List[ToolReference]:
        """Search for relevant tools using embeddings"""
        query_embedding = self.embedder.encode(query)

        # Cosine similarity search
        scores = []
        for tool in self.registry.tools.values():
            if tool.embedding:
                score = cosine_similarity(query_embedding, tool.embedding)
                scores.append((score, tool))

        # Return top-k as tool_references
        return [
            ToolReference(name=t.name, description=t.description)
            for _, t in sorted(scores, reverse=True)[:top_k]
        ]
```

#### 2.3 SDK Client Tool Loading
```python
# llmos/interfaces/sdk_client.py

def _build_agent_options(self, ...):
    # Only load non-deferred tools upfront
    immediate_tools = [
        t for t in self.registry.tools.values()
        if not t.defer_loading
    ]

    # Register tool search tool for deferred discovery
    tool_search_tool = {
        "name": "search_tools",
        "description": "Search for tools by description",
        "input_schema": {...}
    }

    return ClaudeAgentOptions(
        tools=[*immediate_tools, tool_search_tool],
        ...
    )
```

### Phase 3: Tool Use Examples (Priority: LOW)
**Auto-generate examples from successful traces**

#### 3.1 Example Generation from Traces
```python
# llmos/memory/traces_sdk.py

class TraceManager:
    def generate_tool_examples(self, tool_name: str) -> List[Dict]:
        """
        Generate input_examples for a tool from successful traces

        Uses traces where this tool was used successfully as example data.
        """
        examples = []

        for trace in self.list_traces():
            if trace.success_rating >= 0.9 and tool_name in (trace.tools_used or []):
                # Extract the tool call from trace output
                example = self._extract_tool_call_example(trace, tool_name)
                if example:
                    examples.append({
                        "description": f"Successful use in: {trace.goal_text[:50]}",
                        "arguments": example
                    })

        return examples[:3]  # Max 3 examples
```

#### 3.2 Enhanced Tool Registration
```python
# llmos/kernel/component_registry.py

@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: Dict[str, Any]
    input_examples: List[Dict] = None  # NEW: Auto-generated examples

    def to_api_format(self, trace_manager: TraceManager) -> Dict:
        """Convert to Anthropic API format with examples"""
        tool_dict = {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }

        # Auto-add examples from traces
        if trace_manager:
            examples = trace_manager.generate_tool_examples(self.name)
            if examples:
                tool_dict["input_examples"] = examples

        return tool_dict
```

---

## Migration Strategy

### Step 1: Add Beta Headers (Day 1)
- Update `sdk_client.py` to include beta header
- No behavior change, just enables the features

### Step 2: PTC Mode (Week 1)
- Add `PTCModeStrategy` to mode_strategies.py
- Add `_dispatch_ptc` to dispatcher.py
- Add container management for code execution
- Update traces to store tool call arguments

### Step 3: Tool Search (Week 2)
- Create `tool_search.py` with embedding support
- Update `ComponentRegistry` with `defer_loading` field
- Update SDK client to load tools on-demand
- Add embeddings to existing tools

### Step 4: Tool Examples (Week 3)
- Add `generate_tool_examples` to TraceManager
- Update tool registration to include examples
- Optional: Manual curation of critical tool examples

---

## Expected Impact

### Token Reduction
| Mode | Before | After (with PTC) | Savings |
|------|--------|------------------|---------|
| FOLLOWER | ~500 tokens | ~50 tokens | 90% |
| MIXED | ~2000 tokens | ~200 tokens | 90% |
| Tool Search | N/A | Deferred | 85-90% |

### Cost Reduction
| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| 1000 FOLLOWER executions | ~$0.00 | ~$0.00 | Same (already free) |
| 1000 MIXED executions | ~$250 | ~$25 | 90% |
| Large toolset (100 tools) | 100 tools in context | 5-10 on-demand | 90%+ |

### Architecture Improvement
- **Official Support**: Using Anthropic's official patterns instead of custom hacks
- **Future-Proof**: Beta features will become stable
- **Better Integration**: Native Claude features vs. workarounds

---

## Code Changes Summary (IMPLEMENTED)

### New Files
- `llmos/execution/__init__.py` - Execution Layer module
- `llmos/execution/ptc.py` - PTCExecutor, PTCContainer, ToolSequence, ToolCall
- `llmos/execution/tool_search.py` - ToolSearchEngine, ToolDefinition, ToolReference
- `llmos/execution/tool_examples.py` - ToolExampleGenerator, TraceToolCallRecorder

### Modified Files
- `llmos/kernel/config.py` - Added ExecutionLayerConfig with all settings
- `llmos/interfaces/dispatcher.py` - Integrated Execution Layer, added PTC to FOLLOWER mode
- `llmos/interfaces/sdk_client.py` - TraceBuilder now captures full tool_calls for PTC
- `llmos/memory/traces_sdk.py` - ExecutionTrace now stores tool_calls for PTC replay

### Configuration (ExecutionLayerConfig)
```python
@dataclass
class ExecutionLayerConfig:
    # Beta feature flag
    enable_advanced_tool_use: bool = True
    beta_header: str = "advanced-tool-use-2025-11-20"

    # PTC (Programmatic Tool Calling) settings
    enable_ptc: bool = True
    ptc_container_timeout_secs: float = 120.0
    ptc_max_containers: int = 5

    # Tool Search settings
    enable_tool_search: bool = True
    tool_search_use_embeddings: bool = False
    tool_search_embedding_model: str = "all-MiniLM-L6-v2"
    tool_search_top_k: int = 5
    defer_tools_by_default: bool = True

    # Tool Examples settings
    enable_tool_examples: bool = True
    tool_examples_min_success_rate: float = 0.9
    tool_examples_max_per_tool: int = 3
    tool_examples_cache_ttl_secs: float = 300.0
```

### Presets Updated
- `LLMOSConfig.development()` - Execution layer enabled without embeddings
- `LLMOSConfig.production()` - Full execution layer with embeddings
- `LLMOSConfig.testing()` - Execution layer disabled for deterministic tests

---

## Conclusion

Anthropic's Advanced Tool Use features are **complementary** to LLM OS's existing architecture:

### What We Keep (Learning/Evolution Layer)
- **TraceManager**: Still the brain that remembers execution history
- **ExecutionTrace**: Still the record that enables learning
- **ModeSelectionStrategy**: Still decides the best approach
- **Semantic Matching**: Still enables generalization from past experiences

### What We Add (Execution Efficiency Layer)
- **PTC**: Makes CRYSTALLIZED/FOLLOWER execution nearly free (tool results outside context)
- **Tool Search**: Makes LEARNER/ORCHESTRATOR more efficient (on-demand tool loading)
- **Tool Examples**: Makes all modes more reliable (traces become examples)

### The Analogy

Think of it like a skilled craftsman:
- **Learning Layer** = The craftsman's **experience and judgment** (which technique to use?)
- **Execution Layer** = The craftsman's **efficient tools** (how to execute that technique quickly?)

You need both. Experience without efficient tools is slow. Efficient tools without experience is error-prone.

### Summary

| Layer | Purpose | LLM OS Component | Anthropic Feature |
|-------|---------|------------------|-------------------|
| Learning | What to do | TraceManager, Strategies | N/A |
| Execution | How to do it cheaply | Mode dispatch | PTC, Tool Search, Examples |

This is exactly the "JIT optimization" / "caching" pattern discussed in the team meeting:
- **Learning Layer** = The "what to cache" intelligence
- **Execution Layer** = The "cached execution" efficiency

Anthropic has provided the official execution efficiency layer - we provide the learning intelligence on top.

## References

- [Anthropic Advanced Tool Use Announcement](https://www.anthropic.com/news/advanced-tool-use)
- [Tool Search Cookbook](https://github.com/anthropics/anthropic-cookbook/tree/main/misc/tool_search_tool)
- [Programmatic Tool Calling Cookbook](https://github.com/anthropics/anthropic-cookbook/tree/main/misc/programmatic_tool_calling)
