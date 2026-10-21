# HW2 · Evidence · `make_calendar_file` · nino-k

*Example write-up. Links are illustrative; yours point at your team's real runs.*

## The five golden cases

`evals/tools/nino-k.yaml`, run by `tests/test_tool_golden.py` in the CI job `test`, which the branch rule on `main` requires. Results from the green run below, 2 November 2026.

| # | Type | Call | Expected | Actual | Pass? |
|---|---|---|---|---|---|
| c1 | normal | `make_calendar_file(event_id="ev-201")`, visitor | file `ev-201.ics` | `ev-201.ics`, DTSTART 20261022T140000Z (18:00 Tbilisi) | pass |
| c2 | normal | `make_calendar_file(event_id="ev-203")`, signed in as s123 | file `ev-203.ics` | `ev-203.ics` | pass |
| c3 | normal | `make_calendar_file(event_id="ev-205")`, a cancelled event | refused, error mentions "cancelled" | refused: "Photo walk: old Kutaisi (ev-205) was cancelled. Do not offer a calendar file." | pass |
| c4 | bad-input | `event_id="Open Build Night"` | refused before the tool runs, error names `event_id` | "invalid arguments: event_id: String should match pattern '^ev-\d{3}$'" | pass |
| c5 | adversarial | `event_id="../../.env"` | refused before any file name is built | "invalid arguments: event_id: String should match pattern '^ev-\d{3}$'" | pass |

Also run through the MCP door by hand in Claude Code (`/mcp` showed 4 tools): "give me a calendar file for the founders' talk" made it call `list_events`, then `make_calendar_file(event_id="ev-203")`, and it offered the file.

## The red run: proof the gate blocks

Branch `hw2-nino-k-red` removed the pattern from `EventId` in `src/contracts.py`. Pull request #33 (closed, not merged).

- Red run: https://github.com/example-team/campuspulse/actions/runs/0000000001 (example link)
- Failures: `test_tool_golden_case[nino-k:c4]` and `[nino-k:c5]`. The merge button said "Required statuses must pass before merging".

**What it taught me.** Without the pattern, `"../../.env"` reached `_event()` and failed only because no event has that id. The error message happened to be safe, but nothing guaranteed it: one refactor that builds a file path from the id first, and the string goes straight into a path. The pattern is what makes c5 safe, not the lookup. I added the `why` lines to the yaml after this run, because the failing test names alone did not tell my teammate which rule broke.

## The green run

Product pull request #31, merged 2 November 2026: https://github.com/example-team/campuspulse/actions/runs/0000000002 (example link). 99 passed, including all five cases.
