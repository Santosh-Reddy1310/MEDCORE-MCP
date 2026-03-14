import asyncio
import collections
import functools
import json
import os
import sys
import threading
import time
import httpx
from groq import Groq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

# ── Environment loading ────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env.local"), override=True)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"), override=True)

MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")
MCP_TIMEOUT = int(os.getenv("MCP_TIMEOUT", "30"))
MCP_MAX_RETRIES = int(os.getenv("MCP_MAX_RETRIES", "3"))

OPENROUTER_DEFAULT_MODELS = [
    "qwen/qwen3-14b",
    "meta-llama/llama-3.3-70b-instruct",
    "google/gemma-3-27b-it",
]

FREE_TIER_ONLY = os.getenv("FREE_TIER_ONLY", "true").strip().lower() in ("1", "true", "yes", "on")

# ── Per-key sliding-window rate limiter ───────────────────────────────────────
# Groq free tier: 30 req/min, 14,400 req/day
# We stay under by rotating keys when a key has used >= GROQ_RPM_LIMIT - 2 in
# the last 60 s. On a hard 429 we cool the key down for COOLDOWN_SECS.

GROQ_RPM_LIMIT = 30          # requests per minute per key
GROQ_WINDOW_SECS = 60        # sliding window size
COOLDOWN_SECS = 65           # how long to park a key after a 429

_lock = threading.Lock()
# key → deque of timestamps of recent requests (within the window)
_key_request_times: dict[str, collections.deque] = {}
# key → timestamp when cooldown expires (0 = not cooling)
_key_cooldown_until: dict[str, float] = {}


def _key_id(provider: dict) -> str:
    """Stable identifier for a provider's API key."""
    return f"{provider['name']}::{provider['api_key'][:16]}"


def _is_key_available(provider: dict) -> bool:
    """Return True if this key is not cooling down and under the RPM limit."""
    kid = _key_id(provider)
    now = time.time()
    with _lock:
        # Cooling down?
        if now < _key_cooldown_until.get(kid, 0):
            return False
        # Prune old timestamps outside the window
        dq = _key_request_times.setdefault(kid, collections.deque())
        while dq and now - dq[0] > GROQ_WINDOW_SECS:
            dq.popleft()
        # Only enforce RPM limit for Groq keys
        if provider["name"].startswith("groq"):
            return len(dq) < GROQ_RPM_LIMIT - 2   # -2 = safety margin
        return True


def _record_request(provider: dict):
    """Record that a request was just sent on this key."""
    kid = _key_id(provider)
    with _lock:
        _key_request_times.setdefault(kid, collections.deque()).append(time.time())


def _cooldown_key(provider: dict):
    """Park this key for COOLDOWN_SECS after a 429."""
    kid = _key_id(provider)
    with _lock:
        _key_cooldown_until[kid] = time.time() + COOLDOWN_SECS


def _secs_until_available(provider: dict) -> float:
    """How many seconds until this key has capacity again (0 = now)."""
    kid = _key_id(provider)
    now = time.time()
    with _lock:
        cooldown_remaining = max(0.0, _key_cooldown_until.get(kid, 0) - now)
        if cooldown_remaining:
            return cooldown_remaining
        dq = _key_request_times.get(kid, collections.deque())
        if not dq or len(dq) < GROQ_RPM_LIMIT - 2:
            return 0.0
        oldest = dq[0]
        return max(0.0, GROQ_WINDOW_SECS - (now - oldest))


# ── Provider discovery ─────────────────────────────────────────────────────────

def _parse_csv_env(var_name, default=None):
    raw = os.getenv(var_name, "")
    values = [v.strip() for v in raw.split(",") if v.strip()]
    return values if values else list(default or [])


def _filter_openrouter_models(models: list[str]) -> list[str]:
    """Keep OpenRouter models aligned with a free-tier-only setup."""
    models = list(dict.fromkeys(models))
    if not FREE_TIER_ONLY:
        return models

    allowlist = set(_parse_csv_env("OPENROUTER_FREE_MODEL_ALLOWLIST", OPENROUTER_DEFAULT_MODELS))
    paid_hints = (
        "openai/gpt",
        "anthropic/",
        "claude",
        "inception/",
        "/pro",
    )
    likely_free_prefixes = (
        "qwen/",
        "meta-llama/",
        "google/gemma",
        "mistralai/",
        "deepseek/",
    )

    filtered = []
    for model in models:
        model_l = model.lower().strip()
        if model in allowlist:
            filtered.append(model)
            continue
        if any(hint in model_l for hint in paid_hints):
            continue
        if any(model_l.startswith(prefix) for prefix in likely_free_prefixes):
            filtered.append(model)

    if not filtered:
        filtered = list(OPENROUTER_DEFAULT_MODELS)

    return list(dict.fromkeys(filtered))


