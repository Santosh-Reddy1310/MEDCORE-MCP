#!/usr/bin/env python
"""Test Groq API directly."""
import os
from dotenv import load_dotenv
from groq import Groq

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_LOCAL_PATH = os.path.join(PROJECT_ROOT, ".env.local")
load_dotenv(ENV_LOCAL_PATH, override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print(f"GROQ_API_KEY: {GROQ_API_KEY[:20]}...")

try:
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hello, how are you?"}],
        max_tokens=100,
    )
    print(f"✅ SUCCESS: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
