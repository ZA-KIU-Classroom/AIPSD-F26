# Lab 6 · Homework

No new homework this week. HW2 was released in Lab 5 and is due at the end of Week 7; today's journal entry is part of it. It is listed here in full.

**HW2 · "Tool Contract" · 5 points · individual**
**Due: end of Week 7 · Sunday 8 November 2026, 23:59 (Tbilisi time)**
**Submit: your tool in your team repo through a product pull request, your write-up in `hw2/<your-github-username>/` through its own pull request, both merged to `main`, then fill the submission form (link on Teams)**
**Deliver: one function from your capstone wrapped as an MCP tool with a validated, least-privilege contract; 5 golden cases including one adversarial input, run in CI so a failure blocks the merge; your Pattern Journal for Weeks 5, 6 and 7**
**Full brief, folder layout and checklist: `Lab-5/HOMEWORK.md`**

---

## This week's journal entry

Your Week 6 entry goes in `docs/journal/<your-github-username>.md` tonight and is copied into `hw2/<your-github-username>/journal.md` before Sunday 8 November. Three lines: the pattern (Session State), one place you saw it or used it today, one thing you would do differently. "Used it" means a real row in your state contract or a real test, not the definition.

## What this week's lab gives you toward HW2

- **The pattern of a write that the person asked for.** If your HW2 tool writes anything, Lab 6's `remember_interest` is the template: offered to signed-in callers only, a validated argument, identity from the session, a reply that says what happened. Same gates, same log line.
- **A second adversarial case idea.** A tool argument that tries to smuggle a paragraph of instructions into something you later put in a prompt (a "topic" of 400 characters). The `Topic` type in `examples/campuspulse-state/src/contracts.py` refuses it with a length and a pattern. That is a legitimate adversarial case for your golden set.
- **Time.** The 48 hours after this lab are the ones to use: the HW2 deadline is Sunday week, and the midterm period starts the Monday after it.

## HW2 checklist, unchanged from Lab 5

- Product pull request on `main`: contract with `extra="forbid"`, constrained strings and numbers, **no user, student or account field**; registered in both doors; `evals/tools/<your-github-username>.yaml` with 5 cases including one bad-input and one adversarial.
- One red CI run from deliberately weakening your own contract on a throwaway branch (the merge button refused), one green run.
- Write-up pull request on `main`: `hw2/<your-github-username>/contract.md`, `evidence.md`, `journal.md` (Weeks 5, 6 and 7).
- The submission form (link on Teams), filled individually.

## Every deadline in the course

See `SUBMISSIONS.md` at the repo root. The next three: HW2 on Sunday 8 November 23:59; the midterm during Weeks 8 and 9 (on campus, proctored, Weeks 1 to 7); the Safety and Evaluation Audit in Week 11.
