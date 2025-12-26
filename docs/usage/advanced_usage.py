#!/usr/bin/env python3
"""
AI Council Advanced Usage Examples
==================================

This file contains advanced usage patterns and integration examples.
"""

import asyncio
from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode, TaskType
from ai_council.utils.config_builder import ConfigBuilder

async def advanced_usage_demo():
    """Demonstrate advanced AI Council usage patterns."""
    
    print("🚀 AI Council Advanced Usage Demo")
    print("="*50)
    
    # 1. Custom Configuration
    print("\n1. Creating custom configuration...")
    config = (ConfigBuilder()
        .with_execution_mode("ultra_fast", 
            max_parallel_executions=2,
            timeout_seconds=15.0,
            accuracy_requirement=0.6,
            cost_limit_dollars=2.0
        )
        .with_execution_mode("premium_quality",
            max_parallel_executions=10,
            timeout_seconds=180.0,
            accuracy_requirement=0.98,
            cost_limit_dollars=None
        )
        .with_routing_rule("critical_reasoning",
            task_types=[TaskType.REASONING],
            execution_modes=["premium_quality"],
            min_confidence=0.95,
            priority=1
        )
        .build()
    )
    
    # 2. Initialize with custom config
    factory = AICouncilFactory(config=config)
    ai_council = await factory.create_ai_council()
    
    # 3. Advanced request processing
    advanced_requests = [
        {
            "text": "Solve this complex logical puzzle: If all roses are flowers, and some flowers fade quickly, can we conclude that some roses fade quickly?",
            "mode": ExecutionMode.BEST_QUALITY,
            "expected_confidence": 0.9
        },
        {
            "text": "Write a production-ready Python microservice for user authentication with JWT tokens, rate limiting, and comprehensive error handling",
            "mode": ExecutionMode.BALANCED,
            "expected_confidence": 0.8
        },
        {
            "text": "Quick summary of renewable energy benefits",
            "mode": ExecutionMode.FAST,
            "expected_confidence": 0.7
        }
    ]
    
    print("\n2. Processing advanced requests...")
    results = []
    
    for i, req in enumerate(advanced_requests, 1):
        print(f"\n--- Advanced Request {i} ---")
        print(f"Text: {req['text'][:60]}...")
        print(f"Mode: {req['mode'].value}")
        
        try:
            # Cost estimation with detailed breakdown
            estimate = await ai_council.estimate_cost_and_time(
                req['text'], 
                req['mode']
            )
            
            print(f"💰 Estimated Cost: ${estimate.total_cost:.4f}")
            print(f"⏱️  Estimated Time: {estimate.total_time:.1f}s")
            print(f"🎯 Expected Confidence: {req['expected_confidence']}")
            
            # Process with monitoring
            response = await ai_council.process_request(
                req['text'], 
                req['mode']
            )
            
            # Validate response quality
            quality_check = {
                "meets_confidence": response.overall_confidence >= req['expected_confidence'],
                "within_budget": response.cost_breakdown.total_cost <= estimate.total_cost * 1.2,
                "reasonable_length": 50 <= len(response.content) <= 2000
            }
            
            print(f"✅ Response generated")
            print(f"📊 Actual Confidence: {response.overall_confidence:.3f}")
            print(f"💵 Actual Cost: ${response.cost_breakdown.total_cost:.4f}")
            print(f"🤖 Models Used: {', '.join(response.models_used)}")
            print(f"🔍 Quality Check: {all(quality_check.values())}")
            
            results.append({
                "request": req,
                "response": response,
                "quality_check": quality_check,
                "estimate": estimate
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "request": req,
                "error": str(e)
            })
    
    # 4. Batch processing demonstration
    print(f"\n3. Batch processing demonstration...")
    batch_requests = [
        "What is machine learning?",
        "Explain blockchain technology",
        "How does quantum computing work?",
        "What are the benefits of cloud computing?",
        "Describe artificial intelligence applications"
    ]
    
    batch_results = []
    for text in batch_requests:
        try:
            response = await ai_council.process_request(text, ExecutionMode.FAST)
            batch_results.append({
                "text": text,
                "confidence": response.overall_confidence,
                "cost": response.cost_breakdown.total_cost,
                "success": True
            })
        except Exception as e:
            batch_results.append({
                "text": text,
                "error": str(e),
                "success": False
            })
    
    successful_batch = [r for r in batch_results if r.get("success")]
    print(f"✅ Batch processed: {len(successful_batch)}/{len(batch_requests)} successful")
    print(f"💰 Total batch cost: ${sum(r['cost'] for r in successful_batch):.4f}")
    print(f"📊 Average confidence: {sum(r['confidence'] for r in successful_batch) / len(successful_batch):.3f}")
    
    # 5. System monitoring and health checks
    print(f"\n4. System monitoring...")
    status = await ai_council.get_system_status()
    print(f"🟢 System Status: {status.status}")
    print(f"❤️  Health: {status.health}")
    print(f"🤖 Available Models: {len(status.available_models)}")
    print(f"🔧 Circuit Breakers: {len([cb for cb in status.circuit_breakers.values() if cb == 'closed'])}/{len(status.circuit_breakers)} healthy")
    
    # 6. Performance analysis
    print(f"\n5. Performance Analysis...")
    total_requests = len([r for r in results if "response" in r])
    total_cost = sum(r["response"].cost_breakdown.total_cost for r in results if "response" in r)
    avg_confidence = sum(r["response"].overall_confidence for r in results if "response" in r) / max(total_requests, 1)
    
    print(f"📈 Total Requests Processed: {total_requests}")
    print(f"💰 Total Cost: ${total_cost:.4f}")
    print(f"📊 Average Confidence: {avg_confidence:.3f}")
    print(f"⚡ Success Rate: {total_requests}/{len(results)} ({total_requests/len(results)*100:.1f}%)")
    
    # 7. Cleanup
    await ai_council.shutdown()
    print(f"\n🔄 Advanced usage demo completed successfully!")

if __name__ == "__main__":
    asyncio.run(advanced_usage_demo())