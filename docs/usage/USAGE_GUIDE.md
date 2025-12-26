# 🚀 AI Council Usage Guide

**Complete Guide to Using the Multi-Agent AI Orchestration Platform**

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation & Setup](#installation--setup)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [Configuration](#configuration)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [API Reference](#api-reference)

---

## 🚀 Quick Start

### **5-Minute Setup**

```bash
# 1. Clone the repository
git clone https://github.com/shrixtacy/AI-Council.git
cd AI-Council

# 2. Install dependencies
pip install -e .

# 3. Set Python path (Windows)
$env:PYTHONPATH = "."

# 4. Run your first example
python examples/basic_usage.py
```

### **Your First AI Council Request**

```python
from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode

# Initialize
factory = AICouncilFactory()
council = factory.create_ai_council_sync()

# Process request
response = council.process_request_sync(
    "Explain the benefits of renewable energy",
    ExecutionMode.BALANCED
)

print(f"Response: {response.content}")
print(f"Confidence: {response.overall_confidence}")
print(f"Cost: ${response.cost_breakdown.total_cost:.4f}")
```

---

## 🔧 Installation & Setup

### **System Requirements**

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, Linux
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 1GB free space

### **Installation Methods**

#### **Method 1: Development Installation**
```bash
git clone https://github.com/shrixtacy/AI-Council.git
cd AI-Council
pip install -e .
```

#### **Method 2: Production Installation** *(Coming Soon)*
```bash
pip install ai-council
```

### **Environment Setup**

#### **Windows**
```powershell
# Set Python path
$env:PYTHONPATH = "."

# Verify installation
python -c "import ai_council; print('AI Council installed successfully!')"
```

#### **macOS/Linux**
```bash
# Set Python path
export PYTHONPATH="."

# Verify installation
python -c "import ai_council; print('AI Council installed successfully!')"
```

### **Configuration Files**

Create your configuration file:

```yaml
# config/my_ai_council.yaml
system:
  environment: development
  debug: true
  log_level: INFO

execution:
  default_mode: balanced
  max_parallel_executions: 5
  timeout_seconds: 120

models:
  # Add your AI model configurations here
  mock-gpt-4:
    provider: mock
    capabilities: [reasoning, code_generation, creative_output]
    cost_per_token: 0.00003
    reliability_score: 0.95
```

---

## 📖 Basic Usage

### **Core Concepts**

#### **Execution Modes**
Choose the right mode for your needs:

```python
from ai_council.core.models import ExecutionMode

# Fast: Quick responses, lower cost
ExecutionMode.FAST

# Balanced: Good quality, reasonable cost (recommended)
ExecutionMode.BALANCED  

# Best Quality: Highest quality, premium models
ExecutionMode.BEST_QUALITY
```

#### **Task Types**
AI Council automatically classifies tasks:

- `reasoning`: Logical analysis and problem solving
- `research`: Information gathering and analysis
- `code_generation`: Writing and debugging code
- `creative_output`: Creative writing and content
- `fact_checking`: Verifying information accuracy
- `verification`: Validating results and claims

### **Basic Examples**

#### **Simple Question Answering**
```python
from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode

factory = AICouncilFactory()
council = factory.create_ai_council_sync()

# Simple question
response = council.process_request_sync(
    "What is machine learning?",
    ExecutionMode.FAST
)

print(response.content)
```

#### **Complex Analysis**
```python
# Complex business analysis
response = council.process_request_sync(
    """
    Analyze the pros and cons of implementing a microservices 
    architecture for a mid-sized e-commerce platform. Consider 
    scalability, maintenance, cost, and team structure implications.
    """,
    ExecutionMode.BEST_QUALITY
)

print(f"Analysis: {response.content}")
print(f"Confidence: {response.overall_confidence}")
print(f"Models Used: {', '.join(response.models_used)}")
```

#### **Code Generation**
```python
# Code generation request
response = council.process_request_sync(
    """
    Write a Python function that implements a binary search algorithm.
    Include error handling, type hints, and comprehensive docstring.
    Also explain the time complexity.
    """,
    ExecutionMode.BALANCED
)

print(response.content)
```

### **Working with Responses**

```python
# Process response
response = council.process_request_sync("Your question here", ExecutionMode.BALANCED)

# Access response data
content = response.content                    # Main response text
confidence = response.overall_confidence      # Confidence score (0-1)
models_used = response.models_used           # List of models used
total_cost = response.cost_breakdown.total_cost  # Total cost in USD

# Execution metadata
if response.execution_metadata:
    execution_time = response.execution_metadata.total_time
    subtasks_count = len(response.execution_metadata.subtasks)
    
print(f"Response: {content}")
print(f"Confidence: {confidence:.2f}")
print(f"Cost: ${total_cost:.4f}")
print(f"Execution Time: {execution_time:.2f}s")
```

---

## 🔬 Advanced Features

### **Cost Estimation**

Get cost estimates before processing:

```python
# Estimate cost before processing
estimate = council.estimate_cost_and_time(
    "Complex analysis request here",
    ExecutionMode.BEST_QUALITY
)

print(f"Estimated Cost: ${estimate.total_cost:.4f}")
print(f"Estimated Time: {estimate.total_time:.1f}s")
print(f"Confidence: {estimate.confidence:.2f}")

# Proceed if cost is acceptable
if estimate.total_cost < 1.0:  # Less than $1
    response = council.process_request_sync(
        "Complex analysis request here",
        ExecutionMode.BEST_QUALITY
    )
```

### **System Status Monitoring**

```python
# Check system health
status = council.get_system_status()

print(f"Status: {status.status}")
print(f"Health: {status.health}")
print(f"Available Models: {len(status.available_models)}")
print(f"Circuit Breakers: {len(status.circuit_breakers)}")

# Check individual components
for component, state in status.circuit_breakers.items():
    print(f"  {component}: {state}")
```

### **Batch Processing**

Process multiple requests efficiently:

```python
requests = [
    ("What is artificial intelligence?", ExecutionMode.FAST),
    ("Explain quantum computing", ExecutionMode.BALANCED),
    ("Write a sorting algorithm in Python", ExecutionMode.BALANCED)
]

responses = []
for query, mode in requests:
    response = council.process_request_sync(query, mode)
    responses.append(response)
    print(f"Processed: {query[:30]}... (${response.cost_breakdown.total_cost:.4f})")

total_cost = sum(r.cost_breakdown.total_cost for r in responses)
print(f"Total Cost: ${total_cost:.4f}")
```

### **Custom Configuration**

```python
from ai_council.utils.config_builder import ConfigBuilder
from ai_council.core.models import TaskType

# Build custom configuration
config = (ConfigBuilder()
    .with_execution_mode("custom_fast",
        max_parallel_executions=3,
        timeout_seconds=30.0,
        accuracy_requirement=0.7,
        cost_limit_dollars=5.0
    )
    .with_routing_rule("high_accuracy_reasoning",
        task_types=[TaskType.REASONING],
        execution_modes=["best_quality"],
        min_confidence=0.9,
        priority=1
    )
    .build()
)

# Use custom configuration
factory = AICouncilFactory(config=config)
council = factory.create_ai_council_sync()
```

---

## ⚙️ Configuration

### **Configuration Hierarchy**

AI Council uses a hierarchical configuration system:

1. **Default Configuration**: Built-in defaults
2. **System Configuration**: `config/ai_council_example.yaml`
3. **User Configuration**: Custom YAML files
4. **Environment Variables**: Runtime overrides
5. **Programmatic Configuration**: Code-based configuration

### **Configuration File Structure**

```yaml
# Complete configuration example
system:
  environment: production          # development, staging, production
  debug: false                    # Enable debug logging
  log_level: INFO                 # DEBUG, INFO, WARNING, ERROR

execution:
  default_mode: balanced          # fast, balanced, best_quality
  max_parallel_executions: 10     # Maximum concurrent subtasks
  timeout_seconds: 300            # Request timeout
  enable_arbitration: true        # Enable conflict resolution
  enable_synthesis: true          # Enable output synthesis

models:
  gpt-4:
    provider: openai
    api_key_env: OPENAI_API_KEY
    model_name: gpt-4
    max_tokens: 4096
    temperature: 0.7
    cost_per_input_token: 0.00003
    cost_per_output_token: 0.00006
    average_latency: 3.0
    reliability_score: 0.95
    max_context_length: 8192
    capabilities:
      - reasoning
      - code_generation
      - creative_output
    strengths:
      - complex reasoning
      - code generation
      - creative tasks
    weaknesses:
      - high cost
      - slower response

routing:
  rules:
    - name: high_accuracy_reasoning
      task_types: [reasoning]
      execution_modes: [best_quality]
      min_confidence: 0.9
      preferred_models: [gpt-4, claude-3]
      priority: 1
      
    - name: cost_effective_general
      task_types: [creative_output, research]
      execution_modes: [fast, balanced]
      min_confidence: 0.7
      preferred_models: [gpt-3.5-turbo]
      priority: 2

cost:
  max_cost_per_request: 10.0      # Maximum cost per request
  enable_cost_tracking: true      # Track and log costs
  cost_alerts:
    - threshold: 5.0
      action: warn
    - threshold: 8.0
      action: require_approval

monitoring:
  enable_metrics: true            # Enable metrics collection
  metrics_endpoint: /metrics      # Prometheus metrics endpoint
  health_check_endpoint: /health  # Health check endpoint
  
logging:
  format: json                    # json, text
  level: INFO                     # DEBUG, INFO, WARNING, ERROR
  file: logs/ai_council.log      # Log file path
  max_size_mb: 100               # Max log file size
  backup_count: 5                # Number of backup files
```

### **Environment Variables**

Override configuration with environment variables:

```bash
# Model API Keys
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_AI_API_KEY="your-google-key"

# System Configuration
export AI_COUNCIL_LOG_LEVEL="DEBUG"
export AI_COUNCIL_MAX_COST="5.0"
export AI_COUNCIL_TIMEOUT="120"

# Database Configuration (if using persistence)
export AI_COUNCIL_DB_URL="postgresql://user:pass@localhost/ai_council"
export AI_COUNCIL_REDIS_URL="redis://localhost:6379"
```

---

## 🎯 Best Practices

### **Choosing Execution Modes**

| Use Case | Recommended Mode | Reasoning |
|----------|------------------|-----------|
| **FAQ/Simple Questions** | FAST | Quick responses, cost-effective |
| **Business Analysis** | BALANCED | Good quality-cost balance |
| **Strategic Decisions** | BEST_QUALITY | Maximum accuracy needed |
| **Code Generation** | BALANCED | Good balance for most coding tasks |
| **Creative Writing** | FAST or BALANCED | Depends on quality requirements |
| **Research Tasks** | BEST_QUALITY | Comprehensive analysis needed |

### **Cost Optimization**

```python
# 1. Use cost estimation
estimate = council.estimate_cost_and_time(query, mode)
if estimate.total_cost > budget_limit:
    # Use faster mode or simplify query
    mode = ExecutionMode.FAST

# 2. Batch similar requests
similar_queries = [
    "Explain AI concept 1",
    "Explain AI concept 2", 
    "Explain AI concept 3"
]

# Process in batch for better efficiency
for query in similar_queries:
    response = council.process_request_sync(query, ExecutionMode.FAST)

# 3. Cache responses for repeated queries
response_cache = {}
def cached_request(query, mode):
    cache_key = f"{query}:{mode.value}"
    if cache_key not in response_cache:
        response_cache[cache_key] = council.process_request_sync(query, mode)
    return response_cache[cache_key]
```

### **Error Handling**

```python
from ai_council.core.models import AICouncilError, ExecutionError

try:
    response = council.process_request_sync(
        "Your query here",
        ExecutionMode.BALANCED
    )
    
    # Check response quality
    if response.overall_confidence < 0.7:
        print("Warning: Low confidence response")
        
except ExecutionError as e:
    print(f"Execution failed: {e}")
    # Retry with different mode or simplified query
    
except AICouncilError as e:
    print(f"AI Council error: {e}")
    # Handle system-level errors
    
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle unexpected errors
```

### **Performance Optimization**

```python
# 1. Reuse AI Council instances
factory = AICouncilFactory()
council = factory.create_ai_council_sync()  # Create once

# Use the same instance for multiple requests
for query in queries:
    response = council.process_request_sync(query, ExecutionMode.BALANCED)

# 2. Use appropriate timeouts
config = ConfigBuilder().with_timeout(60).build()  # 60 seconds
factory = AICouncilFactory(config=config)

# 3. Monitor system resources
status = council.get_system_status()
if status.health != "healthy":
    # Take corrective action
    council.restart_unhealthy_components()
```

### **Quality Assurance**

```python
# 1. Check confidence scores
response = council.process_request_sync(query, mode)
if response.overall_confidence < 0.8:
    # Request higher quality mode
    response = council.process_request_sync(query, ExecutionMode.BEST_QUALITY)

# 2. Validate critical responses
if is_critical_decision(query):
    # Use best quality mode
    response = council.process_request_sync(query, ExecutionMode.BEST_QUALITY)
    
    # Additional validation
    if response.overall_confidence < 0.9:
        # Manual review required
        flag_for_human_review(response)

# 3. Log important decisions
if response.cost_breakdown.total_cost > 1.0:  # Expensive requests
    log_expensive_request(query, response)
```

---

## 🔧 Troubleshooting

### **Common Issues**

#### **Installation Issues**

**Problem**: `ModuleNotFoundError: No module named 'ai_council'`
```bash
# Solution: Set Python path
$env:PYTHONPATH = "."  # Windows
export PYTHONPATH="."  # macOS/Linux

# Or install in development mode
pip install -e .
```

**Problem**: `ImportError: cannot import name 'AICouncilFactory'`
```bash
# Solution: Check installation
python -c "import ai_council; print(ai_council.__file__)"

# Reinstall if needed
pip uninstall ai-council
pip install -e .
```

#### **Runtime Issues**

**Problem**: `TimeoutError: Request timed out`
```python
# Solution: Increase timeout or use faster mode
config = ConfigBuilder().with_timeout(300).build()  # 5 minutes
factory = AICouncilFactory(config=config)

# Or use faster execution mode
response = council.process_request_sync(query, ExecutionMode.FAST)
```

**Problem**: `CostLimitExceededError: Request exceeds cost limit`
```python
# Solution: Increase cost limit or optimize request
config = ConfigBuilder().with_max_cost(20.0).build()  # $20 limit
factory = AICouncilFactory(config=config)

# Or estimate cost first
estimate = council.estimate_cost_and_time(query, mode)
if estimate.total_cost > 10.0:
    # Simplify query or use faster mode
    mode = ExecutionMode.FAST
```

#### **Quality Issues**

**Problem**: Low confidence responses
```python
# Check confidence and retry with higher quality
response = council.process_request_sync(query, ExecutionMode.BALANCED)
if response.overall_confidence < 0.7:
    # Retry with best quality mode
    response = council.process_request_sync(query, ExecutionMode.BEST_QUALITY)
```

**Problem**: Inconsistent responses
```python
# Enable arbitration for consistency
config = ConfigBuilder().with_arbitration(True).build()
factory = AICouncilFactory(config=config)
```

### **Debugging**

#### **Enable Debug Logging**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in configuration
config = ConfigBuilder().with_log_level("DEBUG").build()
```

#### **System Health Check**
```python
# Check system status
status = council.get_system_status()
print(f"Status: {status.status}")
print(f"Health: {status.health}")

# Check individual components
for component, state in status.circuit_breakers.items():
    if state != "closed":
        print(f"Issue with {component}: {state}")
```

#### **Performance Monitoring**
```python
import time

start_time = time.time()
response = council.process_request_sync(query, mode)
execution_time = time.time() - start_time

print(f"Execution time: {execution_time:.2f}s")
print(f"Cost: ${response.cost_breakdown.total_cost:.4f}")
print(f"Models used: {len(response.models_used)}")
```

---

## 📚 API Reference

### **Core Classes**

#### **AICouncilFactory**
```python
class AICouncilFactory:
    def __init__(self, config: AICouncilConfig = None):
        """Initialize factory with optional configuration."""
        
    def create_ai_council_sync(self) -> AICouncil:
        """Create synchronous AI Council instance."""
        
    async def create_ai_council(self) -> AICouncil:
        """Create asynchronous AI Council instance."""
```

#### **AICouncil**
```python
class AICouncil:
    def process_request_sync(self, query: str, mode: ExecutionMode) -> FinalResponse:
        """Process request synchronously."""
        
    async def process_request(self, query: str, mode: ExecutionMode) -> FinalResponse:
        """Process request asynchronously."""
        
    def estimate_cost_and_time(self, query: str, mode: ExecutionMode) -> CostEstimate:
        """Estimate cost and time for request."""
        
    def get_system_status(self) -> SystemStatus:
        """Get current system status."""
```

#### **ExecutionMode**
```python
class ExecutionMode(Enum):
    FAST = "fast"
    BALANCED = "balanced"
    BEST_QUALITY = "best_quality"
```

#### **FinalResponse**
```python
@dataclass
class FinalResponse:
    content: str                           # Main response content
    overall_confidence: float              # Confidence score (0-1)
    execution_metadata: ExecutionMetadata  # Execution details
    cost_breakdown: CostBreakdown         # Cost information
    models_used: List[str]                # Models used
```

### **Configuration Classes**

#### **ConfigBuilder**
```python
class ConfigBuilder:
    def with_execution_mode(self, name: str, **kwargs) -> ConfigBuilder:
        """Add custom execution mode."""
        
    def with_routing_rule(self, name: str, **kwargs) -> ConfigBuilder:
        """Add routing rule."""
        
    def with_model(self, name: str, **kwargs) -> ConfigBuilder:
        """Add model configuration."""
        
    def with_timeout(self, seconds: int) -> ConfigBuilder:
        """Set request timeout."""
        
    def with_max_cost(self, dollars: float) -> ConfigBuilder:
        """Set maximum cost per request."""
        
    def build(self) -> AICouncilConfig:
        """Build final configuration."""
```

---

## 🎓 Examples & Tutorials

### **Complete Examples**

Check out these comprehensive examples:

- **[Basic Usage](../usage/how_to_use.py)** - Simple integration
- **[Custom Configuration](../usage/custom_config_example.py)** - Advanced configuration
- **[Usage Examples](../usage/usage_example.py)** - Comprehensive usage patterns

### **Integration Examples**

- **[Basic Integration](../../examples/basic_usage.py)** - Infrastructure demo
- **[Complete Integration](../../examples/complete_integration.py)** - Full system demo
- **[Orchestration Example](../../examples/orchestration_example.py)** - Advanced orchestration
- **[Configuration Example](../../examples/configuration_example.py)** - Configuration management

---

## 🆘 Getting Help

### **Documentation**
- **[Architecture Guide](../architecture/ARCHITECTURE.md)** - Deep dive into system design
- **[Business Case](../business/BUSINESS_CASE.md)** - Value proposition and ROI
- **[System Validation](../system_validation_report.md)** - Test results and validation

### **Community**
- **GitHub Issues**: [Report bugs and request features](https://github.com/shrixtacy/AI-Council/issues)
- **Discussions**: [Community discussions and Q&A](https://github.com/shrixtacy/AI-Council/discussions)

### **Support**
- **Email**: support@ai-council.com
- **Documentation**: [Complete documentation](https://ai-council.com/docs)
- **Status Page**: [System status and updates](https://status.ai-council.com)

---

**Happy orchestrating! 🎉**