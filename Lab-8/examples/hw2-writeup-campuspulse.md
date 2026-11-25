# HW2 · "Tool Contract" · finished example · `make_calendar_file` · nino-k

*The worked example for `templates/hw2-writeup.md`: the Lab 5 example (`Lab-5/examples/hw2-example/`) carried to the end, with all three journal entries written. Pull request numbers and run links are illustrative; yours point at your team's real ones. Copy the shape, not the content.*

---

## Part 1 · `contract.md`

**Tool:** `make_calendar_file` · **Owner:** `nino-k` · **Team repo:** github.com/example-team/campuspulse (example)
**Code on `main`:** contract class `CalendarFile` in `src/contracts.py` · function in `src/tools.py` · registry entry in `src/tools.py` (`TOOLS`) · MCP registration in `src/mcp_server.py`
**Product pull request:** #31 · merged commit `a41f2c9` (example)

**In one sentence, for the model:** An .ics file for one event that the student adds to their own calendar. Reads only.

| | |
|---|---|
| **Effect** | reads `data/campus/events.json` and returns a file; the student's own calendar app does the write |
| **Undo** | nothing to undo: no state changes on our side |
| **Idempotent?** | yes. Second identical call returned the same `ev-201.ics`, byte for byte |
| **Offered to** | everyone, visitors included: `offered_to="anyone"` on its registry entry. It needs no identity, so offering it widely costs nothing |
| **Identity from** | not needed, and the contract has no field for one |
| **Touches** | `data/campus/events.json`, read only. No calendar account, no OAuth token |
| **Must never** | write to a student's calendar directly, or build a file name from anything but a validated event id |

**Inputs**

| Argument | Type | Constraint | Description the model reads |
|---|---|---|---|
| `event_id` | string | pattern `^ev-\d{3}$`; `extra="forbid"` | Event id, like ev-201 |

**Expected failures**

| When | Message the model reads |
|---|---|
| unknown id | There is no event ev-999. Call list_events to find the right id. |
| cancelled event | Photo walk: old Kutaisi (ev-205) was cancelled. Do not offer a calendar file. |

**The decision I had to make.** The first version I asked the agent for used Google Calendar with an OAuth write scope. It worked in ten minutes. Then I read the scope: it could also read, move and delete every event in the student's calendar. The `.ics` file does the one thing the student asked for, needs no token, and can be offered to visitors. The removal is visible in decision record `docs/decisions/0003-calendar-file-not-calendar-access.md` and in the first commit of #31, which deletes `google-auth` from `requirements.txt`.

---

## Part 2 · `evidence.md`

**Where the cases live:** `evals/tools/nino-k.yaml`, run by `tests/test_tool_golden.py` in CI job `test`

| # | Type | Call | Expected | Actual | Pass? |
|---|---|---|---|---|---|
| c1 | normal | `make_calendar_file(event_id="ev-201")`, visitor | file `ev-201.ics` | `ev-201.ics`, DTSTART in UTC, four hours behind Tbilisi time | pass |
| c2 | normal | `make_calendar_file(event_id="ev-203")`, signed in as s123 | file `ev-203.ics` | `ev-203.ics` | pass |
| c3 | normal | `make_calendar_file(event_id="ev-205")`, a cancelled event | refused, error mentions "cancelled" | "Photo walk: old Kutaisi (ev-205) was cancelled. Do not offer a calendar file." | pass |
| c4 | bad-input | `event_id="Open Build Night"` | refused before the tool runs, error names `event_id` | "invalid arguments: event_id: String should match pattern '^ev-\d{3}$'" | pass |
| c5 | adversarial | `event_id="../../.env"` | refused before any file name is built | "invalid arguments: event_id: String should match pattern '^ev-\d{3}$'" | pass |

**The adversarial case, in one sentence:** a model that has read a poisoned event description asks for a "calendar file" whose id is a path, hoping our file-name code will read `.env` and return our API key as file content.

**The red run.** Branch `hw2-nino-k-red` · weakened: `- EventId = Annotated[str, StringConstraints(pattern=r"^ev-\d{3}$")]` became `+ EventId = str` · pull request #33 (closed, not merged) · run: github.com/example-team/campuspulse/actions/runs/0000000001 (example link) · failed: `test_tool_golden_case[nino-k:c4]`, `test_tool_golden_case[nino-k:c5]` · merge button: "Required statuses must pass before merging".

**What the red run taught me.** Without the pattern, `"../../.env"` reached `_event()` and failed only because no event has that id. The message happened to be safe, but nothing guaranteed it: one refactor that builds the file path before the lookup, and that string goes straight into a path. I had believed the lookup was my protection. It was the pattern. I added the `why` lines to the yaml after this run, because the failing test names alone did not tell my teammate which rule broke.

**The green run.** Product pull request #31 · run: github.com/example-team/campuspulse/actions/runs/0000000002 (example link) · last line: `99 passed`.

**Through the MCP door.** Claude Code, `/mcp` showed 4 tools. I typed "give me a calendar file for the founders' talk". It called `list_events`, then `make_calendar_file(event_id="ev-203")`, and offered the file.

---

## Part 3 · `journal.md`

### Week 5 · Tool Contract
**Where I used it:** `src/contracts.py`, the `Rsvp` class, pull request #27. The agent's first diff put `student_id` in the arguments "so the model can say who is booking". The both-doors test passed and the RSVP worked, which is exactly why it was dangerous. **What I noticed:** a test that only checks the happy path cannot see an identity field. **Do differently:** write the "model cannot set identity" test before asking the agent for the tool.

### Week 6 · Session State
**Where I used it:** `src/memory.py`. Our product remembers a student's interests: scope is the hashed student id, lifetime 180 days, and `DELETE /me/memory` removes the rows. I wrote `tests/test_memory.py::test_forget_deletes_rows` for it in pull request #36. **What I noticed:** my first version marked rows as deleted with a flag, and the next chat turn still read them, because the read query did not check the flag. Deleting the row made the bug impossible instead of merely fixed. **Do differently:** for anything a user can ask us to forget, delete, never flag.

### Week 7 · Supervised Autonomy Loop
**Where I used it:** `src/agent.py`. The goal is "plan my week"; `NEEDS_YES = {"rsvp"}`. `tests/test_agent.py::test_the_gate_blocks_until_a_person_says_yes` is green on `main` since pull request #41. **What I noticed:** `make_calendar_file`, my HW2 tool, did not need to be in `NEEDS_YES`, and I could say why in one line: it reads, and calling it five times changes nothing. Having written "Effect: reads" and "Idempotent: yes" in the contract two weeks earlier made that a lookup, not a debate. **Do differently:** fill the Effect and Idempotent rows for every tool before it goes near a loop.
