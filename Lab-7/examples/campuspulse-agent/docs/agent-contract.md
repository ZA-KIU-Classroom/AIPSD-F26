# CampusPulse · Agent Contract · the week planner

One page per loop. If a line here and the code disagree, one of them is a bug. Code: `src/agent.py`, `src/gate.py`. Tests: `tests/test_agent.py`, `tests/test_gate.py`.

**Goal, in one sentence.** Given "plan my week", propose events in the student's next 7 days that match their stored interests and do not clash with their classes.

**Why a loop and not one prompt.** The number of steps depends on what the events list contains and on what the gate refuses: a refused event may need a replacement. (Honest note: for this goal a fixed workflow gets close. See `resources/when-not-to-agent.md`.)

**Autonomy Ladder.** Rung 4, governed agent workflow. Delegated: which events to look at, which to recommend, how to react to a refusal. Verified by: the gate's code checks, the student's yes, the trace.

| Step | What happens | Who does it |
|---|---|---|
| Perceive | today, interests (`memory.interests`), classes (`tools.timetable`) | code |
| Reason | which tool next, or done | the model |
| Act | reads run through `call_tool()`; consequential calls go to `gate.propose()` | code |
| Observe | result, refusal, or "parked" goes back as a tool message | code |

## Tools the loop may use

| Tool | Kind | In this loop |
|---|---|---|
| `list_events` | read | runs |
| `make_calendar_file` | read | runs |
| `rsvp` | **consequential** (`confirm=True`) | **proposed only**; runs after the student confirms |
| `check_room`, `remember_interest` | | not offered: a planner does not book rooms, and a plan is not a request to remember |

## The gate

- **What is gated:** every `rsvp`.
- **Checked by code before the student sees it:** arguments valid; event exists, not cancelled, not past, not full; student not already registered; no clash with a class.
- **What the student sees:** one line per action (title, day, time, room, seats left) with a checkbox; one line per refused event with the reason; Confirm and Decline.
- **What a yes runs:** the stored arguments for the ticked actions, through `call_tool()`, identity from the session. No model.
- **Pending plan:** this student only · 15 minutes · single use · replaced by a newer plan · deleted by Forget me. (Row 3 of `docs/state-contract.md`.)

## Budgets and stops

| Guardrail | Value | What the student sees when it trips |
|---|---|---|
| Steps (model turns) | 6 | "I stopped before finishing: step budget (6). Nothing was booked." |
| Time for the run | 45 s | same sentence, time budget |
| Cost for the run | $0.02 | same sentence, cost budget |
| One model call | 12 s timeout, 3 attempts, backoff 0.5 s then 1 s plus jitter; only timeouts, 429 and 5xx are retried | "model unavailable", nothing booked |
| Same call twice | refused with a message to the model | nothing |

## Evidence

- **Trace:** `logs/agent.jsonl`, one line per `reason`, `act` and `finish`, with run id, tokens, cost, `gated`, and the stop reason. No student id, only its hash.
- **Tests that must stay green:** the loop completes a plan and books nothing; the gate blocks until yes; a budget stops a loop that never finishes; a timeout is retried and a dead model stops cleanly; another student cannot confirm my plan.