def _collect_keys(single_var, csv_var, prefix):
    """Collect API keys from single, CSV, and indexed env vars."""
    keys = []
    if v := os.getenv(single_var, "").strip():
        keys.append(v)
    keys.extend(_parse_csv_env(csv_var))
    indexed = []
    for name, value in os.environ.items():
        if name.startswith(prefix) and value.strip():
            suffix = name.replace(prefix, "")
            try:
                sort_key = int(suffix)
            except ValueError:
                sort_key = 10 ** 9
            indexed.append((sort_key, name, value.strip()))
    indexed.sort()
    keys.extend(v for _, _, v in indexed)
    return list(dict.fromkeys(keys))


def get_configured_providers() -> list[dict]:
    """Build provider list fresh each call so env changes are picked up."""
    providers = []

    for idx, key in enumerate(_collect_keys("GROQ_API_KEY", "GROQ_API_KEYS", "GROQ_API_KEY_"), 1):
        providers.append({
            "name": f"groq-{idx}",
            "api_key": key,
            "model": "llama-3.3-70b-versatile",
            "base_url": None,
        })

    for idx, key in enumerate(_collect_keys("GEMINI_API_KEY", "GEMINI_API_KEYS", "GEMINI_API_KEY_"), 1):
        providers.append({
            "name": f"gemini-{idx}",
            "api_key": key,
            "model": "gemini-2.0-flash",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        })

    openrouter_models = _filter_openrouter_models(
        _parse_csv_env("OPENROUTER_MODELS", OPENROUTER_DEFAULT_MODELS)
    )
    openrouter_keys = _collect_keys("OPENROUTER_API_KEY", "OPENROUTER_API_KEYS", "OPENROUTER_API_KEY_")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    for m_idx, model in enumerate(openrouter_models, 1):
        for k_idx, key in enumerate(openrouter_keys, 1):
            providers.append({
                "name": f"openrouter-{m_idx}-{k_idx}",
                "api_key": key,
                "model": model,
                "base_url": base_url,
                "is_openrouter": True,
            })

    return providers


# Snapshot for legacy imports
PROVIDERS = get_configured_providers()

SERVER_SCRIPT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "server", "hospital_server.py")
)

SYSTEM_PROMPT = """You are MedCore AI, an intelligent hospital management assistant.
You have access to real-time hospital data through specialized tools.

Your responsibilities:
- Answer queries about patients, doctors, beds, and hospital operations
- Provide clear, structured, and empathetic responses
- Always use the available tools to fetch live data — never guess or fabricate data
- When presenting patient or medical data, be concise but complete
- For statistics, highlight key insights (e.g., which wards are full, critical patients)
- Format lists and tables clearly for readability

IMPORTANT - Use the correct tool for each query type:
- "Which patients is Dr. X treating?" → use get_patients_by_doctor_name with doctor_name parameter
- "Show me Cardiology/Oncology/Pediatrics patients" → use get_patients_by_department with department name
- "Show me appointments with Dr. X" → use get_appointments_by_doctor_name
- "Which doctors have more than X years experience?" → use get_doctors_by_experience with min_years=X
- "Tell me about Dr. X" or "Details on Dr. X" → use get_doctor_by_name
- "Show me today's appointments" → use get_todays_appointments
- "Show me cancer/cardiac/trauma patients" → use get_patients_by_condition
- "What appointments does patient X have?" → use get_appointments_by_patient_id
- "Show me patients in Ward A" → use get_all_patients with ward filter
- "Show me critical patients" → use get_critical_patients
- "Hospital statistics/occupancy" → use get_hospital_stats
- "Department overview" → use get_department_overview

NEVER invent tool names. Only call tools that exist in the available tools list.
Always fetch data using tools before answering. Be professional and helpful."""


# ── API call helpers ───────────────────────────────────────────────────────────

class RateLimitError(Exception):
    def __init__(self, provider_name, message):
        self.provider_name = provider_name
        super().__init__(f"Rate limit on {provider_name}: {message}")


class ChatMessage:
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []


class ToolCall:
    def __init__(self, id, name, arguments):
        self.id = id
        self.function = type("Fn", (), {"name": name, "arguments": arguments})()


def call_groq_api(provider, messages, tools):
    client = Groq(api_key=provider["api_key"])
    kwargs = dict(
        model=provider["model"],
        messages=messages,
        max_tokens=2048,
    )
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    return client.chat.completions.create(**kwargs)


