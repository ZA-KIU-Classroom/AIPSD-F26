"""The Week 5 live demos. Offline, no key, deterministic. Run from the example root.

    python -m demo.tool_demo naive      three bad tool calls, run by a naive executor: it crashes, it RSVPs
                                        the wrong student, it lets a visitor write
    python -m demo.tool_demo contract   the same three calls through src/act.py: each one is stopped,
                                        the model reads why, and the first one gets repaired
    python -m demo.tool_demo mcp        the MCP door: annotations, the rsvp schema with no student field,
                                        and a spoofed student argument that changes nothing

The "model" here is scripted so the demo cannot surprise us on stage. Each script is what real
models do on a bad day: a garbled argument, an extra field, a tool the caller should not have.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from types import SimpleNamespace

os.environ.setdefault("CAMPUSPULSE_OFFLINE", "1")
os.environ.setdefault("CAMPUSPULSE_TODAY", "2026-10-21")
_tmp = tempfile.mkdtemp(prefix="campuspulse-demo-")
os.environ.setdefault("CAMPUSPULSE_STATE_DIR", _tmp)
os.environ.setdefault("CAMPUSPULSE_TOOL_LOG", os.path.join(_tmp, "tools.jsonl"))

from src import offline, tools  # noqa: E402
from src.act import act  # noqa: E402

BAD_CALLS = {
    "garbled": (None, "Is B204 free tomorrow at six?",
                {"name": "check_room", "arguments": '{"room": "Lab B204; DROP TABLE bookings", "date": "2026-10-22", "start": "18:00"}'},
                {"name": "check_room", "arguments": '{"room": "B204", "date": "2026-10-22", "start": "18:00"}'}),
    "spoof": ("s123", "Save me a seat at Open Build Night, ev-201.",
              {"name": "rsvp", "arguments": '{"event_id": "ev-201", "student": "s999"}'}, None),
    "visitor": (None, "RSVP me to ev-202.",
                {"name": "rsvp", "arguments": '{"event_id": "ev-202"}'}, None),
}


def scripted_model(first: dict, fix: dict | None):
    """Turn 1: the bad call. After an error: the fix if there is one, else a plain explanation."""
    def model(messages: list[dict], schemas: list[dict]) -> dict:
        results = [json.loads(m["content"]) for m in messages if m["role"] == "tool"]
        if not results:
            return {"content": None, "tool_calls": [{"id": "call_1", **first}]}
        if "error" in results[-1] and fix and len(results) == 1:
            return {"content": None, "tool_calls": [{"id": "call_2", **fix}]}
        return {"content": offline._say(results[-1]), "tool_calls": []}
    return model


def naive() -> None:
    """What a first attempt usually looks like: json.loads, then call the function. No contract."""
    print("NAIVE EXECUTOR: tool = TOOLS[name]; tool.run(**json.loads(arguments))\n")
    for label, (student, question, call, _) in BAD_CALLS.items():
        args = json.loads(call["arguments"])
        print(f"[{label}] caller={student or 'not signed in'} · model calls {call['name']}({args})")
        try:
            fn = tools.TOOLS[call["name"]]
            if fn.writes:   # the naive code trusts the model's student, or invents one
                out = fn.run(SimpleNamespace(**args), student=args.get("student", student or "anonymous"))
            else:
                out = fn.run(SimpleNamespace(**args))
            print(f"   RAN: {out.model_dump(mode='json')}")
            if label == "spoof":
                print("   ^ an RSVP was written for s999, a student who never asked.")
            if label == "visitor":
                print("   ^ an anonymous visitor just wrote to the RSVP list.")
        except Exception as e:
            print(f"   CRASH: {type(e).__name__}: {e}  -> the student sees a 500 error")
        print()


def contract() -> None:
    print("CONTRACT: src/act.py · offered? valid? then run, with identity from the server\n")
    for label, (student, question, call, fix) in BAD_CALLS.items():
        reply = act(question, student=student, llm=scripted_model(call, fix))
        print(f"[{label}] caller={student or 'not signed in'} · {question}")
        for c in reply.calls:
            state = "ran" if c["ok"] else f"refused: {c['error']}"
            print(f"   {c['tool']}({c['arguments']}) -> {state}")
        print(f"   student sees: {reply.text}\n")
    print(f"Every line above is in {os.environ['CAMPUSPULSE_TOOL_LOG']}")


def mcp_door() -> None:
    from mcp import Client
    from src.mcp_server import mcp
    os.environ.setdefault("CAMPUSPULSE_STUDENT", "s123")

    async def run() -> None:
        async with Client(mcp) as client:
            listed = (await client.list_tools()).tools
            print("TOOLS THE HOST SEES")
            for t in listed:
                kind = "reads" if t.annotations.read_only_hint else "adds, never deletes"
                print(f"   {t.name:<20} {kind:<20} args: {', '.join(t.input_schema['properties'])}")
            print("\nThe model sends rsvp(event_id='ev-201', student='s999'):")
            r = await client.call_tool("rsvp", {"event_id": "ev-201", "student": "s999"})
            print(f"   result: {r.structured_content}")
            print(f"   stored under: {tools.student_key('s123')} = hash of s123, the signed-in student. "
                  f"s999 was ignored.")

    asyncio.run(run())


if __name__ == "__main__":
    {"naive": naive, "contract": contract, "mcp": mcp_door}[sys.argv[1] if len(sys.argv) > 1 else "contract"]()
