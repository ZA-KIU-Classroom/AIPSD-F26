# Measuring before and after

*Optional reading for Lab 8, Step 4. About 7 minutes.*

## The idea in plain language

"We made it better" is a claim. "The same ten questions: errors the user saw went from 3 to 0, paid calls from 10 to 4" is a measurement. The difference is a fixed set of inputs, run twice, with one thing changed in between, and the raw output kept.

This is the Evidence Rule from Week 4 applied to performance: every feature ships with a test and a log entry. The tests in Step 3 prove the router behaves. The table in Step 4 shows what that behaviour is worth on your product.

## Why it matters in production

In July 2023 three researchers at Stanford and Berkeley published a comparison of the same model name, GPT-4, in March and in June of that year, on a fixed list of tasks. On one of them, deciding whether a number is prime, measured accuracy went from 84 percent to 51 percent. The interesting part for an engineer is not the number. It is that the change was only visible to people who had kept a fixed list of inputs and run it twice. Everyone else had an impression.

Optimisation work has the same trap in a friendlier form. Caches and fallbacks are easy to add and easy to believe in. Teams routinely ship a cache with a hit rate near zero, because something unique (a timestamp, a request id) sits inside every prompt, and they never look.

## The worked example: CampusPulse

**One line per attempt.** Every path through the router calls `note()`:

```
{"ts": ..., "job": "chat", "outcome": "ok", "model": "google/gemini-3.8-flash", "place": 1, "cost_usd": ..., "ms": ...}
{"ts": ..., "job": "chat", "outcome": "failed", "model": "google/gemini-3.8-flash", "place": 1, "why": "TimeoutError"}
{"ts": ..., "job": "chat", "outcome": "ok", "model": "anthropic/claude-haiku-5.5", "place": 2, "cost_usd": ..., "ms": ...}
{"ts": ..., "job": "chat", "outcome": "cache", "saved_usd": ...}
{"ts": ..., "job": "chat", "outcome": "exhausted"}
```

**One function that counts.** `summary()` reads the file and returns nine numbers. A request is one `ok`, one `cache` or one `exhausted`; `failed` lines are attempts inside a request.

**One script that runs the same questions twice.** `templates/measure.py` has a `before` mode that calls your first model directly, and an `after` mode that sends the same list through `complete()`. In both, the first model is treated as down for three requests (a fire drill), so the comparison includes an outage. For CampusPulse offline (`python -m demo.router_demo before` and `after`):

| | Before | After |
|---|---|---|
| Requests | 20 | 20 |
| Errors the user saw | 6 | 0 |
| Paid model calls | 20 attempted | 4 |
| Answered by a fallback | n/a | 1 |
| Answered from cache | n/a | 16 |

Those counts are exact. Milliseconds and dollars are left out of the CampusPulse example because the offline stand-in is instant and free; yours come from live runs.

**Reading your own table.** Four questions to ask of it:

1. *Is the hit rate believable?* The demo's 16 of 20 comes from a list with four different questions. If yours is zero, look for something unique in every prompt.
2. *How often did the fallback fire outside the drill?* More than rarely means your first model or your limit needs attention.
3. *Did the median go down because of the cache, or up because of the fallback?* Both happen in one run. Look at `ms` on `place: 2` lines.
4. *What did you not measure?* Quality. A table of counts cannot say whether model 2's answers are as good. That is the Week 9 lecture.

## Common mistakes and how to spot them

| Mistake | How you spot it |
|---|---|
| Different questions before and after | The two runs are not comparable. Both modes must read the same list |
| Measuring once | One slow network moment decides your median. Run each mode twice and keep both outputs |
| Rounding to nicer numbers | "About 40 percent faster" with no raw lines. Paste the lines |
| Counting the whole log | `summary()` reads the full file. Delete `logs/router.jsonl` before a measured run |
| Reporting only what improved | A table with no row that got worse is usually missing a row. Latency on fallback answers is the usual one |

## Check yourself

1. Your `after` run shows `answered_from_cache: 0` although three questions are repeated. Name two causes and how you would tell them apart.
2. Why does the `before` mode also run the fire drill?
3. Your Demo Day slide will have one number from this page. Which one says most about your product, and what would a judge ask next?
