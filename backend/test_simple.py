print("Hello from test script")
import sys
print(f"Python: {sys.version}")

try:
    from dotenv import load_dotenv
    print("✓ dotenv imported")
    load_dotenv()
    print("✓ .env loaded")
except Exception as e:
    print(f"✗ Error with dotenv: {e}")

try:
    from app.core.provider_config import get_provider_config
    print("✓ provider_config imported")
    config = get_provider_config()
    print(f"✓ Config created: {config}")
    providers = config.get_configured_providers()
    print(f"✓ Configured providers: {providers}")
except Exception as e:
    print(f"✗ Error with provider_config: {e}")
    import traceback
    traceback.print_exc()
