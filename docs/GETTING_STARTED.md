# 🚀 Getting Started with AI Council

Welcome to AI Council! This guide will help you get up and running quickly with the most powerful multi-agent AI orchestration system.

## 📋 Prerequisites

- **Python 3.8+** (Python 3.10+ recommended)
- **Git** for cloning the repository
- **Basic Python knowledge** for integration

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-council.git
cd ai-council
```

### 2. Install Dependencies

```bash
# Install in development mode
pip install -e .

# Or install with all development dependencies
pip install -e ".[dev]"
```

### 3. Verify Installation

```bash
# Run the validation script
python scripts/validate_infrastructure.py

# Run basic tests
python -m pytest tests/test_core_models.py -v
```

You should see:
```
✅ ALL INFRASTRUCTURE COMPONENTS VALIDATED SUCCESSFULLY!
✅ Ready for orchestration component implementation
```

## 🎯 Your First AI Council Request

Let's start with a simple example:

### 1. Create Your First Script

Create a file called `my_first_ai_council.py`:

```python
#!/usr/bin/env python3
"""
My First AI Council Example
"""

from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode

def main():
    print("🚀 Initializing AI Council...")
    
    # Create AI Council instance
    factory = AICouncilFactory()
    ai_council = factory.create_ai_council_sync()
    
    # Your first request
    question = "What are the main benefits of renewable energy?"
    
    print(f"❓ Question: {question}")
    print("🔄 Processing...")
    
    # Process the request
    response = ai_council.process_request_sync(
        question,
        ExecutionMode.BALANCED
    )
    
    # Display results
    print("\n" + "="*50)
    print("📝 AI Council Response:")
    print("="*50)
    print(response.content)
    print(f"\n📊 Confidence: {response.overall_confidence:.2f}")
    print(f"🤖 Models Used: {', '.join(response.models_used)}")
    print(f"💰 Cost: ${response.cost_breakdown.total_cost:.4f}")
    print("="*50)

if __name__ == "__main__":
    main()
```

### 2. Run Your First Script

```bash
# Set Python path (Windows)
$env:PYTHONPATH = "."

# Run your script
python my_first_ai_council.py
```

You should see output like:
```
🚀 Initializing AI Council...
❓ Question: What are the main benefits of renewable energy?
🔄 Processing...

==================================================
📝 AI Council Response:
==================================================
Renewable energy adoption offers significant environmental benefits and long-term economic advantages, though initial costs and infrastructure challenges must be considered.

📊 Confidence: 0.88
🤖 Models Used: model-1, model-2, model-3
💰 Cost: $0.0210
==================================================
```

## 🎮 Try Different Execution Modes

Now let's explore the different execution modes:

```python
#!/usr/bin/env python3
"""
Exploring AI Council Execution Modes
"""

from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode

def compare_execution_modes():
    factory = AICouncilFactory()
    ai_council = factory.create_ai_council_sync()
    
    question = "Explain machine learning in simple terms"
    
    modes = [
        (ExecutionMode.FAST, "🚀 FAST"),
        (ExecutionMode.BALANCED, "⚖️ BALANCED"), 
        (ExecutionMode.BEST_QUALITY, "💎 BEST_QUALITY")
    ]
    
    print(f"Question: {question}\n")
    
    for mode, mode_name in modes:
        print(f"--- {mode_name} MODE ---")
        
        # Get cost estimate first
        estimate = ai_council.estimate_cost_and_time(question, mode)
        print(f"💰 Estimated Cost: ${estimate.total_cost:.4f}")
        print(f"⏱️  Estimated Time: {estimate.total_time:.1f}s")
        
        # Process request
        response = ai_council.process_request_sync(question, mode)
        
        print(f"📊 Confidence: {response.overall_confidence:.2f}")
        print(f"💵 Actual Cost: ${response.cost_breakdown.total_cost:.4f}")
        print(f"📝 Response: {response.content[:100]}...")
        print()

