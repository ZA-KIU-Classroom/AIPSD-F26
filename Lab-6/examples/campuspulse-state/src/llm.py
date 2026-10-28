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

Week 6 additions (nothing above changes; Lab 5's tests pass unchanged):
  * stream(): the same chat call with stream=True. Yields text as it arrives, collects any
    tool calls, and logs usage from the final chunk, with time to first token.
  * transcribe(): one audio clip in (base64, as an input_audio part), the words out.
  * speak(): text in, WAV bytes out, through OpenRouter's /audio/speech endpoint.
  All three are offline-capable through src/offline.py.

The client is built lazily: importing this module needs no key.
"""

import base64
import io
import json
import os
import sys
import time
import wave
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from openai import OpenAI

from . import offline

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LOG_PATH = Path(os.environ.get("CAMPUSPULSE_USAGE_LOG", "logs/usage.jsonl"))
CHAT_MODEL = os.environ.get("CAMPUSPULSE_MODEL", "google/gemini-3.8-flash")
EMBED_MODEL = os.environ.get("CAMPUSPULSE_EMBED_MODEL", "openai/text-embedding-3-small")
TTS_MODEL = os.environ.get("CAMPUSPULSE_TTS_MODEL", "google/gemini-3.8-flash-lite-tts")
TTS_VOICE = os.environ.get("CAMPUSPULSE_TTS_VOICE", "Kore")
TTS_RATE = 24000                 # Gemini TTS returns 24 kHz, mono, 16-bit signed PCM
OFFLINE = os.environ.get("CAMPUSPULSE_OFFLINE") == "1"

# USD per million tokens (input, output). Verified on openrouter.ai, 13 October 2026.
# gemini-3.8-flash is on a 50% promotional price; the standard price is 1.50 / 7.50.
# verify live before you ship
# Week 6, verified 26 October 2026: gemini-3.8-flash accepts audio input at 32 tokens per
# second of audio (about 1,920 tokens a minute); gemini-3.8-flash-lite-tts is 0.50 / 6.00.
PRICES = {
    "google/gemini-3.8-flash": (0.75, 3.75),
    "openai/text-embedding-3-small": (0.02, 0.0),
    "google/gemini-3.8-flash-lite-tts": (0.50, 6.00),
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


def log_usage(resp, latency_ms: int = 0, kind: str = "chat", **extra) -> dict:
    usage = getattr(resp, "usage", None)
    tokens_in = getattr(usage, "prompt_tokens", 0) or 0
    tokens_out = getattr(usage, "completion_tokens", 0) or 0
    model = getattr(resp, "model", None) or (EMBED_MODEL if kind == "embed" else CHAT_MODEL)
    line = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": kind,
        "model": model,
        "tokens_in": tokens_in,            # includes image and audio tokens when there are any
        "tokens_out": tokens_out,
        "cost_usd": cost_usd(model, tokens_in, tokens_out),
        "latency_ms": latency_ms,
        **extra,                           # Week 6: ttft_ms for streams, seconds for audio
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


# ---------------------------------------------------------------- Week 6: streaming

class Stream:
    """One model turn, streamed. Iterate it for text as it arrives; afterwards read .tool_calls,
    .text and .ttft_ms. The model may ask for tools mid-stream; the fragments are collected here
    and src/chat.py decides whether anything runs (the same gates as Week 5).

        s = Stream(messages, tools)
        for piece in s:
            send(piece)                   # the first piece arrives in ~300 ms, not ~4 s
        if s.tool_calls: ...
    """

    def __init__(self, messages: list[dict], tools: list[dict] | None = None):
        self.messages, self.tools = messages, tools or []
        self.text, self.tool_calls, self.ttft_ms, self.usage = "", [], None, None
        self.reasoning_details = None

    def __iter__(self):
        t0 = time.perf_counter()
        parts: dict[int, dict] = {}
        for delta, usage, extra in self._chunks():
            if usage is not None:                                  # OpenRouter: always the last chunk
                self.usage = usage
            if delta is None:
                continue
            if extra.get("reasoning_details"):
                self.reasoning_details = extra["reasoning_details"]
            for tc in getattr(delta, "tool_calls", None) or []:   # fragments, keyed by index
                p = parts.setdefault(tc.index, {"id": "", "name": "", "arguments": ""})
                p["id"] = tc.id or p["id"]
                if tc.function:
                    p["name"] = tc.function.name or p["name"]
                    p["arguments"] += tc.function.arguments or ""
            if delta.content:
                if self.ttft_ms is None:
                    self.ttft_ms = ms_since(t0)                    # time to first token: the UX number
                self.text += delta.content
                yield delta.content
        self.tool_calls = [parts[i] for i in sorted(parts)]
        resp = SimpleNamespace(model=CHAT_MODEL if not OFFLINE else offline.MODEL, usage=self.usage)
        log_usage(resp, latency_ms=ms_since(t0), kind="stream", ttft_ms=self.ttft_ms)

    def _chunks(self):
        if OFFLINE:
            yield from offline.stream(self.messages, self.tools)
            return
        kwargs = {"model": CHAT_MODEL, "messages": self.messages, "stream": True, "temperature": 0}
        if self.tools:
            kwargs.update(tools=self.tools, tool_choice="auto")
        for chunk in client.chat.completions.create(**kwargs):
            delta = chunk.choices[0].delta if chunk.choices else None
            extra = (getattr(delta, "model_extra", None) or {}) if delta is not None else {}
            yield delta, getattr(chunk, "usage", None), extra


def stream(messages: list[dict], tools: list[dict] | None = None) -> Stream:
    return Stream(messages, tools)


# ---------------------------------------------------------------- Week 6: voice

def transcribe(audio: bytes, fmt: str = "wav") -> str:
    """One clip in, the words out. The audio goes to the same chat model as an input_audio part
    (base64; formats like wav, mp3, m4a, ogg). Nothing here stores the clip: it lives in memory
    for one request and is gone. 32 tokens per second, so a 5-second question is about 160 tokens."""
    if OFFLINE:
        t0 = time.perf_counter()
        text, resp = offline.transcribe(audio)
        log_usage(resp, latency_ms=ms_since(t0), kind="transcribe")
        return text
    content = [{"type": "text", "text": "Transcribe this audio exactly. Reply with the words only."},
               {"type": "input_audio", "input_audio": {"data": base64.b64encode(audio).decode("ascii"),
                                                        "format": fmt}}]
    t0 = time.perf_counter()
    resp = client.chat.completions.create(model=CHAT_MODEL, temperature=0,
                                          messages=[{"role": "user", "content": content}])
    log_usage(resp, latency_ms=ms_since(t0), kind="transcribe")
    return (resp.choices[0].message.content or "").strip()


def speak(text: str) -> bytes:
    """Text in, a WAV file out. OpenRouter's /audio/speech returns raw PCM for Gemini TTS;
    we add the 44-byte WAV header so any browser or player opens it. Priced per token of text."""
    if OFFLINE:
        t0 = time.perf_counter()
        pcm, resp = offline.speak(text)
        log_usage(resp, latency_ms=ms_since(t0), kind="speak")
        return pcm_to_wav(pcm)
    text = text[:1500]                       # a spoken answer is short; the budget is explicit
    t0 = time.perf_counter()
    r = client.audio.speech.create(model=TTS_MODEL, input=text, voice=TTS_VOICE, response_format="pcm")
    # The byte stream carries no usage block. We log the input size we know and mark the cost
    # an estimate; the exact charge is on the OpenRouter generation record for this call.
    resp = SimpleNamespace(model=TTS_MODEL, usage=SimpleNamespace(prompt_tokens=len(text) // 4,
                                                                   completion_tokens=0))
    log_usage(resp, latency_ms=ms_since(t0), kind="speak", chars=len(text), estimated=True)
    return pcm_to_wav(r.content)


def pcm_to_wav(pcm: bytes, rate: int = TTS_RATE) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return buf.getvalue()
