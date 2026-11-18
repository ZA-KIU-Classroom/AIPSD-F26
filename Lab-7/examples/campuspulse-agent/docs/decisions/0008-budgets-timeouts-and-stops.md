# 0008 · Every run has a budget, every model call has a timeout, and stopping is a normal ending

**Context.** A loop that asks a model "what next?" ends when the model says it is done. Models do not always say so. Each turn re-sends the whole conversation, so the cost of a run grows faster than its step count: in `demo/agent_demo.py runaway`, turn 40 costs twelve times turn 1 and the run has spent 29 cents without finishing. Separately, the OpenAI SDK's defaults are a 10-minute timeout and 2 silent retries per call.

**Decision.** `Budget` in `src/agent.py`: 6 model turns, 45 seconds, 2 cents per run; 12 seconds and 3 attempts per model call. The budget is checked before every model turn. A call that times out, is rate limited or gets a 5xx is retried after 0.5 s, then 1 s, with up to 0.25 s of random jitter; anything else (a 400, a validation error) is not retried. When we pass a timeout we set the SDK's `max_retries` to 0, so there is one retry layer, ours. The same tool call with the same arguments twice in a run is refused with a message, not executed again.

**Why these numbers.** The scripted run takes 3 turns; live runs took 3 to 4. Six leaves room for one repair and one extra look. Two cents is about thirty ordinary chat turns. Twelve seconds is roughly four times a normal reply. They are starting points: the trace in `logs/agent.jsonl` is how we will tune them.

**A stop is not a crash.** A run that hits a budget returns `status: "stopped"` with the reason, says so to the student in plain words, and keeps anything already proposed so they can still confirm it. Nothing consequential has run, because nothing consequential ever runs inside the loop (decision 0007).

**Evidence.** `tests/test_agent.py`: `test_step_budget_stops_a_loop_that_never_finishes`, `test_cost_budget_stops_the_loop`, `test_a_timeout_is_retried_with_backoff_and_then_succeeds`, `test_a_dead_model_stops_the_run_cleanly`, `test_a_bad_request_is_not_retried`, `test_the_same_call_twice_is_refused_not_repeated`.

**Consequences.** Some honest runs will be cut short. That is cheaper than one runaway. Tools are not retried by the loop: a failed tool call goes back to the model as an observation, and writes only run after a human yes.
