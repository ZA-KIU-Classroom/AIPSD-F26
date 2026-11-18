"""The Week 7 live demos. Offline, no key, deterministic. Run from the example root.

    python -m demo.agent_demo naive     an agent with tools and no gate "plans my week": three seats taken,
                                        one of them during a class, and nobody was asked
    python -m demo.agent_demo plan      the supervised loop on the same goal: the trace step by step, what it
                                        proposed, what the gate's checks refused, then a yes to one action
    python -m demo.agent_demo runaway   a model that never finishes: first with no budget (we cut it at 40),
                                        then with the budget
    python -m demo.agent_demo flaky     a model that times out twice, then one that never answers

The "model" is the scripted planner in src/offline.py. It matches event tags to interests and
checks nothing else, on purpose: the timetable clash and the full event are caught by code.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

os.environ.setdefault("CAMPUSPULSE_OFFLINE", "1")
os.environ.setdefault("CAMPUSPULSE_TODAY", "2026-11-18")
_tmp = tempfile.mkdtemp(prefix="campuspulse-demo-")
os.environ.setdefault("CAMPUSPULSE_STATE_DIR", _tmp)
for _name in ("USAGE", "TOOL", "AGENT"):
    os.environ.setdefault(f"CAMPUSPULSE_{_name}_LOG", os.path.join(_tmp, f"{_name.lower()}.jsonl"))

from src import memory  # noqa: E402
from src.act import as_assistant, call_tool  # noqa: E402
from src.agent import SYSTEM, Budget, perceive, run  # noqa: E402
from src.gate import confirm  # noqa: E402
from src.llm import complete_tools  # noqa: E402
from src.tools import _rsvps, tools_for  # noqa: E402

GOAL, NINO = "Plan my week", "s123"


def _seed() -> None:
    memory.remember_interest(NINO, "tech talks")
    memory.remember_interest(NINO, "free food")


def _seats() -> str:
    taken = _rsvps()
    return f"rsvps.json · {sum(len(v) for v in taken.values())} seat(s) taken" + (f" · {', '.join(taken)}" if taken else "")


def naive() -> None:
    """Week 5's loop with a bigger goal: every tool call runs the moment the model asks."""
    _seed()
    seen, allowed = perceive(NINO), tools_for(NINO)
    classes = "\n".join(f"- {c['day']} {c['start']} to {c['end']}: {c['what']}" for c in seen["classes"])
    messages = [{"role": "system", "content": SYSTEM.format(interests=", ".join(seen["interests"]), classes=classes,
                                                            today=seen["today"].strftime("%A %Y-%m-%d"))},
                {"role": "user", "content": GOAL}]
    print(f"\n1 · tools and a loop, no gate: \"{GOAL}\"\n")
    for step in range(1, 7):
        msg = complete_tools(messages, [t.schema() for t in allowed.values()])
        if not msg["tool_calls"]:
            break
        messages.append(as_assistant(msg))
        for call in msg["tool_calls"]:
            out = call_tool(call, allowed, NINO)
            print(f"   step {step}  {call['name']:<12} {call['arguments']:<28} {'RAN' if out['ok'] else 'failed: ' + out['error'][:44] + '…'}")
            messages.append({"role": "tool", "tool_call_id": call["id"],
                             "content": json.dumps(out.get("result") or {"error": out["error"]})})
    print(f"\n   {_seats()}")
    print("   Nino asked for a plan. She got three bookings, one of them (ev-207) during her Friday Algorithms lab.")
    print("   Nobody asked her. The model never checked her timetable, and nothing in the loop made it.\n")


