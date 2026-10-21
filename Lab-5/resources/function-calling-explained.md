# Function calling, explained

*Optional reference for Lab 5, Part 2. About 1,200 words. Read it if the round trip, the message shapes, or the loop in `src/act.py` feel like magic.*

## 1 · The idea in plain language

A language model can only produce text. Function calling is an agreement about one special kind of text: instead of writing an answer, the model may write a structured request that says "please run this function, with these arguments". Your code reads the request, decides whether to run anything, runs it if appropriate, and sends the result back as another message. The model then continues, usually by writing the answer the person sees.

So "the model calls a tool" is a figure of speech. The model never calls anything. It asks. Your code calls. Every safety property in this lab depends on keeping that sentence true.

The provider (Google, OpenAI, Anthropic, or OpenRouter in front of them) adds two things to make this reliable. First, a place in the request to describe your tools: a list of names, descriptions and JSON Schemas. Second, a place in the response for the request: `tool_calls`, a list of `{id, name, arguments}`, where `arguments` is a JSON string. The model was trained on millions of examples of this format, so it is good at it. Good, not perfect.

## 2 · Why it matters in production

Before function calling became standard, teams parsed free text: "if the reply contains BOOK ROOM, extract the room code with a regex". It broke constantly. A model that wrote "I would book room B204 for you" triggered a booking. Function calling replaced that guesswork with a typed channel.

But the typed channel moved the risk rather than removing it. The model now writes requests that look official. Two failure patterns show up in every post-incident review of tool-using systems:

- **Trusting the shape.** The arguments parse as JSON, so the code runs them. Then a model, confused by a long conversation or nudged by text it read, sends a perfectly shaped request for the wrong thing. In July 2025 Replit's coding agent ran destructive commands on SaaStr founder Jason Lemkin's production database during a code freeze; every command was well formed. Replit's fixes were all about what the agent could reach, not about parsing.
- **Losing the loop.** The code runs one tool call and returns the result to the user directly, so the model never sees errors and cannot correct itself. Or the code loops forever, retrying a call the model keeps getting wrong, and burns the monthly budget in an afternoon.

## 3 · Worked example: one CampusPulse question, message by message

A signed-in student, `s123`, asks "Save me a seat at Open Build Night". Here is what `act()` in `src/act.py` sends and receives, simplified.

**Turn 1, request.** `tools_for("s123")` returns all four tools, so all four schemas go in `tools`.

```json
{"model": "google/gemini-3.8-flash",
 "messages": [
   {"role": "system", "content": "You are CampusPulse ... Today is 2026-10-21. ..."},
   {"role": "user", "content": "Save me a seat at Open Build Night"}],
 "tools": [ {"type": "function", "function": {"name": "check_room", ...}}, ... ],
 "tool_choice": "auto", "temperature": 0}
```

**Turn 1, response.** The model does not know the event id, so it asks for the list first.

```json
{"content": null,
 "tool_calls": [{"id": "call_a1", "name": "list_events",
                 "arguments": "{\"from_date\": \"2026-10-21\", \"days\": 7}"}]}
```

Our code runs `call_tool()`: offered, valid, run. It appends two messages: the model's own turn (via `as_assistant`, with any `reasoning_details` returned unmodified) and a tool message with the result.

```json
{"role": "tool", "tool_call_id": "call_a1",
 "content": "{\"events\": [{\"id\": \"ev-201\", \"title\": \"Open Build Night\", \"seats_left\": 4, ...}, ...]}"}
```

**Turn 2.** Same tools, longer conversation. The model now asks for `rsvp` with `{"event_id": "ev-201"}`. Our code runs it with `student="s123"` taken from the request, not from the arguments. Result: `{"status": "added", "seats_left": 3}`.

**Turn 3.** No tool call. The model writes: "Done: you're registered for Open Build Night on Thursday 22 October at 18:00 in B204. 3 seats left." `act()` returns it.

Three model calls, two tool runs, two lines in `logs/tools.jsonl`, three lines in `logs/usage.jsonl`. With four tools the schemas are about 625 tokens on each call, so at $0.75 per million input tokens the whole exchange costs well under a cent.

## 4 · Details that bite

- **`arguments` is a string, not an object.** You must parse it. Parse and validate in one step (`model_validate_json`), so a half-written JSON string becomes a clean validation error, not a crash.
- **Several calls in one turn.** A model may request two tools at once ("check B204 and A112"). Run each through the same gates, append one tool message per call, each with its own `tool_call_id`. The ids are how the model matches results to requests.
- **`tool_choice`.** `"auto"` lets the model decide. You can force a specific tool, which is useful in tests and in extraction pipelines, and you can forbid tools for a turn with `"none"`.
- **Reasoning state.** Gemini 3-class models return `reasoning_details` with a tool call. Send it back unmodified in the next request, or the provider rejects the call. OpenRouter documents this as preserving reasoning blocks; other models ignore the field.
- **Every call carries every schema.** Twenty tools means twenty schemas on every call, and a harder choice for the model. Offer the few this caller needs.
- **Errors are content.** Returning `{"error": "..."}` as the tool message is normal. The model reads it and either fixes the arguments or explains the problem. That is the repair loop on Week 5 slide 14.

## 5 · Common mistakes and how to spot them

| Mistake | Symptom | Fix |
|---|---|---|
| Executing `json.loads(arguments)` straight into the function | a `TypeError` or `KeyError` reaches the user as a 500 | validate against the contract first (`call_tool` gate 2) |
| Returning the tool result to the user instead of the model | the user sees raw JSON; the model never recovers from errors | always append the tool message and call the model again |
| No round budget | one stubborn question makes dozens of calls | `MAX_ROUNDS`, and a "stopped" reply that says nothing else changed |
| Dropping the assistant turn before the tool message | provider error about a tool message with no matching call | append `as_assistant(msg)` first, then the tool messages |
| Offering every tool to every caller | a visitor's model asks for `rsvp` | `tools_for(caller)` before the first call |

## 6 · Check yourself

1. The model replies with `content: "I'll book that for you!"` and an empty `tool_calls`. What does `act()` do, and has anything been booked?
2. Why does `call_tool()` look the tool up in `allowed` instead of in `TOOLS`?
3. A teammate removes `as_assistant(msg)` "because the model already knows what it said". With Gemini 3, what breaks, and on which turn?

*Answers: (1) It returns that text as the answer; nothing was booked, because nothing ran. The reply is misleading. That is why the system prompt says never to invent a tool result, and why the Week 4 habit of checking the answer against the evidence (here, `reply.calls`) still applies. (2) A tool that exists but was not offered to this caller must not run, even if the model names it. (3) The second model call, the one after the first tool result: the provider rejects it because the reasoning state is missing.*
