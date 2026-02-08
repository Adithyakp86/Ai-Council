# Dynamic Provider Selection and Orchestration

## Overview

The AI Council web application now features intelligent dynamic provider selection and orchestration. The system automatically detects available AI providers at runtime, prioritizes them based on multiple criteria, and implements intelligent fallback when providers fail.

## Key Features

### 1. Runtime Provider Detection

The system detects which AI providers are available based on:
- **API Key Configuration**: Providers with valid API keys in `.env` file
- **Endpoint Configuration**: For local providers like Ollama (no API key needed)
- **Provider Health**: Circuit breaker status and availability

**Benefits:**
- No need to manually configure which providers to use
- Automatically adapts to available resources
- Gracefully handles missing API keys

### 2. Intelligent Provider Prioritization

When routing subtasks to models, the system prioritizes providers based on:

1. **Availability** (40% weight) - Provider must be configured and healthy
2. **Cost** (25% weight) - Lower cost per token = higher priority
3. **Latency** (15% weight) - Faster response time = higher priority
4. **Capabilities** (10% weight) - More task type support = higher priority
5. **Reliability** (10% weight) - Higher reliability score = higher priority

**Example:**
```
For a reasoning task with 3 available providers:
- groq-llama3-70b: Score 87.5 (fast, cheap, reliable)
- together-mixtral-8x7b: Score 82.3 (moderate cost, good capabilities)
- openrouter-gpt4-turbo: Score 75.1 (expensive, but highest quality)

Selected: groq-llama3-70b (highest score)
```

### 3. Automatic Fallback on Failure

If a primary provider fails, the system automatically:
1. Identifies alternative models for the same task type
2. Prioritizes fallback options using the same scoring algorithm
3. Attempts execution with the top fallback model
4. Logs the fallback decision for transparency

**Example Fallback Flow:**
```
Primary: groq-llama3-70b → FAILED (rate limit exceeded)
Fallback: together-mixtral-8x7b → SUCCESS
Result: Task completed with fallback provider
```

### 4. Provider Distribution Across Subtasks

The system distributes subtasks across multiple providers for:
- **Parallel Execution**: Different providers handle different subtasks simultaneously
- **Load Balancing**: Prevents overloading a single provider
- **Cost Optimization**: Uses cheaper providers where appropriate
- **Risk Mitigation**: Reduces dependency on any single provider

### 5. Comprehensive Logging

Every provider selection decision is logged with:
- Subtask ID and type
- Selected model and provider
- Reason for selection
- Alternative models considered
- Cost, latency, and reliability metrics
- Timestamp

**Log Entry Example:**
```json
{
  "subtask_id": "task-123",
  "subtask_type": "reasoning",
  "selected_model": "groq-llama3-70b",
  "selected_provider": "groq",
  "reason": "Best cost/performance ratio",
  "alternatives": ["together-mixtral-8x7b", "openrouter-gpt4-turbo"],
  "cost_per_token": 0.00000069,
  "latency": 0.5,
  "reliability": 0.95,
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

## Response Metadata

The final response includes provider selection metadata:

```json
{
  "content": "Final synthesized response...",
  "overallConfidence": 0.92,
  "providerSelectionLog": [
    {
      "subtask_id": "task-1",
      "selected_provider": "groq",
      "selected_model": "groq-llama3-70b",
      "reason": "Fast inference for reasoning task",
      "alternatives": ["together-mixtral-8x7b"],
      "cost_per_token": 0.00000069,
      "latency": 0.5,
      "reliability": 0.95
    },
    {
      "subtask_id": "task-2",
      "selected_provider": "together",
      "selected_model": "together-mixtral-8x7b",
      "reason": "Good for code generation",
      "alternatives": ["groq-llama3-70b"],
      "cost_per_token": 0.0000006,
      "latency": 1.2,
      "reliability": 0.92
    }
  ],
  "providerUsageSummary": {
    "groq": 3,
    "together": 2,
    "openrouter": 1
  }
}
```

## Configuration

### Setting Up Providers

1. **Add API Keys to `.env`:**
```bash
# Free/Low-Cost Providers (Recommended for getting started)
GEMINI_API_KEY=your_gemini_key_here
HUGGINGFACE_TOKEN=your_hf_token_here
OLLAMA_ENDPOINT=http://localhost:11434

# Paid Providers (Optional)
GROQ_API_KEY=your_groq_key_here
TOGETHER_API_KEY=your_together_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
OPENAI_API_KEY=your_openai_key_here
QWEN_API_KEY=your_qwen_key_here
```

2. **System Auto-Detection:**
   - On startup, the system detects which providers are configured
   - Only models from available providers are registered
   - No manual configuration needed

3. **Verify Available Providers:**
   - Check application logs on startup
   - Look for "Available providers: ..." message
   - Admin dashboard shows provider health status

## Usage Examples

### Example 1: Single Provider Available

```
Configuration:
- Only GEMINI_API_KEY is set

Behavior:
- System detects only Gemini is available
- All subtasks are routed to Gemini models
- No fallback needed (only one provider)

Result:
- providerUsageSummary: { "gemini": 5 }
```

### Example 2: Multiple Providers Available

```
Configuration:
- GROQ_API_KEY, TOGETHER_API_KEY, GEMINI_API_KEY are set

