# <Product name> · Before and After the Router

Save as `docs/measurements.md`. Every number on this page comes from a command you ran on your own product. If a cell would be a guess, write "not measured" and say why.

**Measured at commit:** `<short SHA of the commit you measured, from git rev-parse --short HEAD>`
**The call we protected:** `<function name>` in `<file>`, used by `<feature>`
**Chain:** `<model 1>` then `<model 2>` · **Limit:** `<TIMEOUT_S>` s · **Lifetime:** `<CACHE_TTL_S>` s

## The 10 questions

Paste your `QUESTIONS` list from `evals/measure.py`. Mark the repeats. These must be questions your product really gets; a reader should be able to tell what your product is from this list alone.

## The table

Run `python -m evals.measure before`, delete `logs/router.jsonl`, run `python -m evals.measure after`. Copy the numbers; do not round them into nicer ones.

| | Before (one model, no cache) | After (through `src/router.py`) |
|---|---|---|
| Requests | | |
| Errors the user saw | | |
| Paid model calls | | |
| Answered by a fallback | n/a | |
| Answered from cache | n/a | |
| Sorry sentences | n/a | |
| Median milliseconds | | |
| Dollars spent | | |

## Three raw lines

Paste three lines from your own `logs/router.jsonl`: one `ok` with `place: 1`, one `ok` with `place: 2`, one `cache`. Leave the timestamps in.

## What surprised us

Two or three sentences. Which number was not what you expected, and what in your product explains it? "The cache did nothing because every prompt contains the current time" is a good answer. "It got faster" is not.

## What we would change next

One setting you would now change (the chain order, the limit, the lifetime), and the number on this page that made you think so.
