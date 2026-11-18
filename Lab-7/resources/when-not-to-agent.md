# When not to build an agent (and when several pay)

*Optional reading for Lab 7, Part 1. About 12 minutes.*

## The idea in plain language

"Agent" is one step on a staircase, and each step up costs more money, more latency and more ways to fail. Climb only as far as the problem makes you.

| Step | What it is | Choose it when | CampusPulse |
|---|---|---|---|
| One prompt | question in, answer out | nothing needs doing | explain a regulation |
| One prompt with tools | the user names the action; the model fills the arguments | one action, asked for | "RSVP me to ev-201" (Week 5) |
| A workflow | fixed steps in code; a model works inside a step | you can list the steps before any input arrives | poster → extract → check → queue (Week 3) |
| An agent loop | the model chooses the steps | the number or order of steps depends on what a step finds | "plan my week, and swap anything that clashes" |
| Several agents | loops that call loops | the work splits into independent, valuable pieces | not in CampusPulse |

Three questions place a feature:

1. **Can I write the steps down now?** Yes: it is a workflow. Write it as code.
2. **Does the number or order of steps depend on what is found along the way?** Yes: a loop earns its cost.
3. **Does any step cost someone something if it is wrong?** Then it gets a gate, at whatever level it sits.

## Why it matters in production

A loop is the most expensive and least predictable way to do something a script could do. It takes several model turns where a workflow takes one, each turn re-sends a growing conversation, and it adds failure modes a script does not have: it can wander, repeat, stop early, or summarise something it did not do. All of that is worth paying for when the goal is open-ended, and wasted when it is not.

The teams that publish most about building agents open with the same advice: find the simplest solution that works, and add autonomy only when you can show it helps. Many systems called agents in production are workflows with one model-driven step.

## A worked example: "plan my week", built twice

**As a workflow (about 30 lines).**

1. Code calls `list_events(today, 7)`.
2. Code keeps events whose tags match `memory.interests(student)`.
3. Code drops events where `class_clash()` is true, seats are 0, or the student is already registered. (These are the checks `rsvp_preview()` already makes.)
4. One model turn writes a friendly two-sentence summary of what was kept and what was dropped.
5. The kept events go to the same gate: `put_plan()`, the card, `confirm()`.

**As the loop** (`src/agent.py`, about 180 lines): the model decides to list events, decides which to recommend, reads refusals, and writes the summary.

| | Workflow | Loop |
|---|---|---|
| Model turns | 1 | 3 to 4 |
| Input tokens | about 700 | about 5,000 |
| Who picks the events | code | the model, then code checks |
| Ways to fail | a wrong tag in the data | loops, budgets, repeats, an overstated summary |
| Tests | ordinary unit tests | scripted models, budget tests, a trace |
| "…swap the clash for something similar" | needs new code | handled: it reads the refusal and looks again |
| "…keep Thursday free, I have an exam" | needs new code | handled: the goal is a sentence |

For the fixed goal the workflow wins on every row that has a number. The loop wins the last two rows: goals nobody anticipated. That is the only thing autonomy buys. If your product's users will not ask for those rows, build the workflow.

Notice what both versions share: the gate, a cost budget, and a trace. Those are not agent features. A valid Lab 7 is a workflow with a gate on its consequential step, the three template tests, and a contract that says "workflow" and why.

## When several agents pay

A multi-agent system is several loops: typically a lead that splits a goal and workers that each handle a piece in their own context window (orchestrator and workers), or one model that drafts and another that reviews (maker and critic).

Anthropic's write-up of its own multi-agent research system (June 2025) reported token use of roughly 4 times a chat for a single agent and roughly 15 times for the multi-agent system, and was direct about the trade: these systems work largely by spending enough tokens on the problem, so the task has to be worth it.

They tend to pay when:

- the work splits into pieces that do not depend on each other (research across many sources);
- the material is larger than one context window;
- the answer is worth dollars, not fractions of a cent;
- a minute of latency is acceptable.

They tend to burn money when:

- every piece depends on the others (most coding, most planning for one person);
- workers duplicate each other because the split was vague;
- a summary handed between agents drops the detail that mattered;
- the critic's check could have been ten lines of code.

That last point is the cheapest win in this course. CampusPulse has a maker (the model proposing events) and a critic (`class_clash()` and the seat check). The critic is code: zero tokens, the same answer every time, tested with one assert. Use a model as critic only where the judgment is the job, such as relevance or tone, and then give it a round limit and a stop rule.

## Common mistakes and how to spot them

- **"Agent" in the first sentence of the design.** Say the staircase step first. If the steps are fixed, the sentence ends with "workflow".
- **A loop wrapped around one tool call.** That is Week 5 with extra turns. Spot it: every trace has exactly two steps.
- **A model asked to do arithmetic, date maths or overlap checks.** Code does these exactly.
- **A second agent added to fix the first one's mistakes.** First ask whether a validator in code would catch them.
- **No measurement.** "It feels smarter with three agents" is a feeling. Compare cost, latency and golden-set results on the same inputs (Week 11 gives you the harness).

## Check yourself

1. A feature always does the same four steps, and the third sends an email. Which staircase step is it, and where is the gate?
2. In the table above, which rows would have to matter to your users for the loop to be worth roughly seven times the tokens?
3. Name one check in your capstone that a model currently makes and a short function could make instead. What would the function return on failure?
