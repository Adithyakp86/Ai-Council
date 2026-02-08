# Ollama Setup Guide

## Overview

Ollama provides free, local AI models that run on your machine without requiring API keys or internet connectivity. This is perfect for development, testing, and cost-free prototyping of the AI Council application.

## Benefits of Ollama

- **100% Free**: No API costs, no rate limits, no billing
- **Privacy**: All processing happens locally on your machine
- **Offline**: Works without internet connection
- **Fast**: Low latency for local inference
- **Multiple Models**: Access to Llama 2, Mistral, CodeLlama, Phi, and more

## Installation

### Windows

1. Download the Ollama installer from https://ollama.ai/download/windows
2. Run the installer (OllamaSetup.exe)
3. Follow the installation wizard
4. Ollama will start automatically as a Windows service

### macOS

1. Download the Ollama app from https://ollama.ai/download/mac
2. Open the downloaded .dmg file
3. Drag Ollama to your Applications folder
4. Launch Ollama from Applications
5. Ollama will run in the menu bar

### Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

This will install Ollama and start it as a systemd service.

## Verify Installation

Check that Ollama is running:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Hello, world!",
  "stream": false
}'
```

If Ollama is running, you'll see a JSON response with generated text.

## Pull Required Models

Download the models needed for AI Council:

```bash
# Llama 2 7B - General purpose, good for reasoning and research
ollama pull llama2

# Mistral 7B - Excellent for reasoning and code generation
ollama pull mistral

# CodeLlama 7B - Specialized for code generation and debugging
ollama pull codellama

# Phi 2.7B - Lightweight model for creative output
ollama pull phi
```

**Note**: Each model is several GB in size. Ensure you have sufficient disk space:
- llama2: ~3.8 GB
- mistral: ~4.1 GB
- codellama: ~3.8 GB
- phi: ~1.6 GB

## Test Basic Inference

Test each model with a sample prompt:

```bash
# Test Llama 2
ollama run llama2 "Explain machine learning in one sentence"

# Test Mistral
ollama run mistral "Write a Python function to calculate factorial"

# Test CodeLlama
ollama run codellama "Debug this code: def add(a b): return a + b"

# Test Phi
ollama run phi "Write a haiku about programming"
```

## Verify Models Are Available

List all downloaded models:

```bash
ollama list
```

You should see output like:

```
NAME            ID              SIZE    MODIFIED
llama2:latest   78e26419b446    3.8 GB  2 minutes ago
mistral:latest  61e88e884507    4.1 GB  3 minutes ago
codellama:latest 8fdf8f752f6e   3.8 GB  4 minutes ago
phi:latest      e2fd6321a5fe    1.6 GB  5 minutes ago
```

## API Endpoints

Ollama provides a REST API at `http://localhost:11434`:

### Generate Completion

```bash
POST /api/generate
{
  "model": "llama2",
  "prompt": "Your prompt here",
  "stream": false
}
```

### Chat Completion

```bash
POST /api/chat
{
  "model": "llama2",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false
}
```

### List Models

```bash
GET /api/tags
```

## Integration with AI Council

The AI Council application will automatically detect and use Ollama models if:

1. Ollama is running on `http://localhost:11434`
2. The required models are pulled
3. The `OLLAMA_ENDPOINT` environment variable is set in `backend/.env`:

```env
OLLAMA_ENDPOINT=http://localhost:11434
```

## Troubleshooting

### Ollama Not Running

**Windows**: Check if the Ollama service is running in Task Manager. Restart it if needed.

**macOS**: Check if Ollama is running in the menu bar. Click the icon and select "Restart".

**Linux**: Check service status:
```bash
systemctl status ollama
```

Restart if needed:
```bash
sudo systemctl restart ollama
```

### Connection Refused

If you get "connection refused" errors:

1. Verify Ollama is running: `curl http://localhost:11434`
2. Check firewall settings (allow port 11434)
3. Try restarting Ollama

### Model Not Found

If you get "model not found" errors:

1. List available models: `ollama list`
2. Pull the missing model: `ollama pull <model-name>`
3. Wait for download to complete

### Slow Performance

Ollama performance depends on your hardware:

- **CPU**: Works on any modern CPU, but slower than GPU
- **GPU**: Much faster with NVIDIA GPU (CUDA) or Apple Silicon (Metal)
- **RAM**: Requires 8GB+ for 7B models, 16GB+ for 13B models

To improve performance:
- Close other applications to free up RAM
- Use smaller models (phi instead of llama2)
- Enable GPU acceleration if available

### Out of Memory

If Ollama crashes with OOM errors:

1. Use smaller models (phi, llama2:7b instead of llama2:13b)
2. Close other applications
3. Increase system swap space
4. Reduce concurrent requests

## Advanced Configuration

### Custom Ollama Endpoint

If running Ollama on a different machine or port:

```env
OLLAMA_ENDPOINT=http://192.168.1.100:11434
```

### Model Parameters

Customize model behavior in the adapter:

```python
{
  "temperature": 0.7,  # Creativity (0.0-1.0)
  "top_p": 0.9,        # Nucleus sampling
  "top_k": 40,         # Top-k sampling
  "num_predict": 1000  # Max tokens to generate
}
```

### Running Multiple Models

Ollama can run multiple models simultaneously. The AI Council orchestration will distribute subtasks across available models for parallel execution.

## Resources

- **Official Website**: https://ollama.ai
- **Documentation**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **Model Library**: https://ollama.ai/library
- **GitHub**: https://github.com/ollama/ollama

## Next Steps

After setting up Ollama:

1. Verify all models are pulled and working
2. Configure `OLLAMA_ENDPOINT` in `backend/.env`
3. Run the provider testing script: `python backend/test_all_providers.py`
4. Submit a test query through the AI Council application
5. Verify Ollama models are used in the orchestration

## Cost Comparison

Using Ollama vs Cloud Providers:

| Provider | Cost per 1M tokens | Notes |
|----------|-------------------|-------|
| Ollama | $0.00 | Free, local |
| Groq | $0.27 - $0.79 | Fast, cloud |
| Together AI | $0.60 | Cloud |
| OpenRouter | $0.50 - $30.00 | Varies by model |
| OpenAI | $0.50 - $60.00 | Premium quality |

**Recommendation**: Use Ollama for development and testing to avoid costs. Use cloud providers for production when you need higher quality or faster inference.