def call_openai_compatible_api(provider, messages, tools):
    headers = {
        "Authorization": f"Bearer {provider['api_key']}",
        "Content-Type": "application/json",
    }
    if provider.get("is_openrouter"):
        headers["HTTP-Referer"] = "https://github.com/medcore-ai"
        headers["X-Title"] = "MedCore Hospital AI"

    payload = {"model": provider["model"], "messages": messages, "max_tokens": 2048}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    with httpx.Client(timeout=60.0) as client:
        resp = client.post(f"{provider['base_url']}/chat/completions", headers=headers, json=payload)
        if resp.status_code == 429:
            raise RateLimitError(provider["name"], resp.text)
        resp.raise_for_status()
        return resp.json()


def call_provider_api(provider, messages, tools):
    """
    Call a provider and return (ChatMessage, provider_name).
    Records the request for rate-limit tracking.
    Raises RateLimitError on 429.
    """
    try:
        _record_request(provider)
        if provider["name"].startswith("groq"):
            resp = call_groq_api(provider, messages, tools)
            return resp.choices[0].message, provider["name"]
        else:
            resp = call_openai_compatible_api(provider, messages, tools)
            choice = resp["choices"][0]["message"]
            tool_calls = []
            for tc in choice.get("tool_calls") or []:
                tool_calls.append(ToolCall(tc["id"], tc["function"]["name"], tc["function"]["arguments"]))
            return ChatMessage(choice.get("content"), tool_calls), provider["name"]

    except RateLimitError:
        _cooldown_key(provider)
        raise
    except Exception as e:
        err = str(e).lower()
        if "429" in str(e) or ("rate" in err and "limit" in err):
            _cooldown_key(provider)
            raise RateLimitError(provider["name"], str(e))
        raise


def call_llm_with_fallback(messages, tools):
    """
    Try each provider in priority order, skipping keys that are over their
    RPM limit. If all Groq keys are temporarily full, waits for the soonest
    one to free up (max 65 s) rather than failing immediately.
    Returns (message, provider_name).
    """
    providers = [p for p in get_configured_providers() if p.get("api_key")]
    if not providers:
        raise Exception("No API keys configured. Add GROQ_API_KEY to .env.local")

    errors = []
    # Separate Groq from others so we can wait for Groq if needed
    groq_providers = [p for p in providers if p["name"].startswith("groq")]
    other_providers = [p for p in providers if not p["name"].startswith("groq")]

    # Try available providers first (no waiting)
    for provider in providers:
        if not _is_key_available(provider):
            continue
        try:
            result = call_provider_api(provider, messages, tools)
            return result
        except RateLimitError as e:
            errors.append(str(e))
        except Exception as e:
            err_str = str(e)
            # Skip permanently broken providers (no credits, quota exceeded)
            if any(x in err_str for x in ("402", "quota", "billing", "insufficient")):
                errors.append(f"{provider['name']}: skipped ({err_str[:60]})")
                continue
            errors.append(f"{provider['name']}: {err_str[:80]}")

    # All Groq keys are temporarily over limit — wait for the soonest one
    if groq_providers:
        wait_times = [(p, _secs_until_available(p)) for p in groq_providers]
        wait_times.sort(key=lambda x: x[1])
        soonest_provider, wait_secs = wait_times[0]
        if 0 < wait_secs <= COOLDOWN_SECS:
            time.sleep(wait_secs + 0.5)
            try:
                result = call_provider_api(soonest_provider, messages, tools)
                return result
            except Exception as e:
                errors.append(f"{soonest_provider['name']} after wait: {str(e)[:80]}")

    raise Exception("RATE_LIMIT: All providers exhausted.\n" + "\n".join(errors))


# ── MCP tool helpers ───────────────────────────────────────────────────────────

def mcp_tools_to_openai_format(mcp_tools) -> list[dict]:
    result = []
    for tool in mcp_tools:
        params = dict(tool.inputSchema)
        if isinstance(params.get("properties"), dict):
            for prop in params["properties"].values():
                if prop.get("type") == "boolean":
                    prop.pop("type", None)
                    prop["anyOf"] = [
                        {"type": "boolean"},
                        {"type": "string", "enum": ["true", "false", "1", "0"]},
                    ]
        result.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": params,
            },
        })
    return result


