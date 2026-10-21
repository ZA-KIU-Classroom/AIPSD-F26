# Designing tool contracts

*Optional reference for Lab 5, Part 1 and HW2. About 1,250 words. Read it before you fill `templates/tool-contract.md`, or when your tool keeps getting called with the wrong arguments.*

## 1 · The idea in plain language

A tool contract is the promise between three parties: the model that asks, your code that runs, and the person who reviews it later. It says what the tool is called, what it does, exactly which inputs it accepts, what it returns, how it fails, and who may use it. In this course the contract is not a document that describes the code. It is code: a pydantic class whose JSON Schema is what the model sees and whose validation is what your code enforces. The markdown file you write in Part 1 is the review copy of that class.

Four decisions make or break a contract: the name, the description, the input types, and the failure messages. Effect and permissions get their own guide (`least-privilege-for-tools.md`).

## 2 · Why it matters in production

The model chooses tools by reading names and descriptions, and fills arguments by reading types and descriptions. Everything it knows about your tool is in the schema. When teams report that "the model keeps calling the wrong tool" or "keeps sending dates in the wrong format", the cause is almost always the contract, not the model.

Picture a support assistant with two tools, `get_order` and `get_orders`, whose descriptions differ by one word. The model has nothing else to go on, so it picks between them inconsistently, and the logs fill with calls to the wrong one. Renaming them `find_order_by_number` and `list_recent_orders_for_customer`, and saying in each description when not to use it, fixes it without touching the model. Names are interface design.

## 3 · Worked example: `check_room`, decision by decision

**Name.** A verb and an object, specific enough to be unambiguous among all your tools: `check_room`, not `rooms` or `room_tool`. If a name could describe two of your tools, it describes neither. Avoid names that promise more than the tool does: CampusPulse's calendar tool is `make_calendar_file`, not `add_to_calendar`, because it does not add anything to anyone's calendar.

**Description.** One or two sentences, written for a reader that has never seen your app: what it does, under which rules, and whether it changes anything. CampusPulse: "Is a room free for this slot, under KIU's booking rules? Reads only." The words "Reads only" are there for the model and for the human reviewing the schema. If there is a common wrong use, say so: "Use list_events to find an event id first."

**Inputs.** Make every argument as narrow as the domain allows.

| Instead of | Use | Why |
|---|---|---|
| `room: str` | `Literal["A015", "A112", "B204"]` | the model sees an enum; anything else fails before your code runs |
| `date: str` | `date` | pydantic parses it, so `2026-02-30` and "next Thursday" fail |
| `start: str` | a pattern `^([01]\d|2[0-3]):[0-5]\d$` | "6pm" fails; the description says HH:MM |
| `minutes: int` | `int` with `ge=15, le=240` | no 0, no 600 |
| `query: str` | `str` with `max_length=300` | a 50,000-character "query" is an attack or a bug |

Two rules hold for every contract in this course. `extra="forbid"`, so an argument you did not ask for is an error rather than something silently ignored. And no identity field: no `user_id`, `student_id`, `account`, `role`. Who is calling comes from the session.

Put the constraints in shared type aliases (`RoomCode`, `Day`, `Clock` in `src/contracts.py`). The function-calling door and the MCP door both use them, so the two schemas cannot disagree. `tests/test_mcp.py` proves it.

**Result.** Return a typed model with only what the model needs to answer. `RoomStatus` returns `free`, `clashes` and `rules` because those are what a student needs to hear. It does not return booking ids or internal flags. Every field you return is text the model reads and might repeat to the user.

**Failures.** Separate three cases:

1. *Invalid arguments.* The contract rejects them before your function runs. The message names the field and the rule.
2. *Expected refusals from the world.* The event is full, cancelled, unknown. Raise your one failure type (`ToolFailure`) with a message that says what happened and what to do next.
3. *Bugs.* Anything else. Let it crash, log it, and show the model nothing but "error executing tool". Never put a stack trace, a table name or a file path in a message the model reads.

Some answers are not failures at all. A room that is not free on Sunday is a successful `check_room` call with `free: false` and the rule in `rules`. Reserve failures for "the tool could not do its job", not "the answer is no".

**Idempotency.** For anything that writes, decide what a second identical call does. `rsvp` returns "already registered" and changes nothing. Models retry, networks retry, users double-click: a write tool that is not idempotent will eventually double-book.

## 4 · Granularity: one tool or three?

Two pulls in opposite directions. Fewer, broader tools mean shorter schemas and fewer wrong choices. Narrower tools mean smaller permissions and simpler validation. In practice:

- Split by **effect**: never put a read and a write behind one tool with a `mode` argument. `manage_rsvp(action="add"|"remove")` makes "remove" reachable from every conversation that can "add".
- Split by **caller**: if visitors may use part of it and only signed-in users the rest, that is two tools.
- Merge by **shape**: `check_room_a015`, `check_room_a112` and `check_room_b204` are one tool with an enum.
- Never build a general escape hatch: `run_sql(query)`, `http_get(url)`, `shell(command)`. Each one is every tool at once, with the widest possible permission.

## 5 · Common mistakes and how to spot them

| Mistake | How you spot it | Fix |
|---|---|---|
| Vague description | refused calls cluster on one tool in `logs/tools.jsonl` | say what it does, the format, and when not to use it |
| Free-text arguments where a set would do | odd values in the log ("Lab B204", "b204 ") | `Literal`, or a pattern |
| Identity as an argument | a `user_id` property in the schema | remove it; pass it from the session or `Resolve(...)` |
| Error text from an exception | the model repeats a Python error to the user | catch expected failures, write the message yourself |
| A tool that returns everything | long tool messages, high token counts in `usage.jsonl` | return only what answers the question |
| A schema written by hand next to the code | the two drift; the both-doors test fails | generate it from the class |

## 6 · Check yourself

1. A teammate proposes `update_event(event_id, field, value)` so the model can fix typos in event titles. What is wrong with that contract, and what would you build instead?
2. Your `search_menu(query: str)` tool is called with a 12,000-character query that contains instructions. Which line of the contract should have stopped it, and what should the model read back?
3. Why does `check_room` return `free: false` with a rule for a Sunday instead of raising `ToolFailure("Sunday")`?

*Answers: (1) `field` and `value` make every field of every event writable, including capacity and room, by any conversation; it is a general escape hatch. Build `suggest_title_fix(event_id, new_title)` that records a suggestion for a club lead to approve, with `new_title` length-bounded. (2) `query` needs `max_length`; the model reads "invalid arguments: query: String should have at most 300 characters". (3) The tool did its job: it found out the room is not available and why. A failure would hide the reason, and the model needs the rule to explain it.*
