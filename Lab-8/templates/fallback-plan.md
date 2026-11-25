# <Product name> · Fallback Plan

Five lines. Write them before you touch the starter file. Save as `docs/fallback-plan.md`.

1. **The model call you protect first, and what the user sees today if it fails.** Name the function and the file. Paste the real error text or describe the real screen; do not guess.
2. **The chain, in order, and why this order.** Two models from two different companies. (This goes in `CHAINS`.) Say which of your features uses this chain.
3. **The limit, in seconds, and where the number comes from.** (`TIMEOUT_S`.) Look at your own `logs/usage.jsonl`: what is a normal latency for this call?
4. **The lifetime, in seconds, and what in your data can make a stored answer wrong.** (`CACHE_TTL_S`.) Name the thing that changes: seats, prices, a schedule. Use 0 if nothing may be reused.
5. **The sentence your user reads when every model is down.** (`SORRY`.) It must say what happened to their data or their action.

CampusPulse, filled in:

1. `complete_tools()` in `src/llm.py`, called by the chat endpoint. Today the student sees "Internal Server Error" and a 500.
2. `google/gemini-3.8-flash`, then `anthropic/claude-haiku-5.5`. Flash first because our golden set was written against it; Haiku second because it is another company. Used by chat and the week planner.
3. 12 seconds. Our median for a chat turn is about 2 seconds, so 12 means it is not coming.
4. 600 seconds. Seats on an event can run out, and 10 minutes is the longest a "seats left" answer may be old.
5. "CampusPulse cannot reach its models right now. Nothing was changed. Please try again in a minute."

The one-page version with reasons: `examples/fallback-plan-campuspulse.md`.
