# Memory governance: consent, retention, leakage, and what you never store

*Optional reading for Lab 6, Part 1 (the "never store" section of your contract) and the studio. Lecture Chapter 5 in more depth.*

## 1. The concept, in plain language

Governance is the set of rules that decide what your product is allowed to remember, from whom, for how long, and who can see it. It is not a legal document. It is four questions you can answer for every row of your state contract:

- **Consent.** Did the person know this was being stored, and did they ask for it (or could they reasonably expect it)?
- **Retention.** When does it go away on its own, and does anything (backups, logs, caches) keep a copy past that?
- **Isolation.** Can this ever appear in another person's prompt or answer?
- **Minimisation.** Is this the smallest thing that does the job? Could you store a hash, a category, or nothing?

A product that can answer those four questions for every row is governed. One that cannot is collecting.

## 2. Why it matters in production

**Memory is an attack surface.** In 2024 a security researcher showed that a chat assistant's long-term memory could be planted by prompt injection: a web page or document the user asked the assistant to read contained instructions, the assistant "remembered" them, and from then on every new conversation quietly followed them, including sending the user's messages to a server the attacker controlled. The vendor fixed the exfiltration path. The design lesson stands: anything that writes to memory automatically can be written to by an attacker through the content your model reads. Week 12 attacks CampusPulse this way with a poisoned poster; memory written only on explicit request is the defence you build this week.

**Retention is where privacy promises break.** "We delete your data" is false if the nightly backup keeps it for 90 days and nobody deletes from backups. It is also false if your usage log contains the user's message text. You do not need to solve every case in a student project; you need to write down which ones you have not solved (CampusPulse's decision 0006 does exactly that for backups).

**Isolation failures are silent.** A scope bug produces no error, only a wrong answer that happens to contain someone else's life. See `designing-session-state.md` for the 2023 incident.

## 3. Worked example on CampusPulse

Apply the four questions to the two rows in `docs/state-contract.md`.

**Turns.** Consent: a person typing into a chat expects the chat to remember what they just said; automatic writes are fine for this row only. Retention: 24 hours, enforced by `expires_at` and `expire()`. Isolation: keyed by session id; a new tab is a new session; `recent_turns()` cannot read another session. Minimisation: six turns, 2,000 characters each, no more.

**Interests.** Consent: written only by the `remember_interest` tool, which the model can call only when the student asks; the reply says "Remembered: tech talks. You can delete this any time with the Forget me button." That sentence is the consent record. Retention: 180 days, refreshed on repetition. Isolation: keyed by the hash of the student id; `interests()` cannot read another student. Minimisation: at most ten short strings; the contract's `Topic` type refuses anything over 40 characters, so a "topic" cannot smuggle a paragraph of instructions into the system prompt.

**The never-store list.** The raw student id (hashed everywhere, including logs: Week 5's `student_key()`). Audio (transcribed in memory, discarded in the same request; `tests/test_voice_and_endpoints.py` checks no audio file lands on disk). Inferred facts (decision 0005). Other people's data in anyone's prompt (`test_another_students_interests_are_not_in_my_prompt`).

**Visibility and control.** `GET /me/memory` returns what is held and the lifetimes. `DELETE /me/memory` removes rows and returns counts. Both work with no model involved: when the model is down, forgetting still works.

## 4. Common mistakes and how to spot them

- **Logging message content.** Your usage log should carry numbers (tokens, latency, cost), not text. Check `logs/usage.jsonl` for anything a person typed. The answers log in Week 4 does hold the question; decide whether it should, and write it in the contract.
- **"Remember everything, it's useful."** Every extra row is a leakage path, a retention obligation and a token cost. Start from what the product needs this week.
- **Consent by terms of service.** A line in a policy nobody read is not the same as the reply telling the person what was stored. Put the consent in the moment.
- **No way to see what is held.** If a person cannot look, they cannot trust. One read-only endpoint is enough.
- **Deletion that needs the model.** A `forget` tool fails when the model misreads, is down, or is over budget. Deletion is deterministic code.
- **Different rules for the demo and the product.** If your demo uses a fixed student id, say so in the UI (CampusPulse does: "Signed in as s123 · stand-in until Week 12").

## 5. Check yourself

1. Your product wants to remember a user's dietary restriction to filter events with food. Which of the four questions is hardest, and what would you write under "written when"?
2. A teammate proposes extracting interests automatically from every question "to save the user typing". Name the attack this opens and the week of the course that demonstrates it.
3. `DELETE /me/memory` returns `{"interests": 1, "turns": 2}`. Name two places outside `memory.db` where a copy might still exist, and what your contract should say about each.
