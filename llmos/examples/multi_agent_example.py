#!/usr/bin/env python3
"""
Multi-Agent Example - Demonstrates Phase 2 capabilities

This example shows how to use llmos with:
- Project management
- Dynamic agent creation
- Multi-agent orchestration
- Memory query interface
"""

import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from boot import LLMOS


async def example_1_simple_learner():
    """Example 1: Simple Learner mode (Phase 1 functionality)"""
    print("\n" + "=" * 60)
    print("Example 1: Simple Learner Mode")
    print("=" * 60)

    os = LLMOS(budget_usd=10.0)
    await os.boot()

    # Simple goal - will use Learner mode
    result = await os.execute("Create a Python function to calculate fibonacci numbers")

    print(f"\n✅ Result: {result}")

    await os.shutdown()


async def example_2_project_management():
    """Example 2: Project management (Phase 2 NEW)"""
    print("\n" + "=" * 60)
    print("Example 2: Project Management")
    print("=" * 60)

    os = LLMOS(budget_usd=10.0, project_name="data_analysis")
    await os.boot()

    # Create a project-specific agent
    analyst_agent = os.create_agent(
        name="data-analyst-agent",
        agent_type="specialized",
        category="data_analysis",
        description="Analyzes CSV data files",
        system_prompt="""You are a data analysis specialist.
You can read CSV files, calculate statistics, and generate insights.""",
        tools=["Read", "Write", "Bash"],
        capabilities=["CSV analysis", "Statistical computing", "Data visualization"],
        constraints=["Max 100MB files", "CSV/XLSX formats only"]
    )

    print(f"\n🤖 Created agent: {analyst_agent.name}")
    print(f"   Tools: {', '.join(analyst_agent.tools)}")
    print(f"   Capabilities: {', '.join(analyst_agent.capabilities)}")

    # List all agents
    agents = os.list_agents()
    print(f"\n📋 Total agents: {len(agents)}")
    for agent in agents:
        print(f"   - {agent.name} ({agent.category})")

    await os.shutdown()


async def example_3_orchestration():
    """Example 3: Multi-agent orchestration (Phase 2 NEW)"""
    print("\n" + "=" * 60)
    print("Example 3: Multi-Agent Orchestration")
    print("=" * 60)

    os = LLMOS(budget_usd=10.0, project_name="research_project")
    await os.boot()

    # Complex goal requiring orchestration
    # Will be auto-detected as ORCHESTRATOR mode (has "and" indicator)
    result = await os.execute(
        "Research quantum computing trends and create a summary report",
        mode="AUTO",  # Will auto-detect ORCHESTRATOR
        max_cost_usd=2.0
    )

    print(f"\n✅ Orchestration Result:")
    print(f"   Success: {result.get('success')}")
    print(f"   Mode: {result.get('mode')}")
    print(f"   Steps: {result.get('steps_completed')}/{result.get('total_steps')}")
    print(f"   Cost: ${result.get('cost', 0):.2f}")
    print(f"   Time: {result.get('execution_time', 0):.1f}s")

    await os.shutdown()


async def example_4_agent_creation_on_demand():
    """Example 4: Dynamic agent creation during orchestration"""
    print("\n" + "=" * 60)
    print("Example 4: Dynamic Agent Creation")
    print("=" * 60)

    os = LLMOS(budget_usd=10.0, project_name="quantum_research")
    await os.boot()

    # Force orchestration mode
    result = await os.execute(
        "Create a quantum circuit simulator and test it with a simple circuit",
        mode="ORCHESTRATOR",
        max_cost_usd=3.0
    )

    # The orchestrator will:
    # 1. Detect need for quantum specialist
    # 2. Create quantum-simulation-agent on-demand
    # 3. Delegate circuit simulation to that agent
    # 4. Coordinate results

    print(f"\n✅ Result: {result.get('success')}")

    # Check if new agent was created
    agents = os.list_agents()
    print(f"\n🤖 Agents after execution: {len(agents)}")

    await os.shutdown()


