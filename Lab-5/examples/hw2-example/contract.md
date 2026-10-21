# HW2 · Tool contract · `make_calendar_file` · nino-k

*Example write-up: a CampusPulse student who wrapped the "add to calendar" function. Code on `main`: `src/contracts.py` (`CalendarFile`, `EventId`), `src/tools.py` (`make_calendar_file`, registry entry), `src/mcp_server.py` (`make_calendar_file`), `evals/tools/nino-k.yaml`. Product pull request: #31 (example).*

**In one sentence, for the model:** An .ics file for one event that the student adds to their own calendar. Reads only.

| | |
|---|---|
| **Effect** | reads. It returns a file; the student's own calendar app does the write |
| **Undo** | nothing to undo: no state changes on our side |
| **Idempotent?** | yes |
| **Offered to** | everyone, visitors included. It needs no identity, so offering it widely costs nothing |
| **Identity from** | not needed |
| **Touches** | `data/campus/events.json`, read only. No calendar account, no OAuth token |
| **Must never** | write to a student's calendar directly, or build a file name from anything but a validated event id |

**Inputs**

| Argument | Type | Constraint | Description the model reads |
|---|---|---|---|
| `event_id` | string | pattern `^ev-\d{3}$`; unknown fields refused | Event id, like ev-201 |

**Result.** `filename` (`<event_id>.ics`), `content` (RFC 5545 text, times converted from Tbilisi time to UTC).

**Expected failures**

| When | Message the model reads |
|---|---|
| unknown id | There is no event ev-999. Call list_events to find the right id. |
| cancelled event | Photo walk: old Kutaisi (ev-205) was cancelled. Do not offer a calendar file. |

**Why a file and not calendar access.** The first version I asked the agent for used Google Calendar with an OAuth write scope. It worked in ten minutes. Then I read the scope: it could also read, move and delete every event in the student's calendar. The `.ics` file does the one thing the student asked for, needs no token, and can be offered to visitors. Decision record: `docs/decisions/0003-calendar-file-not-calendar-access.md`.

**Where the five cases live.** `evals/tools/nino-k.yaml`, run in CI by `tests/test_tool_golden.py`. Results and CI links: `evidence.md`.

**Log line.** Tool, arguments, ok or the error, latency. No caller is recorded: the tool never receives one.
