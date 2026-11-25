# CampusPulse · Fallback Plan

*The worked example for `templates/fallback-plan.md`. The code that implements every line is `examples/campuspulse-router/src/router.py`.*

| # | Decision | In code | Why |
|---|---|---|---|
| 1 | Protect `complete_tools()` in `src/llm.py` first | `call=complete_tools` | Chat and the week planner both go through it. Before today a failed call became a 500 and the page showed "Internal Server Error" |
| 2 | Chat and planner: Gemini 3.8 Flash, then Claude Haiku 5.5 | `CHAINS["chat"]` | Two companies, so one outage does not take both. Flash first because the Week 4 golden set was written against its answers; we have not yet measured Haiku on it |
| 3 | One model gets 12 seconds | `TIMEOUT_S = 12` | Median chat latency in our usage log is about 2 seconds. Worst case with two models: 24 seconds, then the sentence |
| 4 | An answer may be reused for 10 minutes | `CACHE_TTL_S = 600` | Seats on an event can run out. Turns that offer tools are never cached, so an RSVP always sees live seats |
| 5 | "CampusPulse cannot reach its models right now. Nothing was changed. Please try again in a minute." | `SORRY` | Says what happened, says the student's bookings are untouched, says what to do |

## What we decided not to do

- **No retry of the same model.** The chain is the retry. Two layers of retries multiply the wait (Week 7).
- **No fallback for our own bugs.** A 400, 401 or 403 is raised. `tests/test_router.py::test_our_own_bug_is_raised_not_hidden_by_the_next_model` holds us to it.
- **No cache key from the question alone.** The key is the job plus every message, so Nino's interests in the system prompt give her a different key from Luka's.

## Open question we carry into the Week 9 lecture

Is Haiku's answer good enough to be in the chat chain at all? We do not know. Until the golden set runs against it, the honest statement is: a second answer beats an error page.
