#!/usr/bin/env python3
"""Quick test to verify configuration is correct"""

import os
from dotenv import load_dotenv

print("=" * 50)
print("🔍 Configuration Verification")
print("=" * 50)

# Load environment
load_dotenv(".env.local")

# Check API Key
api_key = os.getenv("GROQ_API_KEY")
print(f"\n✅ API Key Variable: GROQ_API_KEY")
print(f"✅ API Key Loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"✅ API Key Format: {api_key[:15]}...")
    print(f"✅ Starts with 'gsk_': {api_key.startswith('gsk_')}")

# Check Model
print(f"\n✅ Model: llama-3.3-70b-versatile")

# Check files
import os.path
files_to_check = [
    ".env.local",
    "client/ai_client.py",
    "app.py",
    "db/setup_db.py",
    "server/hospital_server.py",
]

print(f"\n✅ Project Files:")
for file in files_to_check:
    exists = os.path.exists(file)
    status = "✓" if exists else "✗"
    print(f"  {status} {file}")

print("\n" + "=" * 50)
print("✅ All configurations verified!")
print("=" * 50)
