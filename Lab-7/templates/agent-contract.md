# <Product name> · Agent Contract

Five lines. Write them before you touch the starter file. Save as `docs/agent-contract.md`.

1. **The goal, in one sentence.** What can a user hand over that takes more than one step?
2. **The tools this loop may use.** (These go in `LOOP_TOOLS`. Leave out everything the goal does not need.)
3. **The one tool that must wait for a yes, and why.** (This goes in `NEEDS_YES`. A tool needs a yes if a wrong call costs someone something: it books, sends, pays, publishes or deletes.)
4. **The most steps it may take.** (`MAX_STEPS`. Six is a good start.)
5. **What the person sees before they say yes.** One line per proposed action. Write an example.

CampusPulse, filled in:

1. Given "plan my week", propose events in the next 7 days that match the student's interests.
2. `list_events`, `make_calendar_file`, `rsvp`. Not `check_room`, not `remember_interest`.
3. `rsvp`: it takes a seat in the student's name, and a seat another student wanted.
4. Six.
5. "RSVP: Tech talk: shipping LLM apps on a student budget · 2026-11-19 18:00 · A112"

The one-page version with budgets and checks, for later: `examples/agent-contract-campuspulse.md`.
