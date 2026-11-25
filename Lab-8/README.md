# Lab 8 · Fallback Chain · `lab8-optimization`

**Week 8 lecture · live online · 2 hours · pattern: Fallback Chain**
You leave with one file in front of your model calls: when the first model cannot answer, a second one does; when nobody can, your user reads a sentence you wrote; and the same question is not paid for twice. Three tests prove it.

| What you hand in today | Where | When | Graded? |
|---|---|---|---|
| The tag `lab8-optimization` on `main` (router, three tests, one real call, merged) | your team repo | end of lab | not on its own: evidence for the Repository Review |
| **HW2 · "Tool Contract"** (released in Lab 5) | your team repo + form | **Friday of the Lab 8 week, 23:59** | 5 points (individual) · see [HOMEWORK.md](HOMEWORK.md) |

No new homework. This lab needs the Week 8 lecture only. From now on, each lab runs one week behind its lecture.

**Before lab (5 minutes):** pull your team repo. **Decide two things as a team:** the one model call you protect first, and the sentence your user reads when every model is down.

**Lab clock:** 0:00 recap and questions · 0:15 my live demo · 0:25 build · **1:25 checkpoint** · 1:30 studio · 1:43 homework walk-through · 1:55 next week.

## Where is your team? Pick your row.

| Your repo today | Your path | What you skip |
|---|---|---|
| Lab 7 tagged, the loop runs | **On track.** Steps 1 to 4, with your Lab 7 loop as the real call | nothing |
| Lab 5 or 6 works, no Lab 7 loop | **One lab behind.** Steps 1 to 4, with your chat or tool call as the real call | the loop |
| No model call works right now | **Catching up.** Copy `templates/one_call.py` first, then Steps 1 to 4 | everything from earlier labs: today needs one function |

All three rows reach the same checkpoint and the same tag. Finish earlier labs afterwards, in order; `resources/setup-and-troubleshooting.md` has a catch-up list.

---

## Build · 60 min

Same workflow as every slice (`docs/TEAM-REPO.md` section 4): issue, branch `slice-<issue>-<two-words>`, pull request, a teammate approves and squash-merges.

### Step 1 · Five lines of plan · 10 min

Copy `templates/fallback-plan.md` to `docs/fallback-plan.md` and answer its five questions: the call you protect, the chain, the limit, the lifetime, your sorry sentence. The CampusPulse answers are at the bottom of the template.

**Done when:** the five lines are committed on your branch. Unsure about the lifetime? `resources/caching-without-leaks.md`.

### Step 2 · Copy the starter and change four lines · 25 min

1. **Copy `templates/router_starter.py` to `src/router.py`.** It is the file from lecture slides 8 to 13. Read it once, top to bottom.
2. **ADAPT 0, the import.** The router needs one function shaped like `one_call(messages, tools, timeout=..., model=...)`.
   - On track or one lab behind: add `model` and `timeout` to your Lab 5 call and import it. The Week 8 lines in `examples/campuspulse-router/src/llm.py` show the change (two lines).
   - Catching up: copy `templates/one_call.py` to `src/one_call.py`. Done.
3. **Change the settings** from your plan:

| Line | What goes there | From your plan |
|---|---|---|
| `CHAINS` | per job, two models from two different companies | line 2 |
| `TIMEOUT_S` | seconds one model gets | line 3 |
| `CACHE_TTL_S` | seconds an answer may be reused, or 0 | line 4 |
| `SORRY` | the sentence your user reads | line 5 |

4. **Run it once with the real model** from a Python shell: `complete([{"role": "user", "content": "<a real question>"}])`. Run the same line again and read `logs/router.jsonl`: the second line should say `cache`.

Do this step by hand or delegate it at rung 3 (the agent edits, you read every line).

**Done when:** two log lines, the first `ok` with `place: 1`, the second `cache`. A 400 or 401 raised at you? That is correct behaviour: `resources/what-counts-as-down.md`.

### Step 3 · Make the three tests pass · 15 min

1. **Copy `templates/test_router.py` to `tests/test_router.py`.** Nothing to change unless your job is not called `chat`.
2. **Run `pytest tests/test_router.py`.** Test 1: the first model is down, the second answers, and the log says so. Test 2: everything is down, the reply is your `SORRY` sentence and it is not cached. Test 3: a 400 is raised, not passed to the next model.

**Done when:** three green tests, offline, no key.

### Step 4 · Put it in the path · 10 min

