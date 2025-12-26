#!/usr/bin/env python3
"""
AI Council Simple Usage Examples
================================

Easy-to-follow examples for getting started with AI Council.
"""

from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode, TaskType
from ai_council.utils.config import load_config

def simple_usage_demo():
    """Simple demonstration of AI Council usage."""
    
    print("🚀 AI Council Simple Usage Demo")
    print("="*40)
    
    # 1. Basic initialization
    print("\n1. Initializing AI Council...")
    factory = AICouncilFactory()
    ai_council = factory.create_ai_council_sync()
    print("✅ AI Council initialized successfully!")
    
    # 2. Simple request processing
    print("\n2. Processing simple requests...")
    
    simple_requests = [
        {
            "text": "What are the main benefits of renewable energy?",
            "mode": ExecutionMode.FAST,
            "description": "Quick factual question"
        },
        {
            "text": "Explain how machine learning works in simple terms",
            "mode": ExecutionMode.BALANCED,
            "description": "Educational explanation"
        },
        {
            "text": "Write a Python function to calculate the factorial of a number",
            "mode": ExecutionMode.BALANCED,
            "description": "Code generation"
        }
    ]
    
    for i, request in enumerate(simple_requests, 1):
        print(f"\n--- Request {i}: {request['description']} ---")
        print(f"Question: {request['text']}")
        print(f"Mode: {request['mode'].value}")
        
        try:
            # Get cost estimate
            estimate = ai_council.estimate_cost_and_time(
                request['text'], 
                request['mode']
            )
            print(f"💰 Estimated Cost: ${estimate.total_cost:.4f}")
            print(f"⏱️  Estimated Time: {estimate.total_time:.1f}s")
            
            # Process the request
            response = ai_council.process_request_sync(
                request['text'], 
                request['mode']
            )
            
            print(f"✅ Success!")
            print(f"📊 Confidence: {response.overall_confidence:.2f}")
            print(f"🤖 Models Used: {', '.join(response.models_used)}")
            print(f"💵 Actual Cost: ${response.cost_breakdown.total_cost:.4f}")
            print(f"📝 Response Preview: {response.content[:100]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 3. Show execution modes
    print(f"\n3. Available Execution Modes:")
    mode_descriptions = {
        ExecutionMode.FAST: "Quick responses, lower cost, good for simple questions",
        ExecutionMode.BALANCED: "Balanced quality and cost, good for most use cases", 
        ExecutionMode.BEST_QUALITY: "Highest quality, higher cost, best for complex tasks"
    }
    
    for mode, description in mode_descriptions.items():
        print(f"   • {mode.value.upper()}: {description}")
    
    # 4. Show task types
    print(f"\n4. Supported Task Types:")
    task_descriptions = {
        "reasoning": "Logical analysis and problem solving",
        "research": "Information gathering and fact-finding",
        "code_generation": "Writing and debugging code",
        "creative_output": "Creative writing and content generation",
        "fact_checking": "Verifying information accuracy",
        "verification": "Validating results and claims"
    }
    
    for task_type, description in task_descriptions.items():
        print(f"   • {task_type}: {description}")
    
    # 5. System status check
    print(f"\n5. System Status:")
    try:
        status = ai_council.get_system_status()
        print(f"   Status: {status.status}")
        print(f"   Health: {status.health}")
        print(f"   Available Models: {len(status.available_models)}")
        
        if status.status == "operational" and status.health == "healthy":
            print("   🟢 System is fully operational!")
        else:
            print("   🟡 System may have some issues")
            
    except Exception as e:
        print(f"   ❌ Could not get system status: {e}")
    
    # 6. Configuration info
    print(f"\n6. Configuration Information:")
    try:
        config = load_config()
        print(f"   Models configured: {len(config.models)}")
        print(f"   Execution modes: {len(config.execution_modes)}")
        print(f"   Routing rules: {len(config.routing_rules)}")
        print(f"   Max parallel executions: {config.max_parallel_executions}")
        print(f"   Max cost per request: ${config.max_cost_per_request}")
    except Exception as e:
        print(f"   ❌ Could not load configuration: {e}")
    
    print(f"\n✅ Simple usage demo completed!")
    print(f"\n💡 Next Steps:")
    print(f"   • Try different execution modes for your use case")
    print(f"   • Experiment with various types of questions")
    print(f"   • Check out advanced_usage.py for more complex examples")
    print(f"   • Read the documentation in docs/ for detailed guides")

if __name__ == "__main__":
    simple_usage_demo()