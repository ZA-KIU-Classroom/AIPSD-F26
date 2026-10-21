"""Two live breakages for the Lab 4 demo. Offline, no key, deterministic.

    python -m demo.break citations   a model that invents a source: shown without the check, refused with it
    python -m demo.break k           "save tokens, use k=1": the golden set catches the regression

Run from the example root with CAMPUSPULSE_OFFLINE=1 after `python -m src.index`.
"""
from __future__ import annotations

import subprocess
import sys

from src.answer import answer
from src.index import load

QUESTION = "Is the Robotics Club free to join?"


def lying_model(prompt: str, schema: dict | None = None) -> dict:
    """What a real model sometimes does: a plausible fee, and a citation to a source it never saw."""
    return {"answer": "Membership costs 20 GEL per semester [1]. Fees are paid at the first meeting [7].",
            "citations": [1, 7], "grounded": True}


def citations() -> None:
    index = load()
    for check in (False, True):
        result = answer(index, QUESTION, llm=lying_model, check=check)
        print(f"\ncheck_citations {'ON ' if check else 'OFF'} -> {result.status.upper()}")
        print(f"  shown to the student: {result.text}")
        if result.reason:
            print(f"  reason, in logs/answers.jsonl: {result.reason}")
    print("\nNote: with the check ON the invented [7] is caught. The 20 GEL with a real [1] is NOT:"
          "\nthat is the Photography Club's fee, cited to the Robotics page. Only a golden question catches it.")


def k() -> None:
    for kk in ("5", "1"):
        print(f"\n$ python -m evals.run_golden --k {kk}")
        code = subprocess.call([sys.executable, "-m", "evals.run_golden", "--k", kk])
        print(f"exit code {code}: {'merge allowed' if code == 0 else 'merge blocked'}")


if __name__ == "__main__":
    {"citations": citations, "k": k}[sys.argv[1] if len(sys.argv) > 1 else "citations"]()
