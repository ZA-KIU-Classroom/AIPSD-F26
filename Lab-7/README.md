# Lab 7 · Supervised Autonomy Loop · `lab7-agent-loop`

**Week 7 · live online · 2 hours · pattern: Supervised Autonomy Loop**
You leave with one loop in your capstone that takes a goal, runs a few steps on its own, stops after a fixed number of steps, and waits for a person's yes before it does anything that costs someone something. One test proves the yes is real.

| What you hand in today | Where | When | Graded? |
|---|---|---|---|
| The tag `lab7-agent-loop` on `main` (the loop and its gate test, merged) | your team repo | end of lab | not on its own: evidence for the Repository Review |
| **HW2 · "Tool Contract"** (released in Lab 5; today's journal entry is its third and last) | your team repo + form | **one week after Lab 7, 23:59** | 5 points (individual) · see [HOMEWORK.md](HOMEWORK.md) |

No new homework this week. This lab is short on purpose: one part, one checkpoint, and you start from a file that already works.

**Before lab (5 minutes, right after the lecture):** pull your team repo at `lab6-streaming-state`. No new dependency. **Decide two things as a team:** one goal a user could hand your product that takes more than one step, and the one action in it that must wait for a person.

**Lab clock:** 0:00 recap and questions · 0:15 my live demo · 0:25 build · **1:25 checkpoint** · 1:30 studio · 1:43 homework walk-through · 1:55 next week.

---

## Build · 60 min

Same workflow as every slice (`docs/TEAM-REPO.md` section 4): issue, branch `slice-<issue>-<two-words>`, pull request, a teammate approves and squash-merges.

### Step 1 · Five lines of contract · 10 min

Copy `templates/agent-contract.md` to `docs/agent-contract.md` and answer its five questions: the goal, the tools the loop may use, the one tool that needs a yes, the most steps, and what the person sees before saying yes. The CampusPulse answers are at the bottom of the template.

**Done when:** the five lines are committed on your branch.

### Step 2 · Copy the starter and change three lines · 25 min

1. **Copy `templates/agent_starter.py` to `src/agent.py`.** It is the file from lecture slide 8, about 50 lines. Read it once, top to bottom, before you change anything.
2. **Fix the three imports** at the top if your Lab 5 functions have other names: the model call, `call_tool()`, and your tool registry.
3. **Change the three ADAPT lines** using your contract:

| Line | What goes there | From your contract |
|---|---|---|
| `GOAL_PROMPT` | what the loop is for, and how to finish | line 1 |
| `LOOP_TOOLS` | only the tools this goal needs | line 2 |
| `NEEDS_YES` | the tool that books, sends, pays or deletes | line 3 |

4. **Run it once with the real model** from a Python shell or a tiny script: `run("<your goal>", "<a test user>")`. Read what comes back: the status, the proposed actions, the trace.

You may do this step yourself or delegate it at rung 3 (the agent edits, you read every line). The file is short enough to do by hand, and you will understand it better if you do.

**Done when:** a run returns `needs_confirmation` with at least one proposed action. Stuck on which tool needs a yes? `resources/confirmation-gates.md`. A 400 error on the second model turn? `resources/setup-and-troubleshooting.md`.

### Step 3 · Make the gate test pass · 25 min

1. **Copy `templates/test_agent.py` to `tests/test_agent.py`** and change its three ADAPT lines: a test user, one call to your `NEEDS_YES` tool, and `what_changed()`, which returns the thing your tool changes (a file, a table, an outbox).
2. **Run `pytest tests/test_agent.py`.** Test 1 says: after the loop runs, nothing has changed; after `confirm()`, exactly one thing has; a second `confirm()` does nothing. Test 2 says: a model that never finishes is stopped after four steps.
3. **Add one endpoint** so a person can say yes: `POST /plan/confirm` (or your framework's equivalent) that takes a list of action ids and calls `confirm(user, ids)`. Ids only, never arguments. No model in it.
4. **One entry in `docs/delegation-log.md`**, same format as Lab 2.

**✅ Checkpoint (around 1:25):** `pytest` green including the two new tests, and you can show me the gate blocking: run the loop, show that nothing changed, confirm, show that one thing did. Two or three of you will screen-share. Then merge the pull request and tag, on `main`:

```
git switch main && git pull
git tag lab7-agent-loop && git push origin lab7-agent-loop
```

## Studio · 13 min

- **AGENTS.md.** One line under Never: *never run a tool in NEEDS_YES from inside a loop; park it and wait for confirm()*.
- **Journal.** Your Week 7 entry in `docs/journal/<your-github-username>.md`: the pattern, one place you used it today, the one action in your product that must wait for a yes. It is the third and last entry in your HW2 `journal.md`.
- **HW2 check-in.** Open your HW2 branch and your `hw2/` folder. It is due one week from today's lab.

Last 12 minutes: [HOMEWORK.md](HOMEWORK.md) on screen, line by line, and your questions about it.

**Stretch, only if you finished early** (each one is already built in `examples/campuspulse-agent/`):
- Check in code before parking: refuse a proposal that cannot work, with a reason the model can read (`src/gate.py`, `propose()`).
- Park the plan in your Lab 6 store with a lifetime, instead of a dict (`src/memory.py`, `put_plan()`).
- A confirmation card in your page with one checkbox per action (`static/index.html`).

---

## What your repo has at the end of Lab 7

| Path | Created in | Required |
|---|---|---|
| `docs/agent-contract.md`, five lines | Step 1 | yes |
| `src/agent.py` from the starter, three lines adapted | Step 2 | yes |
| `tests/test_agent.py`, two tests green | Step 3 | yes |
| a confirm endpoint that takes ids and calls `confirm()` | Step 3 | yes |
| `docs/delegation-log.md`, one new entry | Step 3 | yes |
| tag `lab7-agent-loop` on `main` | Checkpoint | yes |
| one AGENTS.md line · Week 7 journal entry | Studio | yes |
| checks before parking · a stored plan · a confirmation card | Stretch | no |

## Folder map of this lab

- [HOMEWORK.md](HOMEWORK.md) · what is due, in full: HW2, and where this week's journal entry goes.
- `templates/` · `agent-contract.md` (five lines), `agent_starter.py` (the loop), `test_agent.py` (two tests).
- `examples/` · `campuspulse-agent/`: `src/simple_agent.py` is the starter filled in for CampusPulse, with `python -m demo.simple_demo plan` to run it. The same folder also holds the full version (`src/agent.py`, `src/gate.py`) for the stretch and for the curious. `agent-contract-campuspulse.md` is the one-page contract for that full version.
- `resources/` · optional, and where the depth is. They describe the full version: `the-agent-loop.md`, `confirmation-gates.md`, `guardrails-timeouts-retries-budgets.md`, `when-not-to-agent.md`, `setup-and-troubleshooting.md`.

---

## Homework

No new homework this week. HW2 was released in Lab 5; today's journal entry is its third and last. It is listed here in full.

**HW2 · "Tool Contract" · 5 points · individual**
**Due: one week after Lab 7, 23:59 (Tbilisi time)**
**Submit: your tool in your team repo through a product pull request, your write-up in `hw2/<your-github-username>/` through its own pull request, both merged to `main`, then fill the submission form (link on Teams)**
**Deliver: one function from your capstone wrapped as an MCP tool with a validated, least-privilege contract; 5 golden cases including one adversarial input, run in CI so a failure blocks the merge; your Pattern Journal for Weeks 5, 6 and 7**
**Full brief, folder layout and checklist: `Lab-5/HOMEWORK.md`**

Full notes: [HOMEWORK.md](HOMEWORK.md) · every deadline in the course: `SUBMISSIONS.md` at the repo root.
