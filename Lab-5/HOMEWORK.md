# Lab 5 · Homework

Quiz 1 is due before the Week 6 lab. HW2 is released today and due at the end of Week 7. Both are listed here in full.

**Quiz 1 · individual · 5 points · covers Weeks 1 to 5**
**Opens on the course quiz platform after the Week 5 lecture (link on Teams) · Due: Tuesday 27 October 2026, 23:59 (Tbilisi time), before the Week 6 lab · untimed**
**Five written questions. The course slides are available inside the quiz. You may not use ChatGPT, Claude, Gemini, or any other AI tool to write or rewrite your answers. Every answer is run through Turnitin: if your answers do not meet the threshold for original work, your quiz mark is zero.**

**HW2 · "Tool Contract" · 5 points · individual**
**Due: end of Week 7 · Sunday 8 November 2026, 23:59 (Tbilisi time)**
**Submit: your tool in your team repo through a product pull request, your write-up in `hw2/<your-github-username>/` through its own pull request, both merged to `main`, then fill the submission form (link on Teams)**
**Deliver: one function from your capstone wrapped as an MCP tool with a validated, least-privilege contract; 5 golden cases including one adversarial input, run in CI so a failure blocks the merge; your Pattern Journal for Weeks 5, 6 and 7**
**Full brief, folder layout and checklist: `Lab-5/HOMEWORK.md`**

---

## Quiz 1, in one screen

Five questions, each marked 1, ½ or 0. Four kinds: **trace** (here is a log or an output: what happened, and why), **trade-off** (choose a design for this situation and defend it), **ladder** (place a delegation on the Autonomy Ladder and say how you verify it), **apply** (which patterns fit a new product, and what exactly you build). The slides are there to remind you of a definition. They do not contain the answers: every question describes a situation the slides do not, so a sentence copied from a slide earns nothing. Write in your own words. Short and specific beats long and polished. Spelling fixes in your own sentences are fine; a tool that rewrites your sentences is not.

The best preparation: Week 5 slide 27 (the five patterns on one page), the TRY IT boxes from every lecture, and your own journal.

## HW2, in one screen

**The job.** Take one function from your capstone that a model should be able to ask for, and turn it into a tool the way Lab 5 did: a contract in code, the three gates, an MCP server that serves it, and a golden set that runs in CI and blocks a merge when the contract is weakened. Then write it up.

**Which function.** One your product really needs: a lookup on live data, or an action. **Each member wraps a different function**; the owners table is at the bottom of your `docs/tool-contracts.md` (Lab 5 studio). Not the tool your team built in Lab 5. A function that deletes, pays or sends to other people needs my agreement by email first.

**Where things go.** HW2 is the one homework that touches product code, so it has two pull requests (`docs/TEAM-REPO.md` section 4):

| Pull request | Contains | Who approves |
|---|---|---|
| **Product** · branch `slice-<issue>-hw2-<username>` | your tool in `src/` (contract, function, `TOOLS` registry entry, MCP registration), `evals/tools/<your-github-username>.yaml`, any extra tests | a teammate, like any product change; the repo keeper if `.github/` changes |
| **Write-up** · branch `hw2-<username>` | `hw2/<your-github-username>/contract.md`, `evidence.md`, `journal.md` | a teammate, checking only that you stayed inside your folder |

```
hw2/<your-github-username>/
├── contract.md    one page, from Lab-5/templates/tool-contract.md, with links to your code on main
├── evidence.md    the 5 golden cases with their results; a link to one red CI run that blocked
│                  a merge and one green run; one paragraph on what the red run taught you
└── journal.md     Pattern Journal entries for Weeks 5, 6 and 7
```

**The golden set.** Copy `templates/tool-golden.yaml` to `evals/tools/<your-github-username>.yaml`. Five cases: at least 3 normal, 1 bad input, 1 adversarial. Adversarial means an input written to make the tool do something it must not: another user's identity in the arguments, a path or query smuggled into a string, an id from someone else's data, a huge value, instructions in a text field. `tests/test_tool_golden.py` (set up by your repo keeper in Lab 5) runs every file in `evals/tools/` through `call_tool()`, with no model and no key, inside the CI job your branch rule already requires. Filled examples: `examples/campuspulse-tools/evals/tools/`.

**The red run.** Prove the gate works. On a throwaway branch, weaken your own contract (remove a pattern, drop `extra="forbid"`, add an identity field), push, and open a pull request. CI goes red and the merge button is blocked. Copy that run's link into `evidence.md`, then close the pull request without merging and delete the branch. Then link the green run of your real product pull request.

**Grading (5 points).** Correctness 40 · the tool works through both doors, the contract refuses bad and adversarial input, the five cases pass on `main`. Code quality 20 · small, readable, errors written for the model, nothing destructive. Documentation and journal 20 · a one-page contract a stranger could review, three honest journal entries. Verification evidence 20 · the cases run in CI, the red run really blocked a merge, `evidence.md` shows actual results.

**Before you press submit**

- [ ] Product pull request merged to `main`; `pytest` green on `main`, including your cases in `evals/tools/`
- [ ] Your contract has `extra="forbid"`, a pattern or fixed set on every string, bounds on every number, and no user, student or account field
- [ ] Your tool is registered in the MCP server and passes the both-doors test
- [ ] Expected failures reach the model as messages that say what to do next; nothing leaks a stack trace, a table name or a path
- [ ] Five cases, including one bad input and one adversarial; each has a one-line `why`
- [ ] `evidence.md` links one red run that blocked a merge and one green run
- [ ] `journal.md` has three dated entries, Weeks 5, 6 and 7
- [ ] No key, no `.env`, no personal data anywhere
- [ ] The form is submitted with the links to your write-up folder and your product pull request

Filled write-up: `examples/hw2-example/` (a CampusPulse student who wrapped `make_calendar_file`). Copy its shape, not its content.

## What this week's lab gives you toward them

- The Lab 5 tool, loop, MCP server and `tests/test_tool_golden.py` are the frame HW2 plugs into. Your HW2 tool is one more entry in the same registry and the same server.
- `resources/least-privilege-for-tools.md` ends with the seven locks from Week 5 slide 25. They are the HW2 checklist.
- Your Week 5 journal entry, written in studio, is the first entry in HW2's `journal.md`.

## Every deadline in the course

`SUBMISSIONS.md` at the root of this repo. On any conflict between files, that one wins. Stuck? Email zeshan.ahmad@kiu.edu.ge before the deadline, not after.
