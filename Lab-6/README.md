# Lab 6 · Session State · `lab6-streaming-state`

**Week 6 · live online · 2 hours · pattern: Session State**
You leave with answers that stream as they are written, and one thing your product remembers across turns, with its scope, lifetime and deletion written down, enforced in code, and proven by tests.

| What you hand in today | Where | When | Graded? |
|---|---|---|---|
| The tag `lab6-streaming-state` on `main` (streaming, the state store, `DELETE /me/memory`, tests merged) | your team repo | end of lab | not on its own: evidence for the Repository Review, and the Week 7 planner builds on it |
| **HW2 · "Tool Contract"** (released in Lab 5; today's journal entry is its second entry) | your team repo + form | **Sunday 8 November, 23:59** | 5 points (individual) · see [HOMEWORK.md](HOMEWORK.md) |

No new homework this week. Quiz 1 closed yesterday.

**Before lab (10 minutes, right after the lecture):** pull your team repo at `lab5-tools-mcp`. Run `pip install python-multipart` (file uploads, for the voice stretch). Export the team OpenRouter key as in Lab 5. **Decide one thing your product should remember across turns**: the conversation itself counts, but the interesting row is something about the person (a preference, a setting, a last-viewed item). One row per team today.

**Lab clock:** 0:00 recap and questions · 0:15 my live demo (the same answer whole and streamed, then a memory that leaks, then one that forgets) · 0:30 Parts 1 to 3 · 1:35 studio · 1:48 homework walk-through · 1:55 next week.

---

## Part 1 · Write the state contract · 10 min

No store before a contract. Same rule as the tool contract last week.

1. **Copy `templates/state-contract.md` to `docs/state-contract.md`** and fill one row for conversation turns and one for the thing you chose: what, why, scope (who can read it), lifetime (a number with a unit), written when (who triggers it), deleted by (a path without the model), where it lives.
2. **Fill the "never store" list.** At least: the raw user id (hash it, as your Lab 5 log already does), anything the model inferred rather than the person stated, other people's rows in anyone's prompt.
3. **Check two columns twice.** "Written when": if your answer for a fact about the person is "automatically", change it to "when they ask". "Deleted by": if your answer needs the model, it is wrong.

The CampusPulse version: `examples/state-contract-campuspulse.md`. Two minutes to read.

**Done when:** `docs/state-contract.md` is committed on a branch. Stuck on scope or lifetime? `resources/designing-session-state.md`. Stuck on the "never store" list? `resources/memory-governance.md`.

## Part 2 · Streaming · 25 min

Same workflow as every slice (`docs/TEAM-REPO.md` section 4): issue, branch `slice-<issue>-<two-words>`, pull request, a teammate approves and squash-merges.

Delegate at **rung 3: the agent writes the code, you read every line of the diff.** Point it at exactly three things: `docs/state-contract.md`, your `AGENTS.md`, and `examples/campuspulse-state/` in this lab folder. Ask for a plan first. Quote this line in the task prompt: *usage is logged once per stream, after the last chunk, with time to first token; the log line is written even when the model asked for a tool.*

What must be in the diff. Check each one yourself:

| Must have | Why | If stuck |
|---|---|---|
| A streaming call in your Lab 5 `llm.py`, through the same client, that yields text pieces and reads usage from the last chunk. Nothing else in the file changes; Lab 3, 4 and 5 tests stay green | one logged path for every model call | `examples/campuspulse-state/src/llm.py` · `resources/streaming-explained.md` |
| The log line for a stream has `ttft_ms` | the number the user feels, measured | `Stream.__iter__` |
| An endpoint that returns Server-Sent Events: `token`, `done` (ttft, tokens, cost); `tool` if your turn can call tools | the browser reads it with twenty lines | `src/app.py` · `templates/sse-client.html` |
| If your turn offers tools: fragments stitched by index, then every call through your Lab 5 `call_tool()` | the Week 5 gates do not disappear because the answer streams | `src/chat.py` |
| At least 1 offline test: pieces arrive, they join into the answer, one usage line with `ttft_ms` | the test half of the Evidence Rule | `templates/test_state.py`, test 1 |

**✅ Checkpoint 1 (around 1:05):** with the real model, one streamed answer visible in your page or in `curl -N`, and its line in `logs/usage.jsonl` with `ttft_ms` and real token counts. Two or three of you will screen-share.

## Part 3 · The state store · 30 min

1. **Create the store** (`src/memory.py` or your equivalent) from the two rows of your contract: a write for turns, a write for your chosen row, a read for each that filters by key **and** by expiry, `forget(user, session)` that deletes rows and returns counts, `expire()`. Scope is part of the key; the key holds a hash, never the id. Model: `examples/campuspulse-state/src/memory.py` (SQLite, standard library, no new dependency).
2. **Wire it into the turn:** context in (the last few turns of this session, the person's row in the system prompt, with explicit limits), the two turns written back after the answer. If your chosen row is about the person, write it only when they ask: a tool with a contract (Lab 5), identity from the session, and a reply that says what was stored and how to delete it.
3. **Add `GET /me/memory` and `DELETE /me/memory`** (or your framework's equivalent). Delete needs no model. The reply after a write names the delete path.
4. **Three offline tests** from `templates/test_state.py`: scope (store as A, read as B: empty, and not in B's prompt), lifetime (pin the clock, move it, read: gone; `expire()` removes it), deletion (counts returned, reads empty, rows really gone).
5. **One entry in `docs/delegation-log.md`**, same format as Lab 2.

**✅ Checkpoint 2 (around 1:35):** `pytest` green including the four new tests, a conversation that remembers across two turns, "forget me" that returns counts and empties the next read, pull request merged. Then tag, on `main`:

```
git switch main && git pull
git tag lab6-streaming-state && git push origin lab6-streaming-state
```

Store errors, locked databases, expiry tests that pass for the wrong reason: `resources/setup-and-troubleshooting.md`.

## Part 4 · Studio · 13 min

- **AGENTS.md.** Two lines under Never: *never store a raw user id, a recording, or anything the person did not state* and *never add a memory write the user did not ask for*.
- **Journal.** Your Week 6 entry in `docs/journal/<your-github-username>.md`: the pattern, one place you used it today, one thing you would do differently. It is the second entry in your HW2 `journal.md`.
- **HW2 check-in.** Open your product pull request branch. If your tool is not yet behind a contract and five golden cases, that is your next 48 hours; the deadline is Sunday week.

Last 7 minutes: [HOMEWORK.md](HOMEWORK.md) on screen, line by line.

**Stretch (voice):** hold-to-talk in your page, a clip converted to 16 kHz WAV in the browser, `POST /voice` that transcribes it through the chat model, runs your normal turn, and returns a spoken answer. The clip is never written to disk, and a test says so. Model: `examples/campuspulse-state/static/index.html` and `src/llm.py`; the costs and the pitfalls: `resources/voice-in-voice-out.md`.

---

## What your repo has at the end of Lab 6

| Path | Created in | Required |
|---|---|---|
| `docs/state-contract.md` | Part 1 | yes |
| a streaming call in `llm.py`, an SSE endpoint, `ttft_ms` in the usage log | Part 2 | yes |
| `src/memory.py` (or equivalent), the turn wired to it, `GET` and `DELETE /me/memory` | Part 3 | yes |
| `tests/` four or more offline tests: stream, scope, lifetime, deletion | Parts 2 and 3 | yes |
| `docs/delegation-log.md`, one new entry | Part 3 | yes |
| tag `lab6-streaming-state` on `main` | Checkpoint 2 | yes |
| two AGENTS.md lines · Week 6 journal entry | Studio | yes |
| `POST /voice` and hold-to-talk | Stretch | no |

## Folder map of this lab

- [HOMEWORK.md](HOMEWORK.md) · what is due, in full: HW2, and where this week's journal entry goes.
- `templates/` · `state-contract.md`, `test_state.py`, `sse-client.html`.
- `examples/` · `state-contract-campuspulse.md`; `campuspulse-state/` (the Week 5 reference plus streaming, the state store, `/me/memory`, the voice path, the page, 122 offline tests, the three demos I run in lab).
- `resources/` · optional, and where the depth is: `streaming-explained.md`, `designing-session-state.md`, `memory-governance.md`, `voice-in-voice-out.md`, `setup-and-troubleshooting.md`.

---

## Homework

No new homework this week. HW2 was released in Lab 5 and is due at the end of Week 7; today's journal entry is part of it. It is listed here in full.

**HW2 · "Tool Contract" · 5 points · individual**
**Due: end of Week 7 · Sunday 8 November 2026, 23:59 (Tbilisi time)**
**Submit: your tool in your team repo through a product pull request, your write-up in `hw2/<your-github-username>/` through its own pull request, both merged to `main`, then fill the submission form (link on Teams)**
**Deliver: one function from your capstone wrapped as an MCP tool with a validated, least-privilege contract; 5 golden cases including one adversarial input, run in CI so a failure blocks the merge; your Pattern Journal for Weeks 5, 6 and 7**
**Full brief, folder layout and checklist: `Lab-5/HOMEWORK.md`**

```
your team repo
├── src/                                   your tool: contract, function, MCP registration (product pull request)
├── evals/tools/<your-github-username>.yaml   5 golden cases, runs in CI through tests/test_tool_golden.py
└── hw2/<your-github-username>/
    ├── contract.md      one page: your tool contract, with links to the code
    ├── evidence.md      the 5 cases with results, one red CI run that blocked a merge, one green run
    └── journal.md       Pattern Journal entries for Weeks 5, 6 and 7
```

Full notes: [HOMEWORK.md](HOMEWORK.md) · every deadline in the course: `SUBMISSIONS.md` at the repo root.
