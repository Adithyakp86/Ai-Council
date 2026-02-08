## Google AI / Gemini API Setup Guide

## Overview

Google AI's Gemini API provides free access to powerful AI models with no billing required. The free tier includes 60 requests per minute, making it perfect for development and moderate production use.

## Benefits of Gemini

- **100% Free**: No credit card required, no billing setup
- **Generous Rate Limits**: 60 requests/minute on free tier
- **High Quality**: State-of-the-art models from Google
- **Multimodal**: Gemini Pro Vision supports text + images
- **Fast**: Low latency responses
- **Reliable**: Backed by Google's infrastructure

## Getting Your API Key

### Step 1: Visit Google AI Studio

Go to https://makersuite.google.com/app/apikey

### Step 2: Sign In

Sign in with your Google account. If you don't have one, create a free Google account first.

### Step 3: Create API Key

1. Click "Get API key" or "Create API key"
2. Select "Create API key in new project" (or choose an existing project)
3. Your API key will be generated instantly
4. Copy the API key (it looks like: `AIzaSy...`)

**Important**: Keep your API key secure. Don't commit it to version control or share it publicly.

### Step 4: Save API Key

Add the API key to your `backend/.env` file:

```env
GEMINI_API_KEY=AIzaSy...your_key_here
```

## Available Models

### Gemini Pro

- **Model ID**: `gemini-pro`
- **Best for**: Text generation, reasoning, research, fact-checking
- **Context window**: 32,768 tokens
- **Strengths**: General-purpose, high quality, fast

### Gemini Pro Vision

- **Model ID**: `gemini-pro-vision`
- **Best for**: Multimodal tasks (text + images)
- **Context window**: 16,384 tokens
- **Strengths**: Image understanding, visual reasoning

## Rate Limits

### Free Tier

- **Requests per minute**: 60
- **Requests per day**: Unlimited
- **Cost**: $0.00 (no billing required)

### Handling Rate Limits

The AI Council application automatically handles rate limiting:

1. Tracks request count per minute
2. Waits if limit is reached
3. Falls back to other providers if available
4. Retries with exponential backoff

## Testing Your Setup

### Test 1: Verify API Key

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
```

You should see a JSON response listing available models.

### Test 2: Generate Text

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "contents": [{
      "parts": [{
        "text": "Explain machine learning in one sentence."
      }]
    }]
  }'
```

You should see a JSON response with generated text.

### Test 3: Test via AI Council

```bash
cd backend
python test_gemini_adapter.py
```

This will test:
- API key validity
- Text generation
- Error handling
- Rate limit handling

## Integration with AI Council

The AI Council application will automatically use Gemini models if:

1. `GEMINI_API_KEY` is set in `backend/.env`
2. The API key is valid
3. Rate limits are not exceeded

Gemini models will be prioritized for:
- **Reasoning tasks**: High-quality logical reasoning
- **Research tasks**: Fact-checking and information gathering
- **Creative tasks**: Content generation

## Troubleshooting

### Invalid API Key Error

**Error**: `403 Forbidden` or "Invalid API key"

**Solution**:
1. Verify your API key is correct in `.env`
2. Check for extra spaces or quotes around the key
3. Generate a new API key if needed
4. Ensure the API key has not been restricted

### Rate Limit Exceeded

**Error**: `429 Too Many Requests` or "Rate limit exceeded"

**Solution**:
1. Wait 60 seconds for the rate limit to reset
2. The application will automatically retry
3. Consider using multiple providers to distribute load
4. For higher limits, upgrade to paid tier (optional)

### Model Not Found

**Error**: `404 Not Found` or "Model not found"

**Solution**:
1. Verify model name is correct: `gemini-pro` or `gemini-pro-vision`
2. Check if the model is available in your region
3. Try the other Gemini model

### Quota Exceeded

**Error**: "Quota exceeded"

**Solution**:
1. Free tier has 60 requests/minute limit
2. Wait for quota to reset (resets every minute)
3. Use other providers (Ollama, HuggingFace) as fallback
4. Upgrade to paid tier for higher quotas (optional)

## Advanced Configuration

### Custom Parameters

Customize Gemini behavior in your requests:

```python
{
  "temperature": 0.7,      # Creativity (0.0-1.0)
  "max_tokens": 1000,      # Max output length
  "top_p": 0.95,           # Nucleus sampling
  "top_k": 40,             # Top-k sampling
}
```

### Multimodal Requests (Gemini Pro Vision)

To use images with Gemini Pro Vision:

```python
{
  "contents": [{
    "parts": [
      {"text": "What's in this image?"},
      {"inline_data": {
        "mime_type": "image/jpeg",
        "data": "<base64_encoded_image>"
      }}
    ]
  }]
}
```

### Safety Settings

Control content filtering:

```python
{
  "safetySettings": [
    {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
  ]
}
```

## Cost Comparison

| Provider | Cost per 1M tokens | Rate Limit | Notes |
|----------|-------------------|------------|-------|
| Gemini Pro | $0.00 | 60/min | Free, no billing |
| Ollama | $0.00 | Unlimited | Local only |
| HuggingFace | $0.00 | ~1000/day | Free tier |
| Groq | $0.27 - $0.79 | Varies | Paid |
| OpenAI | $0.50 - $60.00 | Varies | Paid |

## Best Practices

### 1. Use Gemini for Free Tier

Gemini is perfect for:
- Development and testing
- Low to moderate traffic applications
- Cost-sensitive projects
- Prototyping

### 2. Combine with Other Providers

Use Gemini alongside:
- **Ollama**: For local development
- **HuggingFace**: For additional free capacity
- **Paid providers**: For high-volume production

### 3. Monitor Usage

Track your Gemini usage:
- Check request count in logs
- Monitor rate limit errors
- Set up alerts for quota issues

### 4. Handle Errors Gracefully

Always implement:
- Retry logic with exponential backoff
- Fallback to other providers
- User-friendly error messages

## Resources

- **Official Website**: https://ai.google.dev
- **API Documentation**: https://ai.google.dev/docs
- **Get API Key**: https://makersuite.google.com/app/apikey
- **Pricing**: https://ai.google.dev/pricing
- **Community**: https://discuss.ai.google.dev

## Next Steps

After setting up Gemini:

1. Verify API key is working: `python backend/test_gemini_adapter.py`
2. Configure `GEMINI_API_KEY` in `backend/.env`
3. Run the provider testing script: `python backend/test_all_providers.py`
4. Submit a test query through the AI Council application
5. Verify Gemini models are used in the orchestration

## Upgrading to Paid Tier (Optional)

If you need higher rate limits:

1. Go to https://console.cloud.google.com
2. Enable billing for your project
3. Enable the Generative Language API
4. Rate limits increase automatically

**Paid tier benefits**:
- Higher rate limits (1000+ requests/minute)
- Priority support
- SLA guarantees
- Advanced features

**Note**: The free tier is sufficient for most development and moderate production use.
