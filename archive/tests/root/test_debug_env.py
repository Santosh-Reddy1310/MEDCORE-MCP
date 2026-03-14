#!/usr/bin/env python
"""Debug environment loading."""
import os
import sys

print("=" * 70)
print("Debug Environment Loading")
print("=" * 70)

# Check 1: Direct environment
print("\n1. Direct os.getenv():")
print(f"   GROQ_API_KEY: {os.getenv('GROQ_API_KEY')}")

# Check 2: Load dotenv
from dotenv import load_dotenv
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_LOCAL_PATH = os.path.join(PROJECT_ROOT, ".env.local")
print(f"\n2. Loading from: {ENV_LOCAL_PATH}")
load_dotenv(ENV_LOCAL_PATH, override=True)
print(f"   GROQ_API_KEY: {os.getenv('GROQ_API_KEY')}")

# Check 3: Import ai_client
print("\n3. Importing ai_client module:")
sys.path.insert(0, '.')
from client.ai_client import GROQ_API_KEY, PROVIDERS
print(f"   GROQ_API_KEY in module: {GROQ_API_KEY}")
print(f"   PROVIDERS: {[p['name'] for p in PROVIDERS]}")

# Check 4: get_available_providers
from client.ai_client import get_available_providers
available = get_available_providers()
print(f"\n4. Available providers: {[p['name'] for p in available]}")

print("\n" + "=" * 70)
