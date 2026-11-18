# Confirmation gates

*Optional reading for Lab 7, Parts 1 and 3. About 12 minutes.*

## The idea in plain language

When a person names an action ("RSVP me to ev-201"), running it is doing what they asked. When a model picks the action as a step toward a goal ("plan my week"), running it is doing what the model guessed they would want. A confirmation gate turns the guess back into a request: the loop may **propose** a consequential action, and only a person's yes **runs** it.

A gate has two halves, on either side of the person.

- **`propose()`** validates the call, checks everything code can check, and returns a description to show plus the exact arguments to run later. It writes nothing.
- **`confirm()`** receives the person's yes, takes the parked action, and runs it through the same checks as any tool call. No model takes part.

## What counts as consequential

A tool is consequential if a wrong call costs someone something. Practical tests:

- It writes, sends, books, pays, publishes or deletes.
- It affects another person (a seat someone else wanted, an email in someone's inbox).
- It cannot be undone with one click by the person it was done for.
- It spends real money, including yours.

`remember_interest` writes, but the student asked for it in so many words, it affects only them, and one button removes it; in the chat turn it is not gated. `rsvp` chosen by a planner takes a seat from another student; it is. When in doubt, gate it: the cost is one click.

## Why it matters in production

**A gate in the prompt is a request.** "Always ask before booking" can be ignored, misread, or overridden by text the model reads in a tool result. The July 2025 incident with a coding agent and a production database is the public example: the instruction not to change anything was explicit, and nothing in code stood behind it. The company's announced fixes were structural (separate environments, a mode that cannot act), not better wording.

**A gate in the chat is still the model.** If the loop asks "shall I book these?" and the user types "yes", that yes goes back through the model, which then decides what to call. It can misread "yes, the first one". An endpoint that receives action ids cannot.

**What was shown must be what runs.** If the confirm request carries the arguments, then the page, a browser extension, or anyone with `curl` decides what runs. The reference stores the validated arguments at proposal time and accepts only ids afterwards.

## The four properties of a pending plan

A parked plan is state, so it follows Week 6's rules and gets a row in `docs/state-contract.md`.

| Property | In the reference | The bug if you skip it |
|---|---|---|
| Blocked until yes | `propose()` never calls the tool | seats taken that nobody chose |
| Scope: this user only | key is `student:<hash>` | anyone with a plan id confirms your bookings |
| Lifetime | 15 minutes, by `expires_at` | a yes to yesterday's card books today's changed event |
| Single use | `take_plan()` reads and deletes | a double-click books twice, or pays twice |

Also: one pending plan per user (a new plan replaces the old, so a stale card cannot be confirmed), and "forget me" deletes it.

## A worked example on CampusPulse

Run `python -m demo.agent_demo plan` with `src/gate.py` open.

**1. The model asks.** In turn 2 it calls `rsvp` four times. For each call, `run()` sees `tool.confirm` and calls `propose()`.

**2. The contract.** `tool.args.model_validate_json(...)`: Week 5's `Rsvp` model. A malformed id stops here.

**3. The preview.** `rsvp_preview()` in `src/tools.py` makes every check `rsvp()` would make (exists, not cancelled, not past, not already registered, not full) and one more that the model should have made: `class_clash()` against the timetable. For ev-207 it raises `ToolFailure("Robotics demo night (ev-207) clashes with the student's class: Algorithms lab, Fri 16:00 to 18:00. Leave it out or pick another event.")`. The model receives that sentence as its observation and, in its summary, tells the student why the event was left out.

**4. The action.** For ev-206 the preview returns the line the student will read: title, day, time, room, seats left. `propose()` builds `{"id": "a-…", "tool": "rsvp", "arguments": "{\"event_id\":\"ev-206\"}", "summary": "…"}`. The id is a hash of the tool name and the stored arguments.

**5. Parking.** When the run finishes, `put_plan()` stores the list of actions under the student's hash with a 15-minute expiry and returns a plan id.

**6. The card.** The page shows one checkbox per action and one "left out" line per refusal. Nothing on it has happened.

**7. The yes.** `POST /plan/{id}/confirm` with `{"approve": ["a-…"]}`. `confirm()` calls `take_plan()` (read and delete), then `call_tool()` for each approved id with the stored arguments and the student from the session. `rsvp()` re-checks seats, so an event that filled up meanwhile comes back as "not booked: full" while the others still run.

**8. Again.** The same request a second time returns 410: the plan is gone.

The tests: `tests/test_gate.py`. Read `test_the_gate_blocks_until_the_student_says_yes` first; it asserts on the RSVP file, not on the reply.

## Common mistakes and how to spot them

- **The tool runs and the gate is a log line.** Run your loop, then look at your data. Anything changed? There is no gate.
- **Confirm calls the model** "to carry out the plan". After the yes there is no model.
- **Arguments in the confirm request.** Send ids.
- **Everything is gated.** People learn to click yes without reading. Gate what costs something; let reads run.
- **The card says "Booked!"** before the yes, because the model's summary said so. Tell the model the truth in the prompt and in the observation ("NOT booked"), and render the card from the actions, not from the model's text.
- **The preview and the tool disagree.** Share the checks, as `rsvp_preview()` and `rsvp()` do, and let the tool re-check at confirmation.
- **Refusals with no advice.** "Error: clash" makes the model try again. "Leave it out or pick another event" makes it move on.

## Check yourself

1. Your teammate implements the gate as a system prompt line plus a chat question. Name two ways a booking can still happen that the user did not approve.
2. Why does the action id come from a hash of the stored arguments, and why does the confirm body carry only ids?
3. For your capstone's consequential action, fill in the four properties: blocked until yes, scope, lifetime, single use.
