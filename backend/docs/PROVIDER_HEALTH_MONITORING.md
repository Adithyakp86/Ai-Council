# Provider Health Monitoring System

## Overview

The Provider Health Monitoring System provides real-time health status tracking for all AI provider integrations. It checks API key validity, measures response times, and integrates with the circuit breaker system to provide comprehensive provider status information.

## Features

- **API Key Validation**: Checks if API keys are valid without consuming credits
- **Response Time Measurement**: Tracks how long each provider takes to respond
- **Rate Limit Status**: Monitors rate limit information where available
- **Circuit Breaker Integration**: Considers circuit breaker state in health status
- **Caching**: Caches health status for 1 minute to avoid excessive checks
- **Concurrent Checking**: Checks all providers in parallel for fast results
- **Admin Dashboard Integration**: Displays provider status in admin monitoring dashboard

## Architecture

### Components

1. **ProviderHealthStatus**: Data class representing health status
   - `status`: "healthy", "degraded", or "down"
   - `last_check`: Timestamp of last health check
   - `response_time_ms`: Response time in milliseconds
   - `error_message`: Error description if unhealthy

2. **ProviderHealthChecker**: Main health checking service
   - Manages health checks for all providers
   - Implements caching with Redis
   - Integrates with circuit breaker
   - Provides concurrent checking

3. **Provider Clients**: Each provider client implements `health_check()` method
   - Groq: Checks `/models` endpoint
   - Together: Checks `/models` endpoint
   - OpenRouter: Checks `/models` endpoint
   - HuggingFace: Checks API token validity
   - Gemini: Checks `/models` endpoint
   - OpenAI: Checks `/models` endpoint
   - Ollama: Checks `/api/tags` endpoint
   - Qwen: Sends minimal test request

## Usage

### Checking Single Provider

```python
from app.services.provider_health_checker import get_health_checker

checker = get_health_checker()
status = await checker.check_provider_health("groq")

print(f"Status: {status.status}")
print(f"Response Time: {status.response_time_ms}ms")
if status.error_message:
    print(f"Error: {status.error_message}")
```

### Checking All Providers

```python
from app.services.provider_health_checker import get_health_checker

checker = get_health_checker()
statuses = await checker.check_all_providers()

for provider, status in statuses.items():
    print(f"{provider}: {status.status}")
```

### Admin API Endpoint

The health monitoring is integrated into the admin monitoring endpoint:

```bash
GET /api/v1/admin/monitoring
Authorization: Bearer <admin_token>
```

Response includes `provider_health` field:

```json
{
  "provider_health": {
    "groq": {
      "status": "healthy",
      "last_check": "2024-01-01T12:00:00",
      "response_time_ms": 150.5,
      "error_message": null
    },
    "together": {
      "status": "degraded",
      "last_check": "2024-01-01T12:00:00",
      "response_time_ms": 5000.0,
      "error_message": "Slow response"
    },
    "openrouter": {
      "status": "down",
      "last_check": "2024-01-01T12:00:00",
      "response_time_ms": null,
      "error_message": "API key not configured"
    }
  }
}
```

## Health Status Definitions

### Healthy
- Provider is responding normally
- API key is valid
- Response time is acceptable (<5 seconds)
- Circuit breaker is closed

### Degraded
- Provider is responding but slowly (>5 seconds)
- Circuit breaker is in half-open state (testing)
- API key is valid but rate limits are being approached

### Down
- Provider is not responding
- API key is invalid or not configured
- Circuit breaker is open (too many failures)
- Connection timeout or network error

## Caching

Health status is cached in Redis for 1 minute to avoid excessive API calls:

- **Cache Key Format**: `provider:health:{provider_name}`
- **TTL**: 60 seconds
- **Cache Invalidation**: Automatic after TTL expires

Benefits:
- Reduces API calls to providers
- Faster response times for admin dashboard
- Prevents rate limit issues from health checks

## Circuit Breaker Integration

The health checker integrates with the circuit breaker system:

1. **Circuit Breaker Closed**: Normal health check
2. **Circuit Breaker Half-Open**: Mark as "degraded" even if healthy
3. **Circuit Breaker Open**: Mark as "down" regardless of health check

This ensures the health status reflects the actual availability of the provider for request processing.

## Testing

### Unit Tests

Run the comprehensive test suite:

```bash
cd backend
python -m pytest tests/test_provider_health_monitoring.py -v
```

Tests cover:
- Health status conversion
- Individual provider checks
- Caching behavior
- Circuit breaker integration
- Concurrent checking
- Error handling

### Manual Testing

Test with actual API keys:

```bash
cd backend
python test_provider_health.py
```

This script:
- Checks all configured providers
- Demonstrates caching behavior
- Measures response times
- Shows concurrent checking performance

## Configuration

### Environment Variables

Each provider requires an API key or endpoint:

