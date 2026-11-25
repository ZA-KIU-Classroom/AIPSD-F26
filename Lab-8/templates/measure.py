"""Lab 8 measurement: the same questions, before and after the router. Copy to evals/measure.py.

    python -m evals.measure before     one model, no chain, no cache (calls your model directly)
    python -m evals.measure after      the same questions through src/router.py

Both runs are LIVE: they call real models with your key and cost a little (20 short questions).
A fire drill is built in: for the requests listed in DRILL, the first model in your chain is
treated as down, so you can watch the fallback answer. Paste both outputs into docs/measurements.md.
"""
import sys
import time

from src import router
from src.router import CHAINS, TIMEOUT_S, complete, summary

JOB = "chat"
QUESTIONS = [                       # ADAPT: 10 real questions for YOUR product. Repeat at least 3 of them.
    "replace me with a real question",
]
DRILL = (4, 5, 6)                   # request numbers during which the first model is "down"
FIRST = CHAINS[JOB][0]
real_call = complete.__defaults__[-1]                  # the model call your router uses


def ask(text: str) -> list[dict]:
    return [{"role": "user", "content": text}]         # ADAPT if your product adds a system prompt


def drill(n: int):
    def call(messages, tools, timeout=None, model=None):
        if n in DRILL and model == FIRST:
            raise TimeoutError(f"fire drill: {model}")
        return real_call(messages, tools, timeout=timeout, model=model)
    return call


def before() -> None:
    errors, times, spent = 0, [], 0.0
    for n, text in enumerate(QUESTIONS, start=1):
        started = time.perf_counter()
        try:
            answer = drill(n)(ask(text), [], timeout=TIMEOUT_S, model=FIRST)
            spent += (answer.get("usage") or {}).get("cost_usd", 0.0)
            times.append(int((time.perf_counter() - started) * 1000))
        except TimeoutError:
            errors += 1
    times.sort()
    print(f"before · requests {len(QUESTIONS)} · errors the user saw {errors} · paid calls {len(times)} "
          f"· median_ms {times[len(times) // 2] if times else None} · spent_usd {round(spent, 6)}")


def after() -> None:
    router.CACHE.clear()
    start = len(router.LOG.read_text().splitlines()) if router.LOG.exists() else 0
    degraded = sum(1 for n, text in enumerate(QUESTIONS, start=1)
                   if complete(ask(text), job=JOB, call=drill(n)).get("degraded"))
    print(f"after · errors the user saw 0 · sorry sentences {degraded} · log lines added "
          f"{len(router.LOG.read_text().splitlines()) - start}")
    for name, value in summary().items():
        print(f"   {name:<26} {value}")
    print("   (summary() counts the whole log file. For a clean table, delete logs/router.jsonl first.)")


if __name__ == "__main__":
    if len(QUESTIONS) < 10:
        sys.exit("ADAPT first: put 10 real questions for your product in QUESTIONS.")
    {"before": before, "after": after}[sys.argv[1] if len(sys.argv) > 1 else "after"]()
