# Caching without leaks

*Optional reading for Lab 8, Steps 1 and 2. About 8 minutes.*

## The idea in plain language

If two requests would send the model exactly the same thing, the second one does not need the model. Keep the first answer for a while and hand it back. That is a response cache. It saves money and it is fast: a dictionary lookup in place of a network call.

Everything interesting about a cache is in two decisions: what goes into the key, and how long an entry lives.

## Why it matters in production

A cache with the wrong key is a privacy bug. If the key is built from the user's question alone, then the first person to ask "what are my upcoming bookings?" fills the cache, and the next person to ask the same words receives the first person's bookings. Nothing crashed, no test failed, and one user has read another user's data. In Week 6 we called this cross-user leakage and designed session state to prevent it. A careless cache brings it straight back.

A cache with the wrong lifetime is a correctness bug. "Three seats left", served from memory for an hour, is a promise your product cannot keep.

## The worked example: CampusPulse

**The key is everything the model saw.**

```python
key = hashlib.sha256(json.dumps([job, messages], sort_keys=True).encode()).hexdigest()
```

`messages` includes the system prompt, and CampusPulse's system prompt contains the facts our code added for this student: today's date and their stored interests. So:

| Who asks | System prompt contains | Question | Key |
|---|---|---|---|
| Nino | interests: tech talks, free food | What should I go to this week? | one value |
| Luka | interests: football, chess | What should I go to this week? | a different value |
| A visitor, not signed in | no interests | Where is A112? | a third value |
| Another visitor | no interests | Where is A112? | the same third value: shared, and correctly so |

Nino and Luka never share an answer, because their prompts differ. Two visitors asking a public question do share one, because nothing about the request differs. Nobody had to write a rule about users: the rule falls out of hashing the whole input.

**Three things are never cached.**

```python
if saved and not tools and time.time() - saved[0] < CACHE_TTL_S:   # read
...
if not tools:
    CACHE[key] = (time.time(), answer)                             # write
```

1. *A turn that offers tools.* The model may ask for an action, and the result depends on the world right now.
2. *The sorry reply.* It is returned after the loop, where nothing is stored. Otherwise users would keep reading it after the models came back.
3. *Anything older than `CACHE_TTL_S`.* The check happens on read.

**Choosing the lifetime.** Ask what in your data can change and make a stored answer wrong, and how long that can be tolerated. For CampusPulse the fast-moving fact is seats on an event, so 600 seconds. A product that quotes prices might choose 60. A product that explains a fixed regulation might choose a day. `0` switches the cache off and is a respectable answer for anything personal or financial.

**What this cache is not.** It lives in one process's memory, so it empties on restart and is not shared between servers. That is enough for this course. It is also exact-match: "Where is A112?" and "where's A112" are different keys. Matching by meaning (a semantic cache) exists, costs an embedding call per request, and can return an answer to a question that only looked similar. Start with exact match and measure the hit rate before wanting more.

## Common mistakes and how to spot them

| Mistake | How you spot it |
|---|---|
| Key built from the question only | Sign in as two test users, ask the same personal question, compare the answers |
| The current time (to the second) inside the prompt | Hit rate is zero: every prompt is unique. Look at `answered_from_cache` in the summary |
| Caching turns that offer tools | An action is "confirmed" from memory and nothing happened. Check the `not tools` condition is still there |
| Caching the error or sorry reply | Users report the outage lasting ten minutes longer than the provider's status page says |
| No lifetime | Answers from last week. Search for where the stored time is compared |
| A cache nobody can clear | After a bad prompt ships, the bad answers live on. Know how you empty yours (here: restart, or `CACHE.clear()`) |

## Check yourself

1. Your system prompt includes `Today is Wednesday 14:03:27`. What is your cache hit rate, and what is the smallest change that fixes it without lying to the model?
2. Two signed-in users ask "what is the Wi-Fi password in the library?". Should they share a cache entry? What in the key decides?
3. You lower `CACHE_TTL_S` from 600 to 60. Which two numbers in `summary()` do you expect to move, and in which direction?
