# CampusPulse · State Contract

One row per thing the product remembers across turns. If it is not in this table, the product does not store it. `src/memory.py` is the code version of this table and the two must agree; `tests/test_memory.py` proves the scope, lifetime and deletion rows.

| What we remember | Why the product needs it | Scope: who can read it | Lifetime | Written when | Deleted by | Where it lives |
|---|---|---|---|---|---|---|
| The last 6 turns of a conversation | so "and the day after?" means something | this session only (`X-Session-Id`); a new tab is a new session | 24 hours after each turn | every chat turn, automatically | expiry; or "Forget me" (`DELETE /me/memory`) | `memory.db`, kind `turn`, key `session:<id>` |
| Interests ("tech talks", "free food"), at most 10 | so "what's on?" leads with what the student cares about | the signed-in student only, keyed by the hash of their id | 180 days, refreshed when they say it again | only when the student asks ("remember that I like…"), through the `remember_interest` tool | "Forget me" (`DELETE /me/memory`); there is no forget tool | `memory.db`, kind `interest`, key `student:<hash>` |
| RSVPs (Week 5) | the seat list | the event, by hashed student | until the event | the `rsvp` tool | not by the student (an organiser decision; see decision 0003) | `rsvps.json` |

## What we never store

- The student id itself. Every key and log line carries `student_key()`, a 12-character hash.
- Audio. A voice clip is transcribed in memory and discarded in the same request; the transcript becomes an ordinary turn.
- Anything the model "noticed" on its own. Memory writes are explicit: the student asks, the model calls a tool, the reply says what was stored and how to delete it.
- Turns from a different session, or interests from a different student, in anyone's prompt.

## How a student sees and controls it

- `GET /me/memory` shows the interests and the number of recent turns the server holds, with the lifetimes.
- The reply to a memory write always ends with how to delete it.
- "Forget me" removes every row for that student and session, immediately, and returns the counts. Rows are deleted, not flagged.

## What changes the contract

Any new row in this table needs a decision record in `docs/decisions/` and a test in `tests/test_memory.py` for its scope, its lifetime and its deletion.
