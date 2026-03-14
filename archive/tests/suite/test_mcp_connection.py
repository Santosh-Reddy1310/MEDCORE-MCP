"""
Quick test to verify MCP client-server connection works.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from client.ai_client import ask_sync

def test_connection():
    """Test a simple query."""
    print("Testing MCP connection...")
    print("=" * 60)
    
    try:
        result = ask_sync("How many patients are in the hospital?")
        print("\n✓ SUCCESS!")
        print("=" * 60)
        print("\nResponse:")
        print(result)
        return True
    except Exception as e:
        print(f"\n✗ FAILED!")
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
