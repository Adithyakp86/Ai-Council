#!/usr/bin/env python3
"""
Example demonstrating the AI Council configuration management system.

This example shows how to:
1. Create configurations using the ConfigBuilder
2. Add models, routing rules, and execution modes
3. Set up plugins
4. Save and load configurations
5. Use the plugin manager
"""

import tempfile
from pathlib import Path

from ai_council.utils.config import AICouncilConfig, create_default_config
from ai_council.utils.config_builder import (
    ConfigBuilder, create_development_config, create_production_config
)
from ai_council.utils.plugin_manager import create_plugin_manager
from ai_council.core.models import ExecutionMode, TaskType, Priority, RiskLevel


def demonstrate_config_builder():
    """Demonstrate using the ConfigBuilder to create custom configurations."""
    print("=== Configuration Builder Example ===")
    
    # Create a custom configuration using the builder pattern
    config = (ConfigBuilder()
              .with_logging(level="DEBUG", format_json=True)
              .with_system_settings(debug=True, environment="development")
              .with_cost_management(max_cost_per_request=5.0, alert_threshold=2.0)
              
              # Add models
              .add_model("gpt-4", "openai", "OPENAI_API_KEY",
                        cost_per_input_token=0.00003, cost_per_output_token=0.00006,
                        supported_task_types=[TaskType.REASONING, TaskType.CODE_GENERATION],
                        reliability_score=0.95, average_latency=3.0)
              
              .add_model("claude-3", "anthropic", "ANTHROPIC_API_KEY",
                        cost_per_input_token=0.000015, cost_per_output_token=0.000075,
                        supported_task_types=[TaskType.RESEARCH, TaskType.FACT_CHECKING],
                        reliability_score=0.92, average_latency=2.5)
              
              # Add routing rules
              .add_routing_rule("high_accuracy", 
                              task_types=[TaskType.REASONING],
                              priority_levels=[Priority.CRITICAL, Priority.HIGH],
                              preferred_models=["gpt-4"],
                              accuracy_threshold=0.9, weight=2.0)
              
              .add_routing_rule("cost_effective",
                              task_types=[TaskType.RESEARCH],
                              preferred_models=["claude-3"],
                              cost_threshold=0.01, weight=1.0)
              
              # Add execution modes
              .add_execution_mode("custom_fast", ExecutionMode.FAST,
                                max_parallel=2, timeout=20.0, accuracy_requirement=0.7)
              
              .add_execution_mode("custom_quality", ExecutionMode.BEST_QUALITY,
                                max_parallel=6, timeout=180.0, accuracy_requirement=0.95)
              
              # Add plugin (example - would need actual plugin implementation)
              .add_plugin("custom_model", "plugins.custom.MyModel", "CustomAIModel",
                        config={"api_endpoint": "https://api.example.com"})
              
              .build())
    
    print(f"Created configuration with {len(config.models)} models")
    print(f"Routing rules: {[rule.name for rule in config.routing_rules]}")
    print(f"Execution modes: {list(config.execution_modes.keys())}")
    print(f"Plugins: {list(config.plugins.keys())}")
    print()


def demonstrate_predefined_configs():
    """Demonstrate using predefined configuration templates."""
    print("=== Predefined Configuration Templates ===")
    
    # Development configuration
    dev_config = create_development_config()
    print(f"Development config - Debug: {dev_config.debug}, Environment: {dev_config.environment}")
    print(f"Development config - Log level: {dev_config.logging.level}")
    print(f"Development config - Max cost: ${dev_config.cost.max_cost_per_request}")
    
    # Production configuration
    prod_config = create_production_config()
    print(f"Production config - Debug: {prod_config.debug}, Environment: {prod_config.environment}")
    print(f"Production config - JSON logging: {prod_config.logging.format_json}")
    print(f"Production config - Models: {list(prod_config.models.keys())}")
    print()