async def example_5_memory_query():
    """Example 5: Memory query interface (Phase 2 NEW)"""
    print("\n" + "=" * 60)
    print("Example 5: Memory Query Interface")
    print("=" * 60)

    os = LLMOS(budget_usd=10.0)
    await os.boot()

    # Get memory statistics
    mem_stats = os.memory_query.get_memory_statistics()
    print(f"\n📊 Memory Statistics:")
    print(f"   Total traces: {mem_stats['total_traces']}")
    print(f"   Avg success rate: {mem_stats['avg_success_rate']:.0%}")
    print(f"   High confidence: {mem_stats['high_confidence_traces']}")

    # Get recommendations for a goal
    recommendations = await os.memory_query.get_recommendations(
        "Create a Python script to analyze data"
    )

    print(f"\n💡 Recommendations:")
    for rec in recommendations:
        print(f"   - {rec}")

    # Get optimization suggestions
    suggestions = await os.memory_query.get_optimization_suggestions(
        "Process CSV files"
    )

    print(f"\n⚡ Optimization Suggestions:")
    for sug in suggestions:
        print(f"   - {sug}")

    await os.shutdown()


async def example_6_complete_workflow():
    """Example 6: Complete workflow with all Phase 2 features"""
    print("\n" + "=" * 60)
    print("Example 6: Complete Workflow")
    print("=" * 60)

    # Initialize with project
    os = LLMOS(budget_usd=10.0, project_name="complete_demo")
    await os.boot()

    # Step 1: Create specialized agents
    print("\n📝 Step 1: Creating specialized agents...")

    researcher = os.create_agent(
        name="research-agent",
        agent_type="specialized",
        category="research",
        description="Researches topics using web search",
        system_prompt="You are a research specialist. Use WebSearch to find information.",
        tools=["WebSearch", "Read", "Write"],
        capabilities=["Web research", "Information synthesis"],
        constraints=["Academic sources preferred"]
    )

    writer = os.create_agent(
        name="technical-writer-agent",
        agent_type="specialized",
        category="documentation",
        description="Writes technical documentation",
        system_prompt="You are a technical writer. Create clear, structured documentation.",
        tools=["Read", "Write", "Edit"],
        capabilities=["Technical writing", "Markdown formatting"],
        constraints=["Clear, concise style"]
    )

    print(f"   ✅ Created {researcher.name}")
    print(f"   ✅ Created {writer.name}")

    # Step 2: Execute complex goal (orchestration)
    print("\n📝 Step 2: Executing complex goal with orchestration...")

    result = await os.execute(
        "Research latest AI developments and create a technical report",
        mode="ORCHESTRATOR",
        max_cost_usd=3.0
    )

    print(f"\n✅ Orchestration Complete:")
    print(f"   Success: {result['success']}")
    print(f"   Steps: {result.get('steps_completed', 0)}/{result.get('total_steps', 0)}")
    print(f"   Cost: ${result.get('cost', 0):.2f}")

    # Step 3: Check project structure
    print("\n📝 Step 3: Checking project structure...")

    project = os.current_project
    print(f"\n📂 Project: {project.name}")
    print(f"   Components: {project.components_path}")
    print(f"   Output: {project.output_path}")
    print(f"   Memory: {project.memory_path}")
    print(f"   State: {project.state_path}")

    # Step 4: List projects and agents
    print("\n📝 Step 4: System summary...")

    projects = os.list_projects()
    agents = os.list_agents()

    print(f"\n📊 System Summary:")
    print(f"   Projects: {len(projects)}")
    print(f"   Agents: {len(agents)}")
    print(f"   Budget remaining: ${os.token_economy.balance:.2f}")

    await os.shutdown()


