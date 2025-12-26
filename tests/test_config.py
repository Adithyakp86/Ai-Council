"""Tests for configuration management."""

import pytest
import tempfile
from pathlib import Path
from ai_council.utils.config import (
    AICouncilConfig, ModelConfig, LoggingConfig, ExecutionConfig, CostConfig,
    RoutingRule, ExecutionModeConfig, PluginConfig,
    load_config, create_default_config
)
from ai_council.utils.config_builder import ConfigBuilder, create_development_config, create_production_config
from ai_council.core.models import ExecutionMode, TaskType, Priority, RiskLevel


class TestModelConfig:
    """Test ModelConfig data model."""
    
    def test_model_config_creation(self):
        """Test basic model config creation."""
        config = ModelConfig(
            name="gpt-4",
            provider="openai",
            api_key_env="OPENAI_API_KEY",
            cost_per_input_token=0.00003,
            cost_per_output_token=0.00006,
            max_context_length=8192
        )
        assert config.name == "gpt-4"
        assert config.provider == "openai"
        assert config.cost_per_input_token == 0.00003
        assert config.enabled is True


class TestAICouncilConfig:
    """Test AICouncilConfig main configuration class."""
    
    def test_config_creation(self):
        """Test basic config creation."""
        config = AICouncilConfig()
        assert config.logging.level == "INFO"
        assert config.execution.default_mode == ExecutionMode.BALANCED
        assert config.cost.max_cost_per_request == 10.0
        assert config.debug is False
    
    def test_config_validation(self):
        """Test config validation."""
        config = AICouncilConfig()
        config.execution.max_parallel_executions = -1
        
        with pytest.raises(ValueError, match="max_parallel_executions must be positive"):
            config.validate()
    
    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        config_data = {
            "logging": {"level": "DEBUG"},
            "execution": {"default_mode": "fast", "max_parallel_executions": 10},
            "cost": {"max_cost_per_request": 20.0},
            "models": {
                "test-model": {
                    "provider": "test",
                    "api_key_env": "TEST_KEY",
                    "cost_per_input_token": 0.001
                }
            },
            "debug": True
        }
        
        config = AICouncilConfig.from_dict(config_data)
        assert config.logging.level == "DEBUG"
        assert config.execution.default_mode == ExecutionMode.FAST
        assert config.execution.max_parallel_executions == 10
        assert config.cost.max_cost_per_request == 20.0
        assert config.debug is True
        assert "test-model" in config.models
        assert config.models["test-model"].provider == "test"
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = create_default_config()
        config_dict = config.to_dict()
        
        assert "logging" in config_dict
        assert "execution" in config_dict
        assert "cost" in config_dict
        assert "models" in config_dict
        assert config_dict["execution"]["default_mode"] == "balanced"
    
    def test_config_file_operations(self):
        """Test saving and loading config from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"
            
            # Create and save config
            original_config = create_default_config()
            original_config.debug = True
            original_config.save_to_file(config_path)
            
            # Load config from file
            loaded_config = AICouncilConfig.from_file(config_path)
            
            assert loaded_config.debug is True
            assert len(loaded_config.models) == len(original_config.models)
    
    def test_get_model_config(self):
        """Test getting model configuration."""
        config = create_default_config()
        
        gpt4_config = config.get_model_config("gpt-4")
        assert gpt4_config is not None
        assert gpt4_config.name == "gpt-4"
        
        nonexistent_config = config.get_model_config("nonexistent")
        assert nonexistent_config is None


class TestConfigLoading:
    """Test configuration loading functions."""
    
    def test_create_default_config(self):
        """Test creating default configuration."""
        config = create_default_config()
        
        assert isinstance(config, AICouncilConfig)
        assert len(config.models) >= 3  # Should have at least gpt-4, claude-3, and gpt-3.5-turbo
        assert "gpt-4" in config.models
        assert "claude-3" in config.models
        assert "gpt-3.5-turbo" in config.models
        
        # Check routing rules
        assert len(config.routing_rules) > 0
        assert any(rule.name == "high_accuracy_reasoning" for rule in config.routing_rules)
        
        # Check execution modes
        assert len(config.execution_modes) >= 3
        assert "fast" in config.execution_modes
        assert "balanced" in config.execution_modes
        assert "best_quality" in config.execution_modes
    
    def test_load_config_default(self):
        """Test loading config with defaults."""
        config = load_config()
        
        assert isinstance(config, AICouncilConfig)
        assert config.logging.level == "INFO"
        assert config.execution.default_mode == ExecutionMode.BALANCED
    
    def test_load_config_from_file(self):
        """Test loading config from specific file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "custom_config.yaml"
            
            # Create a custom config file
            custom_config = create_default_config()
            custom_config.debug = True
            custom_config.logging.level = "DEBUG"
            custom_config.save_to_file(config_path)
            
            # Load the custom config
            loaded_config = load_config(config_path)
            
            assert loaded_config.debug is True
            assert loaded_config.logging.level == "DEBUG"


