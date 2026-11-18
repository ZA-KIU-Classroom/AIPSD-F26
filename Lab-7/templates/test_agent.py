"""Lab 7 tests: copy to tests/test_agent.py. Two tests, both offline: the "model" is a small
function you write here, so you decide exactly what it asks for.

Change the three lines marked ADAPT. Test 1 is your checkpoint. Test 2 passes as soon as test 1 does.
The CampusPulse versions: Lab-7/examples/campuspulse-agent/tests/test_simple_agent.py
"""
import json

from src.agent import PENDING, confirm, run

USER = "s123"                                           # ADAPT 1: a signed-in test user in your product
NEEDS_A_YES = ("rsvp", {"event_id": "ev-206"})          # ADAPT 2: one call to a tool in your NEEDS_YES


def what_changed():
    """ADAPT 3: return what your consequential tool changes: a file, a table, an outbox.
    It must be empty (or unchanged) before the yes."""
    from src.tools import _rsvps
    return _rsvps()


def scripted(*turns):
    """A fake model: each turn is either a list of (tool, arguments) calls, or the final text."""
    left = list(turns)

    def model(messages, schemas):
        turn = left.pop(0)
        if isinstance(turn, str):
            return {"content": turn, "tool_calls": []}
        return {"content": None, "tool_calls": [
            {"id": f"c{len(messages)}-{i}", "name": name, "arguments": json.dumps(args)} for i, (name, args) in enumerate(turn)]}
    return model


def test_the_gate_blocks_until_a_person_says_yes():
    PENDING.clear()
    before = what_changed()
    plan = run("do it for me", USER, llm=scripted([NEEDS_A_YES], "I proposed one action."))
    assert plan["status"] == "needs_confirmation" and len(plan["proposed"]) == 1
    assert what_changed() == before                         # proposed is not done
    done = confirm(USER, [plan["proposed"][0]["id"]])
    assert done[0]["ok"] and what_changed() != before       # the yes is what did it
    assert confirm(USER, [plan["proposed"][0]["id"]]) == [] # and a plan works once


def test_the_loop_stops_after_max_steps():
    PENDING.clear()
    before = what_changed()
    forever = scripted(*[[NEEDS_A_YES]] * 10)               # a model that never says "done"
    plan = run("do it for me", USER, llm=forever, max_steps=4)
    assert plan["status"] == "stopped" and "4 steps" in plan["text"]
    assert what_changed() == before                         # stopping early does nothing, either