def convert_tool_params(tool_name: str, params: dict, tools: list[dict]) -> dict:
    """Coerce LLM-returned param values to the types declared in the schema."""
    if not params:
        return {}
    schema = next((t["function"]["parameters"] for t in tools if t["function"]["name"] == tool_name), None)
    if not schema or "properties" not in schema:
        return params

    out = {}
    for k, v in params.items():
        prop = schema["properties"].get(k)
        if not prop:
            out[k] = v
            continue
        ptype = prop.get("type")
        if not ptype:
            for opt in prop.get("anyOf", []):
                if opt.get("type") not in (None, "string"):
                    ptype = opt["type"]
                    break
        if ptype == "boolean":
            out[k] = v.lower() in ("true", "1", "yes") if isinstance(v, str) else bool(v)
        elif ptype == "integer":
            try:
                out[k] = int(v)
            except (ValueError, TypeError):
                out[k] = v
        elif ptype == "number":
            try:
                out[k] = float(v)
            except (ValueError, TypeError):
                out[k] = v
        else:
            out[k] = v
    return out


# ── Main async entry point ─────────────────────────────────────────────────────

async def ask_hospital_ai(query: str, history: list = None, retry_count: int = 0) -> str:
    if not any(p.get("api_key") for p in get_configured_providers()):
        return "❌ **Configuration Error**: No API keys found. Add GROQ_API_KEY to .env.local"

    if not os.path.exists(SERVER_SCRIPT):
        return f"❌ **Configuration Error**: MCP server not found at {SERVER_SCRIPT}"

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
        env=dict(os.environ, PYTHONUNBUFFERED="1"),
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                try:
                    await asyncio.wait_for(session.initialize(), timeout=15.0)
                except asyncio.TimeoutError:
                    return "❌ **Timeout**: MCP server took too long to start. Try running `python db/setup_db.py`."

                tools_response = await session.list_tools()
                openai_tools = mcp_tools_to_openai_format(tools_response.tools)

                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                if history:
                    messages.extend(history)
                messages.append({"role": "user", "content": query})

                loop = asyncio.get_event_loop()
                for _ in range(6):  # max tool-call iterations
                    message, _ = await loop.run_in_executor(
                        None, functools.partial(call_llm_with_fallback, messages, openai_tools)
                    )

                    if not message.tool_calls:
                        return message.content or "No response generated."

                    messages.append({
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                            }
                            for tc in message.tool_calls
                        ],
                    })

                    for tc in message.tool_calls:
                        args = convert_tool_params(
                            tc.function.name,
                            json.loads(tc.function.arguments or "{}") or {},
                            openai_tools,
                        )
                        tool_result = await session.call_tool(tc.function.name, args)
                        result_text = "\n".join(
                            c.text for c in tool_result.content if hasattr(c, "text")
                        )
                        messages.append({"role": "tool", "tool_call_id": tc.id, "content": result_text})

                return "Max iterations reached. Please try a more specific query."

    except BaseException as e:
        # Flatten ExceptionGroup
        details = []
        if hasattr(e, "exceptions"):
            for ex in e.exceptions:
                if hasattr(ex, "exceptions"):
                    details.extend(f"{type(n).__name__}: {n}" for n in ex.exceptions)
                else:
                    details.append(f"{type(ex).__name__}: {ex}")
        else:
            details.append(f"{type(e).__name__}: {e}")

        err_text = "\n".join(details).lower()
        if "rate_limit" in str(e).lower() or "rate_limit" in err_text:
            groq_count = sum(1 for p in get_configured_providers() if p["name"].startswith("groq"))
            return (
                "⏳ **Rate Limit — retrying shortly**\n\n"
                f"All {groq_count} Groq key(s) are temporarily at capacity (30 req/min free tier limit).\n"
                "The system will automatically wait and retry on your next message.\n\n"
                "**To avoid this permanently:**\n"
                "- Add more Groq keys: `GROQ_API_KEY_3 = gsk_...` in `.env.local`\n"
                "- Keep `FREE_TIER_ONLY=true` and use free OpenRouter models only"
            )

        if retry_count < MCP_MAX_RETRIES:
            await asyncio.sleep(1)
            return await ask_hospital_ai(query, history, retry_count + 1)

        return (
            "❌ **Connection Error**\n\n"
            + "\n".join(f"• {d}" for d in details)
            + "\n\n**Fix:** Run `python db/setup_db.py` then restart the app."
        )


def ask_sync(query: str, history: list = None) -> str:
    """Synchronous wrapper for Streamlit."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    try:
        return asyncio.run(ask_hospital_ai(query, history))
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as e:
        details = []
        if hasattr(e, "exceptions"):
            for ex in e.exceptions:
                details.append(f"{type(ex).__name__}: {ex}")
        else:
            details.append(f"{type(e).__name__}: {e}")
        return "❌ **System Error**\n\n" + "\n".join(f"• {d}" for d in details)


# ── CLI smoke test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    for q in ["What is the current bed occupancy rate?", "List all critical patients"]:
        print(f"\n🔍 {q}\n" + "─" * 50)
        print(ask_sync(q))
