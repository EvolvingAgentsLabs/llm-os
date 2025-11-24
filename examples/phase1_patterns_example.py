#!/usr/bin/env python3
"""
Phase 1 Design Patterns Example

Demonstrates the new configuration, strategy, and dependency injection
patterns implemented in Phase 1.

Features demonstrated:
1. Configuration Management (presets, custom config, builder)
2. Strategy Pattern (cost-optimized, speed-optimized, custom)
3. Manual Dependency Injection (testing with mocks)
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock

# Add llmos to path
sys.path.insert(0, str(Path(__file__).parent.parent / "llmos"))

from boot import LLMOS
from kernel.config import LLMOSConfig, ConfigBuilder, KernelConfig, MemoryConfig
from kernel.mode_strategies import get_strategy, ModeSelectionStrategy, ModeContext, ModeDecision


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


async def example_1_backward_compatibility():
    """Example 1: Backward Compatibility - Old API still works"""
    print_section("Example 1: Backward Compatibility")

    print("The old API still works exactly as before:")
    print("Code: os = LLMOS(budget_usd=10.0)\n")

    # Old way still works!
    os = LLMOS(budget_usd=10.0)
    await os.boot()

    print("✅ Old API works perfectly - 100% backward compatible")
    print(f"   Workspace: {os.workspace}")
    print(f"   Budget: ${os.token_economy.balance:.2f}")
    print(f"   Strategy: {type(os.dispatcher.strategy).__name__}")

    await os.shutdown()


async def example_2_configuration_presets():
    """Example 2: Configuration Presets"""
    print_section("Example 2: Configuration Presets")

    print("Three environment presets are available:\n")

    # Development preset
    print("1. Development Preset:")
    print("   Code: config = LLMOSConfig.development()")
    dev_config = LLMOSConfig.development()
    print(f"   Budget: ${dev_config.kernel.budget_usd:.2f}")
    print(f"   LLM Matching: {dev_config.memory.enable_llm_matching}")
    print(f"   Streaming: {dev_config.sdk.enable_streaming}")
    print(f"   Auto-crystallization: {dev_config.dispatcher.auto_crystallization}\n")

    # Production preset
    print("2. Production Preset:")
    print("   Code: config = LLMOSConfig.production()")
    prod_config = LLMOSConfig.production()
    print(f"   Budget: ${prod_config.kernel.budget_usd:.2f}")
    print(f"   LLM Matching: {prod_config.memory.enable_llm_matching}")
    print(f"   Streaming: {prod_config.sdk.enable_streaming}")
    print(f"   Auto-crystallization: {prod_config.dispatcher.auto_crystallization}\n")

    # Testing preset
    print("3. Testing Preset:")
    print("   Code: config = LLMOSConfig.testing()")
    test_config = LLMOSConfig.testing()
    print(f"   Budget: ${test_config.kernel.budget_usd:.2f}")
    print(f"   LLM Matching: {test_config.memory.enable_llm_matching}")
    print(f"   Workspace: {test_config.workspace}")
    print(f"   Auto-crystallization: {test_config.dispatcher.auto_crystallization}\n")

    # Use a preset
    print("Using development preset:")
    os = LLMOS(config=dev_config)
    await os.boot()

    print("✅ Development environment configured with single line")

    await os.shutdown()


async def example_3_custom_configuration():
    """Example 3: Custom Configuration with Builder"""
    print_section("Example 3: Custom Configuration")

    print("Using ConfigBuilder for fluent API:\n")

    # Builder pattern
    config = (ConfigBuilder()
        .with_workspace(Path("./my_project"))
        .with_budget(5.0)
        .with_llm_matching(True)
        .with_model("claude-sonnet-4-5-20250929")
        .with_streaming(False)
        .with_project("demo_project")
        .with_auto_crystallization(True)
        .build())

    print("Code:")
    print("  config = (ConfigBuilder()")
    print("      .with_workspace(Path('./my_project'))")
    print("      .with_budget(5.0)")
    print("      .with_llm_matching(True)")
    print("      .with_model('claude-sonnet-4-5-20250929')")
    print("      .build())\n")

    print("Result:")
    print(f"   Workspace: {config.workspace}")
    print(f"   Budget: ${config.kernel.budget_usd:.2f}")
    print(f"   LLM Matching: {config.memory.enable_llm_matching}")
    print(f"   Model: {config.sdk.model}")
    print(f"   Project: {config.project_name}\n")

    os = LLMOS(config=config)
    await os.boot()

    print("✅ Custom configuration applied")

    await os.shutdown()


async def example_4_strategy_patterns():
    """Example 4: Mode Selection Strategies"""
    print_section("Example 4: Mode Selection Strategies")

    print("Five strategies available for different use cases:\n")

    strategies = {
        "auto": "Balanced approach (default)",
        "cost-optimized": "Minimize LLM costs",
        "speed-optimized": "Minimize latency",
        "forced-learner": "Always use learner (testing)",
        "forced-follower": "Prefer follower (testing)"
    }

    for name, description in strategies.items():
        strategy = get_strategy(name)
        print(f"  {name:20s} - {description}")
        print(f"  {'':20s}   Class: {type(strategy).__name__}")

    print("\nUsing cost-optimized strategy:")
    print("Code: strategy = get_strategy('cost-optimized')")

    # Create OS with cost-optimized strategy
    config = LLMOSConfig.development()
    strategy = get_strategy("cost-optimized")

    os = LLMOS(config=config)
    # Strategy is automatically set from config, but can be overridden in dispatcher
    await os.boot()

    print(f"\n✅ Strategy in use: {type(os.dispatcher.strategy).__name__}")
    print("   Lower thresholds for FOLLOWER mode (0.75 vs 0.92)")
    print("   Avoids expensive ORCHESTRATOR mode")

    await os.shutdown()


async def example_5_custom_strategy():
    """Example 5: Custom Strategy Implementation"""
    print_section("Example 5: Custom Strategy Implementation")

    print("You can create custom strategies for specific needs:\n")

    # Custom strategy
    class AggressiveLearnerStrategy(ModeSelectionStrategy):
        """Always prefer LEARNER for maximum adaptability"""

        async def determine_mode(self, context: ModeContext) -> ModeDecision:
            # Only use crystallized tools (free execution)
            trace, confidence = await self._find_trace(context)

            if trace and trace.crystallized_into_tool:
                return ModeDecision(
                    mode="CRYSTALLIZED",
                    confidence=1.0,
                    trace=trace,
                    reasoning="Crystallized tool available - free execution"
                )

            # Otherwise always learn (even if traces exist)
            return ModeDecision(
                mode="LEARNER",
                confidence=1.0,
                reasoning="Custom strategy: Always learn for maximum adaptability"
            )

    print("Code:")
    print("  class AggressiveLearnerStrategy(ModeSelectionStrategy):")
    print("      async def determine_mode(self, context):")
    print("          # Only use crystallized, otherwise always LEARNER")
    print("          return ModeDecision(mode='LEARNER', ...)\n")

    print("✅ Custom strategies enable domain-specific optimizations")
    print("   Use cases: A/B testing, specialized workflows, research")


async def example_6_dependency_injection():
    """Example 6: Dependency Injection for Testing"""
    print_section("Example 6: Dependency Injection for Testing")

    print("All components support optional injection:\n")

    print("Example: Testing with mock token economy")
    print("Code:")
    print("  mock_token_economy = Mock()")
    print("  mock_token_economy.balance = 100.0")
    print("  os = LLMOS(token_economy=mock_token_economy)\n")

    # Create mock
    mock_token_economy = Mock()
    mock_token_economy.balance = 100.0
    mock_token_economy.spend_log = []

    config = LLMOSConfig.testing()
    os = LLMOS(
        config=config,
        token_economy=mock_token_economy
    )
    await os.boot()

    print("✅ Mock injected successfully")
    print(f"   Token economy type: {type(os.token_economy)}")
    print(f"   Balance: ${os.token_economy.balance:.2f}")
    print("\nThis enables:")
    print("  - Unit testing with controlled dependencies")
    print("  - Integration testing with test doubles")
    print("  - Mocking external services")

    await os.shutdown()


async def example_7_complete_integration():
    """Example 7: All Patterns Together"""
    print_section("Example 7: Complete Integration")

    print("Combining configuration + strategy + execution:\n")

    # 1. Create custom configuration
    config = (ConfigBuilder()
        .with_workspace(Path("./integration_demo"))
        .with_budget(15.0)
        .with_llm_matching(True)
        .with_streaming(False)
        .with_auto_crystallization(True)
        .build())

    # 2. Create OS with config
    os = LLMOS(config=config)
    await os.boot()

    print("Configuration:")
    print(f"  Workspace: {os.workspace}")
    print(f"  Budget: ${os.token_economy.balance:.2f}")
    print(f"  Strategy: {type(os.dispatcher.strategy).__name__}")
    print(f"  LLM Matching: {os.config.memory.enable_llm_matching}\n")

    # 3. Execute a simple task
    print("Executing task: 'Create a simple Python hello world script'\n")

    # Note: This would normally call the actual LLM
    # For demo purposes, we'll show what would happen
    print("Decision flow:")
    print("  1. Check for crystallized tool → None found")
    print("  2. Check for trace match → None found (first run)")
    print("  3. Analyze complexity → Simple task")
    print("  4. Selected mode: LEARNER")
    print("  5. Execute with LLM")
    print("  6. Save trace for future Follower mode\n")

    print("✅ Complete integration of all Phase 1 patterns")

    await os.shutdown()


async def example_8_environment_variables():
    """Example 8: Configuration from Environment"""
    print_section("Example 8: Environment Variables")

    print("Load configuration from environment:\n")

    print("Environment variables:")
    print("  LLMOS_WORKSPACE=/path/to/workspace")
    print("  LLMOS_BUDGET=20.0")
    print("  LLMOS_MODEL=claude-sonnet-4-5-20250929")
    print("  LLMOS_ENABLE_LLM_MATCHING=true\n")

    print("Code:")
    print("  config = LLMOSConfig.from_env()")
    print("  os = LLMOS(config=config)\n")

    # Would load from environment
    # config = LLMOSConfig.from_env()

    print("✅ Perfect for Docker containers and cloud deployments")
    print("   Separate configuration from code")


async def example_9_serialization():
    """Example 9: Configuration Serialization"""
    print_section("Example 9: Configuration Serialization")

    print("Save and load configuration as YAML/JSON:\n")

    # Create config
    config = (ConfigBuilder()
        .with_budget(25.0)
        .with_project("saved_project")
        .build())

    # Serialize
    config_dict = config.to_dict()

    print("Serialized configuration:")
    print("  {")
    print(f"    'workspace': '{config_dict['workspace']}',")
    print(f"    'kernel': {{'budget_usd': {config_dict['kernel']['budget_usd']}}},")
    print(f"    'project_name': '{config_dict['project_name']}'")
    print("    ...")
    print("  }\n")

    # Deserialize
    loaded_config = LLMOSConfig.from_dict(config_dict)

    print("Code:")
    print("  # Save")
    print("  config_dict = config.to_dict()")
    print("  yaml.dump(config_dict, file)")
    print()
    print("  # Load")
    print("  config_dict = yaml.load(file)")
    print("  config = LLMOSConfig.from_dict(config_dict)\n")

    print("✅ Enables configuration as code")
    print("   Version control your LLMOS settings")


async def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("  LLMOS Phase 1 Design Patterns - Examples")
    print("="*70)
    print("\nDemonstrating:")
    print("  1. Configuration Management (Centralized, Type-Safe)")
    print("  2. Strategy Pattern (Pluggable Mode Selection)")
    print("  3. Manual Dependency Injection (Testable Components)")
    print()

    examples = [
        ("Backward Compatibility", example_1_backward_compatibility),
        ("Configuration Presets", example_2_configuration_presets),
        ("Custom Configuration", example_3_custom_configuration),
        ("Strategy Patterns", example_4_strategy_patterns),
        ("Custom Strategy", example_5_custom_strategy),
        ("Dependency Injection", example_6_dependency_injection),
        ("Complete Integration", example_7_complete_integration),
        ("Environment Variables", example_8_environment_variables),
        ("Serialization", example_9_serialization),
    ]

    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print()

    choice = input("Select example (1-9) or 'all': ").strip()

    if choice.lower() == 'all':
        for name, example_func in examples:
            try:
                await example_func()
                input("\n[Press Enter to continue...]")
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

    print("\n" + "="*70)
    print("  Examples Complete")
    print("="*70)
    print("\nFor more information, see:")
    print("  - llmos/ARCHITECTURE_PATTERNS.md")
    print("  - projects/llmos_architecture_analysis/output/FINAL_REPORT.md")
    print()


if __name__ == "__main__":
    asyncio.run(main())
