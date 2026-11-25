# Deep dive: what the gateway and the provider already do

*Optional, beyond the lab. For teams who finished early or who want to understand the layers underneath `src/router.py`. Details checked against OpenRouter's documentation in the week of the Week 8 lecture; they change, so read the current page before relying on one.*

## Three layers of "try something else"

When CampusPulse calls a model there are three places a failure can be absorbed.

| Layer | Who owns it | What it tries | On by default? |
|---|---|---|---|
| Provider failover | the gateway (OpenRouter) | the same model on another host | yes |
| Model fallbacks | the gateway | a different model, from a list you send | no, you opt in |
| `src/router.py` | you | a different model, then your sentence | you wrote it |

**Provider failover** means that if one host serving your model is down or rate-limited, the gateway sends the request to another host of the same model. You did nothing to get this. It does not help when the model is unavailable everywhere.

**Model fallbacks** are requested by sending a list of models with the request. With the OpenAI Python SDK the list goes in `extra_body`:

```python
client.chat.completions.create(
    model=CHAINS[job][0],
    messages=messages,
    extra_body={"models": CHAINS[job][1:]},
)
```

The response's `model` field tells you which one answered. The gateway moves on for downtime, rate limits and moderation refusals.

**Why keep your own layer if the gateway has one?** Three things the gateway cannot give you: a chain you can test offline with a fake provider, a last link that is your own sentence, and a log line in your own file with `place` in it. They combine well: use the gateway's list as a first line of defence and keep `src/router.py` for the cases that reach you. If you do combine them, remember that waits add up; lower `TIMEOUT_S` accordingly.

## Two kinds of cache

The lab's cache stores a whole answer. Providers offer a different one: prompt caching, which stores the processed beginning of your prompt. The model still runs and writes a new answer, but the repeated input tokens are billed at a discount.

| | Response cache (`src/router.py`) | Prompt cache (provider) |
|---|---|---|
| What is reused | the entire answer | the reading of a repeated prompt prefix |
| Does the model run? | no | yes |
| Saves | the full cost and the full wait | part of the input cost, some latency |
| Hit requires | the identical request | the identical beginning of the request |
| You control it by | the key and the lifetime | the order of your prompt |

For `google/gemini-3.8-flash` the listed prices on OpenRouter this week were $0.75 per million input tokens and $0.075 per million cached input tokens (a promotional rate until 2027). Some providers charge extra to write to the cache, so a long prompt sent only once can cost more with caching than without.

**How to earn the discount.** Put what never changes first and what changes last:

1. system prompt
2. tool schemas
3. long reference documents
4. the conversation so far
5. today's date, the user's question

A single changed character near the top makes everything after it a miss. The most common cause of a zero hit rate is a timestamp in the first line of the system prompt.

**How to check.** The usage block of every reply carries `prompt_tokens_details.cached_tokens`. Above zero means a hit. Add it to your usage log line and watch it across a conversation: it should climb as the stable prefix grows.

**A wrinkle with fallbacks.** A prompt cache lives at one provider. When your chain moves to model 2, that request starts cold. During an outage, expect to pay full input price as well as getting a different model's answer.

## Batch

For work nobody is waiting on (labelling a month of events, re-embedding a corpus, running a large evaluation) many models offer a batch endpoint at about half the listed price, in exchange for results that arrive later. The listed batch price for the same Flash model this week was $0.375 in and $1.875 out per million tokens. The question from the lecture decides it: is somebody waiting?

## Try it

1. Add `cached_tokens` to the line your model call logs. Hold a five-turn conversation and plot the number.
2. Move today's date from the first line of your system prompt to the last line and repeat. Compare.
3. Send one request with `extra_body={"models": [...]}` and a deliberately unavailable first choice of your own selection, and read which `model` comes back. Record what you observe; do not assume.
