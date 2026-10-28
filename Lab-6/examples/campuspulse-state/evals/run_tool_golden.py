"""Run the tool golden set against the real act() loop. Exit code 1 below the threshold.

    python -m evals.run_tool_golden            # offline if CAMPUSPULSE_OFFLINE=1, live otherwise
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
os.environ.setdefault("CAMPUSPULSE_TODAY", "2026-10-21")


def score(item: dict, reply, rsvps: dict) -> tuple[bool, list[str]]:
    why = []
    first = reply.calls[0]["tool"] if reply.calls else "none"
    if item.get("expect_tool") and first != item["expect_tool"]:
        why.append(f"expected {item['expect_tool']}, model called {first}")
    if "expect_ok" in item and reply.calls and reply.calls[0]["ok"] != item["expect_ok"]:
        why.append(f"expected ok={item['expect_ok']}, got {reply.calls[0]['error'] or 'ok'}")
    text = reply.text.lower()
    why += [f"did not mention '{m}'" for m in item.get("must_mention", []) if m.lower() not in text]
    if item.get("never_rsvp_for"):
        from src.tools import student_key
        if any(student_key(item["never_rsvp_for"]) in seats for seats in rsvps.values()):
            why.append(f"an RSVP was written for {item['never_rsvp_for']}")
    return (not why), why


def run() -> dict:
    spec = yaml.safe_load((HERE / "tools_golden.yaml").read_text(encoding="utf-8"))
    from src.act import act
    rows = []
    for item in spec["items"]:
        os.environ["CAMPUSPULSE_STATE_DIR"] = tempfile.mkdtemp(prefix="golden-")   # fresh state per case
        reply = act(item["question"], student=item.get("student"))
        state = Path(os.environ["CAMPUSPULSE_STATE_DIR"]) / "rsvps.json"
        rsvps = json.loads(state.read_text()) if state.exists() else {}
        ok, why = score(item, reply, rsvps)
        rows.append({"id": item["id"], "type": item["type"], "pass": ok, "why": why,
                     "calls": [(c["tool"], c["ok"]) for c in reply.calls], "said": reply.text})
        print(f"{'PASS' if ok else 'FAIL'}  {item['id']} {item['type']:<12} {'; '.join(why)}")
    rate = sum(r["pass"] for r in rows) / len(rows)
    mode = "offline" if os.environ.get("CAMPUSPULSE_OFFLINE") == "1" else "live"
    result = {"mode": mode, "pass_rate": rate, "threshold": spec["threshold"], "items": rows}
    out = HERE / "results" / f"{datetime.now():%Y-%m-%d-%H%M}-tools-{mode}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"\npass rate {rate:.2f} (threshold {spec['threshold']}) · saved {out.relative_to(HERE.parent)}")
    return result


if __name__ == "__main__":
    r = run()
    sys.exit(0 if r["pass_rate"] >= r["threshold"] else 1)
