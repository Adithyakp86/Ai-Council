# AI Council API Reference

## Overview

This document provides comprehensive API reference for the AI Council library. All classes, methods, and interfaces are documented with examples and usage patterns.

## Core Classes

### AICouncilFactory

The main entry point for creating AI Council instances.

```python
from ai_council.factory import AICouncilFactory

factory = AICouncilFactory(config=None)
```

#### Methods

##### `create_ai_council_sync() -> AICouncilApp`

Creates a synchronous AI Council instance.

**Returns:** `AICouncilApp` - Configured AI Council application

**Example:**
```python
factory = AICouncilFactory()
ai_council = factory.create_ai_council_sync()
```

##### `create_ai_council() -> AICouncilApp` (Async)

Creates an asynchronous AI Council instance.

**Returns:** `AICouncilApp` - Configured AI Council application

**Example:**
```python
factory = AICouncilFactory()
ai_council = await factory.create_ai_council()
```

---

### AICouncilApp

Main application class for processing requests.

#### Methods

##### `process_request_sync(text: str, mode: ExecutionMode) -> FinalResponse`

Process a request synchronously.

**Parameters:**
- `text` (str): The input text to process
- `mode` (ExecutionMode): Execution mode (FAST, BALANCED, BEST_QUALITY)

**Returns:** `FinalResponse` - Complete response with metadata

**Example:**
```python
response = ai_council.process_request_sync(
    "Explain quantum computing",
    ExecutionMode.BALANCED
)
print(response.content)
```

##### `estimate_cost_and_time(text: str, mode: ExecutionMode) -> CostEstimate`

Estimate cost and time before processing.

**Parameters:**
- `text` (str): The input text to analyze
- `mode` (ExecutionMode): Execution mode

**Returns:** `CostEstimate` - Cost and time estimates

**Example:**
```python
estimate = ai_council.estimate_cost_and_time(
    "Complex analysis task",
    ExecutionMode.BEST_QUALITY
)
print(f"Cost: ${estimate.total_cost:.4f}")
print(f"Time: {estimate.total_time:.1f}s")
```

##### `get_system_status() -> SystemStatus`

Get current system health and status.

**Returns:** `SystemStatus` - System health information

**Example:**
```python
status = ai_council.get_system_status()
print(f"Status: {status.status}")
print(f"Health: {status.health}")
```

---

## Data Models

### ExecutionMode

Enumeration of available execution modes.

```python
from ai_council.core.models import ExecutionMode

# Available modes
ExecutionMode.FAST          # Quick, cost-effective
ExecutionMode.BALANCED      # Balanced quality/cost
ExecutionMode.BEST_QUALITY  # Highest quality
```

### Task

Represents a user request to be processed.

```python
@dataclass
class Task:
    id: str
    content: str
    intent: str
    complexity: str
    execution_mode: ExecutionMode
    created_at: datetime
```

**Example:**
```python
from ai_council.core.models import Task, ExecutionMode
from datetime import datetime
import uuid

task = Task(
    id=str(uuid.uuid4()),
    content="Analyze market trends",
    intent="research_and_analysis",
    complexity="medium",
    execution_mode=ExecutionMode.BALANCED,
    created_at=datetime.now()
)
```

### FinalResponse

Complete response from AI Council processing.

```python
@dataclass
class FinalResponse:
    content: str
    overall_confidence: float
    execution_metadata: Optional[ExecutionMetadata]
    cost_breakdown: CostBreakdown
    models_used: List[str]
```

**Properties:**
- `content`: The final synthesized response
- `overall_confidence`: Confidence score (0.0 to 1.0)
- `execution_metadata`: Processing metadata
- `cost_breakdown`: Detailed cost information
- `models_used`: List of AI models used

### CostBreakdown

Detailed cost information for a request.

```python
@dataclass
class CostBreakdown:
    total_cost: float
    model_costs: Dict[str, float]
    token_usage: Dict[str, int]
    execution_time: float
```

