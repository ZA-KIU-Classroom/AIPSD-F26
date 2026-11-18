# Lab 7 · setup and troubleshooting

*Look here when something breaks. Not one of the concept guides.*

## Running the reference

```
cd Lab-7/examples/campuspulse-agent
pip install -r requirements.txt          # same packages as Lab 6
export CAMPUSPULSE_OFFLINE=1 CAMPUSPULSE_TODAY=2026-11-18
pytest -q                                # 142 passed
python -m demo.agent_demo plan
```

PowerShell: `$env:CAMPUSPULSE_OFFLINE="1"; $env:CAMPUSPULSE_TODAY="2026-11-18"`.

**Keep `CAMPUSPULSE_TODAY=2026-11-18` for the reference.** Its seeded events run from 19 to 24 November 2026. With the real date, a later week has no matching events and the planner will say so. Your own product uses the real date.

Live: `export CAMPUSPULSE_OFFLINE=0 OPENROUTER_API_KEY=...`, tell CampusPulse two interests through `/chat` ("remember that I like tech talks"), then `POST /plan`. The commands are in the example's README.

## Symptoms and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| The planner says nothing matches | no interests stored for this student, or the date is outside the seeded week | store an interest through `/chat` first; pin `CAMPUSPULSE_TODAY` |
| 400 from the provider on the second turn | the assistant's turn (with its `tool_calls`, and `reasoning_details` for Gemini) was not appended before the tool messages | Lab 5's `as_assistant()`; one tool message per `tool_call_id` |
| 400 mentioning tool call ids | the model asked for several tools in one turn and you answered with fewer tool messages | append one tool message for every call, including refused ones |
| The loop never ends in a test | your scripted model always returns a tool call and you passed no budget | pass `Budget(max_steps=4)`; that is the test |
| The duplicate check stops your runaway test too early | your scripted model repeats the same arguments | vary one argument per turn, as the template does |
| Every live run stops on the step budget | the prompt never says how to finish, or tool results are too long to use | add "finish with two or three sentences"; return fewer fields from the tool; raise the budget last |
| `cost_usd` is always 0 in the trace | your model call does not return usage, or you are offline | return tokens and cost from the call (the reference adds a `usage` key); offline cost is 0 by design |
| A call hangs for minutes | no timeout: the SDK default is 10 minutes | `client.with_options(timeout=12, max_retries=0)` |
| One failure produces many identical log lines | two retry layers (yours and the SDK's), or you retry non-retryable errors | `max_retries=0` on the SDK; retry only timeouts, connection errors, 429, 5xx |
| The retry test takes several seconds | real `time.sleep` in tests | make `sleep` a parameter and pass a fake |
| Confirm returns 410 at once | the plan id belongs to another user, a newer plan replaced it, or it was already confirmed | request a new plan; check you send the same user header to both endpoints |
| Confirm returns 401 | no signed-in user on the request | send the same identity header as for `/plan` |
| Confirm works twice | the plan is read but not deleted | read and delete in one function (`take_plan()`) |
| The gate test passes but data changed | the test asserts on the reply, not on the data | assert the file or table is empty before the yes |
| "Forget me" leaves a pending plan | the new row is missing from your delete | delete the plan kind too; add the deletion test |
| `database is locked` | a connection left open across calls | open, use, close per call, as `memory._conn()` does |
| An action id changes between runs for the same arguments | Python's built-in `hash()` is salted per process | use `hashlib.sha256`, as `gate.py` does |
| The scripted planner proposes a clashing event | on purpose: it does not check the timetable | that is the demo; the gate refuses it |

## Reading the trace

`logs/agent.jsonl` has one JSON object per line. Useful one-liners:

```
tail -n 20 logs/agent.jsonl
grep '"phase": "finish"' logs/agent.jsonl | tail -n 5          # last five runs: status, stop, steps, cost
grep '"run": "<id>"' logs/agent.jsonl                          # one run, in order
grep '"gated": true' logs/agent.jsonl | grep -c '"ok": false'  # how many proposals the gate refused
```

If a run surprised you, read its trace before you change the prompt. Most surprises are a tool result the model could not use, not a model that "went wrong".

## Using a framework instead of the thirty lines

Allowed. Before Checkpoint 1, be able to point at three places in your code: where the step and cost budget is enforced, where a consequential tool call is intercepted before it runs, and where one trace line per step is written. The three tests in `templates/test_agent.py` must pass. If the framework hides any of the three, wrap it or write the loop yourself.
