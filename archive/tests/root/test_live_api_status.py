#!/usr/bin/env python
"""Quick live API status check for configured providers."""
import os
import sys

from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_LOCAL_PATH = os.path.join(PROJECT_ROOT, ".env.local")
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(ENV_LOCAL_PATH, override=True)
load_dotenv(ENV_PATH, override=True)

sys.path.insert(0, ".")

from client.ai_client import RateLimitError, call_provider_api, get_available_providers


def main():
    providers = get_available_providers()
    print("=" * 90)
    print(f"Live API Status Check | Providers to test: {len(providers)}")
    print("=" * 90)

    if not providers:
        print("No providers with API keys found.")
        return 1

    messages = [{"role": "user", "content": "Reply with exactly: OK"}]

    ok_count = 0
    rl_count = 0
    err_count = 0

    for provider in providers:
        name = provider["name"]
        model = provider["model"]
        try:
            message, _ = call_provider_api(provider, messages, [])
            preview = (message.content or "").strip() if hasattr(message, "content") else ""
            print(f"OK         | {name:14} | {model:45} | {preview[:50]}")
            ok_count += 1
        except RateLimitError as e:
            print(f"RATE_LIMIT | {name:14} | {model:45} | {str(e)[:50]}")
            rl_count += 1
        except Exception as e:
            text = str(e)
            if "429" in text or ("rate" in text.lower() and "limit" in text.lower()):
                print(f"RATE_LIMIT | {name:14} | {model:45} | {text[:50]}")
                rl_count += 1
            else:
                print(f"ERROR      | {name:14} | {model:45} | {type(e).__name__}: {text[:50]}")
                err_count += 1

    print("-" * 90)
    print(f"Summary: OK={ok_count}, RATE_LIMIT={rl_count}, ERROR={err_count}, TOTAL={len(providers)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
