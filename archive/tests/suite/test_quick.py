"""
Test ask_sync with a simple query and timeout.
"""
import sys
import os
import signal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def timeout_handler(signum, frame):
    print("\n⏱ Timeout after 20 seconds")
    sys.exit(1)

# Set 20 second timeout
signal.signal(signal.SIGALRM, timeout_handler) if hasattr(signal, 'SIGALRM') else None

from client.ai_client import ask_sync

print("Testing MCP+Groq integration...")
print("=" * 60)
print("Query: How many patients are in the hospital?")
print()

try:
    result = ask_sync("How many patients are in the hospital?")
    print("\n✓ SUCCESS!")
    print("=" * 60)
    print("\nResponse:")
    print(result)
except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ FAILED!")
    print(f"Error: {type(e).__name__}: {str(e)}")
    sys.exit(1)
