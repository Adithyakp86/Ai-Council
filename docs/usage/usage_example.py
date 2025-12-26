#!/usr/bin/env python3
"""
AI Council Usage Example
========================

This example shows how to use AI Council in your own applications.
"""

import asyncio
from ai_council.factory import AICouncilFactory
from ai_council.core.models import ExecutionMode

async def main():
    """Demonstrate AI Council usage."""
    
    # 1. Initialize AI Council
    print("🚀 Initializing AI Council...")
    factory = AICouncilFactory()
    ai_council = await factory.create_ai_council()
    
    # 2. Process different types of requests
    requests = [
        {
            "text": "Explain quantum computing and its potential applications",
            "mode": ExecutionMode.FAST,
            "description": "Quick explanation"
        },
        {
            "text": "Write a Python function to implement a binary search algorithm with error handling",
            "mode": ExecutionMode.BALANCED,
            "description": "Code generation with analysis"
        },
        {
            "text": "Research the latest developments in renewable energy and provide a comprehensive analysis",
            "mode": ExecutionMode.BEST_QUALITY,
            "description": "Comprehensive research"
        }
    ]
    
    print("\n" + "="*60)
    print("AI COUNCIL USAGE DEMONSTRATION")
    print("="*60)
    
    for i, request in enumerate(requests, 1):
        print(f"\n--- REQUEST {i}: {request['description']} ---")
        print(f"Mode: {request['mode'].value}")
        print(f"Query: {request['text'][:50]}...")
        
        try:
            # Get cost estimate first
            estimate = await ai_council.estimate_cost_and_time(
                request['text'], 
                request['mode']
            )
            print(f"💰 Estimated Cost: ${estimate.total_cost:.4f}")
            print(f"⏱️  Estimated Time: {estimate.total_time:.1f}s")
            
            # Process the request
            response = await ai_council.process_request(
                request['text'], 
                request['mode']
            )
            
            print(f"✅ Success!")
            print(f"📊 Confidence: {response.overall_confidence:.2f}")
            print(f"🤖 Models Used: {', '.join(response.models_used)}")
            print(f"💵 Actual Cost: ${response.cost_breakdown.total_cost:.4f}")
            print(f"📝 Response: {response.content[:100]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 3. Show system status
    print(f"\n--- SYSTEM STATUS ---")
    status = await ai_council.get_system_status()
    print(f"Status: {status.status}")
    print(f"Health: {status.health}")
    print(f"Available Models: {len(status.available_models)}")
    
    # 4. Shutdown
    await ai_council.shutdown()
    print("\n🔄 AI Council shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())