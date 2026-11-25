# CampusPulse · Before and After the Router

*The worked example for `templates/measurements.md`. Read the note on what is and is not measured here.*

**Measured with:** `python -m demo.router_demo before` and `python -m demo.router_demo after`, in `examples/campuspulse-router/`, offline mode.
**The call we protected:** `complete_tools()` in `src/llm.py`, used by chat and the week planner
**Chain:** `google/gemini-3.8-flash` then `anthropic/claude-haiku-5.5` · **Limit:** 12 s · **Lifetime:** 600 s

> **What this example does not show.** The reference runs offline: the stand-in model is instant and free, so milliseconds and dollars would be meaningless and are left as "not measured". The counts are exact and repeatable. Your own page must have all eight rows, from live runs.

## The 20 questions

Four different questions asked 20 times, the way a campus asks them: "What is on this week?" (10 times), "Is the robotics night free?" (4), "Where is A112?" (4), "When does the library close?" (2). For requests 6 to 11 the first model is treated as down.

## The table

| | Before (one model, no cache) | After (through `src/router.py`) |
|---|---|---|
| Requests | 20 | 20 |
| Errors the user saw | 6 | 0 |
| Paid model calls | 20 attempted, 14 answered | 4 |
| Answered by a fallback | n/a | 1 |
| Answered from cache | n/a | 16 |
| Sorry sentences | n/a | 0 |
| Median milliseconds | not measured (offline) | not measured (offline) |
| Dollars spent | not measured (offline) | not measured (offline) |

## Three raw lines

From the demo's `router.jsonl` (timestamps removed here because the demo writes to a temporary folder; keep yours):

```
{"job": "chat", "outcome": "ok", "model": "google/gemini-3.8-flash", "place": 1, "cost_usd": 0.0, "ms": 0}
{"job": "chat", "outcome": "ok", "model": "anthropic/claude-haiku-5.5", "place": 2, "cost_usd": 0.0, "ms": 0}
{"job": "chat", "outcome": "cache", "saved_usd": 0.0}
```

## What surprised us

Only one request out of the six in the outage needed the fallback. The other five were repeats that the cache had already answered before the outage began, so the cache did more for reliability than the second model did. That is an effect of this list: four different questions in twenty is far more repetition than real traffic has.

## What we would change next

The lifetime. Sixteen of twenty answers came from the cache, which means a wrong cached answer would be read sixteen times. For "Is the robotics night free?" we would drop `CACHE_TTL_S` to 120 for any answer that mentions seats, and keep 600 for rooms and opening hours.
