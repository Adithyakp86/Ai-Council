# Provider Configuration System

## Overview

The unified provider configuration system manages all AI provider API keys, endpoints, and health checks in a centralized way. This system:

- Loads API keys from environment variables
- Validates configuration on application startup
- Provides health check functionality for all providers
- Logs which providers are available and which are disabled
- Supports both free and paid providers
- Supports local (Ollama) and cloud providers

## Architecture

### Components

1. **ProviderConfig Class** (`backend/app/core/provider_config.py`)
   - Central configuration manager
   - Loads and validates API keys
   - Performs health checks
   - Provides provider information

2. **ProviderInfo Dataclass**
   - Stores metadata about each provider
   - Includes type (FREE/PAID/LOCAL), status, endpoints, etc.

3. **ProviderStatus Enum**
   - HEALTHY: Provider is working correctly
   - DEGRADED: Provider is responding but with issues
   - DOWN: Provider is not responding
   - DISABLED: Provider is intentionally disabled
   - NOT_CONFIGURED: Provider has no API key set

4. **ProviderType Enum**
   - FREE: No billing required
   - PAID: Requires payment or has paid tiers
   - LOCAL: Runs locally on user's machine

## Supported Providers

### Free Providers (No billing required)

| Provider | Type | Free Tier | Setup |
|----------|------|-----------|-------|
| **Ollama** | LOCAL | Unlimited (runs locally) | [OLLAMA_SETUP.md](OLLAMA_SETUP.md) |
| **Google Gemini** | CLOUD | 60 requests/minute | [GEMINI_SETUP.md](GEMINI_SETUP.md) |
| **HuggingFace** | CLOUD | ~1000 requests/day | [HUGGINGFACE_SETUP.md](HUGGINGFACE_SETUP.md) |

### Paid Providers (Free credits on signup)

| Provider | Type | Free Credits | Setup |
|----------|------|--------------|-------|
| **Groq** | CLOUD | Available on signup | [GROQ_SETUP.md](GROQ_SETUP.md) |
| **Together AI** | CLOUD | $25 on signup | [TOGETHER_SETUP.md](TOGETHER_SETUP.md) |
| **OpenRouter** | CLOUD | $1-5 on signup | [OPENROUTER_SETUP.md](OPENROUTER_SETUP.md) |

### Optional Paid Providers

| Provider | Type | Free Trial | Setup |
|----------|------|------------|-------|
| **OpenAI** | CLOUD | $5 (requires payment method) | [OPENAI_SETUP.md](OPENAI_SETUP.md) |
| **Qwen** | CLOUD | Varies by region | [QWEN_SETUP.md](QWEN_SETUP.md) |

## Configuration

### Environment Variables

All provider configuration is done through environment variables in the `.env` file:

```bash
# Free providers
OLLAMA_ENDPOINT=http://localhost:11434
GEMINI_API_KEY=your_gemini_key_here
HUGGINGFACE_TOKEN=your_hf_token_here

# Paid providers
GROQ_API_KEY=your_groq_key_here
TOGETHER_API_KEY=your_together_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Optional paid providers
OPENAI_API_KEY=your_openai_key_here
QWEN_API_KEY=your_qwen_key_here
```

### Getting Started

**Minimum requirement:** Configure at least ONE provider to use the application.

**Recommended for beginners:**
1. Start with **Ollama** (free, local) or **Gemini** (free, cloud)
2. Add more providers as needed for additional capabilities

See `backend/.env.example` for detailed setup instructions for each provider.

## Usage

### Initialization

The provider configuration is automatically initialized on application startup:

```python
from app.core.provider_config import initialize_provider_config

# Called in app/main.py during startup
provider_config = initialize_provider_config()
```

### Getting Provider Information

```python
from app.core.provider_config import get_provider_config

config = get_provider_config()

# Check if a provider is configured
if config.is_provider_configured("gemini"):
    print("Gemini is configured")

# Get API key for a provider
api_key = config.get_api_key("gemini")

# Get endpoint for a provider
endpoint = config.get_endpoint("gemini")

# Get list of configured providers
configured = config.get_configured_providers()
print(f"Configured providers: {configured}")

# Get detailed info about a provider
info = config.get_provider_info("gemini")
print(f"Display name: {info.display_name}")
print(f"Type: {info.provider_type.value}")
print(f"Status: {info.status.value}")
```

### Health Checks

```python
from app.core.provider_config import get_provider_config

config = get_provider_config()

# Check health of a specific provider
status = await config.check_provider_health("gemini")
print(f"Gemini status: {status.value}")

# Check health of all providers
health_status = await config.check_all_providers_health()
for provider, status in health_status.items():
    print(f"{provider}: {status.value}")
```

### Logging Provider Summary

```python
from app.core.provider_config import get_provider_config

config = get_provider_config()

# Log detailed summary of all providers
config.log_provider_summary()
```

## Health Check Endpoints

