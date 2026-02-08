"""Test script for Ollama adapter."""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.cloud_ai.ollama_client import OllamaClient


def test_ollama_health():
    """Test Ollama health check."""
    print("Testing Ollama health check...")
    client = OllamaClient()
    health = client.health_check()
    print(f"Health status: {health}")
    return health["status"] == "healthy"


def test_ollama_list_models():
    """Test listing Ollama models."""
    print("\nListing available Ollama models...")
    client = OllamaClient()
    models = client.list_models()
    print(f"Available models: {models}")
    return len(models) > 0


def test_ollama_generate():
    """Test Ollama text generation."""
    print("\nTesting Ollama text generation...")
    client = OllamaClient()
    
    # Get available models
    models = client.list_models()
    if not models:
        print("No models available. Please pull a model first:")
        print("  ollama pull llama2")
        return False
    
    # Use first available model
    model = models[0].split(":")[0]  # Remove tag if present
    print(f"Using model: {model}")
    
    prompt = "Explain machine learning in one sentence."
    print(f"Prompt: {prompt}")
    
    try:
        response = client.generate(prompt, model, max_tokens=100)
        print(f"Response: {response}")
        return len(response) > 0
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Ollama Adapter Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health check
    try:
        results.append(("Health Check", test_ollama_health()))
    except Exception as e:
        print(f"Health check failed: {e}")
        results.append(("Health Check", False))
    
    # Test 2: List models
    try:
        results.append(("List Models", test_ollama_list_models()))
    except Exception as e:
        print(f"List models failed: {e}")
        results.append(("List Models", False))
    
    # Test 3: Generate text
    try:
        results.append(("Generate Text", test_ollama_generate()))
    except Exception as e:
        print(f"Generate text failed: {e}")
        results.append(("Generate Text", False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Ollama adapter is working correctly.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running: curl http://localhost:11434")
        print("2. Pull required models: ollama pull llama2")
        print("3. Check Ollama logs for errors")
        print("4. See backend/docs/OLLAMA_SETUP.md for detailed setup")
        return 1


if __name__ == "__main__":
    sys.exit(main())
