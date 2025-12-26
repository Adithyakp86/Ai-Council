"""Configuration builder utilities for AI Council."""

from typing import Dict, List, Optional, Any
from pathlib import Path

from ..core.models import TaskType, ExecutionMode, Priority, RiskLevel
from .config import (
    AICouncilConfig, ModelConfig, RoutingRule, ExecutionModeConfig, 
    PluginConfig, LoggingConfig, ExecutionConfig, CostConfig
)


class ConfigBuilder:
    """Builder class for creating AI Council configurations."""
    
    def __init__(self):
        """Initialize the configuration builder."""
        self.config = AICouncilConfig()
    
    def with_logging(self, level: str = "INFO", format_json: bool = False, 
                    include_timestamp: bool = True, include_caller: bool = False) -> "ConfigBuilder":
        """Configure logging settings.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format_json: Whether to format logs as JSON
            include_timestamp: Whether to include timestamps
            include_caller: Whether to include caller information
            
        Returns:
            Self for method chaining
        """
        self.config.logging = LoggingConfig(
            level=level,
            format_json=format_json,
            include_timestamp=include_timestamp,
            include_caller=include_caller
        )
        return self
    
    def with_execution(self, default_mode: ExecutionMode = ExecutionMode.BALANCED,
                      max_parallel: int = 5, timeout: float = 60.0, max_retries: int = 3,
                      enable_arbitration: bool = True, enable_synthesis: bool = True,
                      accuracy_requirement: float = 0.8) -> "ConfigBuilder":
        """Configure execution settings.
        
        Args:
            default_mode: Default execution mode
            max_parallel: Maximum parallel executions
            timeout: Default timeout in seconds
            max_retries: Maximum retry attempts
            enable_arbitration: Whether to enable arbitration
            enable_synthesis: Whether to enable synthesis
            accuracy_requirement: Default accuracy requirement
            
        Returns:
            Self for method chaining
        """
        self.config.execution = ExecutionConfig(
            default_mode=default_mode,
            max_parallel_executions=max_parallel,
            default_timeout_seconds=timeout,
            max_retries=max_retries,
            enable_arbitration=enable_arbitration,
            enable_synthesis=enable_synthesis,
            default_accuracy_requirement=accuracy_requirement
        )
        return self
    
    def with_cost_management(self, max_cost_per_request: float = 10.0, currency: str = "USD",
                           enable_tracking: bool = True, alert_threshold: float = 5.0) -> "ConfigBuilder":
        """Configure cost management settings.
        
        Args:
            max_cost_per_request: Maximum cost per request
            currency: Currency for cost calculations
            enable_tracking: Whether to enable cost tracking
            alert_threshold: Cost alert threshold
            
        Returns:
            Self for method chaining
        """
        self.config.cost = CostConfig(
            max_cost_per_request=max_cost_per_request,
            currency=currency,
            enable_cost_tracking=enable_tracking,
            cost_alert_threshold=alert_threshold
        )
        return self
    
    def add_model(self, name: str, provider: str, api_key_env: str,
                  cost_per_input_token: float = 0.0, cost_per_output_token: float = 0.0,
                  max_context_length: int = 4096, capabilities: Optional[List[str]] = None,
                  supported_task_types: Optional[List[TaskType]] = None,
                  reliability_score: float = 0.8, average_latency: float = 2.0,
                  strengths: Optional[List[str]] = None, weaknesses: Optional[List[str]] = None,
                  base_url: Optional[str] = None, max_retries: int = 3, 
                  timeout_seconds: float = 30.0, enabled: bool = True) -> "ConfigBuilder":
        """Add a model configuration.
        
        Args:
            name: Model name
            provider: Model provider
            api_key_env: Environment variable for API key
            cost_per_input_token: Cost per input token
            cost_per_output_token: Cost per output token
            max_context_length: Maximum context length
            capabilities: List of capabilities
            supported_task_types: List of supported task types
            reliability_score: Reliability score (0.0-1.0)
            average_latency: Average latency in seconds
            strengths: List of model strengths
            weaknesses: List of model weaknesses
            base_url: Optional base URL for API
            max_retries: Maximum retry attempts
            timeout_seconds: Timeout in seconds
            enabled: Whether model is enabled
            
        Returns:
            Self for method chaining
        """
        model_config = ModelConfig(
            name=name,
            provider=provider,
            api_key_env=api_key_env,
            base_url=base_url,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            cost_per_input_token=cost_per_input_token,
            cost_per_output_token=cost_per_output_token,
            max_context_length=max_context_length,
            capabilities=capabilities or [],
            enabled=enabled,
            reliability_score=reliability_score,
            average_latency=average_latency,
            strengths=strengths or [],
            weaknesses=weaknesses or [],
            supported_task_types=supported_task_types or [],
        )
        self.config.models[name] = model_config
        return self
    
    def add_routing_rule(self, name: str, task_types: Optional[List[TaskType]] = None,
                        priority_levels: Optional[List[Priority]] = None,
                        risk_levels: Optional[List[RiskLevel]] = None,
                        execution_modes: Optional[List[ExecutionMode]] = None,
                        preferred_models: Optional[List[str]] = None,
                        excluded_models: Optional[List[str]] = None,
                        cost_threshold: Optional[float] = None,
                        accuracy_threshold: Optional[float] = None,
                        latency_threshold: Optional[float] = None,
                        weight: float = 1.0, enabled: bool = True) -> "ConfigBuilder":
        """Add a routing rule.
        
        Args:
            name: Rule name
            task_types: Task types this rule applies to
            priority_levels: Priority levels this rule applies to
            risk_levels: Risk levels this rule applies to
            execution_modes: Execution modes this rule applies to
            preferred_models: Preferred models for this rule
            excluded_models: Models to exclude for this rule
            cost_threshold: Cost threshold
            accuracy_threshold: Accuracy threshold
            latency_threshold: Latency threshold
            weight: Rule weight for prioritization
            enabled: Whether rule is enabled
            
        Returns:
            Self for method chaining
        """
        rule = RoutingRule(
            name=name,
            task_types=task_types or [],
            priority_levels=priority_levels or [],
            risk_levels=risk_levels or [],
            execution_modes=execution_modes or [],
            preferred_models=preferred_models or [],
            excluded_models=excluded_models or [],
            cost_threshold=cost_threshold,
            accuracy_threshold=accuracy_threshold,
            latency_threshold=latency_threshold,
            enabled=enabled,
            weight=weight
        )
        self.config.routing_rules.append(rule)
        return self
    
    def add_execution_mode(self, name: str, mode: ExecutionMode,
                          max_parallel: int = 5, timeout: float = 60.0, max_retries: int = 3,
                          enable_arbitration: bool = True, enable_synthesis: bool = True,
                          accuracy_requirement: float = 0.8, cost_limit: Optional[float] = None,
                          preferred_model_types: Optional[List[str]] = None,
                          fallback_strategy: str = "automatic") -> "ConfigBuilder":
        """Add an execution mode configuration.
        
        Args:
            name: Mode name
            mode: Execution mode enum
            max_parallel: Maximum parallel executions
            timeout: Timeout in seconds
            max_retries: Maximum retry attempts
            enable_arbitration: Whether to enable arbitration
            enable_synthesis: Whether to enable synthesis
            accuracy_requirement: Accuracy requirement
            cost_limit: Optional cost limit
            preferred_model_types: Preferred model types
            fallback_strategy: Fallback strategy
            
        Returns:
            Self for method chaining
        """
        mode_config = ExecutionModeConfig(
            mode=mode,
            max_parallel_executions=max_parallel,
            timeout_seconds=timeout,
            max_retries=max_retries,
            enable_arbitration=enable_arbitration,
            enable_synthesis=enable_synthesis,
            accuracy_requirement=accuracy_requirement,
            cost_limit=cost_limit,
            preferred_model_types=preferred_model_types or [],
            fallback_strategy=fallback_strategy
        )
        self.config.execution_modes[name] = mode_config
        return self
    
    def add_plugin(self, name: str, module_path: str, class_name: str,
                  enabled: bool = True, config: Optional[Dict[str, Any]] = None,
                  dependencies: Optional[List[str]] = None, version: str = "1.0.0") -> "ConfigBuilder":
        """Add a plugin configuration.
        
        Args:
            name: Plugin name
            module_path: Python module path
            class_name: Class name within the module
            enabled: Whether plugin is enabled
            config: Plugin-specific configuration
            dependencies: List of required dependencies
            version: Plugin version
            
        Returns:
            Self for method chaining
        """
        plugin_config = PluginConfig(
            name=name,
            module_path=module_path,
            class_name=class_name,
            enabled=enabled,
            config=config or {},
            dependencies=dependencies or [],
            version=version
        )
        self.config.plugins[name] = plugin_config
        return self
    
    def with_directories(self, data_dir: str = "./data", cache_dir: str = "./cache",
                        plugin_dir: str = "./plugins") -> "ConfigBuilder":
        """Configure directory paths.
        
        Args:
            data_dir: Data directory path
            cache_dir: Cache directory path
            plugin_dir: Plugin directory path
            
        Returns:
            Self for method chaining
        """
        self.config.data_dir = data_dir
        self.config.cache_dir = cache_dir
        self.config.plugin_dir = plugin_dir
        return self
    
    def with_system_settings(self, debug: bool = False, environment: str = "production") -> "ConfigBuilder":
        """Configure system settings.
        
        Args:
            debug: Whether to enable debug mode
            environment: Environment name
            
        Returns:
            Self for method chaining
        """
        self.config.debug = debug
        self.config.environment = environment
        return self
    
    def build(self) -> AICouncilConfig:
        """Build and validate the configuration.
        
        Returns:
            The built configuration
            
        Raises:
            ValueError: If configuration is invalid
        """
        self.config.validate()
        return self.config
    
    def save_to_file(self, file_path: Path) -> AICouncilConfig:
        """Build, validate, and save the configuration to a file.
        
        Args:
            file_path: Path to save the configuration
            
        Returns:
            The built configuration
        """
        config = self.build()
        config.save_to_file(file_path)
        return config


