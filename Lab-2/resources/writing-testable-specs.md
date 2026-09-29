# Writing testable specs

*Optional reading for Lab 2, Part 1. About 10 minutes.*

## The idea in plain language

A spec is a list of decisions made before the code exists. When you delegate to an agent, every decision you leave out does not disappear. The agent makes it for you, silently, and it picks something plausible. The spec is where you take those decisions back.

Of the six sections, acceptance criteria carry the most weight, because they define "done." One test decides whether a criterion is finished:

> **Could a script decide pass or fail without asking you?**

If the script would need to ask what you meant, the criterion is still a wish. "Fast" is a wish. "p95 of /chat under 4 s with the 30-event shortlist" is a criterion. "Handles bad input" is a wish. "A week outside 1 to 53 returns 422 with `{"error", "field"}`" is a criterion.

Testable criteria do three jobs at once. They tell the agent what to build. They tell the reviewer what to check. And they become your tests: every criterion you write today is a test you will not have to invent in Week 4, when golden sets arrive, or in Week 11, when they gate your CI.

## Why it matters in production

In 1999, NASA lost the Mars Climate Orbiter. One team's ground software reported thruster impulse in pound-force seconds. The navigation team's software expected newton-seconds. The interface specification between them called for metric units, so on paper the decision had been made. Nobody had a check that would fail when the numbers arrived in the wrong unit. Small errors accumulated over months of flight, and the spacecraft came in too low at Mars and was lost.

The lesson for us is not "write a spec." They had one. The lesson is that **a requirement nobody tests is a requirement nobody enforces.** With agents this matters more, not less: an agent reads your spec once, writes code quickly and confidently, and moves on. If the only thing standing between a misread criterion and production is a human skimming a diff, the misread wins some of the time.

## Worked example: CampusPulse spec v0 to v1

Here is a plausible spec v0 for CampusPulse, the kind most teams write first:

```
## Acceptance criteria
- Users can see events for a week
- Bad input is handled
- Answers are fast and cheap
```

Walk it through the test, one line at a time.

**"Users can see events for a week."** A script would ask: which events? All of them, or only confirmed ones? Which week numbering: ISO weeks, or the university's teaching weeks? What does it return when there are none? Rewrite:

> AC2 · GET /events?week=N returns only confirmed events in ISO week N. A week with no events returns an empty list.

Now a test can be written directly: call with 39, expect exactly `ev-101` and `ev-102`. That test is in `examples/campuspulse-week2/tests/test_events.py`.

**"Bad input is handled."** Handled how? Rewrite:

> AC3 · week outside 1..53 returns 422 with {"error": ..., "field": "week"}.

Note what this does to the agent's options. It can no longer return an empty list for a bad week, or a 500, or FastAPI's default error shape. The one behavior you want is the only one that passes.

**"Answers are fast and cheap."** Split it into two measurable criteria, and anchor each to a number you have already measured:

> AC4 · every model call logs model, tokens in/out, cost_usd, latency_ms.
> AC5 · p95 latency of /chat under 4 s with the 30-event shortlist.

AC4 is checked by a unit test that looks for the usage fields. AC5 is checked by the latency log you built in Week 1. Neither needs you in the room.

**Then name the first slice.** For Lab 2, CampusPulse's first slice is AC2 and AC3: one endpoint, four tests, no model call. It is small enough for an agent to finish in minutes and for a human to review properly. AC1 and AC4 come next, as a second slice.

## Common mistakes

- **Criteria that describe effort instead of outcome.** "Use good error handling" is advice. "Returns 422 with a field name" is an outcome.
- **No error criteria at all.** Error paths are exactly where agents improvise, and where an empty success hides a crash. Write at least one.
- **Numbers pulled from the air.** "Under 100 ms" for a model call is not a requirement; it is a wish that will fail on day one. Anchor numbers to something you measured.
- **Criteria that need a person to judge.** "Answers are helpful" cannot be scripted yet. Either make it specific ("names every confirmed event this week, nothing else") or park it for Week 11, when LLM-as-judge arrives.
- **A slice that is really three features.** If your first slice needs more than three criteria, cut it.
- **Forgetting Out of scope.** A helpful agent builds things nobody asked for. The list of what not to build is part of the spec.

## Check yourself

1. Rewrite "The chatbot should understand Georgian" as a criterion a script could check.
2. Your v1 has five criteria and none mention errors. Which gap is the agent most likely to fill with a guess?
3. Why is it useful that AC2 names specific event ids in its test, rather than "returns some events"?

*Answers to discuss in lab: (1) for example, "3 golden questions asked in Georgian are answered in Georgian and name the correct events"; (2) what happens on bad or missing input: expect empty successes, 500s, or a made-up error shape; (3) "some events" passes when the filter is wrong; exact ids fail the moment the confirmed-only rule breaks.*
