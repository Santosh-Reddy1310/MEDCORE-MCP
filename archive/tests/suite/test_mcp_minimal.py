"""
Minimal MCP connection test - just connect and list tools.
"""
import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "server", "hospital_server.py")

async def test_mcp():
    """Test basic MCP connection."""
    print("Starting MCP test...")
    print(f"Server script: {SERVER_SCRIPT}")
    print(f"Python: {sys.executable}")
    print()
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
        env=dict(os.environ, PYTHONUNBUFFERED="1"),
    )
    
    try:
        print("1. Connecting to MCP server...")
        async with stdio_client(server_params) as (read, write):
            print("   ✓ Connection established")
            
            print("2. Creating client session...")
            async with ClientSession(read, write) as session:
                print("   ✓ Session created")
                
                print("3. Initializing session...")
                await asyncio.wait_for(session.initialize(), timeout=10.0)
                print("   ✓ Session initialized")
                
                print("4. Listing tools...")
                tools_response = await session.list_tools()
                print(f"   ✓ Found {len(tools_response.tools)} tools")
                
                for tool in tools_response.tools[:3]:
                    print(f"      - {tool.name}: {tool.description[:60]}...")

                print("5. Calling representative tools...")
                checks = [
                    ("get_doctors_by_experience", {"min_years": 10}),
                    ("get_appointments_by_doctor_name", {"doctor_name": "Rohit Gupta", "limit": 5}),
                    ("get_appointments_by_patient_id", {"patient_id": 10, "limit": 5}),
                    ("get_recent_admissions", {"days": 3, "limit": 5}),
                    ("get_department_overview", {}),
                    ("get_patients_by_condition", {"condition": "cancer", "limit": 5}),
                    ("get_patients_by_doctor_name", {"doctor_name": "Priya Sharma", "limit": 5}),
                    ("get_patients_by_department", {"department": "Cardiology", "limit": 5}),
                    ("get_todays_appointments", {}),
                ]

                for tool_name, args in checks:
                    res = await session.call_tool(tool_name, args)
                    text_parts = [c.text for c in res.content if hasattr(c, "text")]
                    text = "\n".join(text_parts)
                    if "error" in text.lower():
                        raise RuntimeError(f"Tool {tool_name} returned error: {text[:200]}")
                    print(f"   ✓ {tool_name} OK")
                
                print("\n✅ MCP connection test PASSED!")
                return True
                
    except Exception as e:
        print(f"\n❌ MCP connection test FAILED!")
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp())
    sys.exit(0 if success else 1)
