#!/usr/bin/env python
"""Test direct import without pre-loading env."""
import sys
sys.path.insert(0, '.')

# Import directly without pre-loading
from client.ai_client import GROQ_API_KEY, PROVIDERS, get_available_providers

print("=" * 70)
print("Direct Import Test")
print("=" * 70)

print(f"\nGROQ_API_KEY: {GROQ_API_KEY[:20] if GROQ_API_KEY else 'NOT SET'}...")
print(f"PROVIDERS: {[p['name'] for p in PROVIDERS]}")

available = get_available_providers()
print(f"Available providers: {[p['name'] for p in available]}")

if available:
    print("\n✅ SUCCESS: Providers are available!")
else:
    print("\n❌ ERROR: No providers available!")
    print(f"   GROQ_API_KEY value: {GROQ_API_KEY}")
    print(f"   PROVIDERS list: {PROVIDERS}")
