#!/usr/bin/env python3
"""
AI Council Custom Configuration Example
=======================================

Shows how to create and use custom configurations.
"""

import asyncio
from ai_council.utils.config_builder import ConfigBuilder
from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode, TaskType

async def main():
    """Demonstrate custom configuration usage."""
    
    print("🔧 Creating custom AI Council configuration...")
    
    # 1. Build custom configuration
    config = (ConfigBuilder()
        .with_execution_mode("custom_fast", 
            max_parallel_executions=3,
            timeout_seconds=30.0,
            accuracy_requirement=0.7,
            cost_limit_dollars=5.0
        )
        .with_execution_mode("custom_quality",
            max_parallel_executions=8,
            timeout_seconds=120.0,
            accuracy_requirement=0.95,
            cost_limit_dollars=None
        )
        .with_routing_rule("high_accuracy_reasoning",
            task_types=[TaskType.REASONING],
            execution_modes=["custom_quality"],
            min_confidence=0.9,
            priority=1
        )
        .with_routing_rule("fast_general",
            task_types=[TaskType.CREATIVE_OUTPUT, TaskType.RESEARCH],
            execution_modes=["custom_fast"],
            min_confidence=0.7,
            priority=2
        )
        .build()
    )
    
    print(f"✅ Configuration created with {len(config.execution_modes)} execution modes")
    print(f"📋 Routing rules: {len(config.routing_rules)}")
    
    # 2. Initialize AI Council with custom config
    factory = AICouncilFactory(config=config)
    ai_council = await factory.create_ai_council()
    
    # 3. Test different scenarios
    test_cases = [
        {
            "text": "Solve this complex logical puzzle: If all roses are flowers...",
            "mode": ExecutionMode.BEST_QUALITY,
            "expected": "Should use high accuracy routing"
        },
        {
            "text": "Write a creative story about space exploration",
            "mode": ExecutionMode.FAST,
            "expected": "Should use fast general routing"
        }
    ]
    
    print("\n" + "="*50)
    print("CUSTOM CONFIGURATION TESTING")
    print("="*50)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- TEST {i} ---")
        print(f"Query: {test['text'][:40]}...")
        print(f"Expected: {test['expected']}")
        
        try:
            response = await ai_council.process_request(
                test['text'], 
                test['mode']
            )
            
            print(f"✅ Processed successfully")
            print(f"📊 Confidence: {response.overall_confidence:.2f}")
            print(f"🤖 Models: {', '.join(response.models_used)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 4. Show configuration details
    print(f"\n--- CONFIGURATION SUMMARY ---")
    print(f"Execution Modes: {list(config.execution_modes.keys())}")
    print(f"Routing Rules: {[rule.name for rule in config.routing_rules]}")
    print(f"Default Mode: {config.default_execution_mode}")
    
    await ai_council.shutdown()
    print("\n🔄 Custom configuration demo complete")

if __name__ == "__main__":
    asyncio.run(main())