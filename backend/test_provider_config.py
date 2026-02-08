"""Test script for provider configuration system.

This script tests the unified provider configuration system to ensure:
1. All providers are loaded correctly
2. API keys are read from environment variables
3. Provider status is correctly determined
4. Health checks work as expected
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.provider_config import ProviderConfig, ProviderStatus


async def test_provider_config():
    """Test the provider configuration system."""
    print("=" * 80)
    print("TESTING PROVIDER CONFIGURATION SYSTEM")
    print("=" * 80)
    print()
    
    # Initialize provider config
    config = ProviderConfig()
    
    # Test 1: Get all providers info
    print("Test 1: Get all providers info")
    print("-" * 80)
    all_providers = config.get_all_providers_info()
    print(f"Total providers defined: {len(all_providers)}")
    for name, info in all_providers.items():
        print(f"  - {info.display_name} ({name})")
        print(f"    Type: {info.provider_type.value}")
        print(f"    Configured: {info.is_configured}")
        print(f"    Env var: {info.env_var}")
        if info.free_tier_info:
            print(f"    Free tier: {info.free_tier_info}")
    print()
    
    # Test 2: Get configured providers
    print("Test 2: Get configured providers")
    print("-" * 80)
    configured = config.get_configured_providers()
    print(f"Configured providers: {len(configured)}")
    if configured:
        for provider in configured:
            info = config.get_provider_info(provider)
            print(f"  ✓ {info.display_name}")
    else:
        print("  ⚠️  No providers configured!")
        print("  Please set at least one API key in .env file")
    print()
    
    # Test 3: Check provider health
    print("Test 3: Check provider health")
    print("-" * 80)
    if configured:
        for provider in configured:
            info = config.get_provider_info(provider)
            print(f"Checking {info.display_name}...", end=" ")
            status = await config.check_provider_health(provider)
            
            if status == ProviderStatus.HEALTHY:
                print("✓ HEALTHY")
            elif status == ProviderStatus.DEGRADED:
                print("⚠️  DEGRADED")
            elif status == ProviderStatus.DOWN:
                print("✗ DOWN")
            else:
                print(f"? {status.value}")
    else:
        print("  No providers to check")
    print()
    
    # Test 4: Get API keys (masked)
    print("Test 4: Get API keys (masked)")
    print("-" * 80)
    for provider in configured:
        info = config.get_provider_info(provider)
        api_key = config.get_api_key(provider)
        if api_key:
            # Mask the API key
            if len(api_key) > 10:
                masked = f"{api_key[:4]}...{api_key[-4:]}"
            else:
                masked = "***"
            print(f"  {info.display_name}: {masked}")
    print()
    
    # Test 5: Get endpoints
    print("Test 5: Get endpoints")
    print("-" * 80)
    for provider in configured:
        info = config.get_provider_info(provider)
        endpoint = config.get_endpoint(provider)
        if endpoint:
            print(f"  {info.display_name}: {endpoint}")
    print()
    
    # Test 6: Log provider summary
    print("Test 6: Log provider summary")
    print("-" * 80)
    config.log_provider_summary()
    print()
    
    print("=" * 80)
    print("PROVIDER CONFIGURATION TEST COMPLETE")
    print("=" * 80)
    
    # Return success if at least one provider is configured
    return len(configured) > 0


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the test
    success = asyncio.run(test_provider_config())
    
    if success:
        print("\n✓ Test passed: At least one provider is configured")
        sys.exit(0)
    else:
        print("\n✗ Test failed: No providers configured")
        print("Please configure at least one provider in .env file")
        sys.exit(1)
