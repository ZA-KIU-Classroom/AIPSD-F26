# Gates, logs and the ladder

*Optional reading for Lab 2, Part 3. About 10 minutes.*

## The idea in plain language

On the Autonomy Ladder, Lab 2 lives on rung 3: supervised task delegation. You hand an agent a task across many files, and you supervise. "Supervise" has a precise meaning in this course: the work passes through **gates**, points where nothing continues until a check passes.

Lab 2 uses three:

| Gate | Who checks | What it catches | Cost of the check |
|---|---|---|---|
| 1 · Plan approved before any file is written | you | wrong approach, missing test, scope creep | one minute |
| 2 · Tests read first, then run | you, then the machine | weak or edited tests, broken criteria | a few minutes |
| 3 · CI green before merge, teammate merges | the machine, then a second person | anything you forgot to run; your own blind spots | zero after setup |

Each gate is cheaper than the damage it prevents, and each catches a different kind of mistake. That is why there are three and not one.

The **delegation log** is the gates' memory. After each delegation that mattered, two minutes: what you handed over, what came back wrong, which gate caught it, what you changed. Over a few weeks it tells you where your agent is reliable and where it is not. That is how you earn the right to climb the ladder: with evidence, not optimism.

## Why it matters in production

In July 2025, SaaStr founder Jason Lemkin was building an app with Replit's AI agent. He had told it, repeatedly and in capital letters, not to change anything without permission, and declared a code freeze. The agent ran destructive commands anyway and deleted his production database. It then told him a rollback was impossible, which turned out to be false. Replit acknowledged the failure publicly.

Look at it through this guide. The instructions were clear; they were in the chat, which is guidance, not a gate. The agent had permission to act on production directly, so nothing stood between its decision and the damage. No plan approval, no review of the command, no separation between the environment it was experimenting in and the one that mattered. It was working at rung 4 or 5 of autonomy with rung 1 verification.

Our gates are small versions of the fix. The agent works on a branch, never on `main`. It proposes a plan before touching files. A human reads the change. The machine re-runs the tests. A second person merges. None of those depend on the agent remembering an instruction.

## Worked example: one CampusPulse slice through all three gates

**The slice:** AC2 and AC3 from spec v1, the events endpoint and its error case.

**Gate 1 · the plan.** The agent proposes: add `GET /events`, filter by week, add tests. You check it against AC2 and AC3 and find two gaps: nothing about the confirmed-only rule, and no test for the 422 case. You reply: "Add a status filter per AC2 and a test for week 54 per AC3. Then proceed." One minute. Without this gate, you would have found both gaps in the diff, after the code existed.

**Gate 2 · tests first.** The agent finishes and reports green. You open `tests/test_events.py` before `src/app.py`. There are four tests, one per behavior, and the week 39 test names exact event ids. Nothing weakened. Then you run `pytest tests/test_events.py -q` yourself: `4 passed`. Now the code review can be quick, because the tests are strong.

**Gate 3 · CI and a second person.** You push `slice-4-events-endpoint` and open a pull request that says `Closes #4`. The template makes you tick only what you did. GitHub Actions runs `pytest -q` on a clean machine: green. Your teammate reads the diff, asks one question about the error message, and merges.

**The log.** Entry written in two minutes: the plan gaps you caught at gate 1, nothing wrong at gates 2 and 3, and what you checked. "Nothing went wrong" is a valid entry when it says what you verified.

**Climbing the ladder, later.** After a few slices, your log might show the agent never breaks the error shape but often misses date handling. That is data. You might let it run simple CRUD slices with less plan scrutiny, and keep a line-by-line review on anything with dates. That is rung placement based on evidence, which is the question the whole course keeps asking: what did I delegate, and how do I verify it?

## Common mistakes

- **Skipping the plan because the task looks small.** Small tasks are where scope creep feels harmless.
- **Letting the agent work on `main`.** A branch costs nothing and makes every change reviewable.
- **The same person delegates and merges.** You will approve what you expected to see.
- **Logging only failures.** Then your log says your agent is terrible. Log what you checked on the clean runs too.
- **Logging and never reading the log.** Once a week, look for repeats. A repeat becomes an AGENTS.md rule or a test.
- **Treating CI as the only gate.** CI runs the tests you have. It cannot notice a test that should exist and does not.

## Check yourself

1. Which of the three gates would have caught the Replit incident earliest, if the agent had been set up the way Lab 2 sets it up?
2. Your plan check always passes and your diffs always need fixes. What does that tell you about your plan check?
3. Write the delegation log line for a slice where nothing went wrong. What makes it useful rather than empty?

*Answers to discuss in lab: (1) working on a branch with no direct access to production prevents the damage outright; of the three gates, plan approval catches it first, because destructive steps appear in the plan; (2) it is too shallow: check the plan against each acceptance criterion, including error cases, not just its general shape; (3) name what you verified, e.g. "read 3 tests first, each maps to AC2/AC3; ran pytest; checked requirements.txt unchanged," so a reader knows the result was checked, not assumed.*
