# API Keys Setup Guide

## Overview

This guide explains how to get API keys for all AI providers and configure them in your application. You need **at least ONE provider** configured to use the AI Council application.

## Quick Start - Recommended Setup

For the fastest setup with **100% free** options:

1. **Ollama** (Local, no API key needed) - Best for development
2. **Gemini** (Free, 60 req/min) - Best for cloud usage
3. **HuggingFace** (Free, ~1000 req/day) - Additional free capacity

This combination gives you unlimited local inference + generous cloud quotas, all completely free!

## Where to Put API Keys

All API keys go in the `backend/.env` file:

```bash
# Create .env file from template
cd backend
cp .env.example .env

# Edit .env file and add your API keys
# On Windows: notepad .env
# On Mac/Linux: nano .env
```

## Free Providers (No Billing Required)

### 1. Ollama - Local AI Models [100% FREE]

**Cost**: $0.00 (runs on your machine)  
**Rate Limit**: Unlimited  
**Setup Time**: 5-10 minutes

#### Step 1: Install Ollama

**Windows**:
```bash
# Download from https://ollama.ai/download/windows
# Run OllamaSetup.exe
```

**Mac**:
```bash
# Download from https://ollama.ai/download/mac
# Drag to Applications folder
```

**Linux**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Step 2: Pull Models

```bash
ollama pull llama2      # General purpose (3.8 GB)
ollama pull mistral     # Fast and versatile (4.1 GB)
ollama pull codellama   # Code generation (3.8 GB)
ollama pull phi         # Lightweight (1.6 GB)
```

#### Step 3: Verify Installation

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Hello!",
  "stream": false
}'
```

#### Step 4: Configure in .env

```env
OLLAMA_ENDPOINT=http://localhost:11434
```

**No API key needed!** ✅

📖 **Detailed Guide**: [backend/docs/OLLAMA_SETUP.md](./OLLAMA_SETUP.md)

---

### 2. Google Gemini [FREE]

**Cost**: $0.00 (no billing required)  
**Rate Limit**: 60 requests/minute  
**Setup Time**: 2 minutes

#### Step 1: Get API Key

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API key"
4. Copy the key (starts with `AIzaSy...`)

#### Step 2: Add to .env

```env
GEMINI_API_KEY=AIzaSy...your_key_here
```

#### Step 3: Test

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"
```

📖 **Detailed Guide**: [backend/docs/GEMINI_SETUP.md](./GEMINI_SETUP.md)

---

### 3. HuggingFace [FREE]

**Cost**: $0.00  
**Rate Limit**: ~1000 requests/day  
**Setup Time**: 2 minutes

#### Step 1: Get API Token

1. Go to https://huggingface.co/settings/tokens
2. Sign up/login
3. Click "New token"
4. Select "read" role
5. Copy the token (starts with `hf_...`)

#### Step 2: Add to .env

```env
HUGGINGFACE_TOKEN=hf_...your_token_here
```

#### Step 3: Test

```bash
curl https://api-inference.huggingface.co/models/gpt2 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"inputs": "Hello!"}'
```

📖 **Detailed Guide**: [backend/docs/HUGGINGFACE_SETUP.md](./HUGGINGFACE_SETUP.md)

---

## Paid Providers (Free Credits Available)

### 4. Groq [PAID - Free Credits]

**Cost**: $0.27-0.79 per 1M tokens  
**Free Credits**: Available on signup  
**Rate Limit**: Varies  
**Setup Time**: 2 minutes

#### Step 1: Get API Key

1. Go to https://console.groq.com
2. Sign up for account
3. Navigate to API Keys
4. Create new API key
5. Copy the key

#### Step 2: Add to .env

```env
GROQ_API_KEY=gsk_...your_key_here
```

---

### 5. Together AI [PAID - $25 Free Credits]

**Cost**: $0.60 per 1M tokens  
**Free Credits**: $25 on signup  
**Setup Time**: 2 minutes

