"""The Week 8 demos for the fallback chain. Offline, no key. Run from the example root.

    python -m demo.router_demo before     20 questions, the first model down for 6 of them, no chain
    python -m demo.router_demo after      the same 20 questions through src/router.py
    python -m demo.router_demo dark       every model down: the student reads one calm sentence
    python -m demo.router_demo bug        a 400 is our bug: raised, never passed to the next model

The outage is simulated: a small function raises a timeout for the first model in the chain.
Counts are exact. Milliseconds and dollars are not shown, because the offline stand-in is
instant and free: measure those on your own product, live.
"""
import os
import sys
import tempfile

os.environ.setdefault("CAMPUSPULSE_OFFLINE", "1")
os.environ["CAMPUSPULSE_ROUTER_LOG"] = os.path.join(tempfile.mkdtemp(prefix="router-demo-"), "router.jsonl")
os.environ.setdefault("CAMPUSPULSE_USAGE_LOG", os.path.join(tempfile.mkdtemp(prefix="router-demo-"), "usage.jsonl"))

from src import router                                   # noqa: E402
from src.llm import complete_tools                       # noqa: E402
from src.router import CHAINS, complete, summary         # noqa: E402

FIRST = CHAINS["chat"][0]
ASKED = ["What is on this week?", "Is the robotics night free?", "What is on this week?", "Where is A112?",
         "What is on this week?", "Is the robotics night free?", "What is on this week?", "When does the library close?",
         "Where is A112?", "What is on this week?", "Is the robotics night free?", "What is on this week?",
         "What is on this week?", "Where is A112?", "When does the library close?", "What is on this week?",
         "Is the robotics night free?", "What is on this week?", "Where is A112?", "What is on this week?"]
OUTAGE = range(6, 12)                                    # requests 6 to 11: the first model does not answer


class BadRequest(Exception):
    status_code = 400


def provider(down_now):
    """One model call. `down_now()` says which models are down at this moment."""
    def call(messages, tools, timeout=None, model=None):
        if model in down_now():
            raise TimeoutError(f"{model}: no reply in {timeout} s")
        return complete_tools(messages, tools, timeout=timeout, model=model)
    return call


def ask(text):
    return [{"role": "system", "content": "You are CampusPulse."}, {"role": "user", "content": text}]


def before() -> None:
    errors = 0
    print("\nbefore · one model, no chain, no cache\n")
    for n, text in enumerate(ASKED, start=1):
        call = provider(lambda: [FIRST] if n in OUTAGE else [])
        try:
            call(ask(text), [], timeout=router.TIMEOUT_S, model=FIRST)
            print(f"   {n:>2}  answered        {text}")
        except TimeoutError:
            errors += 1
            print(f"   {n:>2}  ERROR 500       {text}")
    print(f"\n   20 requests · 20 paid model calls attempted · {errors} students saw an error page\n")


def after() -> None:
    print("\nafter · the same 20 questions through the chain\n")
    for n, text in enumerate(ASKED, start=1):
        call = provider(lambda: [FIRST] if n in OUTAGE else [])
        lines_before = len(router.LOG.read_text().splitlines()) if router.LOG.exists() else 0
        complete(ask(text), call=call)
        new = [x for x in router.LOG.read_text().splitlines()[lines_before:]]
        how = ("from cache" if '"cache"' in new[-1] else
               "fallback answered" if len(new) > 1 else "first model")
        print(f"   {n:>2}  {how:<18} {text}")
    print()
    for name, value in summary().items():
        if name not in ("median_ms", "spent_usd", "saved_by_cache_usd"):
            print(f"   {name:<26} {value}")
    print("\n   0 students saw an error page\n")


def dark() -> None:
    print("\nevery model in the chain is down\n")
    answer = complete(ask("What is on this week?"), call=provider(lambda: CHAINS["chat"]))
    print(f"   the student reads: \"{answer['content']}\"")
    print(f"   degraded: {answer['degraded']} · cached: {bool(router.CACHE)}\n")


def bug() -> None:
    def call(messages, tools, timeout=None, model=None):
        raise BadRequest("400: messages[1].content must be a string")
    print("\na 400 from the first model\n")
    try:
        complete(ask("What is on this week?"), call=call)
    except BadRequest as e:
        print(f"   raised to us: {e}")
        print(f"   attempts logged: {summary()['failed_attempts']} · the second model was never asked\n")


if __name__ == "__main__":
    {"before": before, "after": after, "dark": dark, "bug": bug}[sys.argv[1] if len(sys.argv) > 1 else "after"]()