class TestRoutingRule:
    """Test RoutingRule configuration."""
    
    def test_routing_rule_creation(self):
        """Test basic routing rule creation."""
        rule = RoutingRule(
            name="test_rule",
            task_types=[TaskType.REASONING],
            priority_levels=[Priority.HIGH],
            preferred_models=["gpt-4"],
            weight=2.0
        )
        assert rule.name == "test_rule"
        assert TaskType.REASONING in rule.task_types
        assert Priority.HIGH in rule.priority_levels
        assert "gpt-4" in rule.preferred_models
        assert rule.weight == 2.0


class TestExecutionModeConfig:
    """Test ExecutionModeConfig configuration."""
    
    def test_execution_mode_config_creation(self):
        """Test basic execution mode config creation."""
        config = ExecutionModeConfig(
            mode=ExecutionMode.FAST,
            max_parallel_executions=3,
            timeout_seconds=30.0,
            accuracy_requirement=0.7
        )
        assert config.mode == ExecutionMode.FAST
        assert config.max_parallel_executions == 3
        assert config.timeout_seconds == 30.0
        assert config.accuracy_requirement == 0.7


class TestPluginConfig:
    """Test PluginConfig configuration."""
    
    def test_plugin_config_creation(self):
        """Test basic plugin config creation."""
        config = PluginConfig(
            name="test_plugin",
            module_path="plugins.test",
            class_name="TestPlugin",
            enabled=True,
            config={"param1": "value1"},
            dependencies=["requests"]
        )
        assert config.name == "test_plugin"
        assert config.module_path == "plugins.test"
        assert config.class_name == "TestPlugin"
        assert config.enabled is True
        assert config.config["param1"] == "value1"
        assert "requests" in config.dependencies


