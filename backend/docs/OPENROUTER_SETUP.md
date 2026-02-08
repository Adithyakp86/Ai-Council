# OpenRouter Setup Guide

OpenRouter provides unified access to AI models from multiple providers (OpenAI, Anthropic, Google, Meta, and more) through a single API. This guide will help you set up OpenRouter for the AI Council application.

## Overview

**Provider:** OpenRouter  
**Website:** https://openrouter.ai  
**Pricing:** Pay-as-you-go with free credits on signup ($1-5)  
**Free Credits:** Yes, $1-5 on signup (expires after some time)  
**Rate Limits:** Varies by model, generally generous  
**Best For:** Access to premium models (GPT-4, Claude) without separate API keys

## Why Use OpenRouter?

1. **Unified Access**: Single API key for models from OpenAI, Anthropic, Google, Meta, and more
2. **Free Credits**: Get $1-5 in free credits on signup to test the service
3. **Transparent Pricing**: Clear pricing per model with usage tracking
4. **Automatic Fallbacks**: If one model is unavailable, easily switch to another
5. **No Separate Billing**: One account for multiple AI providers
6. **Developer-Friendly**: Simple REST API with OpenAI-compatible format

## Supported Models in AI Council

The AI Council application supports the following OpenRouter models:

### 1. GPT-3.5 Turbo (OpenAI)
- **Model ID:** `openai/gpt-3.5-turbo`
- **Best For:** Fast, cost-effective general-purpose tasks
- **Capabilities:** Reasoning, Research, Code Generation, Creative Output
- **Cost:** $0.50 per 1M input tokens, $1.50 per 1M output tokens
- **Context:** 16,385 tokens
- **Speed:** ~1.5 seconds average latency

### 2. Claude Instant 1 (Anthropic)
- **Model ID:** `anthropic/claude-instant-1`
- **Best For:** Quick responses with good reasoning
- **Capabilities:** Reasoning, Research, Creative Output, Fact Checking
- **Cost:** $1.63 per 1M input tokens, $5.51 per 1M output tokens
- **Context:** 100,000 tokens
- **Speed:** ~1.2 seconds average latency

### 3. Llama 2 70B Chat (Meta)
- **Model ID:** `meta-llama/llama-2-70b-chat`
- **Best For:** Open-source, powerful for research tasks
- **Capabilities:** Reasoning, Research, Creative Output
- **Cost:** $0.70 per 1M input tokens, $0.90 per 1M output tokens
- **Context:** 4,096 tokens
- **Speed:** ~2.0 seconds average latency

### 4. PaLM 2 Chat Bison (Google)
- **Model ID:** `google/palm-2-chat-bison`
- **Best For:** Conversational AI with good fact-checking
- **Capabilities:** Reasoning, Research, Creative Output, Fact Checking
- **Cost:** $0.25 per 1M input tokens, $0.50 per 1M output tokens
- **Context:** 8,192 tokens
- **Speed:** ~1.8 seconds average latency

### 5. Claude 3 Sonnet (Anthropic) - Premium
- **Model ID:** `anthropic/claude-3-sonnet`
- **Best For:** High-quality reasoning and code generation
- **Capabilities:** Reasoning, Research, Code Generation, Fact Checking
- **Cost:** $3.00 per 1M input tokens, $15.00 per 1M output tokens
- **Context:** 200,000 tokens
- **Speed:** ~2.0 seconds average latency

### 6. GPT-4 Turbo (OpenAI) - Premium
- **Model ID:** `openai/gpt-4-turbo`
- **Best For:** Complex reasoning and debugging tasks
- **Capabilities:** Reasoning, Code Generation, Debugging
- **Cost:** $10.00 per 1M input tokens, $30.00 per 1M output tokens
- **Context:** 128,000 tokens
- **Speed:** ~3.0 seconds average latency

## Setup Instructions

### Step 1: Create OpenRouter Account

1. Go to https://openrouter.ai
2. Click **"Sign Up"** in the top right corner
3. Sign up with:
   - Email and password, OR
   - GitHub account, OR
   - Google account
