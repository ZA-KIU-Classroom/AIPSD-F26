# Lab 5 · The Tool Contract · `lab5-tools-mcp`

**Week 5 · live online · 2 hours · pattern: Tool Contract**
You leave with one capability in your capstone that a model can ask to use, behind a contract your code enforces, served through function calling and through an MCP server, with a log line for every call.

| What you hand in today | Where | When | Graded? |
|---|---|---|---|
| The tag `lab5-tools-mcp` on `main` (tool, loop, MCP server and tests merged) | your team repo | end of lab | not on its own: it is what HW2 builds on, and evidence for the Repository Review |
| **Quiz 1** | the course quiz platform | **Tuesday 27 October, 23:59** | 5 points · see [HOMEWORK.md](HOMEWORK.md) |
| **HW2 · "Tool Contract"** | your team repo + form | **Sunday 8 November, 23:59** | 5 points (individual) · see [HOMEWORK.md](HOMEWORK.md) |

**Before lab (10 minutes, right after the lecture):** pull your team repo at `lab4-rag`. Run `pip install "mcp>=2.3"` and check `python -c "import mcp.server; print('ok')"`. Export the team OpenRouter key as in Lab 4. **Pick one capability your users need that the model should be able to ask for**: look something up live, or do something (book, save, send). One per team today; each of you picks your own for HW2.

**Lab clock:** 0:00 recap and questions · 0:15 my live demo (three bad tool calls run by a naive executor, then the same calls through a contract) · 0:30 Parts 1 to 3 · 1:35 studio: HW2 kickoff · 1:48 homework walk-through · 1:55 next week.

---

## Part 1 · Write the contract · 10 min

No code before a contract. Same rule as every spec since Week 2.

1. **Copy `templates/tool-contract.md` to `docs/tool-contracts.md`** and fill one section for today's tool: its name, one sentence on what it does, whether it reads, adds, changes or deletes, every input with its type and constraint, the result, each expected failure with the message the model will read, who is offered it, where the caller's identity comes from, and what it must never do.
2. **Check the last three rows twice.** If your tool needs to know who is calling, that comes from your app's session, never from an argument. If it deletes, stop and ask me before Part 2.

The CampusPulse version, filled in for `check_room` and `rsvp`: `examples/tool-contract-campuspulse.md`. Two minutes to read.

**Done when:** `docs/tool-contracts.md` is committed on a branch. Stuck on naming, granularity or error messages? `resources/designing-tool-contracts.md`.

## Part 2 · Contract, tool, and the loop · 30 min

Same workflow as every slice (`docs/TEAM-REPO.md` section 4): issue, branch `slice-<issue>-<two-words>`, pull request, a teammate approves and squash-merges.

Delegate at **rung 3: the agent writes the code, you read every line of the diff.** Point it at exactly three things: `docs/tool-contracts.md`, your `AGENTS.md`, and `examples/campuspulse-tools/` in this lab folder. Ask for a plan first. Quote these two lines in the task prompt, because agents skip them most: *arguments are validated against the contract before the tool runs; a failure goes back to the model as an error and nothing runs* and *the caller's identity is never a tool argument*.

What must be in the diff. Check each one yourself:

