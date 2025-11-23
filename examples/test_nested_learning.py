#!/usr/bin/env python3
"""
Test Nested Learning Implementation
Demonstrates LLM-based semantic trace matching and MIXED mode execution

This test shows:
1. Creating initial traces (LEARNER mode)
2. Exact matching (FOLLOWER mode via hash/LLM)
3. Semantic matching (FOLLOWER mode via LLM)
4. Similar but different tasks (MIXED mode)
5. Cost savings analysis
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "llmos"))

from datetime import datetime
from memory.traces_sdk import TraceManager, ExecutionTrace
from memory.trace_analyzer import TraceAnalyzer


async def test_semantic_matching():
    """Test semantic trace matching with various similarity levels"""

    print("=" * 80)
    print("🧪 Testing Nested Learning Implementation - Semantic Trace Matching")
    print("=" * 80)
    print()

    # Setup
    workspace = Path("./test_workspace")
    workspace.mkdir(exist_ok=True)
    memories_dir = workspace / "memories"
    memories_dir.mkdir(exist_ok=True)

    # Initialize TraceManager with LLM matching
    trace_manager = TraceManager(
        memories_dir=memories_dir,
        workspace=workspace,
        enable_llm_matching=True
    )

    print("✅ Initialized TraceManager with LLM-based matching")
    print()

    # Create sample traces
    print("📝 Creating sample execution traces...")
    print()

    traces = [
        ExecutionTrace(
            goal_signature="trace_001",
            goal_text="Create a Python file",
            success_rating=0.95,
            usage_count=5,
            created_at=datetime.now(),
            last_used=datetime.now(),
            estimated_cost_usd=0.50,
            estimated_time_secs=15.0,
            mode="LEARNER",
            tools_used=["Write", "Read"],
            output_summary="Created file successfully with 50 lines of code"
        ),
        ExecutionTrace(
            goal_signature="trace_002",
            goal_text="List all files in the directory",
            success_rating=0.98,
            usage_count=10,
            created_at=datetime.now(),
            last_used=datetime.now(),
            estimated_cost_usd=0.30,
            estimated_time_secs=8.0,
            mode="LEARNER",
            tools_used=["Bash", "Glob"],
            output_summary="Listed 25 files successfully"
        ),
        ExecutionTrace(
            goal_signature="trace_003",
            goal_text="Analyze code for bugs",
            success_rating=0.88,
            usage_count=3,
            created_at=datetime.now(),
            last_used=datetime.now(),
            estimated_cost_usd=1.20,
            estimated_time_secs=45.0,
            mode="LEARNER",
            tools_used=["Read", "Grep", "Task"],
            output_summary="Found 3 potential issues"
        ),
    ]

    # Save traces
    for trace in traces:
        trace_manager.save_trace(trace)
        print(f"  ✓ Saved trace: '{trace.goal_text}'")

    print()
    print("=" * 80)
    print("🔍 Test 1: Exact Match (Hash-based)")
    print("=" * 80)
    print()

    exact_match = trace_manager.find_trace("Create a Python file", min_confidence=0.9)
    if exact_match:
        print(f"✅ Found exact match (hash-based)")
        print(f"   Goal: {exact_match.goal_text}")
        print(f"   Success rate: {exact_match.success_rating:.0%}")
        print(f"   Mode: FOLLOWER (cost: $0)")
    else:
        print("❌ No exact match found")

    print()
    print("=" * 80)
    print("🔍 Test 2: Semantic Match - Minor Variation")
    print("=" * 80)
    print()

    query1 = "Create a Python file called helpers.py"
    print(f"Query: '{query1}'")
    print(f"Expected: Match 'Create a Python file' with HIGH confidence")
    print()

    result1 = await trace_manager.find_trace_with_llm(query1, min_confidence=0.75)
    if result1:
        matched_trace, confidence = result1
        print(f"✅ Semantic match found!")
        print(f"   Matched: '{matched_trace.goal_text}'")
        print(f"   Confidence: {confidence:.0%}")

        if confidence >= 0.92:
            mode = "FOLLOWER"
            cost = "$0.00"
        elif confidence >= 0.75:
            mode = "MIXED"
            cost = "$0.25"
        else:
            mode = "LEARNER"
            cost = "$0.50"

        print(f"   Recommended mode: {mode}")
        print(f"   Estimated cost: {cost}")
    else:
        print("❌ No semantic match found")

    print()
    print("=" * 80)
    print("🔍 Test 3: Semantic Match - Synonym Variation")
    print("=" * 80)
    print()

    query2 = "Show me all files"
    print(f"Query: '{query2}'")
    print(f"Expected: Match 'List all files in the directory' with MEDIUM-HIGH confidence")
    print()

    result2 = await trace_manager.find_trace_with_llm(query2, min_confidence=0.75)
    if result2:
        matched_trace, confidence = result2
        print(f"✅ Semantic match found!")
        print(f"   Matched: '{matched_trace.goal_text}'")
        print(f"   Confidence: {confidence:.0%}")

        if confidence >= 0.92:
            mode = "FOLLOWER"
            cost = "$0.00"
        elif confidence >= 0.75:
            mode = "MIXED"
            cost = "$0.25"
        else:
            mode = "LEARNER"
            cost = "$0.50"

        print(f"   Recommended mode: {mode}")
        print(f"   Estimated cost: {cost}")
    else:
        print("❌ No semantic match found")

    print()
    print("=" * 80)
    print("🔍 Test 4: Smart Trace Finding (Auto Mode Detection)")
    print("=" * 80)
    print()

    query3 = "List all Python files in the project"
    print(f"Query: '{query3}'")
    print(f"Expected: MIXED mode (similar to 'List all files', but with filtering)")
    print()

    trace, confidence, mode = await trace_manager.find_trace_smart(query3)
    if trace:
        print(f"✅ Smart match found!")
        print(f"   Matched: '{trace.goal_text}'")
        print(f"   Confidence: {confidence:.0%}")
        print(f"   Auto-detected mode: {mode}")

        if mode == "FOLLOWER":
            print(f"   💡 Will execute trace directly ($0)")
        elif mode == "MIXED":
            print(f"   💡 Will use trace as guidance for LLM ($0.25)")
            print(f"   💡 Trace provides structure, LLM adapts for Python filter")
        else:
            print(f"   💡 Will use full LLM reasoning ($0.50)")
    else:
        print("❌ No match found")
        print(f"   Mode: {mode} (LEARNER - novel task)")

    print()
    print("=" * 80)
    print("🔍 Test 5: Unrelated Task (Should Not Match)")
    print("=" * 80)
    print()

    query4 = "Solve quadratic equation"
    print(f"Query: '{query4}'")
    print(f"Expected: No match, LEARNER mode required")
    print()

    trace, confidence, mode = await trace_manager.find_trace_smart(query4)
    if trace:
        print(f"⚠️  Unexpected match found")
        print(f"   Matched: '{trace.goal_text}'")
        print(f"   Confidence: {confidence:.0%}")
    else:
        print(f"✅ No match (as expected)")
        print(f"   Confidence: {confidence:.0%}")
        print(f"   Mode: {mode}")
        print(f"   💡 Novel task - full LEARNER mode required ($0.50)")

    print()
    print("=" * 80)
    print("💰 Cost Savings Analysis")
    print("=" * 80)
    print()

    scenarios = [
        ("Exact repeat: 'Create a Python file'", "FOLLOWER", "$0.00", "100%"),
        ("Minor variation: 'Create a Python file named X'", "FOLLOWER/MIXED", "$0.00-$0.25", "50-100%"),
        ("Similar task: 'List Python files'", "MIXED", "$0.25", "50%"),
        ("Novel task: 'Solve quadratic equation'", "LEARNER", "$0.50", "0%"),
    ]

    print("Scenario Comparison:")
    print()
    for scenario, mode, cost, savings in scenarios:
        print(f"  {scenario}")
        print(f"    Mode: {mode}")
        print(f"    Cost: {cost}")
        print(f"    Savings vs LEARNER: {savings}")
        print()

    print("Key Insight:")
    print("  - Old system (hash-only): 'Create Python file' ≠ 'Create Python file named X'")
    print("  - New system (LLM): Understands semantic equivalence → 50-100% savings!")
    print()

    # Cleanup
    import shutil
    if workspace.exists():
        shutil.rmtree(workspace)

    print("=" * 80)
    print("✅ Test Complete!")
    print("=" * 80)


async def test_analyzer_directly():
    """Test TraceAnalyzer directly for detailed analysis"""

    print()
    print("=" * 80)
    print("🔬 Direct TraceAnalyzer Testing")
    print("=" * 80)
    print()

    workspace = Path("./test_workspace")
    workspace.mkdir(exist_ok=True)

    analyzer = TraceAnalyzer(workspace)

    # Test similarity analysis
    test_cases = [
        {
            "current": "Create a new file",
            "previous": "Create a file",
            "expected_range": (0.90, 1.0),
        },
        {
            "current": "List all Python files",
            "previous": "List all files in directory",
            "expected_range": (0.70, 0.90),
        },
        {
            "current": "Analyze code for bugs",
            "previous": "Create a file",
            "expected_range": (0.0, 0.30),
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"  Current:  '{test_case['current']}'")
        print(f"  Previous: '{test_case['previous']}'")
        print(f"  Expected: {test_case['expected_range'][0]:.0%} - {test_case['expected_range'][1]:.0%}")

        confidence = await analyzer.analyze_goal_similarity(
            goal=test_case["current"],
            trace_goal=test_case["previous"],
            trace_metadata={
                "success_rating": 0.95,
                "usage_count": 5,
                "mode": "LEARNER"
            }
        )

        print(f"  Result: {confidence:.0%}")

        min_expected, max_expected = test_case["expected_range"]
        if min_expected <= confidence <= max_expected:
            print(f"  ✅ Within expected range")
        else:
            print(f"  ⚠️  Outside expected range")

        print()

    # Cleanup
    import shutil
    if workspace.exists():
        shutil.rmtree(workspace)

    print("=" * 80)
    print("✅ Direct Analyzer Test Complete!")
    print("=" * 80)


async def main():
    """Run all tests"""
    try:
        await test_semantic_matching()
        await test_analyzer_directly()

    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  🧬 NESTED LEARNING IMPLEMENTATION TEST                                   ║
║                                                                           ║
║  Tests LLM-based semantic trace matching and execution mode selection    ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)

    asyncio.run(main())