```bash
# Cloud Providers
GROQ_API_KEY=your_groq_key
TOGETHER_API_KEY=your_together_key
OPENROUTER_API_KEY=your_openrouter_key
HUGGINGFACE_TOKEN=your_hf_token
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
QWEN_API_KEY=your_qwen_key

# Local Provider
OLLAMA_ENDPOINT=http://localhost:11434
```

### Timeouts

Health checks have a 10-second timeout to prevent hanging:

```python
TIMEOUT = 10.0  # seconds
```

## Frontend Integration

The admin dashboard displays provider health status:

### System Monitoring Component

```typescript
interface ProviderHealthStatus {
  status: 'healthy' | 'degraded' | 'down';
  last_check: string;
  response_time_ms?: number;
  error_message?: string;
}

// Display in admin dashboard
{Object.entries(providerHealth).map(([provider, status]) => (
  <div key={provider}>
    <span className={getStatusColor(status.status)}>
      {provider}: {status.status}
    </span>
    {status.response_time_ms && (
      <span>{status.response_time_ms.toFixed(0)}ms</span>
    )}
  </div>
))}
```

### Status Colors

- **Healthy**: Green (✓)
- **Degraded**: Yellow (⚠)
- **Down**: Red (✗)

## Monitoring and Alerts

### Logging

Health check results are logged:

```python
logger.info(f"Provider {provider} health: {status}")
logger.error(f"Provider {provider} health check failed: {error}")
```

### Future Enhancements

Potential improvements:
1. **Alerts**: Send notifications when providers go down
2. **Metrics**: Track uptime percentage over time
3. **Historical Data**: Store health check history in database
4. **Auto-Retry**: Automatically retry failed health checks
5. **Rate Limit Tracking**: Monitor remaining rate limit quota
6. **Cost Tracking**: Track API costs per provider

## Troubleshooting

### Provider Shows as "Down" but API Key is Valid

1. Check if circuit breaker is open:
   ```python
   from app.services.cloud_ai.circuit_breaker import get_circuit_breaker
   cb = get_circuit_breaker()
   state = cb.get_state("provider_name")
   print(f"Circuit breaker state: {state}")
   ```

2. Check Redis cache:
   ```bash
   redis-cli GET provider:health:provider_name
   ```

3. Clear cache and retry:
   ```bash
   redis-cli DEL provider:health:provider_name
   ```

### Slow Health Checks

If health checks are taking too long:

1. Check network connectivity
2. Verify provider API is not experiencing issues
3. Check if rate limits are being hit
4. Review timeout settings

### Cache Not Working

If caching is not working:

1. Verify Redis is running:
   ```bash
   redis-cli PING
   ```

2. Check Redis connection in logs
3. Verify REDIS_URL environment variable

## API Reference

### ProviderHealthChecker

#### `check_provider_health(provider: str) -> ProviderHealthStatus`

Check health of a single provider with caching.

**Parameters:**
- `provider`: Provider name (groq, together, openrouter, etc.)

**Returns:**
- `ProviderHealthStatus` object

**Example:**
```python
status = await checker.check_provider_health("groq")
```

#### `check_all_providers() -> Dict[str, ProviderHealthStatus]`

Check health of all providers concurrently.

**Returns:**
- Dictionary mapping provider names to health status

**Example:**
```python
statuses = await checker.check_all_providers()
```

### Provider Client Health Check

Each provider client implements:

#### `health_check() -> Dict[str, any]`

Check if provider API is accessible and API key is valid.

**Returns:**
- Dictionary with health information:
  - `status`: "healthy", "error", or "down"
  - `provider`: Provider name
  - `error`: Error message if unhealthy
  - Additional provider-specific fields

**Example:**
```python
from app.services.cloud_ai.groq_client import GroqClient

client = GroqClient(api_key="your_key")
health = client.health_check()
print(health["status"])
```

## Performance

### Benchmarks

Typical performance metrics:

- **Single Provider Check**: 100-500ms (first check)
- **Single Provider Check (cached)**: <10ms
- **All Providers Check**: 500-2000ms (concurrent)
- **Cache Hit Rate**: >90% in production

### Optimization Tips

1. Use caching for frequent checks
2. Check all providers concurrently
3. Set appropriate timeouts
4. Monitor Redis performance

## Security

### API Key Protection

- API keys are never exposed in health check responses
- Health checks use minimal API calls
- No sensitive data is cached
- Logs do not contain API keys

### Rate Limiting

Health checks are designed to minimize API usage:
- Cached for 1 minute
- Use lightweight endpoints
- Minimal request payloads
- Respect provider rate limits

## Conclusion

The Provider Health Monitoring System provides comprehensive visibility into the health and performance of all AI provider integrations. It enables proactive monitoring, quick troubleshooting, and informed decision-making for system administrators.
