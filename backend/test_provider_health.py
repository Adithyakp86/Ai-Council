"""Test script for provider health monitoring system.

This script tests the health monitoring system with actual API keys (if configured).
It demonstrates:
1. Checking individual provider health
2. Checking all providers concurrently
3. Caching behavior
4. Response time measurement
"""

import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.provider_health_checker import get_health_checker


async def test_individual_provider(provider: str):
    """Test health check for a single provider."""
    print(f"\n{'='*60}")
    print(f"Testing {provider.upper()} Provider Health")
    print(f"{'='*60}")
    
    checker = get_health_checker()
    
    # First check (no cache)
    print(f"\n1. First check (no cache):")
    start_time = datetime.now()
    status = await checker.check_provider_health(provider)
    elapsed = (datetime.now() - start_time).total_seconds() * 1000
    
    print(f"   Status: {status.status}")
    print(f"   Response Time: {status.response_time_ms:.2f}ms")
    print(f"   Total Time (including overhead): {elapsed:.2f}ms")
    if status.error_message:
        print(f"   Error: {status.error_message}")
    print(f"   Last Check: {status.last_check}")
    
    # Second check (should use cache)
    print(f"\n2. Second check (should use cache):")
    start_time = datetime.now()
    status = await checker.check_provider_health(provider)
    elapsed = (datetime.now() - start_time).total_seconds() * 1000
    
    print(f"   Status: {status.status}")
    print(f"   Response Time: {status.response_time_ms:.2f}ms")
    print(f"   Total Time (including overhead): {elapsed:.2f}ms")
    print(f"   ✓ Cache hit! (much faster)")


async def test_all_providers():
    """Test health check for all providers concurrently."""
    print(f"\n{'='*60}")
    print(f"Testing ALL Providers Concurrently")
    print(f"{'='*60}")
    
    checker = get_health_checker()
    
    start_time = datetime.now()
    statuses = await checker.check_all_providers()
    elapsed = (datetime.now() - start_time).total_seconds() * 1000
    
    print(f"\nTotal time to check {len(statuses)} providers: {elapsed:.2f}ms")
    print(f"\nResults:")
    print(f"{'Provider':<15} {'Status':<12} {'Response Time':<15} {'Error'}")
    print(f"{'-'*70}")
    
    for provider, status in sorted(statuses.items()):
        response_time = f"{status.response_time_ms:.2f}ms" if status.response_time_ms else "N/A"
        error = status.error_message[:40] + "..." if status.error_message and len(status.error_message) > 40 else (status.error_message or "")
        
        # Color code status
        status_display = status.status
        if status.status == "healthy":
            status_display = f"✓ {status.status}"
        elif status.status == "degraded":
            status_display = f"⚠ {status.status}"
        else:
            status_display = f"✗ {status.status}"
        
        print(f"{provider:<15} {status_display:<12} {response_time:<15} {error}")


async def test_configured_providers():
    """Test only providers that have API keys configured."""
    print(f"\n{'='*60}")
    print(f"Testing Configured Providers Only")
    print(f"{'='*60}")
    
    # Check which providers have API keys configured
    provider_env_vars = {
        "groq": "GROQ_API_KEY",
        "together": "TOGETHER_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "huggingface": "HUGGINGFACE_TOKEN",
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "ollama": "OLLAMA_ENDPOINT",
        "qwen": "QWEN_API_KEY",
    }
    
    configured_providers = []
    for provider, env_var in provider_env_vars.items():
        if os.getenv(env_var):
            configured_providers.append(provider)
    
    if not configured_providers:
        print("\n⚠ No providers configured!")
        print("Set API keys in .env file to test providers.")
        print("\nExample:")
        print("  GROQ_API_KEY=your_key_here")
        print("  GEMINI_API_KEY=your_key_here")
        return
    
    print(f"\nConfigured providers: {', '.join(configured_providers)}")
    
    checker = get_health_checker()
    
    for provider in configured_providers:
        status = await checker.check_provider_health(provider)
        
        status_icon = "✓" if status.status == "healthy" else ("⚠" if status.status == "degraded" else "✗")
        print(f"\n{status_icon} {provider.upper()}: {status.status}")
        if status.response_time_ms:
            print(f"  Response time: {status.response_time_ms:.2f}ms")
        if status.error_message:
            print(f"  Error: {status.error_message}")


async def main():
    """Run all health monitoring tests."""
    print("\n" + "="*60)
    print("Provider Health Monitoring System Test")
    print("="*60)
    
    # Test 1: Check configured providers
    await test_configured_providers()
    
    # Test 2: Check all providers (including unconfigured ones)
    await test_all_providers()
    
    # Test 3: Test caching with a specific provider (if any configured)
    provider_env_vars = {
        "groq": "GROQ_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "ollama": "OLLAMA_ENDPOINT",
    }
    
    for provider, env_var in provider_env_vars.items():
        if os.getenv(env_var):
            await test_individual_provider(provider)
            break
    
    print(f"\n{'='*60}")
    print("Test Complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
