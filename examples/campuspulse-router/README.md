# CampusPulse · the fallback chain (Week 8 reference)

Week 7's app, unchanged, plus one file: `src/router.py`, about 40 lines. It is the code shown in the Week 8 lecture and what Lab 8's starter is made from. Ask the first model; if it is down, ask the next; if all are down, return a sentence we wrote; and do not pay twice for the same question.

```
pip install -r requirements.txt          # no new dependency this week
export CAMPUSPULSE_OFFLINE=1
pytest                                   # 152 offline tests: 145 from Weeks 4 to 7, 7 new in tests/test_router.py
python -m demo.router_demo before        # 20 questions, first model down for 6, no chain: 6 error pages
python -m demo.router_demo after         # the same 20 through the chain: 3 first model, 1 fallback, 16 cache
python -m demo.router_demo dark          # every model down: the sorry sentence, not cached
python -m demo.router_demo bug           # a 400 is raised, the second model is never asked
python -m src.router                     # the summary of logs/router.jsonl
```

Week 8 changes to earlier files: `src/llm.py` (`complete_tools()` takes an optional `model`; one new price) and `tests/conftest.py` (a temp path for the router log). Nothing else moved. To protect the week planner, pass the router in: `run("Plan my week", "s123", llm=complete)`; `tests/test_router.py::test_the_week_7_loop_runs_through_the_chain` does exactly that.

Not verified live: the chain was exercised offline with a simulated outage. Run one live question through `complete()` before the lecture.

---

*Below: the Week 7 page, unchanged.*

# CampusPulse · the week planner behind a gate (Week 7 reference)

Week 6's app, unchanged, plus one thing: a planner agent. **Start with `src/simple_agent.py`**: it is the whole idea in about 50 lines, it is the code shown in the lecture, and it is what Lab 7's starter file is made from (`python -m demo.simple_demo plan`). The rest of this page describes the full version of the same loop, for the lab's stretch and for the curious.

In the full version, "Plan my week" becomes a loop that reads the student's interests (Week 6 memory) and timetable, lists events through the Week 5 tools, and proposes RSVPs. It books nothing. Every proposed booking is checked by code, parked for 15 minutes, and runs only when the student ticks it and presses Confirm. 

## Run it

```
pip install -r requirements.txt          # no new dependency this week
cp .env.example .env                     # only needed for live runs

# offline: no key, no network, no cost. Tests, CI and the classroom demos use this.
export CAMPUSPULSE_OFFLINE=1 CAMPUSPULSE_TODAY=2026-11-18
pytest                                   # 145 offline tests: 122 from Weeks 4 to 6, 23 new
python -m demo.simple_demo plan          # the 50-line loop: four proposals, no bookings, then Nino's yes
python -m demo.simple_demo runaway       # the 50-line loop stopping a model that never finishes
python -m demo.agent_demo naive          # tools, a loop and no gate: three seats taken, nobody asked
python -m demo.agent_demo plan           # the supervised loop: trace, proposals, refusals, one yes
python -m demo.agent_demo runaway        # a loop with no budget, then the same loop inside one
python -m demo.agent_demo flaky          # timeouts: retried with backoff, then a clean stop

# the app, offline: press "Plan my week" on the page
python -m src.index && uvicorn src.app:app --reload     # http://127.0.0.1:8000/

# live
export CAMPUSPULSE_OFFLINE=0 OPENROUTER_API_KEY=...
unset CAMPUSPULSE_TODAY
curl -s localhost:8000/chat -H 'content-type: application/json' -H 'X-Session-Id: demo' -H 'X-Student-Id: s123' \
     -d '{"question": "remember that I like tech talks"}' > /dev/null
curl -s localhost:8000/plan -H 'content-type: application/json' -H 'X-Student-Id: s123' -d '{"goal": "Plan my week"}'
```

The seeded events for the planner are dated 19 to 24 November 2026. On a later date, set `CAMPUSPULSE_TODAY=2026-11-18` or add events to `data/campus/events.json`.

Logs: `logs/agent.jsonl` is new: one line per step of every run (`reason`, `act`, `finish`), with tokens, cost, whether an action was gated, and why the run stopped. `logs/usage.jsonl` and `logs/tools.jsonl` are as before; a confirmed RSVP appears in `tools.jsonl` like any other tool call.

## Where things are

| File | What it does | Lecture slide |
|---|---|---|
| `src/simple_agent.py` · `tests/test_simple_agent.py` | the 50-line loop: `LOOP_TOOLS`, `NEEDS_YES`, `MAX_STEPS`, `run()`, `confirm()`, and its three tests | 8, 12, 13 |
| `src/agent.py` | the loop: `perceive()`, `call_model()` with timeout and retries, `Budget`, `run()`, the trace | full version |
| `src/gate.py` | `propose()` (check and park, never run) and `confirm()` (run what was shown, once) | full version |
| `src/tools.py` | Week 6's file plus `Tool.confirm`, event `tags`, `timetable()`, `class_clash()`, `rsvp_preview()` | full version |
| `src/memory.py` | Week 6's store plus the third row: `put_plan()`, `take_plan()`, `drop_plans()`; `forget()` counts plans | full version |
| `src/llm.py` | `complete_tools()` gains `timeout` and returns `usage` | full version |
| `src/app.py` | `POST /plan`, `POST /plan/{id}/confirm`, `DELETE /plan/{id}` | full version |
| `src/offline.py` | the scripted planner: matches tags to interests and checks nothing else, on purpose | |
| `static/index.html` | a Plan my week button, the confirmation card with checkboxes, Confirm and Decline | full version |
| `docs/agent-contract.md` | the loop on one page: goal, tools, what is gated, budgets, stops, what the person sees | full version |
| `docs/state-contract.md` · `docs/decisions/0007`, `0008` | the pending-plan row; why the gate is in code; the budget numbers | full version |
| `tests/test_agent.py` · `tests/test_gate.py` | the 20 new tests | full version |
| `demo/agent_demo.py` | the four live demos | |

## Three things that surprise people

- **The OpenAI SDK waits 10 minutes and retries twice by default.** Fine for a script, wrong inside a loop with a 45-second budget. `complete_tools(timeout=12)` sets the timeout and turns the SDK's retries off, so the loop's own three attempts are the only retry layer.
- **The cost of a run grows faster than its steps.** Each model turn re-sends the whole conversation so far. `demo/agent_demo.py runaway` shows turn 40 costing twelve times turn 1.
- **The confirm request carries ids, not arguments.** The page sends back which boxes were ticked. What runs is what the server parked when the student was shown the card, so nothing can change in between.

Model and price, re-checked 16 November 2026: `google/gemini-3.8-flash`, $0.75 in / $3.75 out per million tokens on OpenRouter. Verify before you ship.
