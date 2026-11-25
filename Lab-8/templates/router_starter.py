"""Lab 8 starter: a fallback chain in about 40 lines. It is the file from lecture slides 8 to 13.

Copy this file to src/router.py in your team repo. It already works. Change the lines marked
ADAPT (three settings, one sentence, one import), then run templates/test_router.py.

Three ideas, and nothing else:
  the chain   for each kind of job, an ordered list of models. Ask the first; if it cannot
              answer, ask the next. The last link is a sentence you wrote, not a model.
  the limit   one model gets TIMEOUT_S seconds. Slow counts as down.
  the cache   the same question inside CACHE_TTL_S seconds is answered from memory, for free.

Every call writes one line to logs/router.jsonl. `python -m src.router` prints the summary
you paste into docs/measurements.md.

The CampusPulse version of this file: Lab-8/examples/campuspulse-router/src/router.py
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

# ADAPT 0: your one model call. It must accept (messages, tools, timeout=..., model=...) and
# return a dict with "content" and "tool_calls". Two ways to get one:
#   on track   add `model` and `timeout` to your Lab 5 call (see the Week 8 lines in
#              examples/campuspulse-router/src/llm.py) and import it here
#   behind     copy templates/one_call.py to src/one_call.py and keep the line below
from src.one_call import one_call

CHAINS = {                                      # ADAPT 1: per job, who answers, in order. Two companies.
    "chat": ["google/gemini-3.8-flash", "anthropic/claude-haiku-5.5"],
}
TIMEOUT_S = 12                                  # ADAPT 2: seconds one model gets
CACHE_TTL_S = 600                               # ADAPT 3: seconds an answer may be reused. 0 = never
SORRY = "We cannot reach our models right now. Nothing was changed. Please try again in a minute."   # ADAPT 4: your sentence

CACHE: dict[str, tuple[float, dict]] = {}       # key -> (when, answer). A dict is enough for today.
LOG = Path(os.environ.get("ROUTER_LOG", "logs/router.jsonl"))


def temporary(error: Exception) -> bool:
    """Is the next model worth a try? A timeout, a dropped connection, a 429 or a 5xx: yes.
    A 400, 401 or 403 is our own bug. Another model will not fix it, so it is raised."""
    name = type(error).__name__
    return ("Timeout" in name or "Connection" in name
            or getattr(error, "status_code", None) in (408, 429, 500, 502, 503, 504))


def complete(messages: list[dict], tools: list[dict] | None = None, job: str = "chat", call=one_call) -> dict:
    key = hashlib.sha256(json.dumps([job, messages], sort_keys=True).encode()).hexdigest()
    saved = CACHE.get(key)
    if saved and not tools and time.time() - saved[0] < CACHE_TTL_S:      # THE CACHE: seen it, still fresh
        return note(job, "cache", saved[1], saved_usd=cost(saved[1]))
    for place, model in enumerate(CHAINS[job], start=1):                  # THE CHAIN: first, then next
        started = time.perf_counter()
        try:
            answer = call(messages, tools or [], timeout=TIMEOUT_S, model=model)      # THE LIMIT
        except Exception as error:
            if not temporary(error):
                raise                                                     # our bug: fail loudly
            note(job, "failed", model=model, place=place, why=type(error).__name__)
            continue                                                      # their outage: next model
        if not tools:
            CACHE[key] = (time.time(), answer)                            # only plain answers are reused
        return note(job, "ok", answer, model=model, place=place, cost_usd=cost(answer),
                    ms=int((time.perf_counter() - started) * 1000))
    return note(job, "exhausted", {"content": SORRY, "tool_calls": [], "degraded": True})


def cost(answer: dict) -> float:
    return (answer.get("usage") or {}).get("cost_usd", 0.0)


def note(job: str, outcome: str, answer: dict | None = None, **fields) -> dict | None:
    """One line per attempt. This file is the evidence for the before/after table."""
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps({"ts": round(time.time(), 3), "job": job, "outcome": outcome, **fields}) + "\n")
    return answer


def summary(path: Path | None = None) -> dict:
    """Read the log, count what happened. `python -m src.router` prints it."""
    path = path or LOG
    lines = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    count = lambda outcome: sum(1 for x in lines if x["outcome"] == outcome)      # noqa: E731
    ok = sorted(x["ms"] for x in lines if x["outcome"] == "ok")
    return {"requests": count("ok") + count("cache") + count("exhausted"),
            "answered_by_first_model": sum(1 for x in lines if x["outcome"] == "ok" and x["place"] == 1),
            "answered_by_a_fallback": sum(1 for x in lines if x["outcome"] == "ok" and x["place"] > 1),
            "answered_from_cache": count("cache"),
            "sorry_message": count("exhausted"),
            "failed_attempts": count("failed"),
            "median_ms": ok[len(ok) // 2] if ok else None,
            "spent_usd": round(sum(x.get("cost_usd", 0) for x in lines), 6),
            "saved_by_cache_usd": round(sum(x.get("saved_usd", 0) for x in lines), 6)}


if __name__ == "__main__":
    for name, value in summary().items():
        print(f"{name:<26} {value}")