def create_openai_model_config(model_name: str, cost_per_input: float, cost_per_output: float,
                              context_length: int = 4096, task_types: Optional[List[TaskType]] = None) -> ModelConfig:
    """Create a standard OpenAI model configuration.
    
    Args:
        model_name: Name of the OpenAI model
        cost_per_input: Cost per input token
        cost_per_output: Cost per output token
        context_length: Maximum context length
        task_types: Supported task types
        
    Returns:
        Model configuration
    """
    return ModelConfig(
        name=model_name,
        provider="openai",
        api_key_env="OPENAI_API_KEY",
        cost_per_input_token=cost_per_input,
        cost_per_output_token=cost_per_output,
        max_context_length=context_length,
        capabilities=["reasoning", "code_generation", "creative_output"],
        reliability_score=0.9,
        average_latency=2.0,
        supported_task_types=task_types or [TaskType.REASONING, TaskType.CODE_GENERATION],
        enabled=True
    )


def create_anthropic_model_config(model_name: str, cost_per_input: float, cost_per_output: float,
                                 context_length: int = 200000, task_types: Optional[List[TaskType]] = None) -> ModelConfig:
    """Create a standard Anthropic model configuration.
    
    Args:
        model_name: Name of the Anthropic model
        cost_per_input: Cost per input token
        cost_per_output: Cost per output token
        context_length: Maximum context length
        task_types: Supported task types
        
    Returns:
        Model configuration
    """
    return ModelConfig(
        name=model_name,
        provider="anthropic",
        api_key_env="ANTHROPIC_API_KEY",
        cost_per_input_token=cost_per_input,
        cost_per_output_token=cost_per_output,
        max_context_length=context_length,
        capabilities=["reasoning", "research", "fact_checking"],
        reliability_score=0.92,
        average_latency=2.5,
        supported_task_types=task_types or [TaskType.REASONING, TaskType.RESEARCH, TaskType.FACT_CHECKING],
        enabled=True
    )


