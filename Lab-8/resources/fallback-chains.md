# Fallback chains

*Optional reading for Lab 8, Steps 1 and 2. About 8 minutes.*

## The idea in plain language

Your product calls a model over the network. That call can fail for reasons that have nothing to do with your code: the provider is overloaded, a data centre has a problem, your account hit a rate limit. A fallback chain is an ordered list of what to try. Ask the first model. If it cannot answer in time, ask the second. If nobody answers, return something you prepared in advance.

It is the same idea as a spare tyre. You do not expect to need it on any given day. You carry it because the day you need it, nothing else will do.

## Why it matters in production

On 10 June 2025, OpenAI had a partial outage that lasted most of a working day. Their published write-up says ChatGPT error rates peaked at about 35 percent and API availability dropped to 75 percent. For every product built on that API with a single model and no alternative, a quarter of requests failed for hours, and their users saw whatever that product shows when a call raises: usually a blank panel or "Internal Server Error".

Those teams had no bug. They had a single point of failure they did not own. Outages like this are not rare events for any provider; the only question is whether your user notices.

## The worked example: CampusPulse

`examples/campuspulse-router/src/router.py` is about forty lines. Read it with these four decisions in mind.

**1. The chain is data, not code.**

```python
CHAINS = {
    "chat": ["google/gemini-3.8-flash", "anthropic/claude-haiku-5.5"],
}
```

Changing who answers is a one-line edit that a reviewer can read. The two models come from different companies on purpose: two models from one provider usually share the same outage.

**2. The loop is the whole mechanism.**

```python
for place, model in enumerate(CHAINS[job], start=1):
    try:
        answer = call(messages, tools or [], timeout=TIMEOUT_S, model=model)
    except Exception as error:
        if not temporary(error):
            raise
        note(job, "failed", model=model, place=place, why=type(error).__name__)
        continue
    ...
    return note(job, "ok", answer, model=model, place=place, ...)
```

Same messages, same tools, the next name. `place` is recorded so the log can tell you later how often the second model is doing the first one's job.

**3. The last link is a sentence.**

```python
return note(job, "exhausted", {"content": SORRY, "tool_calls": [], "degraded": True})
```

The reply has the same shape as a model's reply, so nothing downstream breaks. `degraded` lets the page show it differently. `SORRY` is written by a person: "CampusPulse cannot reach its models right now. Nothing was changed. Please try again in a minute."

**4. `call` is a parameter.** That is what makes the three lab tests possible: a test passes in a fake provider and decides which model is down.

Run the four demos to see each path:

```
python -m demo.router_demo before    # no chain: 6 of 20 students see an error
python -m demo.router_demo after     # the same 20 through the chain: 0
python -m demo.router_demo dark      # every model down: the sentence
python -m demo.router_demo bug       # a 400: raised, second model never asked
```

## Common mistakes and how to spot them

| Mistake | How you spot it |
|---|---|
| Two models from the same provider in the chain | One status page covers both. Check where each model is hosted |
| A chain with one model and a retry | Your worst case is three long waits and then an error. Count the seconds |
| A fallback with a much smaller context window | It fails on exactly your longest prompts. Send your longest real prompt to the second model once |
| The second model does not support something the first does (tools, images, strict JSON) | The fallback "works" in tests with plain text and fails on the real feature. Test the real feature against model 2 directly |
| No log of which model answered | You cannot answer "how often does the fallback fire?" Look for `place` in your log |
| A sorry sentence that says nothing about the user's action | The user does not know whether their booking went through. Read your sentence as a user |

## Check yourself

1. Your chain is `[A, B]` with a 12-second limit. A is down and B takes 3 seconds. How long does the user wait, and what does the log contain?
2. Why is the last link not a third model?
3. A teammate wants the chain to live in an environment variable "so we can change it without a deploy". Name one benefit and one risk for your team.
