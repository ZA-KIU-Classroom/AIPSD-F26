# Designing session state

*Optional reading for Lab 6, Parts 1 and 3. This is the pattern of the week: Session State. Read it before you fill in your state contract.*

## 1. The concept, in plain language

A model has no memory. Every call starts from nothing; whatever it "remembers" is text you put back into the prompt. So memory is not a property of the model, it is a feature of your application, and like every feature it has to be designed, tested and documented.

The pattern says: conversation memory is an engineered store with an explicit **scope** (who can read it), **lifetime** (when it dies on its own) and **deletion** (how a person kills it early). If a thing you remember does not have all three written down, you have not designed it, you have accumulated it.

There are usually two or three kinds of state in a chat product:

- **Turns.** What was said in this conversation, so "and the day after?" makes sense. Scope: this session. Lifetime: short, hours to a day. Written: automatically.
- **Facts about the person.** Preferences, interests, settings. Scope: this signed-in user. Lifetime: long, but finite. Written: when they ask, or when they set it in a settings screen.
- **The world.** Bookings, orders, RSVPs. That is not memory, that is your database; it was there before Week 6 and has its own rules.

Separating these is most of the design. The mistake is one `history` list that holds everything for everyone forever.

## 2. Why it matters in production

**Leakage.** If scope is wrong, one user's memory appears in another's answer. It does not crash. It does not log. You learn about it from a screenshot on social media. In March 2023, a bug in a caching library used by ChatGPT let some users see titles from other users' conversation histories, and for a window of hours a small number of subscribers could see fragments of other people's billing details. The product was taken offline while it was fixed. The underlying problem was state keyed to the wrong thing under concurrency: exactly a scope error.

**Growth.** If lifetime is missing, the store grows until the prompt no longer fits (Context as Budget, Week 1) and every turn gets slower and more expensive. Teams discover this when a long-running user's requests start timing out.

**Trust and law.** If deletion is missing or fake, you cannot honestly answer "what do you know about me?" or "delete it". In the EU and the UK, people have a right to have their personal data erased; a soft delete that keeps the rows does not satisfy it. More practically, the first time a student asks a campus assistant to forget something and it does not, they stop using it.

## 3. Worked example on CampusPulse

**The contract first.** `docs/state-contract.md` has two rows: the last six turns (scope: session, lifetime: 24 hours, written automatically, deleted by expiry or the button) and interests (scope: hashed student, lifetime: 180 days, written only when the student asks, deleted by the button). Plus a "never store" list: the raw student id, audio, inferred facts, anyone else's data.

**The store.** `src/memory.py` is one SQLite table, `memory(key, kind, role, value, created_at, expires_at)`. Scope is part of the key: `session:<id>` for turns, `student:<hash>` for interests. Every read filters by key and by `expires_at > now()`. There is no "all rows" read in the product.

**Writes.** `add_turn()` runs after every chat turn, for the session only. `remember_interest()` runs only from the `remember_interest` tool, which the model can call only for a signed-in student (Week 5's `tools_for()` never offers write tools to visitors), with a validated `topic`, with identity from the session. The reply says what was stored and how to delete it.

**Reads.** `build_messages()` in `src/chat.py` puts `Known interests: …` in the system prompt and the session's last turns before the new question. Six turns and ten interests are hard limits: the budget is explicit.

**Deletion and expiry.** `forget(student, session)` deletes rows and returns the counts; `DELETE /me/memory` calls it. `expire()` runs at startup. `tests/test_memory.py` pins the clock (`CAMPUSPULSE_NOW`) to prove a turn is invisible after 24 hours and gone after `expire()`.

**Try it:** `python -m demo.state_demo leak` shows a naive list leaking Nino's chess into Giorgi's answer, then the same two chats through the store.

## 4. Common mistakes and how to spot them

- **One list for everyone.** Symptom: an answer mentions something this user never said. Spot it with a two-user test: store for A, read as B, assert empty.
- **Scope by the wrong key.** Keying turns by student instead of session means two open tabs interleave; keying interests by session means they vanish when the tab closes. Ask "who should read this?" for each row.
- **Lifetime declared, not enforced.** A comment says "24 hours" and nothing deletes. Spot it: a test that moves the clock.
- **Soft deletes.** `deleted_at` set, rows kept. Spot it: after `forget()`, count rows in the table directly, not through your own read function.
- **The id in the key.** `student:s123` in a database that gets backed up and pasted into bug reports. Store a hash.
- **Silent writes.** Extracting "facts" from every turn and storing them. The person did not ask, cannot see them, and a poisoned input can plant them. Write only on request (decision 0005).
- **Memory in the system prompt that is not in the contract.** If `build_messages()` injects something the table does not list, the table is wrong. Keep them in one place and test that they agree.

## 5. Check yourself

1. A teammate wants to remember "the last event the user looked at" so they can say "book it" without naming it. Fill in its scope, lifetime, written-when and deleted-by, and say which key it goes under.
2. Why is `forget` an endpoint and not a tool the model can call? Give the failure that would happen if it were a tool.
3. Your interests row has lifetime 180 days. The user states the same interest again on day 170. What should happen to the clock, and which test proves it?