Behavior:
- System detects 3 available providers
- Subtasks distributed based on prioritization:
  - Fast reasoning tasks → Groq (fastest)
  - Code generation → Together (good for code)
  - Research tasks → Gemini (free tier)

Result:
- providerUsageSummary: { "groq": 3, "together": 2, "gemini": 1 }
```

### Example 3: Provider Failure with Fallback

```
Scenario:
- Primary provider (Groq) hits rate limit
- Fallback to Together AI

WebSocket Updates:
1. "routing_complete": Assigned to groq-llama3-70b
2. "execution_progress": {
     "status": "completed",
     "usedFallback": true,
     "primaryModelFailed": "groq-llama3-70b",
     "fallbackModel": "together-mixtral-8x7b",
     "fallbackReason": "Rate limit exceeded"
   }

Result:
- Task completed successfully using fallback
- User sees transparent fallback information
```

## Benefits

### For Users
- **Reliability**: Automatic fallback ensures tasks complete even if providers fail
- **Transparency**: See which providers handled which parts of your request
- **Cost Efficiency**: System automatically uses cheaper providers when appropriate
- **Performance**: Faster providers are prioritized for time-sensitive tasks

### For Developers
- **Flexibility**: Easy to add/remove providers by changing `.env` file
- **Observability**: Comprehensive logging of all provider decisions
- **Maintainability**: No hardcoded provider logic
- **Scalability**: Distributes load across multiple providers

### For System Operators
- **Resilience**: System continues working even if some providers are down
- **Cost Control**: Automatic optimization reduces API costs
- **Monitoring**: Provider usage metrics in response metadata
- **Configuration**: Simple environment variable management

## Implementation Details

### Provider Detection Flow

```
1. Application Startup
   ↓
2. Load ProviderConfig
   ↓
3. Check environment variables for API keys
   ↓
4. Mark providers as available/unavailable
   ↓
5. Log provider summary
   ↓
6. Ready to process requests
```

### Request Processing Flow

```
1. User submits request
   ↓
2. Detect available providers at runtime
   ↓
3. Initialize AI Council with only available providers
   ↓
4. Task decomposition (AI Council)
   ↓
5. For each subtask:
   a. Get models for task type
   b. Filter to available providers
   c. Prioritize by scoring algorithm
   d. Select top model
   e. Log selection decision
   ↓
6. Execute subtasks (with fallback on failure)
   ↓
7. Synthesize results
   ↓
8. Include provider metadata in response
```

### Prioritization Algorithm

```python
def calculate_priority_score(model):
    # Normalize each metric to 0-100 scale
    availability_score = 100  # Already filtered
    cost_score = normalize_cost(model.cost_per_token)
    latency_score = normalize_latency(model.average_latency)
    capabilities_score = normalize_capabilities(model.capabilities)
    reliability_score = model.reliability_score * 100
    
    # Weighted sum
    total_score = (
        availability_score * 0.40 +
        cost_score * 0.25 +
        latency_score * 0.15 +
        capabilities_score * 0.10 +
        reliability_score * 0.10
    )
    
    return total_score
```

## Testing

Run the dynamic provider selection tests:

```bash
cd backend
python -m pytest tests/test_dynamic_provider_selection.py -v
```

Test coverage includes:
- Provider detection with/without API keys
- Ollama detection without API key
- Provider prioritization by cost
- Filtering unavailable providers
- Provider selection logging
- Model registration with available providers only
- Provider usage summary in responses

## Troubleshooting

### No Providers Available

**Symptom:** Error message "No AI providers configured or available"

**Solution:**
1. Check `.env` file has at least one provider API key
2. Verify API key format is correct
3. Check application logs for provider detection messages
4. Try a free provider first (Gemini or HuggingFace)

### Provider Fallback Not Working

**Symptom:** Request fails instead of using fallback

**Solution:**
1. Ensure multiple providers are configured
2. Check that fallback providers support the same task type
3. Review provider selection logs for details
4. Verify circuit breaker hasn't opened all providers

### Unexpected Provider Selection

**Symptom:** System selects expensive provider when cheaper one is available

**Solution:**
1. Check prioritization scores in logs
2. Verify cheaper provider supports the task type
3. Review execution mode settings (BEST_QUALITY prioritizes quality over cost)
4. Check if cheaper provider's circuit breaker is open

## Future Enhancements

Potential improvements for future versions:

1. **Dynamic Weight Adjustment**: Allow users to customize prioritization weights
2. **Provider Quotas**: Set usage limits per provider
3. **Cost Budgets**: Automatically switch to cheaper providers when approaching budget
4. **Performance Learning**: Adjust priorities based on historical performance
5. **Geographic Routing**: Prefer providers with lower latency based on user location
6. **Provider Health Monitoring**: Real-time health checks and automatic circuit breaker management

## Related Documentation

- [Provider Configuration Guide](./PROVIDER_CONFIGURATION.md)
- [API Keys Setup](./API_KEYS_SETUP.md)
- [Circuit Breaker Documentation](../app/services/cloud_ai/circuit_breaker.py)
- [Model Registry](../app/services/cloud_ai/model_registry.py)
