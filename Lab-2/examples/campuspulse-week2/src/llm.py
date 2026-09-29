"""Every model call goes through this file, and every call logs usage (AGENTS.md, AC4)."""
import json
import logging
import os
import time

from openai import OpenAI

MODEL = os.getenv("CAMPUSPULSE_MODEL", "google/gemini-3.8-flash")
PRICE_IN_PER_M = float(os.getenv("PRICE_IN_PER_M", "0.75"))     # verify on openrouter.ai before trusting
PRICE_OUT_PER_M = float(os.getenv("PRICE_OUT_PER_M", "3.75"))

log = logging.getLogger("campuspulse.llm")
_client = None


def client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
    return _client


def chat(system: str, user: str, max_tokens: int = 300) -> tuple[str, dict]:
    started = time.perf_counter()
    resp = client().chat.completions.create(
        model=MODEL,
        temperature=0.3,
        max_tokens=max_tokens,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    u = resp.usage
    usage = {
        "model": MODEL,
        "tokens_in": u.prompt_tokens,
        "tokens_out": u.completion_tokens,
        "cost_usd": round((u.prompt_tokens * PRICE_IN_PER_M + u.completion_tokens * PRICE_OUT_PER_M) / 1_000_000, 6),
        "latency_ms": round((time.perf_counter() - started) * 1000),
    }
    log.info("model_call %s", json.dumps(usage))
    return resp.choices[0].message.content or "", usage
