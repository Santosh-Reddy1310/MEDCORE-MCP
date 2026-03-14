#!/usr/bin/env python
"""Test environment loading in Streamlit context."""
import os
import sys

print("=" * 60)
print("Testing Streamlit Environment Loading")
print("=" * 60)

# Simulate what app.py does
from dotenv import load_dotenv
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_LOCAL_PATH = os.path.join(PROJECT_ROOT, ".env.local")
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")

print(f"\nLoading from: {ENV_LOCAL_PATH}")
load_dotenv(ENV_LOCAL_PATH, override=True)
load_dotenv(ENV_PATH, override=True)

# Check if GROQ_API_KEY is loaded
groq_key = os.getenv("GROQ_API_KEY")
print(f"✅ GROQ_API_KEY loaded: {groq_key[:20] if groq_key else 'NOT SET'}...")

# Now import ai_client
sys.path.insert(0, ".")
from client.ai_client import GROQ_API_KEY as AI_GROQ_KEY
print(f"✅ GROQ_API_KEY in ai_client: {AI_GROQ_KEY[:20] if AI_GROQ_KEY else 'NOT SET'}...")

# Check available providers
from client.ai_client import get_available_providers
providers = get_available_providers()
print(f"✅ Available providers: {[p['name'] for p in providers]}")

if not providers:
    print("\n❌ ERROR: No providers available!")
    print(f"   GROQ_API_KEY: {AI_GROQ_KEY}")
else:
    print("\n✅ SUCCESS: Environment is properly configured!")
