"""Test script for Qwen (Alibaba Cloud) integration."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.cloud_ai.qwen_client import QwenClient
from app.services.cloud_ai.qwen_adapter import QwenAdapter


def test_qwen_integration():
    """Test Qwen API integration with all models."""
    
    print("Testing Qwen integration...\n")
    
    # Check if API key is configured
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        print("❌ QWEN_API_KEY not found in environment variables")
        print("   Please add QWEN_API_KEY to backend/.env")
        print("   Get your API key from: https://dashscope.aliyun.com")
        return False
    
    print("✓ Qwen API key configured")
    
    # Test models
    models = [
        ("qwen-turbo", "Fast and cost-effective"),
        ("qwen-plus", "Balanced performance"),
        ("qwen-max", "Best quality"),
    ]
    
    test_prompt = "Explain what artificial intelligence is in one sentence."
    
    for model_id, description in models:
        print(f"\nTesting {model_id} ({description})...")
        
        try:
            # Create adapter
            adapter = QwenAdapter(
                model_id=model_id,
                api_key=api_key
            )
            
            # Generate response
            response = adapter.generate_response(
                prompt=test_prompt,
                temperature=0.7,
                max_tokens=100
            )
            
            print(f"✓ {model_id} response:")
            print(f"  {response[:150]}{'...' if len(response) > 150 else ''}")
            
        except Exception as e:
            print(f"❌ {model_id} failed: {e}")
            return False
    
    # Test health check
    print("\nTesting health check...")
    try:
        client = QwenClient(api_key=api_key)
        health = client.health_check()
        
        if health["status"] == "healthy":
            print(f"✓ Health check passed")
            print(f"  Provider: {health['provider']}")
            print(f"  Models available: {', '.join(health['models_available'])}")
            if "note" in health:
                print(f"  Note: {health['note']}")
        else:
            print(f"❌ Health check failed: {health.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("✓ All Qwen integration tests passed!")
    print("="*60)
    print("\nQwen models are now available for AI Council orchestration.")
    print("\nAvailable models:")
    print("  - qwen-turbo: Fast and cost-effective")
    print("  - qwen-plus: Balanced performance with 32K context")
    print("  - qwen-max: Best quality for complex tasks")
    print("\nNote: This is an optional integration.")
    print("The application works without Qwen using other providers.")
    
    return True


def test_qwen_with_different_parameters():
    """Test Qwen with various parameters."""
    
    print("\n" + "="*60)
    print("Testing Qwen with different parameters...")
    print("="*60)
    
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        print("Skipping parameter tests - API key not configured")
        return
    
    adapter = QwenAdapter(model_id="qwen-turbo", api_key=api_key)
    
    # Test 1: Low temperature (more focused)
    print("\n1. Testing with low temperature (0.3)...")
    try:
        response = adapter.generate_response(
            prompt="What is 2+2?",
            temperature=0.3,
            max_tokens=50
        )
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: High temperature (more creative)
    print("\n2. Testing with high temperature (0.9)...")
    try:
        response = adapter.generate_response(
            prompt="Write a creative opening line for a story.",
            temperature=0.9,
            max_tokens=100
        )
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Longer response
    print("\n3. Testing with longer max_tokens (500)...")
    try:
        response = adapter.generate_response(
            prompt="Explain the concept of machine learning.",
            temperature=0.7,
            max_tokens=500
        )
        print(f"   Response length: {len(response)} characters")
        print(f"   First 200 chars: {response[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")


def main():
    """Run all tests."""
    
    print("="*60)
    print("Qwen (Alibaba Cloud) Integration Test")
    print("="*60)
    
    # Run basic integration test
    success = test_qwen_integration()
    
    if success:
        # Run parameter tests
        test_qwen_with_different_parameters()
        
        print("\n" + "="*60)
        print("All tests completed successfully!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("Tests failed. Please check the errors above.")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
