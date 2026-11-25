# Lab 8 · Homework

No new homework this week. HW2 was released in Lab 5 and is due this week. It is listed here in full.

```text
HW2 · "Tool Contract" · 5 points · individual
Due: Friday of the Lab 8 week, 23:59 (Tbilisi time)
Submit: your tool in your team repo through a product pull request, your write-up in hw2/<your-github-username>/ through its own pull request, both merged to main, then fill the submission form (link on Teams)
Deliver: one function from your capstone wrapped as an MCP tool with a validated, least-privilege contract; 5 golden cases including one adversarial input, run in CI so a failure blocks the merge; your Pattern Journal for Weeks 5, 6 and 7
Full brief, folder layout and checklist: Lab-5/HOMEWORK.md · write-up template and a finished example: Lab-8/templates/hw2-writeup.md and Lab-8/examples/hw2-writeup-campuspulse.md
```

---

## The deadline, in plain words

Friday of the week Lab 8 runs, at 23:59 Tbilisi time. Both lab groups have the same deadline. The exact calendar date is in the Teams post. This replaces every earlier HW2 date, including "one week after Lab 7" in `Lab-7/HOMEWORK.md`. Nothing else about HW2 has changed.

## What is new in this folder, and what is not

Nothing was added to HW2. Two files here make it easier to finish:

- `templates/hw2-writeup.md` · one page of prompts for the three files in `hw2/<your-github-username>/` (`contract.md`, `evidence.md`, `journal.md`). Every prompt asks for something only your own repo has: a pull request number, a CI run link, the exact text of an error.
- `examples/hw2-writeup-campuspulse.md` · the same page, finished, for a CampusPulse student. Copy its shape, not its content.

The brief, the folder layout, the grading split and the checklist are still `Lab-5/HOMEWORK.md`.

## Before you fill the form

- [ ] Product pull request merged to `main`; `pytest` green on `main`, including your cases in `evals/tools/<your-github-username>.yaml`
- [ ] Write-up pull request merged to `main`: `contract.md`, `evidence.md`, `journal.md` (Weeks 5, 6 and 7)
- [ ] `evidence.md` links one red CI run that blocked a merge and one green run
- [ ] No key, no `.env`, no personal data anywhere
- [ ] The form (link on Teams), filled once, by you, with your full name and your KIU email

## If you are behind on HW2

Do these in order and stop when the time runs out; partial work that is merged earns more than complete work that is not.

1. The tool and its contract, merged (correctness, 40).
2. The five cases in `evals/tools/`, green in CI (verification, part of 20).
3. The red run and its link (verification, the rest of 20).
4. The three write-up files (documentation and journal, 20).

Stuck on a merge because a teammate is not answering? Email me the pull request link before the deadline, not after.

## What this week's lab gives you toward later work

Today's journal entry (Fallback Chain) is not part of HW2. It starts the journal that the Repository Review reads at the end of the semester.
