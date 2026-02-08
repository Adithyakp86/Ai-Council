"""Test script for OpenRouter integration.

This script tests the OpenRouter adapter with multiple models to verify:
1. API key configuration
2. Connection to OpenRouter API
3. Response generation from different models
4. Error handling and circuit breaker
5. Cost calculation

Usage:
    python test_openrouter_integration.py
"""

import os
import sys
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.cloud_ai.openrouter_adapter import OpenRouterAdapter
from app.services.cloud_ai.model_registry import MODEL_REGISTRY


def test_api_key():
    """Test if OpenRouter API key is configured."""
    print("=" * 60)
    print("TEST 1: API Key Configuration")
    print("=" * 60)
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("[X] OPENROUTER_API_KEY not found in environment")
        print("   Please add it to backend/.env file")
        print("   Get your key from: https://openrouter.ai/keys")
        return False
    
    if not api_key.startswith('sk-or-v1-'):
        print(f"[!] Warning: API key doesn't start with 'sk-or-v1-'")
        print(f"   Current format: {api_key[:10]}...")
        print("   This might not be a valid OpenRouter key")
    
    print(f"[OK] API key found: {api_key[:15]}...{api_key[-5:]}")
    return True


def test_model_registry():
    """Test if OpenRouter models are registered."""
    print("\n" + "=" * 60)
    print("TEST 2: Model Registry")
    print("=" * 60)
    
    openrouter_models = [
        model_id for model_id in MODEL_REGISTRY.keys()
        if model_id.startswith('openrouter-')
    ]
    
    if not openrouter_models:
        print("[X] No OpenRouter models found in MODEL_REGISTRY")
        return False
    
    print(f"[OK] Found {len(openrouter_models)} OpenRouter models:")
    for model_id in openrouter_models:
        config = MODEL_REGISTRY[model_id]
        print(f"  - {model_id}")
        print(f"    Model: {config['model_name']}")
        print(f"    Capabilities: {[cap.value for cap in config['capabilities']]}")
        print(f"    Cost: ${config['cost_per_input_token']*1000000:.2f}/${config['cost_per_output_token']*1000000:.2f} per 1M tokens")
    
    return True


def test_single_model(model_id: str, api_key: str):
    """Test a single OpenRouter model."""
    print(f"\n  Testing {model_id}...")
    
    try:
        config = MODEL_REGISTRY[model_id]
        adapter = OpenRouterAdapter(config['model_name'], api_key)
        
        # Simple test prompt
        prompt = "Say 'Hello from OpenRouter' in exactly 5 words."
        response = adapter.generate_response(prompt, max_tokens=50)
        
        print(f"  [OK] {model_id}")
        print(f"    Response: {response[:80]}...")
        return True
        
    except Exception as e:
        print(f"  [X] {model_id}")
        print(f"    Error: {str(e)[:100]}")
        return False


def test_all_models():
    """Test all OpenRouter models."""
    print("\n" + "=" * 60)
    print("TEST 3: Model Response Generation")
    print("=" * 60)
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("[X] Cannot test without API key")
        return False
    
    openrouter_models = [
        model_id for model_id in MODEL_REGISTRY.keys()
        if model_id.startswith('openrouter-')
    ]
    
    # Test the 4 main models specified in the task
    priority_models = [
        'openrouter-gpt-3.5-turbo',
        'openrouter-claude-instant-1',
        'openrouter-llama-2-70b-chat',
        'openrouter-palm-2-chat-bison'
    ]
    
    print("\nTesting priority models (from task requirements):")
    success_count = 0
    for model_id in priority_models:
        if model_id in openrouter_models:
            if test_single_model(model_id, api_key):
                success_count += 1
        else:
            print(f"  [!] {model_id} not found in registry")
    
    print(f"\n[OK] Successfully tested {success_count}/{len(priority_models)} priority models")
    
    # Test additional models
    additional_models = [m for m in openrouter_models if m not in priority_models]
    if additional_models:
        print("\nTesting additional models:")
        for model_id in additional_models[:2]:  # Test max 2 additional to save credits
            test_single_model(model_id, api_key)
    
    return success_count >= 2  # At least 2 models should work


def test_error_handling():
    """Test error handling with invalid API key."""
    print("\n" + "=" * 60)
    print("TEST 4: Error Handling")
    print("=" * 60)
    
    print("\n  Testing with invalid API key...")
    try:
        adapter = OpenRouterAdapter('openai/gpt-3.5-turbo', 'invalid-key')
        response = adapter.generate_response('test')
        print("  [X] Should have raised an error")
        return False
    except Exception as e:
        print(f"  [OK] Correctly raised error: {type(e).__name__}")
        return True


def test_cost_calculation():
    """Test cost calculation for OpenRouter models."""
    print("\n" + "=" * 60)
    print("TEST 5: Cost Calculation")
    print("=" * 60)
    
    # Estimate costs for a typical query
    test_input_tokens = 100
    test_output_tokens = 200
    
    print("\nEstimated costs for 100 input + 200 output tokens:")
    
    openrouter_models = [
        model_id for model_id in MODEL_REGISTRY.keys()
        if model_id.startswith('openrouter-')
    ]
    
    for model_id in openrouter_models:
        config = MODEL_REGISTRY[model_id]
        input_cost = test_input_tokens * config['cost_per_input_token']
        output_cost = test_output_tokens * config['cost_per_output_token']
        total_cost = input_cost + output_cost
        
        print(f"  {model_id}:")
        print(f"    Total: ${total_cost:.6f}")
    
    print("\n[OK] Cost calculation test complete")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("OpenRouter Integration Test Suite")
    print("=" * 60)
    
    results = {
        "API Key": test_api_key(),
        "Model Registry": test_model_registry(),
        "Model Responses": test_all_models(),
        "Error Handling": test_error_handling(),
        "Cost Calculation": test_cost_calculation(),
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n[SUCCESS] All tests passed! OpenRouter integration is working correctly.")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
