#!/usr/bin/env python
"""Test Groq API with tools."""
import os
from dotenv import load_dotenv
from groq import Groq

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_LOCAL_PATH = os.path.join(PROJECT_ROOT, ".env.local")
load_dotenv(ENV_LOCAL_PATH, override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print(f"GROQ_API_KEY: {GROQ_API_KEY[:20]}...")

# Sample tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_patients",
            "description": "Get list of patients",
            "parameters": {
                "type": "object",
                "properties": {
                    "condition": {
                        "type": "string",
                        "description": "Medical condition to filter by"
                    }
                },
                "required": []
            }
        }
    }
]

try:
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Show me patients with diabetes"}],
        tools=tools,
        tool_choice="auto",
        max_tokens=100,
    )
    print(f"✅ SUCCESS")
    print(f"Content: {response.choices[0].message.content}")
    print(f"Tool calls: {response.choices[0].message.tool_calls}")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