def create_development_config() -> AICouncilConfig:
    """Create a configuration suitable for development.
    
    Returns:
        Development configuration
    """
    return (ConfigBuilder()
            .with_logging(level="DEBUG", include_caller=True)
            .with_system_settings(debug=True, environment="development")
            .with_cost_management(max_cost_per_request=1.0, alert_threshold=0.5)
            .add_model("gpt-3.5-turbo", "openai", "OPENAI_API_KEY",
                      cost_per_input_token=0.0000015, cost_per_output_token=0.000002,
                      supported_task_types=[TaskType.REASONING])
            .add_routing_rule("dev_fast", preferred_models=["gpt-3.5-turbo"], weight=2.0)
            .build())


def create_production_config() -> AICouncilConfig:
    """Create a configuration suitable for production.
    
    Returns:
        Production configuration
    """
    return (ConfigBuilder()
            .with_logging(level="INFO", format_json=True)
            .with_system_settings(debug=False, environment="production")
            .with_execution(max_parallel=10, timeout=120.0)
            .add_model("gpt-4", "openai", "OPENAI_API_KEY",
                      cost_per_input_token=0.00003, cost_per_output_token=0.00006,
                      supported_task_types=[TaskType.REASONING, TaskType.CODE_GENERATION])
            .add_model("claude-3", "anthropic", "ANTHROPIC_API_KEY",
                      cost_per_input_token=0.000015, cost_per_output_token=0.000075,
                      supported_task_types=[TaskType.REASONING, TaskType.RESEARCH])
            .add_routing_rule("high_quality", task_types=[TaskType.REASONING],
                            preferred_models=["gpt-4", "claude-3"], accuracy_threshold=0.9)
            .add_execution_mode("production", ExecutionMode.BEST_QUALITY,
                              max_parallel=8, timeout=180.0, accuracy_requirement=0.95)
            .build())