async def example_7_sdk_memory():
    """Example 7: Claude SDK Memory System (Phase 2 Enhancement)"""
    print("\n" + "=" * 60)
    print("Example 7: Claude SDK Memory")
    print("=" * 60)

    os = LLMOS(budget_usd=10.0)
    await os.boot()

    # The memory query interface uses Claude SDK file-based memory
    # Let's search for similar tasks using keyword matching
    print("\n🔍 Searching for tasks similar to 'analyze CSV data'...")

    similar_tasks = await os.memory_query.find_similar_tasks(
        goal="analyze CSV data",
        limit=5,
        min_confidence=0.7
    )

    print(f"\n✅ Found {len(similar_tasks)} similar tasks:")
    for i, task in enumerate(similar_tasks, 1):
        print(f"   {i}. {task.goal_text[:60]}...")
        print(f"      Success: {task.success_rating:.0%}, Used: {task.usage_count} times")

    # Show memory statistics
    mem_stats = os.memory_query.get_memory_statistics()
    print(f"\n💾 Memory Statistics:")
    print(f"   Total traces: {mem_stats.get('total_traces', 0)}")
    print(f"   High-confidence: {mem_stats.get('high_confidence_count', 0)}")
    print(f"   Facts stored: {mem_stats.get('facts_count', 0)}")
    print(f"   Insights: {mem_stats.get('insights_count', 0)}")

    await os.shutdown()


async def example_8_cross_project_learning():
    """Example 8: Cross-project learning insights (Phase 2 Enhancement)"""
    print("\n" + "=" * 60)
    print("Example 8: Cross-Project Learning")
    print("=" * 60)

    os = LLMOS(budget_usd=10.0)
    await os.boot()

    # Get common patterns across projects
    print("\n🌐 Analyzing common patterns across projects...")

    patterns = await os.get_cross_project_insights(
        min_projects=2,
        min_confidence=0.7
    )

    print(f"\n✅ Found {len(patterns)} cross-project patterns:")
    for pattern in patterns[:5]:  # Show top 5
        print(f"\n   📊 {pattern.title}")
        print(f"      Type: {pattern.insight_type}")
        print(f"      Projects: {', '.join(pattern.projects_involved)}")
        print(f"      Impact: {pattern.impact}")
        print(f"      Recommendation: {pattern.recommendation}")

    # Get reusable agent patterns
    print("\n\n🤖 Identifying reusable agent patterns...")

    reusable_agents = await os.get_reusable_agents(
        min_success_rate=0.8,
        min_usage_count=3
    )

    print(f"\n✅ Found {len(reusable_agents)} reusable agent patterns:")
    for agent in reusable_agents[:3]:  # Show top 3
        print(f"\n   🔧 {agent.agent_name}")
        print(f"      Category: {agent.category}")
        print(f"      Success Rate: {agent.success_rate:.0%}")
        print(f"      Usage: {agent.usage_count} times across {len(agent.projects_used)} projects")
        print(f"      Recommended for: {', '.join(agent.recommended_for)}")

    # Get project learning summary
    projects = os.list_projects()
    if projects:
        print(f"\n\n📚 Learning Summary for '{projects[0].name}'...")
        summary = await os.get_project_summary(projects[0].name)

        print(f"\n✅ Project Stats:")
        print(f"   Total executions: {summary['total_executions']}")
        print(f"   Average success: {summary['avg_success_rate']:.0%}")
        print(f"   Total cost: ${summary['total_cost']:.2f}")
        print(f"   High-confidence traces: {summary['high_confidence_traces']}")

        if summary['top_patterns']:
            print(f"\n   Top patterns:")
            for p in summary['top_patterns']:
                print(f"      - {p['type']}: {p['count']} times")

    await os.shutdown()


async def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print(" LLM OS - Multi-Agent Examples (Phase 2)")
    print("=" * 80)

    examples = [
        ("Simple Learner Mode", example_1_simple_learner),
        ("Project Management", example_2_project_management),
        ("Multi-Agent Orchestration", example_3_orchestration),
        ("Dynamic Agent Creation", example_4_agent_creation_on_demand),
        ("Memory Query Interface", example_5_memory_query),
        ("Complete Workflow", example_6_complete_workflow),
        ("Claude SDK Memory (NEW)", example_7_sdk_memory),
        ("Cross-Project Learning (NEW)", example_8_cross_project_learning),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")

    print("\nSelect example (1-8) or 'all' to run all:")
    choice = input("> ").strip()

    if choice.lower() == 'all':
        for name, example_func in examples:
            try:
                await example_func()
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}")
                import traceback
                traceback.print_exc()
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        idx = int(choice) - 1
        name, example_func = examples[idx]
        try:
            await example_func()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice")

    print("\n" + "=" * 80)
    print(" Examples Complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
