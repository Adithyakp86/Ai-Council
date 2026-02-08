# OpenAI Integration Setup Guide

## Overview

OpenAI provides industry-leading language models including GPT-3.5 and GPT-4. This integration is **OPTIONAL** and requires a payment method, but includes $5 in free trial credits.

**Note:** This is a premium integration for users who need the highest quality AI capabilities. Free alternatives are available (Gemini, HuggingFace, Ollama).

## Features

- **GPT-3.5-Turbo**: Fast and cost-effective for most tasks
- **GPT-4**: Most capable model with superior reasoning
- **GPT-4-Turbo**: Latest GPT-4 with improved performance and larger context
- Industry-leading quality and reliability
- Extensive context windows (up to 128K tokens)
- Function calling and JSON mode support

## Pricing (as of 2024)

| Model | Input Cost | Output Cost | Context Window |
|-------|-----------|-------------|----------------|
| GPT-3.5-Turbo | $0.50 per 1M tokens | $1.50 per 1M tokens | 16K tokens |
| GPT-4 | $30 per 1M tokens | $60 per 1M tokens | 8K tokens |
| GPT-4-Turbo | $10 per 1M tokens | $30 per 1M tokens | 128K tokens |

**Free Trial:** New accounts receive $5 in free credits (valid for 3 months).

## Setup Instructions

### Step 1: Create OpenAI Account

