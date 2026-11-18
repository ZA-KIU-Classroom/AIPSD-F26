# The agent loop

*Optional reading for Lab 7, Part 2. About 10 minutes.*

## The idea in plain language

An agent is a model using tools in a loop. That is the whole definition. You already have the two ingredients: a model that can ask for a tool (Week 5) and code that decides whether the tool runs (`call_tool()`). The only new thing is the word "loop": after a tool runs, its result goes back to the model, and the model is asked again, "what next?". It keeps going until the model replies with text and no tool call, or until your code stops it.

The loop has four phases, and it helps to say who does each one.

| Phase | What happens | Who does it |
|---|---|---|
| Perceive | read the facts that are true right now | code |
| Reason | given everything so far, pick the next tool, or finish | the model |
| Act | run the tool, or park it if it is consequential | code |
| Observe | hand the result back as a tool message | code |

The model does one of the four. If your design has the model perceiving ("ask it what day it is") or acting ("let it write to the database"), you have given away something code does better.

## Why it matters in production

Two properties of a loop are easy to miss until they hurt.

**The model decides when the loop ends.** A `for` loop over a list ends when the list does. An agent loop ends when a language model chooses to stop asking for tools. Most of the time it does. Sometimes it asks for "one more look" forever, or alternates between two tools. Without a budget, that run ends when your credit does.

**Every turn re-sends everything.** The model has no memory between calls, so turn 3 contains the system prompt, the goal, the calls and results of turns 1 and 2, and only then asks its question. A three-step plan in the reference costs roughly what eight ordinary chat turns cost. In `python -m demo.agent_demo runaway`, turn 40 costs twelve times turn 1, and the run has spent 29 cents without finishing.

A failure story worth knowing: in July 2025 a coding agent, told in capitals to make no more changes during a code freeze, ran destructive commands against a production database after misreading an empty query result as a fault to repair. The model's reasoning was wrong, but that is not the lesson; models are sometimes wrong. The lesson is that between "the model decided" and "the command ran" there was no code at all. The loop below has code there.

## A worked example on CampusPulse

Open `examples/campuspulse-agent/src/agent.py` next to this.

**1. Before the loop.** `run()` filters the tool registry twice: `tools_for(student)` (Week 5: a visitor gets no write tools) and `PLANNER_TOOLS` (this loop gets three of the five). Then `perceive()` reads today's date, the student's interests from the Week 6 store, and their classes. These go into the system prompt as five short lines.

**2. The first turn.** The model sees the prompt and the goal "Plan my week". It replies with one tool call: `list_events(from_date="2026-11-18")`. That is a read, so it runs through `call_tool()` and the events come back as a tool message.

**3. The second turn.** The model now sees the events. It replies with several `rsvp` calls in one turn. Each is consequential (`tool.confirm` is true), so none of them runs. Each goes to `propose()`, which either parks it or refuses it with a reason. The model receives one tool message per call: "added to the plan; NOT booked", or "ev-207 clashes with the student's class…".

**4. The third turn.** The model has nothing left to ask for. It writes two sentences: what it proposed, what it left out, and why. No tool calls, so the loop ends with status `needs_confirmation`.

**5. The trace.** `logs/agent.jsonl` now holds nine lines for this run: three `reason`, five `act`, one `finish`. Run `python -m demo.agent_demo plan` and read them in order.

Notice what the loop cannot do. It cannot call a tool outside its tuple. It cannot run past six turns, 45 seconds or two cents. It cannot return a status that says something was booked, because there is no such status.

## Common mistakes and how to spot them

- **The model call is hard-coded inside the loop.** You then cannot test a model that never finishes, or one that asks for the dangerous tool. Make it a parameter (`llm=`), as the reference does. Spot it: your tests need a network.
- **The assistant's turn is not appended before the tool messages.** The provider rejects the next call with a 400. Use Lab 5's `as_assistant()`.
- **Parallel tool calls answered with one message.** If the model asks for four tools in one turn, it needs four tool messages, each with its own `tool_call_id`.
- **Tool results pasted in whole.** A 6,000-token result is re-sent on every later turn. Return only the fields the next decision needs.
- **No "how to finish" in the prompt.** The model keeps exploring. Say what done looks like: "finish with two or three sentences".
- **A stop that raises.** Hitting the budget is a normal ending. Return a status and a reason, and tell the user in a sentence.

## Check yourself

1. In the planner, which phases are done by code, and what would go wrong if the model did Perceive?
2. A run took 5 turns. Why is its cost more than 5 times the cost of turn 1?
3. The model asks for three tools in a single turn. How many messages do you append before calling the model again, and what must each contain?
