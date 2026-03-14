#!/usr/bin/env python
"""Test multi-provider fallback system."""
import sys
sys.path.insert(0, '.')

from client.ai_client import ask_sync, get_available_providers, _rate_limited_providers

print("=" * 60)
print("Testing Multi-Provider Fallback System")
print("=" * 60)

# Show available providers
providers = get_available_providers()
print(f"\nConfigured providers: {[p['name'] for p in providers]}")
print(f"Rate-limited providers: {_rate_limited_providers}")

# Test query
print("\n" + "-" * 60)
print("Testing query: 'How many doctors work here?'")
print("-" * 60)

result = ask_sync("How many doctors work here?")
print("\nResult:")
print(result)

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