1. Go to [https://platform.openai.com](https://platform.openai.com)
2. Click "Sign up" and create an account
3. Verify your email address

### Step 2: Add Payment Method

1. Go to [https://platform.openai.com/account/billing/overview](https://platform.openai.com/account/billing/overview)
2. Click "Add payment method"
3. Enter your credit/debit card information
4. **Note:** You'll receive $5 in free trial credits automatically

### Step 3: Get API Key

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Give it a name (e.g., "AI Council Integration")
4. Copy the API key (starts with `sk-`)
5. **Important:** Save this key securely - you won't be able to see it again!

### Step 4: Configure Environment Variable

Add your API key to `backend/.env`:

```bash
# OpenAI - Requires payment method ($5 free trial)
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Step 5: Test the Integration

Run the test script to verify everything works:

```bash
cd backend
python test_openai_integration.py
```

Expected output:
```
✅ All tests passed! OpenAI integration is working correctly.
```

### Step 6: Try the Examples

Run the example script to see OpenAI in action:

```bash
cd backend
python examples/openai_example.py
```

## Usage in AI Council

Once configured, OpenAI models are automatically available in the AI Council orchestration system:

```python
from app.services.cloud_ai.openai_adapter import OpenAIAdapter

# Create adapter
adapter = OpenAIAdapter(model_id="gpt-3.5-turbo", api_key=api_key)

# Generate response
response = adapter.generate_response(
    "Explain quantum computing in simple terms",
    max_tokens=200,
    temperature=0.7
)
```

## Available Models

### GPT-3.5-Turbo
- **Best for:** General tasks, fast responses, cost-effective
- **Capabilities:** Reasoning, research, code generation, creative writing
- **Context:** 16K tokens
- **Speed:** ~1 second average latency

### GPT-4
- **Best for:** Complex reasoning, high-quality outputs
- **Capabilities:** All tasks, superior reasoning, fact-checking, debugging
- **Context:** 8K tokens
- **Speed:** ~3 seconds average latency
- **Note:** Requires GPT-4 API access (may need to join waitlist)

### GPT-4-Turbo
- **Best for:** Long documents, complex analysis
- **Capabilities:** All tasks, large context window
- **Context:** 128K tokens
- **Speed:** ~2.5 seconds average latency
- **Note:** Latest model with best performance

## Model Selection in AI Council

The AI Council orchestration system automatically selects the best model for each subtask based on:

1. **Task Type:** Code generation → GPT-3.5/GPT-4
2. **Complexity:** Simple → GPT-3.5, Complex → GPT-4
3. **Execution Mode:**
   - FAST: Prefers GPT-3.5-Turbo (cheaper, faster)
   - BALANCED: Mix of GPT-3.5 and GPT-4
   - BEST_QUALITY: Prefers GPT-4 (highest quality)

## Cost Management

### Monitor Usage

1. Go to [https://platform.openai.com/usage](https://platform.openai.com/usage)
2. View real-time usage and costs
3. Set up usage alerts

### Set Spending Limits

1. Go to [https://platform.openai.com/account/billing/limits](https://platform.openai.com/account/billing/limits)
2. Set monthly spending limit
3. Set email alerts for usage thresholds

### Cost Optimization Tips

1. **Use GPT-3.5 for simple tasks:** 20x cheaper than GPT-4
2. **Limit max_tokens:** Only request what you need
3. **Use FAST mode:** Minimizes decomposition and uses cheaper models
4. **Monitor per-request costs:** Check orchestration metadata
5. **Mix with free providers:** Use Gemini/HuggingFace for research tasks

## Troubleshooting

### Error: "Invalid API key"

**Solution:**
1. Verify API key is correct (starts with `sk-`)
2. Check for extra spaces or newlines
3. Regenerate key if needed

### Error: "Rate limit exceeded"

**Solution:**
1. Check your usage tier at [https://platform.openai.com/account/limits](https://platform.openai.com/account/limits)
2. Wait a few seconds and retry
3. Implement exponential backoff (already built into circuit breaker)

### Error: "Insufficient quota"

**Solution:**
1. Check your balance at [https://platform.openai.com/account/billing/overview](https://platform.openai.com/account/billing/overview)
2. Add more credits or update payment method
3. Free trial credits expire after 3 months

### Error: "Model not found" (GPT-4)

**Solution:**
1. GPT-4 access may require joining waitlist
2. Use GPT-3.5-Turbo instead
3. Check [https://platform.openai.com/docs/models](https://platform.openai.com/docs/models) for available models

## Comparison with Other Providers

| Feature | OpenAI | Gemini (Free) | HuggingFace (Free) |
|---------|--------|---------------|-------------------|
| Cost | $0.50-60/1M tokens | Free | Free |
| Quality | Highest | High | Medium |
| Speed | Fast (1-3s) | Fast (2s) | Slower (2-3s) |
| Context | Up to 128K | 32K | 4-32K |
| Reliability | 98% | 92% | 85% |
| Setup | Payment required | No payment | No payment |

**When to use OpenAI:**
- Need highest quality outputs
- Complex reasoning tasks
- Production applications
- Budget allows for premium service

**When to use free alternatives:**
- Development and testing
- Simple tasks
- Budget constraints
- Learning and experimentation

## Security Best Practices

1. **Never commit API keys to git**
   - Use `.env` file (already in `.gitignore`)
   - Use environment variables in production

2. **Rotate keys regularly**
   - Generate new keys every 90 days
   - Revoke old keys immediately

3. **Use separate keys for dev/prod**
   - Different keys for different environments
   - Easier to track usage and revoke if needed

4. **Monitor for unusual activity**
   - Check usage dashboard regularly
   - Set up email alerts
   - Investigate unexpected spikes

## Additional Resources

- **Official Documentation:** [https://platform.openai.com/docs](https://platform.openai.com/docs)
- **API Reference:** [https://platform.openai.com/docs/api-reference](https://platform.openai.com/docs/api-reference)
- **Pricing:** [https://openai.com/pricing](https://openai.com/pricing)
- **Usage Dashboard:** [https://platform.openai.com/usage](https://platform.openai.com/usage)
- **Community Forum:** [https://community.openai.com](https://community.openai.com)
- **Status Page:** [https://status.openai.com](https://status.openai.com)

## Support

If you encounter issues:

1. Check this documentation first
2. Review OpenAI's official docs
3. Check the status page for outages
4. Contact OpenAI support: [https://help.openai.com](https://help.openai.com)
5. Open an issue in the AI Council repository

## Next Steps

After setting up OpenAI:

1. ✅ Test the integration with `test_openai_integration.py`
2. ✅ Try the examples in `examples/openai_example.py`
3. ✅ Monitor your usage at [https://platform.openai.com/usage](https://platform.openai.com/usage)
4. ✅ Set spending limits to control costs
5. ✅ Use OpenAI models in your AI Council orchestration
6. ✅ Compare quality with free alternatives (Gemini, HuggingFace)
7. ✅ Optimize costs by mixing providers based on task complexity

---

**Remember:** OpenAI is an optional premium integration. The AI Council system works great with free providers (Gemini, HuggingFace, Ollama) for most use cases!