def plan() -> None:
    _seed()
    print(f"\n1 · the supervised loop: \"{GOAL}\"\n")
    r = run(GOAL, student=NINO)
    for line in r.trace:
        if line["phase"] == "reason":
            print(f"   step {line['step']}  REASON   {line['tokens_in']:>4} tokens in · asked for {line['calls']} tool call(s)")
        elif line["phase"] == "act":
            what = "PARKED for confirmation" if line["gated"] and line["ok"] else "REFUSED by the gate" if line["gated"] else "ran (a read)"
            print(f"           ACT      {line['tool']:<12} {what}")
        else:
            print(f"           FINISH   {line['status']} · stop: {line['stop']} · {line['steps']} steps · ${line['cost_usd']}")
    print(f"\n   {r.text}\n")
    print("2 · what the student sees\n")
    for a in r.proposed:
        print(f"   [ ] {a['summary']}")
    for x in r.rejected:
        print(f"    x  left out: {x['error']}")
    print(f"\n   {_seats()}   ← proposed is not booked\n")
    print("3 · the student ticks the first box and presses Confirm: POST /plan/<id>/confirm, no model involved\n")
    done = confirm(NINO, r.plan_id, [r.proposed[0]["id"]])
    for x in done["ran"]:
        print(f"   booked: {x['summary']}")
    for s in done["skipped"]:
        print(f"   not ticked, not booked: {s}")
    print(f"\n   {_seats()}")
    print(f"   confirm again with the same plan id → {confirm(NINO, r.plan_id, [r.proposed[0]['id']])}   (single use)\n")


def _restless():
    days = iter(range(1, 999))

    def model(messages, schemas, timeout=None):
        n = next(days)
        return {"content": None, "usage": {"tokens_in": 900 + 420 * n, "tokens_out": 30,
                                           "cost_usd": round((900 + 420 * n) * 0.75e-6 + 30 * 3.75e-6, 6)},
                "tool_calls": [{"id": f"c{n}", "name": "list_events",
                                "arguments": json.dumps({"from_date": "2026-11-18", "days": n % 14 + 1})}]}
    return model


def runaway() -> None:
    print("\n1 · a model that always wants one more look, and a loop with no budget (we cut it at 40 steps)\n")
    r = run(GOAL, student=NINO, llm=_restless(), budget=Budget(max_steps=40, max_cost_usd=99, max_seconds=999))
    costs = [x["cost_usd"] for x in r.trace if x["phase"] == "reason"]
    for n in (1, 5, 10, 20, 40):
        print(f"   step {n:>2}  this turn ${costs[n - 1]:.4f}   run so far ${sum(costs[:n]):.4f}")
    print(f"\n   Every turn re-sends everything before it, so turn 40 costs {costs[-1] / costs[0]:.0f} times turn 1.")
    print(f"   ${sum(costs):.2f} for one student pressing one button, and it has not finished.\n")
    print("2 · the same model inside the default budget: 6 steps, 45 seconds, 2 cents\n")
    r = run(GOAL, student=NINO, llm=_restless())
    print(f"   status: {r.status} · stop: {r.stop} · steps: {r.steps} · cost: ${r.cost_usd}")
    print(f"   the student sees: \"{r.text}\"\n")


def flaky() -> None:
    def waited(seconds: float) -> None:
        print(f"           waiting {seconds:.2f} s before the next attempt")

    attempts = []

    def twice(messages, schemas, timeout=None):
        attempts.append(timeout)
        if len(attempts) > 3:
            return complete_tools(messages, schemas)
        print(f"   attempt {len(attempts)}  timeout {timeout:.0f} s  ", end="")
        if len(attempts) < 3:
            print("→ no reply: TimeoutError")
            raise TimeoutError
        print("→ answered")
        return complete_tools(messages, schemas)

    print("\n1 · the model times out twice, then answers: backoff, then carry on\n")
    _seed()
    r = run(GOAL, student=NINO, llm=twice, sleep=waited)
    print(f"\n   status: {r.status} · stop: {r.stop} · {r.steps} steps · the student never saw the two failures\n")
    print("2 · the model never answers: three attempts, then a clean stop\n")

    def dead(messages, schemas, timeout=None):
        print("   attempt      → no reply: TimeoutError")
        raise TimeoutError

    r = run(GOAL, student=NINO, llm=dead, sleep=waited)
    print(f"\n   status: {r.status} · stop: {r.stop}")
    print(f"   the student sees: \"{r.text}\"   · {_seats()}\n")


if __name__ == "__main__":
    {"naive": naive, "plan": plan, "runaway": runaway, "flaky": flaky}[sys.argv[1] if len(sys.argv) > 1 else "plan"]()
