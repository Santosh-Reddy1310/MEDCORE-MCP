import asyncio
import json
import os
import sys
from groq import Groq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv(".env.local")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env.local file")

MODEL = "llama-3.3-70b-versatile"

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "server", "hospital_server.py")

SYSTEM_PROMPT = """You are MedCore AI, an intelligent hospital management assistant.
You have access to real-time hospital data through specialized tools.

Your responsibilities:
- Answer queries about patients, doctors, beds, and hospital operations
- Provide clear, structured, and empathetic responses
- Always use the available tools to fetch live data — never guess or fabricate data
- When presenting patient or medical data, be concise but complete
- For statistics, highlight key insights (e.g., which wards are full, critical patients)
- Format lists and tables clearly for readability

Always fetch data using tools before answering. Be professional and helpful."""


def mcp_tools_to_groq_format(mcp_tools) -> list[dict]:
    """Convert MCP tool definitions to Groq/OpenAI function format."""
    groq_tools = []
    for tool in mcp_tools:
        groq_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        })
    return groq_tools


async def ask_hospital_ai(query: str, history: list = None) -> str:
    """
    Main function — takes a user query, connects to MCP server,
    runs Groq tool-calling loop, returns final AI response.
    """
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Fetch available tools from MCP server
            tools_response = await session.list_tools()
            groq_tools = mcp_tools_to_groq_format(tools_response.tools)

            client = Groq(api_key=GROQ_API_KEY)

            # Build message history
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": query})

            # ── Tool calling loop ──────────────────────────
            MAX_ITERATIONS = 5
            for _ in range(MAX_ITERATIONS):
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=groq_tools,
                    tool_choice="auto",
                    max_tokens=2048,
                )

                message = response.choices[0].message

                # If no tool calls → final answer
                if not message.tool_calls:
                    return message.content or "No response generated."

                # Add assistant message with tool calls
                messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in message.tool_calls
                    ],
                })

                # Execute each tool call via MCP
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except Exception:
                        tool_args = {}

                    # Call MCP tool
                    tool_result = await session.call_tool(tool_name, tool_args)
                    result_text = tool_result.content[0].text if tool_result.content else "{}"

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_text,
                    })

            return "Max tool iterations reached. Please try a more specific query."


def ask_sync(query: str, history: list = None) -> str:
    """Synchronous wrapper for Streamlit compatibility."""
    return asyncio.run(ask_hospital_ai(query, history))


# ── CLI test ───────────────────────────────────
if __name__ == "__main__":
    test_queries = [
        "What is the current bed occupancy rate?",
        "Show me all critical patients",
        "Which doctors are available right now?",
    ]
    for q in test_queries:
        print(f"\n🔍 Query: {q}")
        print("─" * 50)
        result = ask_sync(q)
        print(result)
        print()