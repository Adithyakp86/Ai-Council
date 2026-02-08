# Together AI Setup Guide

This guide will help you set up Together AI integration for the AI Council web application.

## Overview

Together AI provides high-performance inference for open-source AI models with:
- **$25 free credits** on signup (generous for prototyping)
- Fast inference with optimized infrastructure
- Support for latest open-source models (Llama, Mixtral, Yi, and more)
- Competitive pricing for production workloads
- Simple REST API with streaming support

## Supported Models

The AI Council integration supports three Together AI models:

### 1. Llama-2-70B-Chat
- **Model ID**: `togethercomputer/llama-2-70b-chat`
- **Capabilities**: Research, Creative Output, Reasoning
- **Context Length**: 4,096 tokens
- **Best For**: General-purpose tasks, research, creative writing
- **Cost**: ~$0.90 per 1M tokens

### 2. Mixtral-8x7B-Instruct
- **Model ID**: `mistralai/Mixtral-8x7B-Instruct-v0.1`
- **Capabilities**: Reasoning, Code Generation
- **Context Length**: 32,768 tokens
- **Best For**: Complex reasoning, code generation, long-context tasks
- **Cost**: ~$0.60 per 1M tokens

### 3. Nous-Hermes-2-Yi-34B
- **Model ID**: `NousResearch/Nous-Hermes-2-Yi-34B`
- **Capabilities**: Reasoning, Research, Code Generation, Creative Output
- **Context Length**: 4,096 tokens
- **Best For**: Instruction following, multi-task scenarios, balanced performance
- **Cost**: ~$0.80 per 1M tokens

## Step-by-Step Setup

### Step 1: Create Together AI Account

