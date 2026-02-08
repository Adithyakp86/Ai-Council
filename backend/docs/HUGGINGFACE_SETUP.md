# HuggingFace Inference API Setup Guide

## Overview

HuggingFace provides free access to thousands of AI models through their Inference API. The free tier includes approximately 1000 requests per day, making it perfect for development and moderate production use.

## Benefits of HuggingFace

- **100% Free**: No credit card required
- **Generous Limits**: ~1000 requests/day on free tier
- **Huge Model Library**: Access to thousands of open-source models
- **Easy to Use**: Simple REST API
- **Community-Driven**: Active community and support
- **No Vendor Lock-in**: All models are open-source

## Getting Your API Token

### Step 1: Create HuggingFace Account

Go to https://huggingface.co and click "Sign Up"

### Step 2: Verify Email

Check your email and verify your account

### Step 3: Generate Access Token

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Give it a name (e.g., "AI Council")
4. Select role: "read" (sufficient for inference)
5. Click "Generate token"
6. Copy the token (it looks like: `hf_...`)

**Important**: Keep your token secure. Don't commit it to version control.

### Step 4: Save API Token

Add the token to your `backend/.env` file:

```env
HUGGINGFACE_TOKEN=hf_...your_token_here
```

## Available Models

### Mistral 7B Instruct

- **Model ID**: `mistralai/Mistral-7B-Instruct-v0.2`
- **Best for**: Reasoning, creative writing
- **Context window**: 32,768 tokens
- **Strengths**: High quality, fast, versatile

### Llama 2 7B Chat

- **Model ID**: `meta-llama/Llama-2-7b-chat-hf`
- **Best for**: Reasoning, research, conversation
- **Context window**: 4,096 tokens
- **Strengths**: Well-rounded, reliable

### FLAN-T5 XXL

- **Model ID**: `google/flan-t5-xxl`
- **Best for**: Reasoning, fact-checking, Q&A
- **Context window**: 512 tokens
- **Strengths**: Fast, accurate for short tasks

## Rate Limits

### Free Tier

- **Requests per day**: ~1000
- **Concurrent requests**: Limited
- **Cost**: $0.00 (no billing required)

### Model Loading

Some models may need to "warm up" when first accessed:
- First request may take 20-60 seconds
- Subsequent requests are fast (1-3 seconds)
- Models stay loaded for ~15 minutes of inactivity

### Handling Rate Limits

The AI Council application automatically handles rate limiting:

1. Tracks request count
2. Falls back to other providers if limit reached
3. Retries with exponential backoff
4. Queues requests during model loading

## Testing Your Setup

### Test 1: Verify API Token

```bash
curl https://api-inference.huggingface.co/models/gpt2 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "Hello, world!"}'
```

You should see a JSON response with generated text.

### Test 2: Test Mistral Model

```bash
curl https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": "Explain machine learning in one sentence.",
    "parameters": {"max_new_tokens": 100}
  }'
```

### Test 3: Test via AI Council

```bash
cd backend
python test_huggingface_adapter.py
```

This will test:
- API token validity
- Text generation with multiple models
- Error handling
- Model loading handling

## Integration with AI Council

The AI Council application will automatically use HuggingFace models if:

1. `HUGGINGFACE_TOKEN` is set in `backend/.env`
2. The API token is valid
3. Rate limits are not exceeded

HuggingFace models will be used for:
- **Reasoning tasks**: Mistral and Llama 2
- **Creative tasks**: Mistral for content generation
- **Fact-checking**: FLAN-T5 for Q&A

## Troubleshooting

### Invalid API Token Error

**Error**: `401 Unauthorized` or "Invalid token"

**Solution**:
1. Verify your token is correct in `.env`
2. Check for extra spaces or quotes around the token
3. Ensure token has "read" permission
4. Generate a new token if needed

### Rate Limit Exceeded

**Error**: `429 Too Many Requests`

**Solution**:
1. Free tier has ~1000 requests/day limit
2. Wait 24 hours for quota to reset
3. Use other providers (Ollama, Gemini) as fallback
4. Upgrade to Pro tier for higher limits (optional)

### Model is Loading

**Error**: `503 Service Unavailable` with "Model is loading"