### SystemStatus

System health and status information.

```python
@dataclass
class SystemStatus:
    status: str              # "operational", "degraded", "down"
    health: str              # "healthy", "warning", "critical"
    available_models: List[str]
    circuit_breakers: Dict[str, str]
    performance_metrics: Dict[str, float]
```

---

## Configuration Classes

### AICouncilConfig

Main configuration class for AI Council.

```python
from ai_council.utils.config import AICouncilConfig

config = AICouncilConfig(
    models={},
    execution_modes={},
    routing_rules=[],
    plugins=[]
)
```

### ConfigBuilder

Builder pattern for creating configurations.

```python
from ai_council.utils.config_builder import ConfigBuilder

config = (ConfigBuilder()
    .with_execution_mode("custom_fast", 
        max_parallel_executions=3,
        timeout_seconds=30.0
    )
    .with_routing_rule("high_accuracy",
        task_types=[TaskType.REASONING],
        min_confidence=0.9
    )
    .build()
)
```

#### Methods

##### `with_execution_mode(name: str, **kwargs) -> ConfigBuilder`

Add custom execution mode.

**Parameters:**
- `name` (str): Mode name
- `max_parallel_executions` (int): Max parallel tasks
- `timeout_seconds` (float): Timeout limit
- `accuracy_requirement` (float): Required accuracy (0.0-1.0)
- `cost_limit_dollars` (float): Cost limit

##### `with_routing_rule(name: str, **kwargs) -> ConfigBuilder`

Add routing rule for task assignment.

**Parameters:**
- `name` (str): Rule name
- `task_types` (List[TaskType]): Applicable task types
- `execution_modes` (List[str]): Applicable execution modes
- `min_confidence` (float): Minimum confidence required
- `priority` (int): Rule priority

##### `build() -> AICouncilConfig`

Build the final configuration.

---

## Component Interfaces

### AnalysisEngine

Analyzes user input and determines processing strategy.

```python
from ai_council.analysis.engine import AnalysisEngine

engine = AnalysisEngine()
```

#### Methods

##### `analyze_intent(input_text: str) -> str`

Analyze user intent from input text.

##### `determine_complexity(input_text: str) -> str`

Determine task complexity level.

##### `classify_task_type(input_text: str) -> List[TaskType]`

Classify the type of task from input.

### TaskDecomposer

Breaks complex tasks into manageable subtasks.

```python
from ai_council.analysis.decomposer import TaskDecomposer

decomposer = TaskDecomposer()
```

#### Methods

##### `decompose(task: Task) -> List[Subtask]`

Decompose a task into subtasks.

##### `validate_decomposition(subtasks: List[Subtask]) -> bool`

Validate that decomposition is complete and consistent.

### ModelRegistry

Manages available AI models and their capabilities.

```python
from ai_council.routing.registry import ModelRegistry

registry = ModelRegistry()
```

#### Methods

##### `register_model(model_id: str, capabilities: ModelCapabilities) -> None`

Register a new AI model.

##### `get_models_for_task_type(task_type: TaskType) -> List[str]`

Get suitable models for a task type.

##### `get_model_cost_profile(model_id: str) -> CostProfile`

Get cost information for a model.

---

## Error Handling

### AICouncilError

Base exception class for AI Council errors.

```python
from ai_council.core.interfaces import AICouncilError

try:
    response = ai_council.process_request_sync(text, mode)
except AICouncilError as e:
    print(f"AI Council error: {e}")
```

### Common Exceptions

- `ModelNotFoundError`: Requested model not available
- `TaskDecompositionError`: Failed to decompose task
- `ArbitrationError`: Failed to resolve conflicts
- `CostLimitExceededError`: Request exceeds cost limits
- `TimeoutError`: Request timed out

---

## Usage Patterns

### Basic Usage