1. **Send one real feature through the router.** Replace one direct model call with `complete(...)`. On track: your Lab 7 loop takes it as an argument, `run(goal, user, llm=complete)`.
2. **Use the feature once, then once more with the same input.** Read `logs/router.jsonl`.
3. **One entry in `docs/delegation-log.md`**, same format as Lab 2.

**✅ Checkpoint (around 1:25):** `pytest` green including the three new tests, and you can show me your own feature going through the router: two log lines, `ok` then `cache`. Two or three of you will screen-share. Then merge and tag, on `main`:

```
git switch main && git pull
git tag lab8-optimization && git push origin lab8-optimization
```

## After the lab, before Lab 9 · about 20 min · not graded

The table that shows what the router is worth on your product. It is evidence for the Repository Review and for your Demo Day slide.

1. Copy `templates/measure.py` to `evals/measure.py` and put 10 real questions for your product in `QUESTIONS`, with at least 3 repeats.
2. Run `python -m evals.measure before`, then `python -m evals.measure after`. Both are live. For three requests the first model is treated as down, so you see the fallback answer.
3. Copy `templates/measurements.md` to `docs/measurements.md` and fill it from the two outputs. Guide: `resources/measuring-before-and-after.md`.

## Studio · 13 min

- **AGENTS.md.** One line under Always: *every model call goes through `complete()` in `src/router.py`; never call a model directly*.
- **Journal.** Your Week 8 entry in `docs/journal/<your-github-username>.md`: the pattern, the call you protected today, the sentence your user reads when everything is down.
- **HW2 check-in.** Open `hw2/<your-github-username>/`. It is due Friday of this week. `templates/hw2-writeup.md` walks you through the three files.

Last 12 minutes: [HOMEWORK.md](HOMEWORK.md) on screen, line by line.

**Stretch, only if you finished early:**
- Start the before and after table now (see "After the lab").
- Four more tests, including "the same question is paid for once" (in `examples/campuspulse-router/tests/test_router.py`).
- Show `degraded` replies differently on your page.

---

## What your repo has at the end of Lab 8

| Path | Created in | Required |
|---|---|---|
| `docs/fallback-plan.md`, five lines | Step 1 | yes |
| `src/router.py` from the starter, settings adapted | Step 2 | yes |
| `tests/test_router.py`, three tests green | Step 3 | yes |
| one real feature calling `complete()` | Step 4 | yes |
| `docs/delegation-log.md`, one new entry | Step 4 | yes |
| tag `lab8-optimization` on `main` | Checkpoint | yes |
| one AGENTS.md line · Week 8 journal entry | Studio | yes |
| `evals/measure.py` with your 10 questions · `docs/measurements.md` | after the lab, before Lab 9 | yes, not graded |
| more tests · a degraded banner | Stretch | no |

## Folder map of this lab

- [HOMEWORK.md](HOMEWORK.md) · what is due: HW2, in full.
- `templates/` · `fallback-plan.md`, `router_starter.py`, `test_router.py`, `one_call.py`, `measure.py`, `measurements.md`, `hw2-writeup.md`.
- `examples/` · every template filled in for CampusPulse: `fallback-plan-campuspulse.md`, `measurements-campuspulse.md`, `hw2-writeup-campuspulse.md`, and `campuspulse-router/` (the Lab 7 reference plus `src/router.py`, its tests, and `python -m demo.router_demo before|after|dark|bug`).
- `resources/` · optional, and where the depth is: `fallback-chains.md`, `what-counts-as-down.md`, `caching-without-leaks.md`, `measuring-before-and-after.md`, the deep dive `deep-dive-gateway-and-prompt-caching.md`, and `setup-and-troubleshooting.md`.

---

## Homework

No new homework this week. HW2 was released in Lab 5 and is due this week. It is listed here in full.

```text
HW2 · "Tool Contract" · 5 points · individual
Due: Friday of the Lab 8 week, 23:59 (Tbilisi time)
Submit: your tool in your team repo through a product pull request, your write-up in hw2/<your-github-username>/ through its own pull request, both merged to main, then fill the submission form (link on Teams)
Deliver: one function from your capstone wrapped as an MCP tool with a validated, least-privilege contract; 5 golden cases including one adversarial input, run in CI so a failure blocks the merge; your Pattern Journal for Weeks 5, 6 and 7
Full brief, folder layout and checklist: Lab-5/HOMEWORK.md · write-up template and a finished example: Lab-8/templates/hw2-writeup.md and Lab-8/examples/hw2-writeup-campuspulse.md
```

Full notes: [HOMEWORK.md](HOMEWORK.md).

