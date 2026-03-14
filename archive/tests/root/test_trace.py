#!/usr/bin/env python
"""Trace the issue step by step."""
import os
import sys
from dotenv import load_dotenv

print("Step 1: Load environment")
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_LOCAL_PATH = os.path.join(PROJECT_ROOT, ".env.local")
load_dotenv(ENV_LOCAL_PATH, override=True)
print(f"  GROQ_API_KEY from env: {os.getenv('GROQ_API_KEY')[:20]}...")

print("\nStep 2: Import ai_client")
sys.path.insert(0, '.')
from client import ai_client
print(f"  GROQ_API_KEY in module: {ai_client.GROQ_API_KEY[:20] if ai_client.GROQ_API_KEY else 'NOT SET'}...")
print(f"  PROVIDERS: {[p['name'] for p in ai_client.PROVIDERS]}")

print("\nStep 3: Check get_available_providers")
available = ai_client.get_available_providers()
print(f"  Available: {[p['name'] for p in available]}")

print("\nStep 4: Call ask_sync")
result = ai_client.ask_sync("How many patients are there?")
print(f"  Result: {result[:100]}...")