4. Verify your email address (check spam folder if needed)

### Step 2: Get Your API Key

1. After logging in, go to https://openrouter.ai/keys
2. Click **"Create Key"** button
3. Give your key a name (e.g., "AI Council Development")
4. Optional: Set a spending limit to control costs
5. Click **"Create"**
6. **IMPORTANT:** Copy your API key immediately - it won't be shown again!
   - Format: `sk-or-v1-...` (starts with `sk-or-v1-`)

### Step 3: Check Your Free Credits

1. Go to https://openrouter.ai/credits
2. You should see $1-5 in free credits
3. Note: Free credits may expire after 30-90 days
4. You can add a payment method later if needed

### Step 4: Configure AI Council Backend

1. Open `backend/.env` file (create from `.env.example` if it doesn't exist)
2. Add your OpenRouter API key:

```bash
# OpenRouter - $1-5 free credits on signup
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

3. Save the file

### Step 5: Verify Configuration

Run the verification script to test your OpenRouter setup:

```bash
cd backend
python -c "
from app.services.cloud_ai.openrouter_adapter import OpenRouterAdapter
import os

api_key = os.getenv('OPENROUTER_API_KEY')
if not api_key:
    print('❌ OPENROUTER_API_KEY not found in environment')
    exit(1)

print('✓ API key found')
print('Testing OpenRouter connection...')

try:
    adapter = OpenRouterAdapter('openai/gpt-3.5-turbo', api_key)
    response = adapter.generate_response('Say hello in one word')
    print(f'✓ OpenRouter is working! Response: {response}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

Expected output:
```
✓ API key found
Testing OpenRouter connection...
✓ OpenRouter is working! Response: Hello
```

## Testing Multiple Models

Test all supported OpenRouter models:

```bash
cd backend
python -c "
from app.services.cloud_ai.openrouter_adapter import OpenRouterAdapter
import os

api_key = os.getenv('OPENROUTER_API_KEY')
models = [
    'openai/gpt-3.5-turbo',
    'anthropic/claude-instant-1',
    'meta-llama/llama-2-70b-chat',
    'google/palm-2-chat-bison'
]

for model in models:
    try:
        adapter = OpenRouterAdapter(model, api_key)
        response = adapter.generate_response('Say hello')
        print(f'✓ {model}: {response[:50]}...')
    except Exception as e:
        print(f'❌ {model}: {e}')
"
```

## Usage in AI Council

Once configured, OpenRouter models will be automatically available in the AI Council orchestration system. The system will:

1. **Automatic Selection**: Choose the best OpenRouter model based on task type
2. **Cost Optimization**: Prefer cheaper models (PaLM 2, Llama 2) for simple tasks
3. **Quality Optimization**: Use premium models (GPT-4, Claude 3) for complex tasks
4. **Parallel Execution**: Distribute subtasks across multiple OpenRouter models
5. **Fallback**: Switch to other providers if OpenRouter is unavailable

### Example: Using OpenRouter in a Request

When you submit a request through the AI Council web interface:

```
User Query: "Explain quantum computing and write a Python example"

AI Council Orchestration:
├─ Subtask 1: Explain quantum computing
│  └─ Assigned to: openrouter-claude-instant-1 (good for explanations)
│
└─ Subtask 2: Write Python example
   └─ Assigned to: openrouter-gpt-3.5-turbo (good for code)

Total Cost: ~$0.002 (using free credits)
```

## Cost Management

### Monitoring Usage

1. Go to https://openrouter.ai/activity
2. View your usage by model and date
3. Track remaining credits
4. Set up spending alerts

### Cost Optimization Tips

1. **Use Cheaper Models First**: Start with GPT-3.5 or PaLM 2 for testing
2. **Set Spending Limits**: Configure limits in OpenRouter dashboard
3. **Monitor in AI Council**: Check cost breakdown in response metadata
4. **Use Free Providers**: Combine with Gemini or HuggingFace for zero-cost options

### Estimated Costs

Based on typical AI Council usage:

| Task Type | Model | Tokens | Cost per Request |
|-----------|-------|--------|------------------|
| Simple query | GPT-3.5 Turbo | ~500 | $0.0005 |
| Medium query | Claude Instant | ~1000 | $0.003 |
| Complex query | GPT-4 Turbo | ~2000 | $0.08 |
| Code generation | GPT-3.5 Turbo | ~800 | $0.0015 |

**Note:** $1 in free credits = ~2000 simple queries or ~12 complex queries

## Required Headers

OpenRouter requires two special headers for all requests:

1. **HTTP-Referer**: Your application URL (e.g., `https://aicouncil.app`)
2. **X-Title**: Your application name (e.g., `AI Council`)

These are automatically included by the OpenRouter adapter. No action needed!

## Troubleshooting

### Error: "Invalid API key"

**Solution:**
1. Check that your API key starts with `sk-or-v1-`
2. Verify the key is correctly copied (no extra spaces)
3. Regenerate the key at https://openrouter.ai/keys

### Error: "Insufficient credits"

**Solution:**
1. Check your balance at https://openrouter.ai/credits
2. Add a payment method if free credits are exhausted
3. Use free providers (Gemini, HuggingFace) as alternatives

### Error: "Model not found"

**Solution:**
1. Verify the model ID is correct (e.g., `openai/gpt-3.5-turbo`)
2. Check OpenRouter's model list: https://openrouter.ai/models
3. Some models may be temporarily unavailable

### Error: "Rate limit exceeded"

**Solution:**
1. Wait a few seconds and retry
2. OpenRouter has generous rate limits, but they vary by model
3. Use circuit breaker to automatically handle rate limits

### Slow Response Times

**Solution:**
1. Some models (GPT-4, Claude 3) are slower due to their size
2. Use faster models (GPT-3.5, Claude Instant) for time-sensitive tasks
3. Check OpenRouter status: https://openrouter.ai/status

## Advanced Configuration

### Custom Model Selection

You can force AI Council to use specific OpenRouter models:

```python
from app.services.execution_mode_config import ExecutionModeConfig

# Force GPT-4 for all tasks (expensive but highest quality)
config = ExecutionModeConfig(
    mode="custom",
    preferred_models=["openrouter-gpt4-turbo"]
)
```

### Mixing Providers

Combine OpenRouter with other providers for optimal cost/quality:

```python
# Use free providers for simple tasks, OpenRouter for complex ones
config = ExecutionModeConfig(
    mode="balanced",
    cheap_models=["gemini-pro", "huggingface-mistral-7b"],
    premium_models=["openrouter-gpt4-turbo", "openrouter-claude-3-sonnet"]
)
```

## Security Best Practices

1. **Never commit API keys**: Keep `.env` file out of version control
2. **Use environment variables**: Don't hardcode keys in code
3. **Rotate keys regularly**: Generate new keys every 90 days
4. **Set spending limits**: Prevent unexpected charges
5. **Monitor usage**: Check OpenRouter dashboard weekly

## Additional Resources

- **OpenRouter Documentation**: https://openrouter.ai/docs
- **Model Pricing**: https://openrouter.ai/models
- **API Reference**: https://openrouter.ai/docs/api-reference
- **Discord Community**: https://discord.gg/openrouter
- **Status Page**: https://openrouter.ai/status

## Next Steps

After setting up OpenRouter:

1. ✅ Test with a simple query in AI Council
2. ✅ Try different models to compare quality and cost
3. ✅ Monitor your usage and remaining credits
4. ✅ Set up additional providers (Gemini, HuggingFace) for fallback
5. ✅ Configure execution modes to optimize cost/quality trade-offs

## Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review OpenRouter documentation: https://openrouter.ai/docs
3. Check AI Council logs: `backend/logs/`
4. Join OpenRouter Discord: https://discord.gg/openrouter
5. Open an issue on AI Council GitHub repository

---

**Last Updated:** 2024-01-15  
**OpenRouter Version:** v1  
**AI Council Version:** 1.0.0
