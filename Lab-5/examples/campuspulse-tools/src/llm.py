"""The only file that talks to a model.

Week 2 gave us complete(); Week 3 added complete_json(), which sends an image and asks
for a strict JSON schema back. Every call writes one usage line so cost and latency are
never a surprise. That line is the "log entry" half of the Evidence Rule for anything
that calls a model.

Week 4 changes to the Lab 3 version (everything else is unchanged):
  * complete_json(): `image` and `schema` are now optional, so text-only calls (grounded
    answers) use it too. Lab 3 code calls it as complete_json(prompt, image=..., schema=...)
    and keeps working.
  * embed(): new. Turns texts into unit-length vectors through the same client.
  * log_usage(): gains `kind` ("chat" or "embed"). Old calls still work.
  * CAMPUSPULSE_OFFLINE=1 routes both calls through src/offline.py: no key, no network,
    no cost. Tests and the classroom demo use it. Real answers need the real model.

Week 5 addition (nothing above changes; Lab 4's tests pass unchanged):
  * complete_tools(): one model turn that may ask for tools. Returns a plain dict:
    {"content", "tool_calls": [{"id", "name", "arguments"}], "reasoning_details"}.
    The model only ASKS; src/act.py decides whether anything runs.

The client is built lazily: importing this module needs no key.
"""

import base64
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from openai import OpenAI

from . import offline

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LOG_PATH = Path(os.environ.get("CAMPUSPULSE_USAGE_LOG", "logs/usage.jsonl"))
CHAT_MODEL = os.environ.get("CAMPUSPULSE_MODEL", "google/gemini-3.8-flash")
EMBED_MODEL = os.environ.get("CAMPUSPULSE_EMBED_MODEL", "openai/text-embedding-3-small")
OFFLINE = os.environ.get("CAMPUSPULSE_OFFLINE") == "1"

# USD per million tokens (input, output). Verified on openrouter.ai, 13 October 2026.
# gemini-3.8-flash is on a 50% promotional price; the standard price is 1.50 / 7.50.
# verify live before you ship
PRICES = {
    "google/gemini-3.8-flash": (0.75, 3.75),
    "openai/text-embedding-3-small": (0.02, 0.0),
    offline.MODEL: (0.0, 0.0),
}

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError("OPENROUTER_API_KEY is not set; copy .env.example to .env")
        _client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=key)
    return _client


class _LazyClient:
    """Lets the on-screen code say client.chat... without building it at import."""

    def __getattr__(self, name):
        return getattr(get_client(), name)


client = _LazyClient()


def data_url(image: bytes) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(image).decode("ascii")


def ms_since(t0: float) -> int:
    return int((time.perf_counter() - t0) * 1000)


def cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    price_in, price_out = PRICES.get(model, (0.0, 0.0))
    return round((tokens_in * price_in + tokens_out * price_out) / 1_000_000, 6)


def log_usage(resp, latency_ms: int = 0, kind: str = "chat") -> dict:
    usage = getattr(resp, "usage", None)
    tokens_in = getattr(usage, "prompt_tokens", 0) or 0
    tokens_out = getattr(usage, "completion_tokens", 0) or 0
    model = getattr(resp, "model", None) or (EMBED_MODEL if kind == "embed" else CHAT_MODEL)
    line = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": kind,
        "model": model,
        "tokens_in": tokens_in,            # includes image tokens when there is an image
        "tokens_out": tokens_out,
        "cost_usd": cost_usd(model, tokens_in, tokens_out),
        "latency_ms": latency_ms,
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(line) + "\n")
    if os.environ.get("CAMPUSPULSE_VERBOSE") == "1":
        print(json.dumps(line), file=sys.stderr)
    return line


def complete_json(prompt: str, image: bytes | None = None, schema: dict | None = None) -> dict:
    if OFFLINE:
        t0 = time.perf_counter()
        out, resp = offline.complete_json(prompt)
        log_usage(resp, latency_ms=ms_since(t0))
        return out
    content = [{"type": "text", "text": prompt}]
    if image is not None:
        content.append({"type": "image_url", "image_url": {"url": data_url(image)}})
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": content}],
        response_format={"type": "json_schema",
                         "json_schema": {"name": "reply", "schema": schema or {}, "strict": True}},
        temperature=0,
    )
    log_usage(resp, latency_ms=ms_since(t0))
    return json.loads(resp.choices[0].message.content)


def embed(texts: list[str]) -> np.ndarray:
    if OFFLINE:
        return offline.embed(texts, log=log_usage)
    t0 = time.perf_counter()
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    log_usage(resp, latency_ms=ms_since(t0), kind="embed")
    v = np.array([d.embedding for d in resp.data], dtype=np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)   # unit length


def complete_tools(messages: list[dict], tools: list[dict]) -> dict:
    if OFFLINE:
        t0 = time.perf_counter()
        msg, resp = offline.complete_tools(messages, tools)
        log_usage(resp, latency_ms=ms_since(t0))
        return msg
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=CHAT_MODEL, messages=messages, tools=tools, tool_choice="auto", temperature=0)
    log_usage(resp, latency_ms=ms_since(t0))
    m = resp.choices[0].message
    calls = [{"id": c.id, "name": c.function.name, "arguments": c.function.arguments or "{}"}
             for c in (m.tool_calls or [])]
    extra = getattr(m, "model_extra", None) or {}
    return {"content": m.content, "tool_calls": calls, "reasoning_details": extra.get("reasoning_details")}


def embed_model_name() -> str:
    """The model the index was (or will be) built with. Index and queries must match."""
    return offline.MODEL if OFFLINE else EMBED_MODEL