**Solution**:
1. This is normal for first request to a model
2. Wait 20-60 seconds and retry
3. The application will automatically retry
4. Subsequent requests will be fast

### Model Not Found

**Error**: `404 Not Found`

**Solution**:
1. Verify model name is correct
2. Check if model exists: https://huggingface.co/models
3. Some models require acceptance of terms
4. Try a different model from the list above

## Advanced Configuration

### Custom Parameters

Customize HuggingFace behavior:

```python
{
  "temperature": 0.7,      # Creativity (0.0-1.0)
  "max_new_tokens": 1000,  # Max output length
  "top_p": 0.9,            # Nucleus sampling
  "do_sample": True,       # Enable sampling
}
```

### Using Different Models

Browse thousands of models at https://huggingface.co/models

Filter by:
- **Task**: Text generation, summarization, etc.
- **Library**: transformers, diffusers, etc.
- **License**: MIT, Apache 2.0, etc.

To use a different model:
1. Find model on HuggingFace
2. Copy model ID (e.g., `username/model-name`)
3. Add to MODEL_REGISTRY in `model_registry.py`
4. Test with sample prompt

### Inference Endpoints (Paid)

For production use, consider Inference Endpoints:
- Dedicated infrastructure
- No rate limits
- Faster inference
- Custom models
- Pricing: ~$0.60/hour

## Cost Comparison

| Provider | Cost per 1M tokens | Rate Limit | Notes |
|----------|-------------------|------------|-------|
| HuggingFace | $0.00 | ~1000/day | Free tier |
| Gemini Pro | $0.00 | 60/min | Free, no billing |
| Ollama | $0.00 | Unlimited | Local only |
| Groq | $0.27 - $0.79 | Varies | Paid |
| OpenAI | $0.50 - $60.00 | Varies | Paid |

## Best Practices

### 1. Use HuggingFace for Free Tier

HuggingFace is perfect for:
- Development and testing
- Low to moderate traffic applications
- Experimenting with different models
- Cost-sensitive projects

### 2. Combine with Other Providers

Use HuggingFace alongside:
- **Ollama**: For local development
- **Gemini**: For additional free capacity
- **Paid providers**: For high-volume production

### 3. Handle Model Loading

Always implement:
- Retry logic for 503 errors
- Wait for model to load (20-60 seconds)
- Cache frequently used models
- Fallback to other providers

### 4. Monitor Usage

Track your HuggingFace usage:
- Check request count in logs
- Monitor rate limit errors
- Set up alerts for quota issues
- Consider Pro tier if needed

## Resources

- **Official Website**: https://huggingface.co
- **API Documentation**: https://huggingface.co/docs/api-inference
- **Get API Token**: https://huggingface.co/settings/tokens
- **Model Library**: https://huggingface.co/models
- **Community**: https://discuss.huggingface.co

## Next Steps

After setting up HuggingFace:

1. Verify API token is working: `python backend/test_huggingface_adapter.py`
2. Configure `HUGGINGFACE_TOKEN` in `backend/.env`
3. Run the provider testing script: `python backend/test_all_providers.py`
4. Submit a test query through the AI Council application
5. Verify HuggingFace models are used in the orchestration

## Upgrading to Pro (Optional)

If you need higher rate limits:

1. Go to https://huggingface.co/pricing
2. Subscribe to Pro ($9/month)
3. Benefits:
   - Higher rate limits
   - Priority support
   - Early access to features
   - Inference Endpoints discounts

**Note**: The free tier is sufficient for most development and moderate production use.

## Popular Models to Try

### Text Generation

- `mistralai/Mistral-7B-Instruct-v0.2` - Best overall
- `meta-llama/Llama-2-7b-chat-hf` - Reliable
- `tiiuae/falcon-7b-instruct` - Fast

### Code Generation

- `bigcode/starcoder` - Code completion
- `Salesforce/codegen-16B-multi` - Multi-language

### Summarization

- `facebook/bart-large-cnn` - News summarization
- `google/pegasus-xsum` - Extreme summarization

### Question Answering

- `google/flan-t5-xxl` - General Q&A
- `deepset/roberta-base-squad2` - Extractive Q&A

Explore more at https://huggingface.co/models
