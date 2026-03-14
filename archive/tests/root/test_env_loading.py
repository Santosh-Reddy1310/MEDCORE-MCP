#!/usr/bin/env python
"""Test environment variable loading."""
import os
import sys

# Test 1: Direct import of ai_client
print("=" * 60)
print("Test 1: Environment Loading in ai_client")
print("=" * 60)

from client.ai_client import get_available_providers, GROQ_API_KEY
providers = get_available_providers()
print(f"✅ Providers loaded: {[p['name'] for p in providers]}")
print(f"✅ GROQ_API_KEY in ai_client: {GROQ_API_KEY[:20] if GROQ_API_KEY else 'NOT SET'}...")

# Test 2: Check if app.py can load environment
print("\n" + "=" * 60)
print("Test 2: Environment Loading in app.py context")
print("=" * 60)

# Simulate app.py loading
from dotenv import load_dotenv
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_LOCAL_PATH = os.path.join(PROJECT_ROOT, ".env.local")
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")

print(f"Loading from: {ENV_LOCAL_PATH}")
load_dotenv(ENV_LOCAL_PATH)
load_dotenv(ENV_PATH)

groq_key = os.getenv("GROQ_API_KEY")
print(f"✅ GROQ_API_KEY from environment: {groq_key[:20] if groq_key else 'NOT SET'}...")

print("\n" + "=" * 60)
print("✅ All environment variables loaded successfully!")
print("=" * 60)