def demonstrate_config_file_operations():
    """Demonstrate saving and loading configurations from files."""
    print("=== Configuration File Operations ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "example_config.yaml"
        
        # Create and save a configuration
        config = create_default_config()
        config.debug = True
        config.logging.level = "DEBUG"
        
        print(f"Saving configuration to {config_path}")
        config.save_to_file(config_path)
        
        # Load the configuration back
        loaded_config = AICouncilConfig.from_file(config_path)
        print(f"Loaded configuration - Debug: {loaded_config.debug}")
        print(f"Loaded configuration - Log level: {loaded_config.logging.level}")
        print(f"Loaded configuration - Models: {list(loaded_config.models.keys())}")
        print()


def demonstrate_routing_rules():
    """Demonstrate routing rule functionality."""
    print("=== Routing Rules Example ===")
    
    config = create_default_config()
    
    # Get all routing rules
    all_rules = config.get_routing_rules()
    print(f"Total routing rules: {len(all_rules)}")
    
    # Get rules for specific task type
    reasoning_rules = config.get_routing_rules(task_type=TaskType.REASONING)
    print(f"Reasoning task rules: {[rule.name for rule in reasoning_rules]}")
    
    # Get rules for specific execution mode
    fast_rules = config.get_routing_rules(execution_mode=ExecutionMode.FAST)
    print(f"Fast execution rules: {[rule.name for rule in fast_rules]}")
    
    # Add a new routing rule
    from ai_council.utils.config import RoutingRule
    new_rule = RoutingRule(
        name="debug_rule",
        task_types=[TaskType.DEBUGGING],
        preferred_models=["gpt-4"],
        accuracy_threshold=0.85,
        weight=1.5
    )
    config.add_routing_rule(new_rule)
    print(f"Added new rule: {new_rule.name}")
    print()


def demonstrate_execution_modes():
    """Demonstrate execution mode configuration."""
    print("=== Execution Modes Example ===")
    
    config = create_default_config()
    
    # Show available execution modes
    print("Available execution modes:")
    for mode_name, mode_config in config.execution_modes.items():
        print(f"  {mode_name}: {mode_config.mode.value}")
        print(f"    Max parallel: {mode_config.max_parallel_executions}")
        print(f"    Timeout: {mode_config.timeout_seconds}s")
        print(f"    Accuracy requirement: {mode_config.accuracy_requirement}")
        print(f"    Cost limit: {mode_config.cost_limit}")
        print()


def demonstrate_plugin_management():
    """Demonstrate plugin management (conceptual - no actual plugins loaded)."""
    print("=== Plugin Management Example ===")
    
    config = AICouncilConfig()
    
    # Add some example plugin configurations
    from ai_council.utils.config import PluginConfig
    
    plugins = [
        PluginConfig(
            name="custom_model",
            module_path="plugins.models.custom",
            class_name="CustomModel",
            enabled=True,
            config={"api_key": "custom_key", "endpoint": "https://api.custom.com"},
            dependencies=["requests", "custom_sdk"]
        ),
        PluginConfig(
            name="enhanced_analyzer",
            module_path="plugins.analysis.enhanced",
            class_name="EnhancedAnalyzer",
            enabled=False,  # Disabled for this example
            config={"use_advanced_features": True}
        )
    ]
    
    for plugin in plugins:
        config.add_plugin(plugin)
    
    # Show plugin information
    print(f"Total plugins configured: {len(config.plugins)}")
    enabled_plugins = config.get_enabled_plugins()
    print(f"Enabled plugins: {[p.name for p in enabled_plugins]}")
    
    # Create plugin manager (won't actually load plugins in this example)
    try:
        plugin_manager = create_plugin_manager(config)
        print(f"Plugin manager created successfully")
        
        # Show plugin info
        plugin_info = plugin_manager.get_plugin_info()
        for plugin_name, info in plugin_info.items():
            print(f"  {plugin_name}: enabled={info['enabled']}, has_instance={info['has_instance']}")
    except Exception as e:
        print(f"Plugin manager creation failed (expected in example): {e}")
    
    print()


def demonstrate_model_configuration():
    """Demonstrate model configuration features."""
    print("=== Model Configuration Example ===")
    
    config = create_default_config()
    
    # Show model details
    for model_name, model_config in config.models.items():
        print(f"Model: {model_name}")
        print(f"  Provider: {model_config.provider}")
        print(f"  Cost per input token: ${model_config.cost_per_input_token}")
        print(f"  Cost per output token: ${model_config.cost_per_output_token}")
        print(f"  Max context length: {model_config.max_context_length:,}")
        print(f"  Reliability score: {model_config.reliability_score}")
        print(f"  Average latency: {model_config.average_latency}s")
        print(f"  Supported task types: {[tt.value for tt in model_config.supported_task_types]}")
        print(f"  Strengths: {model_config.strengths}")
        print(f"  Weaknesses: {model_config.weaknesses}")
        print()


def main():
    """Run all configuration examples."""
    print("AI Council Configuration Management Examples")
    print("=" * 50)
    print()
    
    try:
        demonstrate_config_builder()
        demonstrate_predefined_configs()
        demonstrate_config_file_operations()
        demonstrate_routing_rules()
        demonstrate_execution_modes()
        demonstrate_plugin_management()
        demonstrate_model_configuration()
        
        print("All configuration examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()