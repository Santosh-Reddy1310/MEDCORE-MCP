import asyncio
from dotenv import load_dotenv
load_dotenv('.env.local')

from client.ai_client import ask_hospital_ai, get_configured_providers, get_available_providers

print("Configured providers:")
for p in get_configured_providers():
    print(f"  {p['name']} - key: {p['api_key'][:15]}..." if p['api_key'] else f"  {p['name']} - NO KEY")

print("\nAvailable providers (not rate limited):")
for p in get_available_providers():
    print(f"  {p['name']}")

print("\nRunning test query...")
result = asyncio.run(ask_hospital_ai("How many patients are currently admitted?"))
print("\nResult:")
print(result)
