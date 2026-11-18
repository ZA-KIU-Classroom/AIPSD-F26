# Guardrails: budgets, timeouts, retries

*Optional reading for Lab 7, Parts 2 and 3. About 12 minutes.*

## The idea in plain language

A loop that calls a model can go wrong in four boring ways before it does anything dramatic: it never finishes, one call hangs, one call fails for a moment, or it repeats itself. Each has a small, separate fix. None of the fixes is a prompt.

| Failure | Guardrail | In the reference |
|---|---|---|
| never says "done" | a **budget** for the run: steps, seconds, dollars | `Budget.exceeded()`, checked before every model turn |
| a call hangs | a **timeout** per model call | `call_timeout = 12.0` |
| a call fails for a moment | a **retry with backoff**, only for retryable errors | `call_model()` |
| repeats the same call | a **duplicate refusal** | the `asked` set in `run()` |

## Why it matters in production

**Budgets.** Cost per turn grows, because every turn re-sends the conversation. So a step limit alone does not bound money, and neither bounds time when a call hangs. Three budgets, because there are three things to run out of. Pick numbers from evidence: the reference's honest runs take 3 to 4 turns, so 6 leaves room for one repair and one extra look; two cents is about thirty chat turns.

**Timeouts.** The OpenAI Python SDK's default timeout is 10 minutes, and it retries twice by itself. Those are sensible defaults for a script. Inside a loop with a 45-second budget, one hung call outlasts the whole budget thirteen times. Set a timeout per call, and when you do, turn the SDK's retries off, so there is one retry layer and you can see it:

```python
api = client.with_options(timeout=timeout, max_retries=0)
```

**Retries.** A retry is a bet that the same request will succeed a moment later. That is true for a timeout, a dropped connection, a 429 (rate limit) and a 5xx (the provider's fault). It is false for a 400 (your request is malformed), a 401 (your key is wrong) or a validation error: those will fail identically every time, and retrying them is paying three times for the same error.

Wait between attempts, and wait longer each time: 0.5 s, 1 s, 2 s. Add a little randomness (jitter). When a provider has a bad minute, thousands of clients fail together; without jitter they all come back on the same tick and push it over again.

Two layers of retries multiply. Three attempts of yours on top of the SDK's three is up to nine calls for one turn. This is the most common reason a "small" incident produces a large bill.

**Writes and retries.** If a write times out, you do not know whether it happened. Retrying is safe only if the operation is *idempotent*: doing it twice has the same effect as doing it once. Week 5's `rsvp` is (the second call returns "already registered"). A payment is not, unless you send an idempotency key the server uses to recognise a repeat. In the reference the loop never retries a tool at all: reads fail back to the model as observations, and writes run only after a human yes.

## A worked example on CampusPulse

Run `python -m demo.agent_demo flaky`, with `src/agent.py` open.

**1.** `run()` reaches `call_model()`. Attempt 1 calls the model with `timeout=12.0`. The demo's model raises `TimeoutError`.

**2.** `TimeoutError` is in `RETRYABLE`, and this is attempt 1 of 3, so we sleep `0.5 * 2**0` plus up to 0.25 s of jitter. The demo prints the wait.

**3.** Attempt 2 fails the same way. We sleep about 1 second.

**4.** Attempt 3 answers. `call_model()` returns, and the loop continues. The student saw nothing.

**5.** In the second half of the demo the model never answers. On attempt 3, `call_model()` raises `ModelUnavailable`. `run()` catches exactly that, and returns `status: "stopped"`, `stop: "model unavailable (TimeoutError, 3 attempts)"`. The student reads: "I stopped before finishing… Nothing was booked." The RSVP file is untouched.

Now `python -m demo.agent_demo runaway`. The model always asks for one more read with a slightly different argument, so the duplicate check never fires. With no budget it reaches turn 40 and 29 cents. With the default budget, `exceeded()` returns `"step budget (6)"` at the top of the seventh turn, and the run ends having spent about a cent.

The tests that pin this down are in `tests/test_agent.py`: `test_step_budget_stops_a_loop_that_never_finishes`, `test_cost_budget_stops_the_loop`, `test_a_timeout_is_retried_with_backoff_and_then_succeeds` (it passes a fake `sleep` and checks the two waits), `test_a_dead_model_stops_the_run_cleanly`, `test_a_bad_request_is_not_retried`.

## Common mistakes and how to spot them

- **`except Exception: retry`.** Catches 400s and your own bugs. Spot it: a typo in a schema produces three identical errors in the log.
- **No jitter.** Works in the lab, fails in a real incident.
- **Real `time.sleep` in tests.** Your suite gets slow, so people stop running it. Pass `sleep` as a parameter and give tests a fake.
- **The budget checked after the model call.** You pay for the turn that breaks the budget. Check at the top.
- **A budget stop with no message.** The user sees a spinner, then nothing. Always return the reason and a sentence.
- **Budget numbers with no source.** Write where they came from (decision record 0008 does) and what would make you change them.
- **Retrying the tool that writes.** Ask: did the first attempt happen? If you cannot say, and the tool is not idempotent, do not retry.

## Check yourself

1. Your loop has `max_steps = 6` and nothing else. Name two ways it can still cost far more, or take far longer, than you intended.
2. Which of these do you retry, and why: 429, 400, a timeout on `list_events`, a timeout on a payment?
3. Why does the reference set `max_retries=0` on the SDK when it passes its own timeout?
