import traceback
from client.ai_client import get_available_providers, call_provider_api

messages = [{"role": "user", "content": "Reply with OK"}]
providers = [p for p in get_available_providers() if p["name"].startswith("groq")]
print("groq providers:", [p["name"] for p in providers])

for p in providers:
    print("\nTesting", p["name"], p["model"])
    try:
        message, provider_name = call_provider_api(p, messages, [])
        print("OK", provider_name, (message.content or "")[:80])
    except Exception as e:
        print("ERROR", type(e).__name__, str(e))
        traceback.print_exc()
