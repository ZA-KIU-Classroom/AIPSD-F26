# 0007 · The agent proposes, the student confirms, code runs what was shown

**Context.** The Week 7 planner turns one sentence ("plan my week") into several tool calls. In Week 5 a student who typed "RSVP me to ev-201" got an RSVP at once, and that was right: they named the action. A planner picks the actions itself. If its `rsvp` calls ran as they were made, a student would find seats taken in their name that they never chose, some of them during their classes.

**Decision.** Tools are marked `confirm=True` when they are consequential (today: `rsvp`). Inside the planner loop a consequential call never runs. `gate.propose()` validates it against the contract, runs every check the tool would run plus the timetable, and parks it as an action in a pending plan. The plan is stored for the signed-in student for 15 minutes. `POST /plan/{id}/confirm` runs the ticked actions through Week 5's `call_tool()` with the stored arguments. No model takes part in the confirmation. A plan can be confirmed once; a newer plan replaces an older one.

**Why here and not in the prompt.** "Ask before booking" in a system prompt is a request. The Replit incident of July 2025 is the public example: an instruction not to change anything, in capitals, and a production database deleted anyway. A gate in code cannot be talked out of its job, by the model or by text the model reads. And because the yes carries action ids, not arguments, nothing can change between what the student saw and what runs.

**Why 15 minutes.** Seats fill and timetables change. A yes given to a stale card is a yes to something else. The preview is re-checked by the tool itself at confirmation (full, cancelled, already registered), so an old plan fails safe even inside the window.

**Evidence.** `tests/test_gate.py`: `test_the_gate_blocks_until_the_student_says_yes`, `test_scope_another_student_cannot_confirm_my_plan`, `test_lifetime_a_plan_cannot_be_confirmed_after_15_minutes`, `test_a_plan_is_single_use_and_a_new_plan_replaces_the_old_one`, `test_deletion_forget_me_removes_a_pending_plan`.

**Consequences.** One more click for the student. The planner cannot finish a booking on its own, which is the point. A third row in `docs/state-contract.md`, so `forget()` now returns a `plans` count and two Week 6 assertions changed to include it.
