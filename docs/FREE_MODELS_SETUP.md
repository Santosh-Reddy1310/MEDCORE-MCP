# Free Models Configuration

## Overview
MedCore MCP is now configured to use **only free models** across multiple providers for cost-effective operation.

## Configured Free Model Providers

### 1. **Groq** (Primary)
- **Model**: `llama-3.3-70b-versatile`
- **API Key**: `GROQ_API_KEY`
- **Status**: ✅ Free tier available
- **Speed**: Ultra-fast inference

### 2. **Ollama** (Fallback)
- **Model**: `llama2`
- **API Key**: `OLLAMA_API_KEY`
- **Status**: ✅ Free open-source
- **Speed**: Fast local inference

### 3. **SambaNova** (Fallback)
- **Model**: `Meta-Llama-3.1-70B-Instruct`
- **API Key**: `SAMBANOVA_API_KEY`
- **Status**: ✅ Free tier available
- **Speed**: Very fast

### 4. **OpenRouter** (Fallback)
- **Model**: `meta-llama/llama-2-70b-chat`
- **API Key**: `OPENROUTER_API_KEY`
- **Status**: ✅ Free models available
- **Speed**: Fast

## Environment Configuration

### `.env.local` Setup
```env
GROQ_API_KEY = gsk_YOUR_GROQ_API_KEY
OLLAMA_API_KEY = YOUR_OLLAMA_API_KEY

# Fallback API Keys (used when primary hits rate limit)
SAMBANOVA_API_KEY = YOUR_SAMBANOVA_API_KEY
OPENROUTER_API_KEY = YOUR_OPENROUTER_API_KEY
```

## Provider Fallback Strategy

The system uses automatic fallback when a provider:
1. Hits rate limits (429 errors)
2. Becomes temporarily unavailable
3. Fails to respond

**Priority Order**:
1. Groq (fastest, most reliable)
2. Ollama (local, always available)
3. SambaNova (very fast)
4. OpenRouter (diverse models)

## Cost Analysis

| Provider | Model | Cost | Status |
|----------|-------|------|--------|
| Groq | llama-3.3-70b | FREE | ✅ |
| Ollama | llama2 | FREE | ✅ |
| SambaNova | Llama-3.1-70B | FREE | ✅ |
| OpenRouter | Llama-2-70B | FREE | ✅ |

**Total Monthly Cost**: $0 (all free tiers)

## Features

✅ **Automatic Fallback**: Seamless switching between providers
✅ **Rate Limit Handling**: Tracks and avoids rate-limited providers
✅ **Cost Optimization**: Uses only free models
✅ **High Availability**: 4 independent providers
✅ **Tool Calling**: All providers support function calling for MCP tools

## Testing

### Verify Providers
```bash
python test_providers.py
```

Output:
```
Free Model Providers Configuration
======================================================================
📋 Configured Providers:
  • groq            | Model: llama-3.3-70b-versatile             | API Key: ✓
  • ollama          | Model: llama2                              | API Key: ✓
  • sambanova       | Model: Meta-Llama-3.1-70B-Instruct         | API Key: ✓
  • openrouter      | Model: meta-llama/llama-2-70b-chat         | API Key: ✓
✅ Available Providers (with API keys):
  • groq            | Model: llama-3.3-70b-versatile
  • ollama          | Model: llama2
  • sambanova       | Model: Meta-Llama-3.1-70B-Instruct
  • openrouter      | Model: meta-llama/llama-2-70b-chat
======================================================================
Total: 4/4 providers ready
```

### Run Health Check
```bash
python health_check.py
```

### Start Web UI
```bash
python -m streamlit run app.py
```

## Files Modified

- `.env.local` - Added OLLAMA_API_KEY, removed paid providers
- `client/ai_client.py` - Updated PROVIDERS list with free models only
- `docs/FREE_MODELS_SETUP.md` - This documentation

## Migration from Paid Models

### Removed
- ❌ Anthropic Claude (paid)
- ❌ Any other paid providers

### Added
- ✅ Ollama (free open-source)
- ✅ SambaNova (free tier)
- ✅ OpenRouter (free models)

## Performance Notes

- **Groq**: Fastest inference, recommended for production
- **Ollama**: Best for local/private deployments
- **SambaNova**: Excellent balance of speed and quality
- **OpenRouter**: Good fallback with diverse model options

## Support

For issues with specific providers:
1. Check `.env.local` for correct API keys
2. Run `python health_check.py` to verify setup
3. Check provider status pages for outages
4. Review logs in Streamlit for detailed errors
