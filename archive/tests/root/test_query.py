#!/usr/bin/env python
"""Test a simple query to verify the system works."""
import os
import sys
from dotenv import load_dotenv

# Load environment FIRST
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_LOCAL_PATH = os.path.join(PROJECT_ROOT, ".env.local")
load_dotenv(ENV_LOCAL_PATH, override=True)

sys.path.insert(0, '.')

from client.ai_client import ask_sync

print("=" * 70)
print("Testing Hospital AI Query")
print("=" * 70)

query = "Show me all patients with diabetes"
print(f"\n🔍 Query: {query}")
print("-" * 70)

result = ask_sync(query)
print(result)

print("\n" + "=" * 70)
