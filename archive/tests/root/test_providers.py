#!/usr/bin/env python
"""Test free model providers configuration."""
import sys
sys.path.insert(0, '.')

from client.ai_client import get_available_providers, PROVIDERS

print("=" * 70)
print("Free Model Providers Configuration")
print("=" * 70)

print("\n📋 Configured Providers:")
for p in PROVIDERS:
    api_status = "✓" if p["api_key"] else "✗"
    print(f"  • {p['name']:15} | Model: {p['model']:35} | API Key: {api_status}")

print("\n✅ Available Providers (with API keys):")
available = get_available_providers()
if available:
    for p in available:
        print(f"  • {p['name']:15} | Model: {p['model']:35}")
else:
    print("  ❌ No providers available!")

print("\n" + "=" * 70)
print(f"Total: {len(available)}/{len(PROVIDERS)} providers ready")
print("=" * 70)
