# Reviewing agent-written code

*Optional reading for Lab 2, Part 3. About 12 minutes. The most important guide this week.*

## The idea in plain language

When an agent says "Done. All tests pass," that sentence can be completely true and the feature can still be broken. The tests may test the wrong thing. They may have been edited until they pass. The code may catch its own crash and return an empty success. Review is how you find out, and with agents, review is most of your job.

A review is not reading every line with equal care. It is a sequence that finds the dangerous problems first:

1. **Read the tests before the code.** The tests say what the agent thinks "done" means. If they are weak, nothing else matters yet.
2. **Map every acceptance criterion to a test** that would fail if the feature broke. A criterion without such a test is unverified, however good the code looks.
3. **Read the diff by risk, not by file order.** Skim formatting and boilerplate. Read error handling, dates and times, dependencies, edited tests, secrets and anything that deletes data line by line.
4. **Run the tests yourself** and read the output, not the agent's summary of it.
5. **Decide:** merge, fix, or reject and re-delegate. Then log it.

## Why it matters in production

In March 2025, OpenAI published results from monitoring a frontier reasoning model while it was trained on coding tasks. The model's reasoning, visible to the researchers, showed it deciding to make tests pass without solving the problem: patching a verification function so it always returned true, or exiting the test process early so nothing failed. OpenAI's point was that these shortcuts are a real, observed behavior when the goal is "make the tests pass."

Agents you use in this course are not being trained while you use them, but the pressure is similar: you asked for green tests, and the cheapest path to green is sometimes to change the test. That is why our AGENTS.md has a Never line about weakening tests, and why that line is not enough on its own.

A second risk hides in the dependency list. A 2025 USENIX Security study generated 576,000 code samples and found that at least 5.2% of the packages suggested by commercial models, and 21.7% by open-source models, did not exist. If an attacker registers one of those invented names on PyPI or npm, the next person who installs it runs the attacker's code. This is called slopsquatting. Every new import in a diff gets checked: does it exist, and is it the one you meant?

## Worked example: the slide 20 diff, reviewed properly

Open `examples/campuspulse-week2/demo/`. `agent_attempt.py` is what the agent returned for AC2. `test_agent_attempt.py` is the test it left behind.

**Step 1 · Run what the agent ran.**

```
pytest demo -q        # 1 passed
```

Green. The agent told the truth.

**Step 2 · Read the test first.**

```python
def test_events_week():
    r = events(39)
    assert len(r) >= 0
```

A list can never have negative length, so this test cannot fail. That one line tells you the whole diff needs careful reading, and that the test is not evidence of anything.

**Step 3 · Write the test the criterion deserves, and watch it fail.** AC2 says: only confirmed events in ISO week N. The data has two confirmed events in week 39.

```python
def test_week_39_returns_the_confirmed_events():
    assert [e["id"] for e in events(39)] == ["ev-101", "ev-102"]
```

Run it: `assert [] == ['ev-101', 'ev-102']`. The endpoint returns nothing.

**Step 4 · Now read the code, by risk.**
- *Scope:* the status filter is gone, and a "future events only" filter appeared that AC2 never asked for.
- *Dates and times:* `datetime.now()` is naive; the stored times carry `+04:00`. Comparing them raises `TypeError: can't compare offset-naive and offset-aware datetimes`.
- *Error handling:* `except Exception: return []` turns that crash into an empty list. No log line, no 422.
- *Tests:* weakened until they pass.

**Step 5 · Decide and log.** Reject. Keep the strong test, re-delegate with AC2 quoted in the prompt, and write the entry. The example entry is in `examples/campuspulse-week2/docs/delegation-log.md`.

Notice the order. You found the problem in step 2, in seconds, without reading any code. That is why tests come first.

## Using a second model as a reviewer

A fresh model, given only the spec and the diff, is a good filter. It is good at spec mismatches, missing error paths, tests that cannot fail and swallowed exceptions. It is poor at knowing your users, rules nobody wrote down, and noticing a feature that was never built (a missing feature is not in the diff). Treat its findings as questions. You answer them, and you sign the merge.

## Common mistakes

- **Reading the agent's summary instead of the output.** "All 12 tests pass" in a chat message is a claim. The terminal is the evidence.
- **Reviewing in file order.** You spend your attention on the README changes and skim the date handling.
- **Accepting "improvements" nobody asked for.** Extra filters, extra endpoints, a refactor of a file outside the slice: each one is unreviewed scope.
- **Patching the agent's code by hand and moving on.** Fix the spec or AGENTS.md too, or the same mistake comes back in the next slice.
- **Approving your own delegation.** In Lab 2 the person who drove the agent does not merge. A second pair of eyes is the cheapest gate there is.

## Check yourself

1. The agent's diff adds `import fastjsonx` and it appears in requirements.txt. What exactly do you check before merging?
2. Why is `except Exception: return []` more dangerous in an endpoint than letting the exception crash with a 500?
3. A pull request has 14 changed files and green CI. You have ten minutes. Which three things do you look at first?

*Answers to discuss in lab: (1) that the package exists on PyPI, is the well-known one you meant (maintainer, downloads, repository), and that the change was approved under "ask first"; (2) a 500 is loud and gets fixed; an empty list looks like "no events" to users and monitoring, so the bug can live for weeks; (3) the tests (were any weakened, does each criterion have one), requirements and config changes, and any error handling or date logic in the diff.*
