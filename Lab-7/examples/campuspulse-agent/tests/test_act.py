"""The function-calling loop: offered? valid? then run, with identity from the server."""
import json
import os

from src.act import MAX_ROUNDS, act, call_tool
from src.tools import tools_for


def call(name, **args):
    return {"id": "c1", "name": name, "arguments": json.dumps(args)}


def test_valid_call_runs_and_returns_data():
    out = call_tool(call("check_room", room="B204", date="2026-10-29", start="15:00"), tools_for(None), None)
    assert out["ok"] and out["result"]["free"] is True


def test_invalid_arguments_never_reach_the_tool():
    out = call_tool(call("check_room", room="B204; DROP", date="2026-10-29", start="15:00"), tools_for(None), None)
    assert not out["ok"] and out["error"].startswith("invalid arguments: room")


def test_a_tool_not_offered_is_not_run():
    out = call_tool(call("rsvp", event_id="ev-201"), tools_for(None), None)
    assert not out["ok"] and "no tool named 'rsvp'" in out["error"]


def test_a_tool_that_does_not_exist_is_not_run():
    out = call_tool(call("delete_all_rsvps"), tools_for("s123"), "s123")
    assert not out["ok"]


def test_model_cannot_choose_the_student():
    out = call_tool(call("rsvp", event_id="ev-201", student="s999"), tools_for("s123"), "s123")
    assert not out["ok"] and "student" in out["error"]


def test_every_call_writes_one_log_line_without_the_student_id():
    log = os.environ["CAMPUSPULSE_TOOL_LOG"]
    before = open(log).read().count("\n") if os.path.exists(log) else 0
    call_tool(call("rsvp", event_id="ev-201"), tools_for("s123"), "s123")
    lines = open(log).read().splitlines()
    assert len(lines) == before + 1
    last = json.loads(lines[-1])
    assert last["tool"] == "rsvp" and last["ok"] and last["student"] != "s123"


def test_end_to_end_offline_answer():
    reply = act("Is B204 free on 2026-10-29 at 15:00 for 90 minutes?")
    assert reply.status == "answered" and "free" in reply.text and reply.calls[0]["ok"]


def test_visitor_asking_to_rsvp_is_told_to_sign_in():
    reply = act("Please RSVP me to ev-201")
    assert reply.calls == [] and "sign in" in reply.text


def test_the_model_reads_the_error_and_can_repair():
    turns = []

    def model(messages, schemas):
        turns.append(messages[-1]["role"])
        if len(turns) == 1:
            return {"content": None, "tool_calls": [call("check_room", room="b204", date="2026-10-29", start="15:00")]}
        if len(turns) == 2:
            assert "invalid arguments" in json.loads(messages[-1]["content"])["error"]
            return {"content": None, "tool_calls": [call("check_room", room="B204", date="2026-10-29", start="15:00")]}
        return {"content": "B204 is free.", "tool_calls": []}

    reply = act("Is B204 free?", llm=model)
    assert reply.text == "B204 is free." and [c["ok"] for c in reply.calls] == [False, True]


def test_loop_stops_after_the_budget():
    def stubborn(messages, schemas):
        return {"content": None, "tool_calls": [call("check_room", room="nope", date="x", start="y")]}

    reply = act("Is B204 free?", llm=stubborn)
    assert reply.status == "stopped" and len(reply.calls) == MAX_ROUNDS


def test_reasoning_details_are_echoed_back():
    seen = []

    def model(messages, schemas):
        seen.append(messages)
        if len(seen) == 1:
            return {"content": None, "reasoning_details": [{"type": "reasoning.encrypted", "data": "x"}],
                    "tool_calls": [call("list_events", from_date="2026-10-21")]}
        return {"content": "ok", "tool_calls": []}

    act("What's on?", llm=model)
    assistant = [m for m in seen[1] if m["role"] == "assistant"][0]
    assert assistant["reasoning_details"] == [{"type": "reasoning.encrypted", "data": "x"}]