| Must have | Why | If stuck |
|---|---|---|
| `complete_tools()` added to your Lab 4 `llm.py`, through the same client, logging usage. Nothing else in the file changes; Lab 3 and Lab 4 tests stay green | one logged path for every model call | `examples/campuspulse-tools/src/llm.py` · `resources/function-calling-explained.md` |
| A contract class with `extra="forbid"`; every string has a pattern or a fixed set of values, every number has bounds; **no user, student or account field** | the schema the model sees and the check your code runs are one class | `src/contracts.py` |
| The tool returns a pydantic result; failures you expect raise one exception type with a message written for the model | the model can recover; a bug still crashes loudly | `src/tools.py` · `ToolFailure` |
| `call_tool()` with the three gates: offered to this caller? arguments valid? identity from you? It never raises, returns a dict with `ok`, `error` and `result` like the example (the HW2 golden runner reads those keys), and writes **one log line per call** | the log entry half of the Evidence Rule, for actions | `src/act.py` |
| A loop with a round budget that sends errors back to the model, and echoes `reasoning_details` | bounded repair; Gemini 3 rejects the next call without it | `act()` and `as_assistant()` |
| An endpoint (or your app's equivalent) where the caller comes from the request, not from the model | stand-in for real sign-in until Week 12 | `src/app.py` · `POST /act` |
| At least 4 offline tests: a valid call runs; invalid arguments never reach the tool; a tool not offered never runs; the model cannot set identity | the test half of the Evidence Rule | `tests/test_act.py` |
| One entry in `docs/delegation-log.md` | same format as Lab 2 | `Lab-2/templates/delegation-log.md` |

**✅ Checkpoint 1 (around 1:10):** with the real model, ask one question that makes it call your tool, and send one bad call (wrong type, or a tool the caller was not offered). Show me the answer and both lines in `logs/tools.jsonl`. Two or three of you will screen-share.

## Part 3 · The MCP server · 20 min

1. **Add `mcp>=2.3` to `requirements.txt`.** SDK 2.x calls the server class `MCPServer`; tutorials that say `FastMCP` are for version 1.
2. **Create `src/mcp_server.py`** with your tool. Use the type aliases from your contract module in the signature, so both doors share one schema. Add annotations (`read_only_hint`, `destructive_hint`). Turn your expected failures into `ToolError`. If the tool needs the caller, fill that parameter with `Resolve(...)`, never from the arguments. Model: `examples/campuspulse-tools/src/mcp_server.py`.
3. **Copy the both-doors test** from `examples/campuspulse-tools/tests/test_mcp.py` into `tests/test_mcp.py`, plus one call through `Client(mcp)`. It must pass offline.
4. **Connect a host.** From your repo root: `claude mcp add --env <YOUR_IDENTITY_VAR>=<test-user> --transport stdio <name> -- python -m src.mcp_server`, then `/mcp` in Claude Code. Cursor and VS Code: `resources/connecting-mcp-hosts.md`. Ask the host one question that uses your tool. Paste the question and its answer into your pull request description.
5. **Repo keeper:** copy `templates/test_tool_golden.py` to `tests/` and create `evals/tools/` with a `.gitkeep`. From now on, every file in `evals/tools/` runs in CI. HW2 uses it.

**✅ Checkpoint 2 (around 1:35):** `pytest` green including the both-doors test, a host answering through your server, pull request merged. Then tag, on `main`:

```
git switch main && git pull
git tag lab5-tools-mcp && git push origin lab5-tools-mcp
```

Server not connecting? `resources/connecting-mcp-hosts.md` has the five usual causes.

## Part 4 · Studio · 13 min

- **HW2 owners.** Add a short table to the bottom of `docs/tool-contracts.md`: each member and the capstone function they will wrap for HW2. **No two members wrap the same function.** Not enough functions? Talk to me now, not on Sunday.
- **AGENTS.md.** Add two lines under Never: *never put a user, student or account id in a tool's arguments* and *never add a tool that deletes or sends without asking first*.
- **Journal.** Your Week 5 entry in `docs/journal/<your-github-username>.md`: the pattern, one place you used it today, one thing you would do differently. It is the first entry in your HW2 `journal.md`.

Last 7 minutes: [HOMEWORK.md](HOMEWORK.md) on screen, line by line.

**Stretch:** wrap your Week 4 `answer()` as a read-only tool, so one conversation can look something up in your documents and then act on it. Write its contract first.

---

## What your repo has at the end of Lab 5

| Path | Created in | Required |
|---|---|---|
| `docs/tool-contracts.md` | Part 1 | yes |
| `src/` contract module, the tool, `call_tool()` and the loop, `complete_tools()` in `llm.py`, an endpoint | Part 2 | yes |
| `tests/` four or more offline tests for the gates | Part 2 | yes |
| `docs/delegation-log.md`, one new entry | Part 2 | yes |
| `src/mcp_server.py` · `tests/test_mcp.py` · `mcp>=2.3` in `requirements.txt` | Part 3 | yes |
| `tests/test_tool_golden.py` · `evals/tools/` | Part 3 (repo keeper) | yes |
| tag `lab5-tools-mcp` on `main` | Checkpoint 2 | yes |
| HW2 owners table · two AGENTS.md lines · Week 5 journal entry | Studio | yes |

## Folder map of this lab

- [HOMEWORK.md](HOMEWORK.md) · what is due, in full, including the HW2 brief and checklist.
- `templates/` · `tool-contract.md`, `tool-golden.yaml`, `test_tool_golden.py`.
- `examples/` · `tool-contract-campuspulse.md`; `campuspulse-tools/` (the Week 4 reference plus four tools, the loop, an MCP server, 99 offline tests, the demo I run in lab); `hw2-example/` (a filled HW2 write-up folder).
- `resources/` · optional, and where the depth is: `function-calling-explained.md`, `designing-tool-contracts.md`, `mcp-in-practice.md`, `least-privilege-for-tools.md`, `connecting-mcp-hosts.md`.

---

## Homework

Quiz 1 is due before the Week 6 lab. HW2 is released today and due at the end of Week 7. Both are listed here in full.

**Quiz 1 · individual · 5 points · covers Weeks 1 to 5**
**Opens on the course quiz platform after the Week 5 lecture (link on Teams) · Due: Tuesday 27 October 2026, 23:59 (Tbilisi time), before the Week 6 lab · untimed**
**Five written questions. The course slides are available inside the quiz. You may not use ChatGPT, Claude, Gemini, or any other AI tool to write or rewrite your answers. Every answer is run through Turnitin: if your answers do not meet the threshold for original work, your quiz mark is zero.**

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