1. Go to [https://api.together.xyz](https://api.together.xyz)
2. Click **"Sign Up"** in the top right corner
3. Sign up with your email or GitHub account
4. Verify your email address

### Step 2: Get Your API Key

1. After logging in, navigate to the **API Keys** section
2. Click **"Create new API key"**
3. Give your key a descriptive name (e.g., "AI Council Development")
4. Click **"Create"**
5. **Copy your API key immediately** - it won't be shown again!
   - Format: `together_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 3: Check Your Free Credits

1. Navigate to the **Billing** section in your dashboard
2. You should see **$25 in free credits** automatically applied
3. These credits are generous and should last for extensive prototyping
4. Credits typically expire after 3 months

### Step 4: Configure Your Application

1. Open your `backend/.env` file
2. Add your Together AI API key:

```bash
# Together AI - $25 free credits on signup
TOGETHER_API_KEY=together_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

3. Save the file

### Step 5: Verify the Integration

Run the test script to verify your Together AI integration:

```bash
cd backend
python -c "
from app.services.cloud_ai.together_adapter import TogetherAdapter
import os

api_key = os.getenv('TOGETHER_API_KEY')
if not api_key:
    print('❌ TOGETHER_API_KEY not found in environment')
    exit(1)

print('Testing Together AI integration...')
print()

# Test Mixtral-8x7B
print('1. Testing Mixtral-8x7B-Instruct...')
adapter = TogetherAdapter('mistralai/Mixtral-8x7B-Instruct-v0.1', api_key)
response = adapter.generate_response('What is 2+2? Answer in one word.')
print(f'   Response: {response[:100]}')
print('   ✅ Mixtral-8x7B working!')
print()

# Test Llama-2-70B
print('2. Testing Llama-2-70B-Chat...')
adapter = TogetherAdapter('togethercomputer/llama-2-70b-chat', api_key)
response = adapter.generate_response('Say hello in one sentence.')
print(f'   Response: {response[:100]}')
print('   ✅ Llama-2-70B working!')
print()

# Test Nous-Hermes-2-Yi-34B
print('3. Testing Nous-Hermes-2-Yi-34B...')
adapter = TogetherAdapter('NousResearch/Nous-Hermes-2-Yi-34B', api_key)
response = adapter.generate_response('Write a haiku about AI.')
print(f'   Response: {response[:100]}')
print('   ✅ Nous-Hermes-2-Yi-34B working!')
print()

print('🎉 All Together AI models are working correctly!')
"
```

Expected output:
```
Testing Together AI integration...

1. Testing Mixtral-8x7B-Instruct...
   Response: Four
   ✅ Mixtral-8x7B working!

2. Testing Llama-2-70B-Chat...
   Response: Hello! It's nice to meet you.
   ✅ Llama-2-70B working!

3. Testing Nous-Hermes-2-Yi-34B...
   Response: Silicon minds awake,
   Learning patterns, making sense,
   Future unfolds bright.
   ✅ Nous-Hermes-2-Yi-34B working!

🎉 All Together AI models are working correctly!
```

## Usage in AI Council

Once configured, Together AI models will be automatically available in the AI Council orchestration system:

### Model Selection

The orchestration layer will automatically select Together AI models based on:
- **Task type**: Code generation → Mixtral, Research → Llama-2, Balanced → Nous-Hermes
- **Execution mode**: FAST mode prefers cheaper models, BEST_QUALITY prefers higher reliability
- **Cost optimization**: Together AI models offer good value for open-source options
- **Availability**: Falls back to other providers if Together AI is unavailable

### Example Orchestration

For a complex query like "Explain quantum computing and write a Python simulation":

1. **Analysis**: AI Council detects this needs both explanation and code
2. **Decomposition**: Splits into two subtasks
   - Subtask 1: "Explain quantum computing" → Assigned to Llama-2-70B (research)
   - Subtask 2: "Write Python simulation" → Assigned to Mixtral-8x7B (code generation)
3. **Parallel Execution**: Both models process simultaneously via Together AI
4. **Synthesis**: Results combined into coherent response

## Cost Management

### Free Credits

- **Initial credits**: $25 on signup
- **Typical usage**: 
  - Simple query (100 tokens): ~$0.00009
  - Complex query (1000 tokens): ~$0.0009
  - **Estimate**: ~25,000-30,000 queries with free credits
- **Expiration**: Usually 3 months from signup

### Production Pricing

After free credits are exhausted:

| Model | Input Cost | Output Cost | Total per 1M tokens |
|-------|-----------|-------------|---------------------|
| Llama-2-70B | $0.90 | $0.90 | $0.90 |
| Mixtral-8x7B | $0.60 | $0.60 | $0.60 |
| Nous-Hermes-2-Yi-34B | $0.80 | $0.80 | $0.80 |

### Cost Optimization Tips

1. **Use execution modes wisely**:
   - FAST mode: Uses cheaper models when possible
   - BALANCED mode: Balances cost and quality
   - BEST_QUALITY mode: May use more expensive models

2. **Monitor usage**:
   - Check Together AI dashboard regularly
   - Set up billing alerts
   - Review cost breakdown in AI Council admin panel

3. **Combine with free providers**:
   - Use Ollama for local development (free)
   - Use Gemini for simple queries (free tier)
   - Use Together AI for production workloads

## Troubleshooting

### Error: "Invalid API key"

**Solution**: 
- Verify your API key is correct in `.env`
- Ensure there are no extra spaces or quotes
- Check that the key starts with `together_`

### Error: "Rate limit exceeded"

**Solution**:
- Together AI has rate limits on free tier
- Wait a few minutes and try again
- Consider upgrading to paid tier for higher limits

### Error: "Insufficient credits"

**Solution**:
- Check your credit balance in Together AI dashboard
- Add payment method to continue using the service
- Switch to free providers (Ollama, Gemini) temporarily

### Error: "Model not found"

**Solution**:
- Verify the model ID is correct
- Check Together AI documentation for available models
- Some models may be temporarily unavailable

### Slow Response Times

**Solution**:
- Together AI typically responds in 1-2 seconds
- Slow responses may indicate high load
- Try a different model or time of day
- Check your internet connection

## API Reference

### Together AI Client

```python
from app.services.cloud_ai.together_adapter import TogetherAdapter

# Initialize adapter
adapter = TogetherAdapter(
    model_id='mistralai/Mixtral-8x7B-Instruct-v0.1',
    api_key='your_api_key_here'
)

# Generate response
response = adapter.generate_response(
    prompt='Your prompt here',
    temperature=0.7,      # Creativity (0.0-1.0)
    max_tokens=1000,      # Maximum response length
    top_p=0.9,           # Nucleus sampling
    top_k=50             # Top-k sampling
)

print(response)
```

### Available Parameters

- **temperature** (float, 0.0-1.0): Controls randomness
  - 0.0: Deterministic, focused
  - 0.7: Balanced (default)
  - 1.0: Creative, diverse

- **max_tokens** (int): Maximum response length
  - Default: 1000
  - Range: 1-4096 (model dependent)

- **top_p** (float, 0.0-1.0): Nucleus sampling threshold
  - Default: 0.9
  - Lower values = more focused

- **top_k** (int): Top-k sampling
  - Default: 50
  - Lower values = more focused

## Additional Resources

- **Together AI Documentation**: [https://docs.together.ai](https://docs.together.ai)
- **API Reference**: [https://docs.together.ai/reference](https://docs.together.ai/reference)
- **Model Library**: [https://docs.together.ai/docs/inference-models](https://docs.together.ai/docs/inference-models)
- **Pricing**: [https://www.together.ai/pricing](https://www.together.ai/pricing)
- **Status Page**: [https://status.together.ai](https://status.together.ai)

## Support

If you encounter issues:

1. Check the [Together AI Status Page](https://status.together.ai)
2. Review the [Together AI Documentation](https://docs.together.ai)
3. Contact Together AI support: support@together.ai
4. Check AI Council logs: `backend/logs/`

## Next Steps

After setting up Together AI:

1. ✅ Test all three models with the verification script
2. ✅ Submit a test query through the web interface
3. ✅ Monitor costs in the Together AI dashboard
4. ✅ Configure other providers for redundancy (see `backend/docs/`)
5. ✅ Set up production monitoring and alerts

---

**Note**: Together AI is one of several providers supported by AI Council. For a complete multi-provider setup, see:
- `OLLAMA_SETUP.md` - Local models (free)
- `GEMINI_SETUP.md` - Google AI (free tier)
- `HUGGINGFACE_SETUP.md` - HuggingFace (free tier)
- `OPENROUTER_SETUP.md` - Multi-provider access (free credits)
