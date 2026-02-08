# API Keys Quick Start

## Get Started in 5 Minutes

### Option 1: 100% Free (Recommended for Development)

```bash
# 1. Install Ollama (local AI, no API key needed)
# Download from: https://ollama.ai

# 2. Pull a model
ollama pull llama2

# 3. Configure .env
echo "OLLAMA_ENDPOINT=http://localhost:11434" >> backend/.env

# 4. Start the app
cd backend && poetry run uvicorn app.main:app --reload
```

### Option 2: Free Cloud Providers

```bash
# 1. Get Gemini API key (free, 60 req/min)
# Visit: https://makersuite.google.com/app/apikey

# 2. Add to .env
echo "GEMINI_API_KEY=your_key_here" >> backend/.env

# 3. Start the app
cd backend && poetry run uvicorn app.main:app --reload
```

### Option 3: OpenRouter (Multiple Providers, $1-5 Free Credits)

```bash
# 1. Sign up at https://openrouter.ai
# 2. Get API key from https://openrouter.ai/keys
# 3. Add to .env
echo "OPENROUTER_API_KEY=sk-or-v1-your_key_here" >> backend/.env

# 4. Test the integration
python backend/test_openrouter_integration.py

# 5. Start the app
cd backend && poetry run uvicorn app.main:app --reload
```

## Available Providers

| Provider | Cost | Setup Time | Best For |
|----------|------|------------|----------|
| **Ollama** | Free | 5 min | Local development, unlimited usage |
| **Gemini** | Free | 2 min | Cloud usage, 60 req/min |
| **HuggingFace** | Free | 2 min | Additional capacity, ~1000 req/day |
| **OpenRouter** | $1-5 credits | 2 min | Access to GPT-4, Claude, etc. |
| **Groq** | Paid | 2 min | Ultra-fast inference |
| **Together AI** | $25 credits | 2 min | Diverse model selection |

## Detailed Guides

- **Ollama**: [backend/docs/OLLAMA_SETUP.md](docs/OLLAMA_SETUP.md)
- **Gemini**: [backend/docs/GEMINI_SETUP.md](docs/GEMINI_SETUP.md)
- **HuggingFace**: [backend/docs/HUGGINGFACE_SETUP.md](docs/HUGGINGFACE_SETUP.md)
- **OpenRouter**: [backend/docs/OPENROUTER_SETUP.md](docs/OPENROUTER_SETUP.md)
- **All Providers**: [backend/docs/API_KEYS_SETUP.md](docs/API_KEYS_SETUP.md)

## Testing Your Setup

```bash
# Test all configured providers
cd backend
python test_all_providers.py

# Test specific provider
python test_ollama_adapter.py
python test_openrouter_integration.py
```

## Need Help?

1. Check the detailed setup guides in `backend/docs/`
2. Review troubleshooting section in each guide
3. Ensure `.env` file has correct API keys
4. Verify providers are running (for Ollama)
