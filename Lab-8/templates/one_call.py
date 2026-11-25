"""One model call through OpenRouter, in 15 lines. For teams whose Lab 5 call is missing or broken.

Copy to src/one_call.py. Needs `pip install openai` and OPENROUTER_API_KEY in your environment
(never in a file you commit). The router asks for exactly this shape:

    one_call(messages, tools, timeout=12, model="google/gemini-3.8-flash")
        -> {"content": "...", "tool_calls": [...], "usage": {"cost_usd": 0.0001}}
"""
import os

from openai import OpenAI

_client = None


def one_call(messages: list[dict], tools: list[dict], timeout: float | None = None, model: str | None = None) -> dict:
    global _client
    if _client is None:
        _client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
    api = _client.with_options(timeout=timeout, max_retries=0)       # the router owns the waiting and the retrying
    reply = api.chat.completions.create(model=model, messages=messages, **({"tools": tools} if tools else {}))
    message = reply.choices[0].message
    calls = [{"id": c.id, "name": c.function.name, "arguments": c.function.arguments or "{}"}
             for c in (message.tool_calls or [])]
    spent = getattr(reply.usage, "cost", None) or 0.0                # OpenRouter reports dollars here; 0.0 if absent
    return {"content": message.content, "tool_calls": calls, "usage": {"cost_usd": spent}}