class TestExtendedAICouncilConfig:
    """Test extended AICouncilConfig functionality."""
    
    def test_add_routing_rule(self):
        """Test adding routing rules."""
        config = AICouncilConfig()
        
        rule = RoutingRule(
            name="test_rule",
            task_types=[TaskType.REASONING],
            preferred_models=["gpt-4"]
        )
        
        config.add_routing_rule(rule)
        assert len(config.routing_rules) == 1
        assert config.routing_rules[0].name == "test_rule"
    
    def test_get_routing_rules(self):
        """Test getting routing rules with filters."""
        config = create_default_config()
        
        # Get all rules
        all_rules = config.get_routing_rules()
        assert len(all_rules) > 0
        
        # Get rules for specific task type
        reasoning_rules = config.get_routing_rules(task_type=TaskType.REASONING)
        assert len(reasoning_rules) > 0
        assert all(TaskType.REASONING in rule.task_types or not rule.task_types for rule in reasoning_rules)
    
    def test_add_plugin(self):
        """Test adding plugins."""
        config = AICouncilConfig()
        
        plugin = PluginConfig(
            name="test_plugin",
            module_path="plugins.test",
            class_name="TestPlugin"
        )
        
        config.add_plugin(plugin)
        assert "test_plugin" in config.plugins
        assert config.plugins["test_plugin"].name == "test_plugin"
    
    def test_get_enabled_plugins(self):
        """Test getting enabled plugins."""
        config = AICouncilConfig()
        
        # Add enabled plugin
        enabled_plugin = PluginConfig(
            name="enabled_plugin",
            module_path="plugins.enabled",
            class_name="EnabledPlugin",
            enabled=True
        )
        config.add_plugin(enabled_plugin)
        
        # Add disabled plugin
        disabled_plugin = PluginConfig(
            name="disabled_plugin",
            module_path="plugins.disabled",
            class_name="DisabledPlugin",
            enabled=False
        )
        config.add_plugin(disabled_plugin)
        
        enabled_plugins = config.get_enabled_plugins()
        assert len(enabled_plugins) == 1
        assert enabled_plugins[0].name == "enabled_plugin"
    
    def test_extended_validation(self):
        """Test extended validation for new config sections."""
        config = AICouncilConfig()
        
        # Add invalid routing rule
        invalid_rule = RoutingRule(
            name="",  # Empty name should fail
            weight=-1.0  # Negative weight should fail
        )
        config.routing_rules.append(invalid_rule)
        
        with pytest.raises(ValueError, match="Routing rule must have a name"):
            config.validate()
        
        # Fix name but keep negative weight
        invalid_rule.name = "test_rule"
        with pytest.raises(ValueError, match="weight cannot be negative"):
            config.validate()


class TestConfigBuilder:
    """Test ConfigBuilder utility."""
    
    def test_config_builder_basic(self):
        """Test basic config builder functionality."""
        config = (ConfigBuilder()
                 .with_logging(level="DEBUG")
                 .with_system_settings(debug=True)
                 .add_model("test-model", "test-provider", "TEST_API_KEY")
                 .build())
        
        assert config.logging.level == "DEBUG"
        assert config.debug is True
        assert "test-model" in config.models
        assert config.models["test-model"].provider == "test-provider"
    
    def test_config_builder_routing_rules(self):
        """Test adding routing rules with builder."""
        config = (ConfigBuilder()
                 .add_routing_rule("test_rule", 
                                 task_types=[TaskType.REASONING],
                                 preferred_models=["gpt-4"])
                 .build())
        
        assert len(config.routing_rules) == 1
        assert config.routing_rules[0].name == "test_rule"
        assert TaskType.REASONING in config.routing_rules[0].task_types
    
    def test_config_builder_execution_modes(self):
        """Test adding execution modes with builder."""
        config = (ConfigBuilder()
                 .add_execution_mode("custom_fast", ExecutionMode.FAST,
                                   max_parallel=2, timeout=15.0)
                 .build())
        
        assert "custom_fast" in config.execution_modes
        assert config.execution_modes["custom_fast"].mode == ExecutionMode.FAST
        assert config.execution_modes["custom_fast"].max_parallel_executions == 2
    
    def test_config_builder_plugins(self):
        """Test adding plugins with builder."""
        config = (ConfigBuilder()
                 .add_plugin("test_plugin", "plugins.test", "TestPlugin",
                           config={"param": "value"})
                 .build())
        
        assert "test_plugin" in config.plugins
        assert config.plugins["test_plugin"].module_path == "plugins.test"
        assert config.plugins["test_plugin"].config["param"] == "value"
    
    def test_create_development_config(self):
        """Test creating development configuration."""
        config = create_development_config()
        
        assert config.debug is True
        assert config.environment == "development"
        assert config.logging.level == "DEBUG"
        assert config.cost.max_cost_per_request == 1.0
    
    def test_create_production_config(self):
        """Test creating production configuration."""
        config = create_production_config()
        
        assert config.debug is False
        assert config.environment == "production"
        assert config.logging.format_json is True
        assert len(config.models) >= 2
        assert len(config.routing_rules) >= 1
        assert len(config.execution_modes) >= 1