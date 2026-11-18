# Lab 7 · Homework

No new homework this week. HW2 was released in Lab 5; today's journal entry is its third and last. It is listed here in full.

**HW2 · "Tool Contract" · 5 points · individual**
**Due: one week after Lab 7, 23:59 (Tbilisi time)**
**Submit: your tool in your team repo through a product pull request, your write-up in `hw2/<your-github-username>/` through its own pull request, both merged to `main`, then fill the submission form (link on Teams)**
**Deliver: one function from your capstone wrapped as an MCP tool with a validated, least-privilege contract; 5 golden cases including one adversarial input, run in CI so a failure blocks the merge; your Pattern Journal for Weeks 5, 6 and 7**
**Full brief, folder layout and checklist: `Lab-5/HOMEWORK.md`**

---

## The deadline, in plain words

Seven days after your Lab 7 session, at 23:59 Tbilisi time. Both lab groups have the same deadline. This replaces the date printed in `Lab-5/HOMEWORK.md` and `Lab-6/HOMEWORK.md`, which was set before the midterm moved. Nothing else about HW2 has changed.

## This week's journal entry

Your Week 7 entry goes in `docs/journal/<your-github-username>.md` tonight and is copied into `hw2/<your-github-username>/journal.md` before the deadline. Three lines: the pattern (Supervised Autonomy Loop), one place you saw it or used it today, and the one action in your product that must wait for a yes. "Used it" means a real line in your agent contract or a real test, not the definition.

Your `journal.md` now needs three entries: Week 5 (Tool Contract), Week 6 (Session State), Week 7 (Supervised Autonomy Loop).

## What this week's lab gives you toward HW2

- **A sharper answer to "is my tool least-privilege?"** Today you marked tools as read or consequential. Say which one your HW2 tool is in `contract.md`, in one sentence, and why. If it is consequential, say what would have to confirm it inside a loop.
- **A better adversarial case.** A tool that is safe when a person asks for it by name can be unsafe when a loop calls it five times. A golden case that calls your tool twice with the same arguments and expects the second call to be harmless (idempotent, or refused with a clear message) is a legitimate adversarial case.
- **Error messages written for a model.** `rsvp_preview()` in `examples/campuspulse-agent/src/tools.py` returns errors that say what to do next ("Leave it out or pick another event"). If your tool's failure messages only say what went wrong, improve one and note it in `evidence.md`.

## HW2 checklist, unchanged from Lab 5

- Product pull request on `main`: contract with `extra="forbid"`, constrained strings and numbers, **no user, student or account field**; registered in both doors; `evals/tools/<your-github-username>.yaml` with 5 cases including one bad-input and one adversarial.
- One red CI run from deliberately weakening your own contract on a throwaway branch (the merge button refused), one green run.
- Write-up pull request on `main`: `hw2/<your-github-username>/contract.md`, `evidence.md`, `journal.md` (Weeks 5, 6 and 7).
- The submission form (link on Teams), filled individually.

## Every deadline in the course

See `SUBMISSIONS.md` at the repo root. Next after HW2: the Safety and Evaluation Audit, in the evaluation week.
