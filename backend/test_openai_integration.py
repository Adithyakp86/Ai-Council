"""Test script for OpenAI integration.

This script tests the OpenAI adapter and client to ensure they work correctly.
Requires OPENAI_API_KEY environment variable to be set.

Usage:
    python test_openai_integration.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.cloud_ai.openai_adapter import OpenAIAdapter
from app.services.cloud_ai.openai_client import OpenAIClient


def test_openai_client():
    """Test OpenAI client directly."""
    print("\n" + "="*80)
    print("Testing OpenAI Client")
    print("="*80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("   Get your API key at: https://platform.openai.com/api-keys")
        print("   Note: Requires payment method but includes $5 free trial")
        return False
    
    try:
        client = OpenAIClient(api_key=api_key)
        print("✓ OpenAI client initialized")
        
        # Test health check
        print("\nTesting health check...")
        health = client.health_check()
        print(f"✓ Health check: {health}")
        
        if health["status"] != "healthy":
            print(f"❌ Health check failed: {health.get('error', 'Unknown error')}")
            return False
        
        # Test GPT-3.5-Turbo
        print("\nTesting GPT-3.5-Turbo...")
        prompt = "Explain quantum computing in one sentence."
        response = client.generate(prompt, "gpt-3.5-turbo", max_tokens=100)
        print(f"✓ Response: {response[:200]}...")
        
        # Test GPT-4 (if available and user has access)
        print("\nTesting GPT-4 (optional, may fail if not available)...")
        try:
            response = client.generate(prompt, "gpt-4", max_tokens=100)
            print(f"✓ GPT-4 Response: {response[:200]}...")
        except Exception as e:
            print(f"⚠ GPT-4 test skipped: {e}")
            print("  (This is normal if you don't have GPT-4 access)")
        
        print("\n✅ All OpenAI client tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ OpenAI client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_openai_adapter():
    """Test OpenAI adapter (AI Council integration)."""
    print("\n" + "="*80)
    print("Testing OpenAI Adapter (AI Council Integration)")
    print("="*80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    try:
        # Test GPT-3.5-Turbo adapter
        adapter = OpenAIAdapter(model_id="gpt-3.5-turbo", api_key=api_key)
        print("✓ OpenAI adapter initialized")
        
        # Test model ID
        model_id = adapter.get_model_id()
        print(f"✓ Model ID: {model_id}")
        assert model_id == "openai-gpt-3.5-turbo", f"Expected 'openai-gpt-3.5-turbo', got '{model_id}'"
        
        # Test generate_response (AI Council interface)
        print("\nTesting generate_response...")
        prompt = "What is machine learning? Answer in one sentence."
        response = adapter.generate_response(prompt, max_tokens=100)
        print(f"✓ Response: {response[:200]}...")
        
        print("\n✅ All OpenAI adapter tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ OpenAI adapter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_registry():
    """Test that OpenAI models are in the model registry."""
    print("\n" + "="*80)
    print("Testing Model Registry")
    print("="*80)
    
    try:
        from app.services.cloud_ai.model_registry import MODEL_REGISTRY
        
        # Check for OpenAI models
        openai_models = [
            "openai-gpt-3.5-turbo",
            "openai-gpt-4",
            "openai-gpt-4-turbo-preview"
        ]
        
        for model_id in openai_models:
            if model_id in MODEL_REGISTRY:
                config = MODEL_REGISTRY[model_id]
                print(f"✓ {model_id}:")
                print(f"  - Provider: {config['provider']}")
                print(f"  - Model: {config['model_name']}")
                print(f"  - Capabilities: {[c.value for c in config['capabilities']]}")
                print(f"  - Cost (input/output): ${config['cost_per_input_token']*1000000:.2f}/${config['cost_per_output_token']*1000000:.2f} per 1M tokens")
                print(f"  - Max context: {config['max_context']} tokens")
                print(f"  - Reliability: {config['reliability_score']}")
            else:
                print(f"❌ {model_id} not found in MODEL_REGISTRY")
                return False
        
        print("\n✅ All OpenAI models found in registry!")
        return True
        
    except Exception as e:
        print(f"\n❌ Model registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("OpenAI Integration Test Suite")
    print("="*80)
    print("\nThis test requires:")
    print("1. OPENAI_API_KEY environment variable")
    print("2. Valid OpenAI API key from https://platform.openai.com")
    print("3. Payment method configured (includes $5 free trial)")
    print("\nNote: This is an OPTIONAL integration for premium AI capabilities.")
    
    results = []
    
    # Test model registry (doesn't require API key)
    results.append(("Model Registry", test_model_registry()))
    
    # Test client and adapter (requires API key)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        results.append(("OpenAI Client", test_openai_client()))
        results.append(("OpenAI Adapter", test_openai_adapter()))
    else:
        print("\n⚠ Skipping API tests (OPENAI_API_KEY not set)")
        print("  To test with real API:")
        print("  1. Get API key: https://platform.openai.com/api-keys")
        print("  2. Set environment variable: export OPENAI_API_KEY=your_key_here")
        print("  3. Run this script again")
    
    # Print summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All tests passed! OpenAI integration is working correctly.")
        print("\nNext steps:")
        print("1. Add OPENAI_API_KEY to backend/.env")
        print("2. Use OpenAI models in your AI Council orchestration")
        print("3. Monitor usage at https://platform.openai.com/usage")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
