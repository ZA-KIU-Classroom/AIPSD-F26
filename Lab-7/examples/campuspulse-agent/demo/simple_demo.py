"""The Week 7 demos for the 50-line loop. Offline, no key. Run from the example root.

    python -m demo.simple_demo plan       the loop proposes four events, books none; Nino says yes to three
    python -m demo.simple_demo runaway    a model that never finishes, stopped after six steps

(The agent with no gate at all is `python -m demo.agent_demo naive`.)
"""
import json
import sys

from demo import agent_demo as base          # sets the offline environment and the temp folders
from src.simple_agent import confirm, run


def plan() -> None:
    base._seed()
    print('\n1 · the loop: "Plan my week"\n')
    r = run(base.GOAL, base.NINO)
    for t in r["trace"]:
        print(f"   step {t['step']}  {t['tool']:<12} {'PARKED, waiting for a yes' if t['parked'] else 'ran (a read)'}")
    print(f"\n   status: {r['status']}\n")
    print("2 · what Nino sees\n")
    for a in r["proposed"]:
        print(f"   [ ] {a['id']}  {a['summary']}")
    print(f"\n   {base._seats()}   ← proposed is not booked\n")
    print("3 · Nino has a lab on Friday at 17:00, so she leaves a2 unticked and presses Confirm\n")
    for a, out in zip([x for x in r["proposed"] if x["id"] != "a2"], confirm(base.NINO, ["a1", "a3", "a4"])):
        print(f"   {a['id']}  {'booked' if out['ok'] else 'not booked: ' + out['error'][:38]}")
    print(f"\n   {base._seats()}")
    print(f"   press Confirm again → {confirm(base.NINO, ['a1'])}   (a plan works once)\n")


def runaway() -> None:
    def never_done(messages, schemas):
        return {"content": None, "tool_calls": [{"id": f"c{len(messages)}", "name": "list_events",
                                                 "arguments": json.dumps({"from_date": "2026-11-18"})}]}
    print("\na model that always wants one more look\n")
    r = run(base.GOAL, base.NINO, llm=never_done)
    print(f"   steps taken: {r['trace'][-1]['step']}   status: {r['status']}")
    print(f"   Nino reads: \"{r['text']}\"   · {base._seats()}\n")


if __name__ == "__main__":
    {"plan": plan, "runaway": runaway}[sys.argv[1] if len(sys.argv) > 1 else "plan"]()
