# What counts as down

*Optional reading for Lab 8, Steps 2 and 3. About 7 minutes.*

## The idea in plain language

A chain has to decide, for every error, between two actions: try the next model, or stop and tell the developers. The rule is short. If the problem is on the provider's side and temporary, move on. If the problem is in our own request, raise. And if a model is merely slow, treat slow as down after a fixed number of seconds.

## Why it matters in production

The dangerous chain is not the one that fails. It is the one that never fails.

Picture a team whose chain catches every exception and moves to the next model. One Friday a refactor changes how tool schemas are built, and the first model starts rejecting every request with a 400. Nothing visible happens. The second model, more tolerant of the malformed schema, answers everything. The dashboard is green. Two weeks later someone notices the bill has changed shape and the answers read differently, and nobody can say since when. The chain worked exactly as written and hid a bug for two weeks.

This is a composite of a failure pattern that reliability engineers describe often, not a single documented incident. The defence is cheap: a fallback must only cover failures that are not your fault.

## The worked example: CampusPulse

```python
def temporary(error: Exception) -> bool:
    name = type(error).__name__
    return ("Timeout" in name or "Connection" in name
            or getattr(error, "status_code", None) in (408, 429, 500, 502, 503, 504))
```

| The call raised | `temporary()` | What the router does | Why |
|---|---|---|---|
| a timeout after `TIMEOUT_S` | True | next model | slow counts as down |
| a dropped connection | True | next model | the network or the provider |
| 429 Too Many Requests | True | next model | their capacity or our rate limit; another provider has its own |
| 500, 502, 503, 504 | True | next model | their servers |
| 400 Bad Request | False | raise | our request is malformed |
| 401, 403 | False | raise | our key or our permissions |
| a validation error from our own code | False | raise | our bug |

The check looks at the error's class name and its `status_code`, so it works with the OpenAI SDK's exceptions and with the plain `TimeoutError` a test raises.

**The limit.** In Week 7 we read the SDK's defaults: a 10-minute timeout and silent retries. The router passes `timeout=TIMEOUT_S` to every call and your model call turns the SDK's own retries off. Twelve seconds comes from the usage log: CampusPulse's median chat turn is about 2 seconds, so a call that has taken 12 is not coming. Worst case with two models is 24 seconds, then the sentence. If 24 is too long for your product, lower the number; do not add a third model.

**What about a refusal or an empty answer?** A model that replies "I can't help with that" has answered. The router returns it. Whether that answer is good enough is a question for a golden set (the Week 9 lecture), not for the chain.

**What about tool turns?** The chain may repeat a model call that offered tools, because the model only asks for a tool. Your own code runs it afterwards, behind the Lab 5 gates and the Lab 7 confirmation. A booking is never repeated by the chain.

## Common mistakes and how to spot them

| Mistake | How you spot it |
|---|---|
| `except Exception: continue` | Your third lab test fails: a 400 comes back as an answer from model 2 |
| Treating 429 as "our bug" | During a provider's busy hour your users see the sorry sentence while model 2 sits idle |
| No timeout passed to the call | One hung request holds a user for minutes. Search your model call for `timeout` |
| SDK retries left on | Up to three hidden attempts per link. Search for `max_retries` |
| Logging failures only as text | You cannot count them. Each failed attempt should be one JSON line with the model and the reason |

## Check yourself

1. Your log shows 200 lines with `outcome: ok, place: 2` in a day and zero lines with `outcome: failed`. What is wrong with that picture?
2. A provider returns 200 OK with an empty `content`. Should the chain move on? Argue both sides in one sentence each.
3. Which of these should be raised: a 404 "model not found", a 503, a 422 "invalid schema"? Why?