#### Step 1: Get API Key

1. Go to https://api.together.xyz
2. Sign up for account
3. Navigate to API Keys
4. Create new API key
5. Copy the key

#### Step 2: Add to .env

```env
TOGETHER_API_KEY=...your_key_here
```

---

### 6. OpenRouter [PAID - $1-5 Free Credits]

**Cost**: Varies by model ($0.50-30 per 1M tokens)  
**Free Credits**: $1-5 on signup  
**Setup Time**: 2 minutes  
**Special Feature**: Unified access to OpenAI, Anthropic, Google, Meta models

#### Step 1: Get API Key

1. Go to https://openrouter.ai
2. Sign up for account
3. Navigate to Keys
4. Create new API key
5. Copy the key (starts with `sk-or-v1-...`)

#### Step 2: Add to .env

```env
OPENROUTER_API_KEY=sk-or-v1-...your_key_here
```

#### Step 3: Test

```bash
cd backend
python test_openrouter_integration.py
```

📖 **Detailed Guide**: [backend/docs/OPENROUTER_SETUP.md](./OPENROUTER_SETUP.md)

---

## Optional Paid Providers

### 7. OpenAI [PAID - $5 Free Trial]

**Cost**: $0.50-60 per 1M tokens  
**Free Trial**: $5 (requires payment method)  
**Setup Time**: 5 minutes

#### Step 1: Get API Key

1. Go to https://platform.openai.com
2. Sign up and add payment method
3. Navigate to API Keys
4. Create new API key
5. Copy the key

#### Step 2: Add to .env

```env
OPENAI_API_KEY=sk-...your_key_here
```

---

### 8. Qwen (Alibaba Cloud) [OPTIONAL - Free Tier in Some Regions]

**Cost**: ~$2-12 per 1M tokens (varies by region)  
**Free Tier**: Available in some regions  
**Setup Time**: 5 minutes  
**Special Feature**: Strong multilingual support (Chinese + English)

#### Step 1: Get API Key

1. Go to https://dashscope.aliyun.com
2. Sign up for account (may require phone verification)
3. Navigate to API Keys section
4. Create new API key
5. Copy the key

#### Step 2: Add to .env

```env
QWEN_API_KEY=sk-...your_key_here
```

#### Step 3: Test

```bash
cd backend
python test_qwen_integration.py
```

📖 **Detailed Guide**: [backend/docs/QWEN_SETUP.md](./QWEN_SETUP.md)

**Note**: This is an optional integration. The application works perfectly without Qwen using other providers.

---

## Complete .env File Example

Here's a complete example with all providers configured:

```env
# ============================================================================
# DATABASE & REDIS (Required)
# ============================================================================
DATABASE_URL=postgresql://user:password@localhost:5432/ai_council
REDIS_URL=redis://localhost:6379/0

# ============================================================================
# JWT & SECURITY (Required)
# ============================================================================
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7

# ============================================================================
# AI PROVIDERS - FREE OPTIONS
# ============================================================================

# Ollama - Local (No API key needed)
OLLAMA_ENDPOINT=http://localhost:11434

# Gemini - Free tier
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# HuggingFace - Free tier
HUGGINGFACE_TOKEN=hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# ============================================================================
# AI PROVIDERS - PAID OPTIONS (Optional)
# ============================================================================

# Groq
GROQ_API_KEY=gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Together AI
TOGETHER_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# OpenRouter
OPENROUTER_API_KEY=sk-or-XXXXXXXXXXXXXXXXXXXXXXXX

# OpenAI (Optional)
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Qwen (Optional)
QWEN_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# ============================================================================
# AI DEPLOYMENT MODE
# ============================================================================
# Options: local, cloud, hybrid
AI_DEPLOYMENT_MODE=hybrid

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000
FRONTEND_URL=http://localhost:3000
```

## Testing Your Setup

After adding API keys, test them:

```bash
cd backend

# Test all providers
python test_all_providers.py

# Test specific provider
python test_ollama_adapter.py
python test_gemini_adapter.py
python test_huggingface_adapter.py
```

## Deployment Modes

### Local Mode (Development)

Use only Ollama - no API keys needed, 100% free:

```env
AI_DEPLOYMENT_MODE=local
OLLAMA_ENDPOINT=http://localhost:11434
```

**Pros**: Free, unlimited, private  
**Cons**: Requires local resources, slower on CPU

---

### Cloud Mode (Production)

Use only cloud providers:

```env
AI_DEPLOYMENT_MODE=cloud
GEMINI_API_KEY=...
HUGGINGFACE_TOKEN=...
```

**Pros**: Fast, scalable, no local resources  
**Cons**: Costs money (except free tiers), rate limits

---

### Hybrid Mode (Recommended)

Use both local and cloud:

```env
AI_DEPLOYMENT_MODE=hybrid
OLLAMA_ENDPOINT=http://localhost:11434
GEMINI_API_KEY=...
HUGGINGFACE_TOKEN=...
```

**Pros**: Best of both worlds, fallback options  
**Cons**: Requires local resources + API keys

## Cost Optimization Tips

### 1. Start with Free Providers

Use this priority order:
1. Ollama (local, unlimited)
2. Gemini (60 req/min)
3. HuggingFace (~1000 req/day)

This gives you substantial capacity at $0 cost.

### 2. Add Paid Providers as Needed

Only add paid providers when:
- Free tier limits are exceeded
- You need higher quality models
- You need faster response times
- You need specific model capabilities

### 3. Monitor Usage

Track your usage in the admin dashboard:
- Requests per provider
- Cost per provider
- Rate limit status
- Provider health

### 4. Use Execution Modes Wisely

- **FAST mode**: Uses cheaper models, fewer subtasks
- **BALANCED mode**: Mix of cheap and premium models
- **BEST_QUALITY mode**: Uses premium models, higher cost

## Troubleshooting

### "No providers configured" Error

**Solution**: Add at least one API key to `.env` or set up Ollama

### "Invalid API key" Error

**Solution**: 
1. Check for typos in `.env`
2. Verify key is active in provider dashboard
3. Check for extra spaces or quotes
4. Regenerate key if needed

### "Rate limit exceeded" Error

**Solution**:
1. Wait for rate limit to reset
2. Add additional providers as fallback
3. Upgrade to paid tier if needed

### Ollama "Connection refused" Error

**Solution**:
1. Verify Ollama is running: `curl http://localhost:11434`
2. Start Ollama service
3. Check firewall settings

## Security Best Practices

### 1. Never Commit API Keys

Add `.env` to `.gitignore`:

```gitignore
.env
.env.local
.env.*.local
```

### 2. Use Environment Variables

Never hardcode API keys in code:

```python
# ❌ BAD
api_key = "sk-1234567890"

# ✅ GOOD
api_key = os.getenv("GEMINI_API_KEY")
```

### 3. Rotate Keys Regularly

Change API keys every 90 days or if compromised.

### 4. Use Separate Keys for Dev/Prod

Use different API keys for development and production environments.

### 5. Monitor Usage

Set up alerts for unusual usage patterns that might indicate key compromise.

## Next Steps

1. ✅ Add API keys to `backend/.env`
2. ✅ Test providers: `python backend/test_all_providers.py`
3. ✅ Start backend: `cd backend && poetry run uvicorn app.main:app --reload`
4. ✅ Start frontend: `cd frontend && npm run dev`
5. ✅ Open http://localhost:3000 and test!

## Support

- **Ollama**: https://github.com/ollama/ollama/issues
- **Gemini**: https://discuss.ai.google.dev
- **HuggingFace**: https://discuss.huggingface.co
- **Groq**: https://console.groq.com/docs
- **Together AI**: https://docs.together.ai
- **OpenRouter**: https://openrouter.ai/docs
- **OpenAI**: https://platform.openai.com/docs