```python
from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode

# Initialize
factory = AICouncilFactory()
ai_council = factory.create_ai_council_sync()

# Process request
response = ai_council.process_request_sync(
    "Your question here",
    ExecutionMode.BALANCED
)

print(response.content)
```

### With Cost Estimation

```python
# Estimate first
estimate = ai_council.estimate_cost_and_time(text, mode)
print(f"Estimated cost: ${estimate.total_cost:.4f}")

if estimate.total_cost < 1.0:  # Budget check
    response = ai_council.process_request_sync(text, mode)
```

### Custom Configuration

```python
from ai_council.utils.config_builder import ConfigBuilder

config = (ConfigBuilder()
    .with_execution_mode("fast_mode", 
        max_parallel_executions=2,
        timeout_seconds=15.0
    )
    .build()
)

factory = AICouncilFactory(config=config)
ai_council = factory.create_ai_council_sync()
```

### Error Handling

```python
from ai_council.core.interfaces import AICouncilError

try:
    response = ai_council.process_request_sync(text, mode)
    print(f"Success: {response.content}")
except AICouncilError as e:
    print(f"Error: {e}")
    # Handle error appropriately
```

---

## Performance Considerations

### Execution Modes

- **FAST**: ~1-3 seconds, $0.001-0.01 per request
- **BALANCED**: ~3-10 seconds, $0.01-0.05 per request  
- **BEST_QUALITY**: ~10-30 seconds, $0.05-0.20 per request

### Optimization Tips

1. **Use appropriate execution mode** for your use case
2. **Estimate costs** before processing expensive requests
3. **Configure timeouts** based on your requirements
4. **Monitor system status** for health checks
5. **Use caching** for repeated similar requests

---

## Integration Examples

### Web API Integration

```python
from flask import Flask, request, jsonify
from ai_council.factory import AICouncilFactory

app = Flask(__name__)
ai_council = AICouncilFactory().create_ai_council_sync()

@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    
    try:
        response = ai_council.process_request_sync(
            data['text'],
            ExecutionMode[data.get('mode', 'BALANCED')]
        )
        
        return jsonify({
            'content': response.content,
            'confidence': response.overall_confidence,
            'cost': response.cost_breakdown.total_cost
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Batch Processing

```python
def process_batch(requests):
    results = []
    
    for req in requests:
        try:
            response = ai_council.process_request_sync(
                req['text'], 
                req.get('mode', ExecutionMode.BALANCED)
            )
            results.append({
                'id': req['id'],
                'response': response.content,
                'confidence': response.overall_confidence
            })
        except Exception as e:
            results.append({
                'id': req['id'],
                'error': str(e)
            })
    
    return results
```

---

## Testing

### Unit Testing

```python
import unittest
from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode

class TestAICouncil(unittest.TestCase):
    def setUp(self):
        self.ai_council = AICouncilFactory().create_ai_council_sync()
    
    def test_basic_processing(self):
        response = self.ai_council.process_request_sync(
            "Test question",
            ExecutionMode.FAST
        )
        self.assertIsNotNone(response.content)
        self.assertGreater(response.overall_confidence, 0)
```

### Integration Testing

```python
def test_full_workflow():
    factory = AICouncilFactory()
    ai_council = factory.create_ai_council_sync()
    
    # Test cost estimation
    estimate = ai_council.estimate_cost_and_time(
        "Complex analysis task",
        ExecutionMode.BEST_QUALITY
    )
    assert estimate.total_cost > 0
    
    # Test processing
    response = ai_council.process_request_sync(
        "Complex analysis task",
        ExecutionMode.BEST_QUALITY
    )
    assert response.content
    assert response.overall_confidence > 0.5
```

---

## Version Information

- **Current Version**: 1.0.0
- **Python Compatibility**: 3.8+
- **Dependencies**: See `pyproject.toml`

For more examples and advanced usage, see the `examples/` directory and `docs/usage/` guides.