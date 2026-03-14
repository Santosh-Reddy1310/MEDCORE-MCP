from dotenv import load_dotenv
load_dotenv('.env.local')

from client.ai_client import get_configured_providers, call_provider_api

messages = [{"role": "user", "content": "say hello in 5 words"}]
tools = []  # no tools, just test basic call

for provider in get_configured_providers():
    name = provider['name']
    # Only test groq-2, gemini-1, openrouter-1-1 to save time
    if name not in ('groq-1', 'groq-2', 'gemini-1', 'openrouter-1-1'):
        continue
    try:
        msg, pname = call_provider_api(provider, messages, tools)
        content = msg.content if hasattr(msg, 'content') else str(msg)
        print(f"[OK] {name}: {content[:80]}")
    except Exception as e:
        print(f"[FAIL] {name}: {type(e).__name__}: {str(e)[:200]}")
