# Qwen (Alibaba Cloud) Setup Guide

This guide will help you set up Qwen (Alibaba Cloud's DashScope API) for use with the AI Council application.

## Overview

**Qwen** is Alibaba Cloud's large language model series, offering competitive performance with strong multilingual capabilities (especially Chinese and English). It provides a free tier in some regions and competitive pricing.

**Status:** Optional integration  
**Cost:** Free tier available in some regions, paid tiers vary by region  
**Best for:** Multilingual tasks, Chinese language processing, general reasoning

## Features

- **Strong Multilingual Support**: Excellent performance in Chinese and English
- **Competitive Reasoning**: Good performance on reasoning and generation tasks
- **Free Tier**: Available in some regions (check availability)
- **Fast Response Times**: Optimized for low latency
- **Web Search Integration**: Optional web search capabilities
- **Multiple Model Tiers**: Choose between turbo, plus, and max variants

## Supported Models

| Model | Context | Best For | Relative Cost |
|-------|---------|----------|---------------|
| `qwen-turbo` | 8K | Fast, cost-effective tasks | $ |
| `qwen-plus` | 32K | Balanced performance | $$ |
| `qwen-max` | 8K | Best quality, complex reasoning | $$$ |

## Step-by-Step Setup

### 1. Create Alibaba Cloud Account

1. Go to [https://dashscope.aliyun.com](https://dashscope.aliyun.com)
2. Click "Sign Up" or "登录" (Login)
3. Create an account or sign in with existing Alibaba Cloud account
4. Complete account verification (may require phone number)

**Note:** Availability and free tier access may vary by region. Check the DashScope website for current offerings in your region.

### 2. Get API Key

1. After logging in, navigate to the API Keys section
2. Click "Create API Key" or "创建API Key"
3. Copy your API key (starts with `sk-...`)
4. Store it securely - you won't be able to see it again

**Important:** Keep your API key secure and never commit it to version control.

### 3. Configure Environment Variable

Add your Qwen API key to `backend/.env`:

```bash
# Qwen (Alibaba Cloud) - Free tier in some regions
QWEN_API_KEY=sk-your-actual-api-key-here
```

### 4. Verify Setup

Test your Qwen integration:

```bash
cd backend
python test_qwen_integration.py
```

Expected output:
```
Testing Qwen integration...
✓ Qwen API key configured
✓ Successfully connected to Qwen API
✓ qwen-turbo response: [response text]
✓ qwen-plus response: [response text]
✓ qwen-max response: [response text]

Qwen integration test passed!
```

## Usage in AI Council

Once configured, Qwen models will be automatically available for orchestration:

```python
from app.services.cloud_ai.qwen_adapter import QwenAdapter

# Initialize adapter
adapter = QwenAdapter(
    model_id="qwen-turbo",
    api_key=os.getenv("QWEN_API_KEY")
)

# Generate response
response = adapter.generate_response("Explain quantum computing")
```

## Model Selection Guide

### Qwen-Turbo
- **Use for:** Quick responses, simple tasks, high-volume requests
- **Strengths:** Fast, cost-effective
- **Limitations:** Less capable on complex reasoning

### Qwen-Plus
- **Use for:** Balanced tasks, code generation, research
- **Strengths:** Good quality-to-cost ratio, larger context window
- **Limitations:** Moderate cost

### Qwen-Max
- **Use for:** Complex reasoning, critical tasks, high-quality output
- **Strengths:** Best quality, strong reasoning
- **Limitations:** Higher cost, smaller context than Plus

## Pricing Information

Pricing varies by region. As of 2024, approximate costs:

- **Qwen-Turbo**: ~$2 per 1M tokens
- **Qwen-Plus**: ~$4 per 1M tokens
- **Qwen-Max**: ~$12 per 1M tokens

**Free Tier:** Some regions offer free tier access. Check [https://dashscope.aliyun.com](https://dashscope.aliyun.com) for current availability.

## Rate Limits

Rate limits vary by account type and region:

- **Free Tier**: Typically 60-100 requests per minute
- **Paid Tier**: Higher limits based on subscription

Monitor your usage in the DashScope console.

## Troubleshooting

### Error: "Invalid API key"

**Solution:**
1. Verify your API key is correct in `.env`
2. Check that the key hasn't expired
3. Ensure your account is active and verified

### Error: "Rate limit exceeded"

**Solution:**
1. Wait for the rate limit window to reset
2. Implement exponential backoff in your requests
3. Consider upgrading to a paid tier for higher limits

### Error: "Region not supported"

**Solution:**
1. Check if Qwen is available in your region
2. Consider using a VPN or proxy if necessary
3. Use alternative providers (Gemini, HuggingFace) if Qwen is unavailable

### Slow Response Times

**Solution:**
1. Use `qwen-turbo` for faster responses
2. Reduce `max_tokens` parameter
3. Check your network connection
4. Consider using a closer region if available

## Advanced Features

### Web Search Integration

Enable web search for real-time information:

```python
response = adapter.generate_response(
    "What are the latest developments in AI?",
    enable_search=True
)
```

### Custom Parameters

Fine-tune generation:

```python
response = adapter.generate_response(
    prompt="Write a creative story",
    temperature=0.9,  # Higher for more creativity
    top_p=0.95,
    top_k=50,
    max_tokens=2000
)
```

## Comparison with Other Providers

| Feature | Qwen | Gemini | OpenAI |
|---------|------|--------|--------|
| Free Tier | Some regions | Yes | $5 trial |
| Multilingual | Excellent | Good | Excellent |
| Chinese Support | Excellent | Good | Good |
| Context Window | Up to 32K | 32K | Up to 128K |
| Response Speed | Fast | Fast | Fast |
| Cost | Low-Medium | Free | Medium-High |

## Best Practices

1. **Start with Turbo**: Test with `qwen-turbo` before using more expensive models
2. **Monitor Costs**: Track usage in DashScope console
3. **Use Appropriate Models**: Match model to task complexity
4. **Implement Caching**: Cache responses for repeated queries
5. **Handle Errors**: Implement retry logic with exponential backoff
6. **Secure API Keys**: Never expose keys in client-side code

## Resources

- **Official Documentation**: [https://help.aliyun.com/zh/dashscope/](https://help.aliyun.com/zh/dashscope/)
- **API Reference**: [https://help.aliyun.com/zh/dashscope/developer-reference/api-details](https://help.aliyun.com/zh/dashscope/developer-reference/api-details)
- **DashScope Console**: [https://dashscope.console.aliyun.com/](https://dashscope.console.aliyun.com/)
- **Pricing**: Check DashScope website for current regional pricing

## Support

For issues specific to Qwen:
- Check the [DashScope documentation](https://help.aliyun.com/zh/dashscope/)
- Contact Alibaba Cloud support
- Check the AI Council GitHub issues for integration problems

## Optional Integration Note

**This integration is optional.** The AI Council application works perfectly without Qwen. Only set it up if:
- You need strong Chinese language support
- You're in a region with free tier access
- You want additional provider diversity
- You prefer Alibaba Cloud's ecosystem

If you don't configure Qwen, the application will use other available providers (Gemini, HuggingFace, Ollama, etc.).