### Basic Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "providers": {
    "configured": 3,
    "names": ["ollama", "gemini", "groq"]
  }
}
```

### Detailed Provider Health Check

```bash
GET /health/providers
```

Response:
```json
{
  "status": "healthy",
  "providers": {
    "ollama": "healthy",
    "gemini": "healthy",
    "groq": "healthy"
  }
}
```

## Testing

### Test Provider Configuration

Run the test script to verify your provider configuration:

```bash
cd backend
python test_provider_config.py
```

This will:
1. Load all provider definitions
2. Check which providers are configured
3. Perform health checks on configured providers
4. Display API keys (masked)
5. Show endpoints
6. Log a detailed summary

### Expected Output

```
================================================================================
TESTING PROVIDER CONFIGURATION SYSTEM
================================================================================

Test 1: Get all providers info
--------------------------------------------------------------------------------
Total providers defined: 8
  - Ollama (ollama)
    Type: local
    Configured: True
    Env var: OLLAMA_ENDPOINT
    Free tier: Completely free - runs locally on your hardware
  ...

Test 2: Get configured providers
--------------------------------------------------------------------------------
Configured providers: 3
  ✓ Ollama
  ✓ Google Gemini
  ✓ Groq

Test 3: Check provider health
--------------------------------------------------------------------------------
Checking Ollama... ✓ HEALTHY
Checking Google Gemini... ✓ HEALTHY
Checking Groq... ✓ HEALTHY

...

================================================================================
PROVIDER CONFIGURATION TEST COMPLETE
================================================================================

✓ Test passed: At least one provider is configured
```

## Troubleshooting

### No Providers Configured

**Error:** "NO AI PROVIDERS CONFIGURED!"

**Solution:**
1. Copy `backend/.env.example` to `backend/.env`
2. Add at least one API key to `.env`
3. Restart the application

### Provider Shows as DOWN

**Possible causes:**
1. Invalid API key
2. Network connectivity issues
3. Provider service is down
4. Rate limit exceeded

**Solutions:**
1. Verify API key is correct
2. Check network connection
3. Check provider status page
4. Wait for rate limit to reset

### Ollama Shows as DOWN

**Possible causes:**
1. Ollama is not installed
2. Ollama service is not running
3. Wrong endpoint URL

**Solutions:**
1. Install Ollama from https://ollama.ai
2. Start Ollama: `ollama serve`
3. Verify endpoint: `curl http://localhost:11434/api/tags`
4. Check OLLAMA_ENDPOINT in `.env`

## Best Practices

### For Development

1. **Use free providers first:**
   - Start with Ollama (local) or Gemini (cloud)
   - Add paid providers only when needed

2. **Test with multiple providers:**
   - Configure at least 2-3 providers
   - Test orchestration across different providers

3. **Monitor health regularly:**
   - Check `/health/providers` endpoint
   - Set up alerts for provider failures

### For Production

1. **Configure multiple providers:**
   - Have at least 2-3 providers for redundancy
   - Mix free and paid providers for cost optimization

2. **Implement fallback logic:**
   - Use the orchestration system's automatic fallback
   - Monitor which providers are being used

3. **Track costs:**
   - Monitor usage of paid providers
   - Set up cost alerts
   - Use free providers when possible

4. **Secure API keys:**
   - Never commit `.env` file to version control
   - Use environment variables in production
   - Rotate API keys regularly

## Integration with AI Council

The provider configuration system integrates with the AI Council orchestration system:

1. **Provider Selection:**
   - Orchestration layer queries available providers
   - Selects best provider for each subtask
   - Falls back to alternative providers on failure

2. **Cost Optimization:**
   - Prioritizes free providers when possible
   - Uses paid providers for complex tasks
   - Tracks cost per provider

3. **Health Monitoring:**
   - Checks provider health before routing
   - Skips unhealthy providers
   - Logs provider selection decisions

## API Reference

### ProviderConfig Class

```python
class ProviderConfig:
    def get_api_key(self, provider_name: str) -> Optional[str]
    def get_endpoint(self, provider_name: str) -> Optional[str]
    def is_provider_configured(self, provider_name: str) -> bool
    def get_configured_providers(self) -> List[str]
    def get_available_providers(self) -> List[str]
    def get_provider_info(self, provider_name: str) -> Optional[ProviderInfo]
    def get_all_providers_info(self) -> Dict[str, ProviderInfo]
    async def check_provider_health(self, provider_name: str) -> ProviderStatus
    async def check_all_providers_health(self) -> Dict[str, ProviderStatus]
    def log_provider_summary(self) -> None
```

### Helper Functions

```python
def get_provider_config() -> ProviderConfig
def initialize_provider_config() -> ProviderConfig
```

## See Also

- [API Keys Setup Guide](API_KEYS_SETUP.md)
- [Ollama Setup](OLLAMA_SETUP.md)
- [Gemini Setup](GEMINI_SETUP.md)
- [HuggingFace Setup](HUGGINGFACE_SETUP.md)
- [Groq Setup](GROQ_SETUP.md)
- [Together AI Setup](TOGETHER_SETUP.md)
- [OpenRouter Setup](OPENROUTER_SETUP.md)
- [OpenAI Setup](OPENAI_SETUP.md)
- [Qwen Setup](QWEN_SETUP.md)
