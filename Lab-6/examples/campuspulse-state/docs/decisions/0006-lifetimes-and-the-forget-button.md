# 0006 · Turns live 24 hours, interests 180 days, and forgetting deletes rows

**Context.** State needs a lifetime or it grows forever and outlives the reason it was stored. It also needs a deletion path a person can find.

**Decision.** Turns expire 24 hours after they are written (a conversation is a day). Interests expire 180 days after they were last stated (a semester). `memory.expire()` runs at startup; every read also filters by expiry, so a row past its lifetime is invisible before it is removed. `forget()` deletes rows; it never sets a flag.

**Why.** 24 hours keeps "and the day after?" working across a lunch break without keeping a month of chat for a student who left. 180 days matches how long an interest stated in October is likely still true. Soft deletes ("deleted_at") keep the data and only hide it; a student who presses "Forget me" means the rows, not a flag.

**Evidence.** `tests/test_memory.py::test_lifetime_a_turn_is_gone_after_24_hours`, `::test_lifetime_an_interest_lasts_180_days`, `::test_deletion_is_total_and_immediate`.

**Consequences.** Backups would need the same deletion applied to them; CampusPulse keeps none yet, and that is written down here rather than forgotten.