if __name__ == "__main__":
    compare_execution_modes()
```

## 🔍 Understanding the Results

When AI Council processes your request, you get:

### Response Object
- **`content`**: The final synthesized answer
- **`overall_confidence`**: How confident the system is (0.0 to 1.0)
- **`models_used`**: Which AI models were involved
- **`cost_breakdown`**: Detailed cost information
- **`execution_metadata`**: Processing details

### Confidence Scores
- **0.9-1.0**: Very high confidence, reliable answer
- **0.7-0.9**: Good confidence, generally trustworthy
- **0.5-0.7**: Moderate confidence, consider verification
- **0.0-0.5**: Low confidence, requires careful review

## 🛠️ Next Steps

### 1. Explore Examples
```bash
# Run the comprehensive examples
python examples/basic_usage.py
python examples/complete_integration.py
python examples/orchestration_example.py
```

### 2. Try Different Task Types

AI Council handles various task types:

```python
# Code generation
response = ai_council.process_request_sync(
    "Write a Python function to calculate fibonacci numbers",
    ExecutionMode.BALANCED
)

# Research and analysis  
response = ai_council.process_request_sync(
    "Research the latest developments in quantum computing",
    ExecutionMode.BEST_QUALITY
)

# Creative writing
response = ai_council.process_request_sync(
    "Write a short story about AI and humans working together",
    ExecutionMode.BALANCED
)
```

### 3. Learn About Configuration

```python
from ai_council.utils.config import load_config

# Load and examine the configuration
config = load_config()
print(f"Available models: {list(config.models.keys())}")
print(f"Execution modes: {list(config.execution_modes.keys())}")
```

### 4. Explore Advanced Features

- **Custom Configuration**: Create your own execution modes and routing rules
- **Cost Optimization**: Fine-tune cost vs. quality trade-offs
- **System Monitoring**: Monitor system health and performance
- **Batch Processing**: Process multiple requests efficiently

## 📚 Learning Resources

### Documentation
- **[Architecture Guide](./architecture/ARCHITECTURE.md)**: Understand how AI Council works
- **[Usage Guide](./usage/USAGE_GUIDE.md)**: Comprehensive usage examples
- **[API Reference](../API_REFERENCE.md)**: Complete API documentation
- **[Business Case](./business/BUSINESS_CASE.md)**: Why AI Council matters

### Examples
- **[Basic Usage](../examples/basic_usage.py)**: Simple infrastructure demo
- **[Complete Integration](../examples/complete_integration.py)**: Full system demo
- **[Configuration](../examples/configuration_example.py)**: Configuration management
- **[Advanced Usage](./usage/advanced_usage.py)**: Complex scenarios

## 🆘 Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
# Make sure Python path is set
$env:PYTHONPATH = "."  # Windows
export PYTHONPATH="."  # Linux/Mac
```

#### Tests failing
```bash
# Run the validation script
python scripts/validate_infrastructure.py

# Check specific test
python -m pytest tests/test_core_models.py -v
```

#### Configuration issues
```bash
# Check configuration loading
python -c "from ai_council.utils.config import load_config; print(load_config())"
```

### Getting Help

1. **Check the documentation** in the `docs/` directory
2. **Run the examples** to see working code
3. **Check the test files** for usage patterns
4. **Review the system validation report** for system status

## 🎉 Congratulations!

You've successfully set up AI Council and made your first request! You now have access to a production-grade multi-agent AI orchestration system.

### What You've Learned
- ✅ How to install and set up AI Council
- ✅ How to make your first AI request
- ✅ Understanding execution modes and their trade-offs
- ✅ How to interpret AI Council responses
- ✅ Where to find more advanced features

### Next Steps
- Explore the comprehensive examples
- Read the architecture documentation
- Try custom configurations
- Integrate AI Council into your projects

**Welcome to the future of AI orchestration!** 🚀