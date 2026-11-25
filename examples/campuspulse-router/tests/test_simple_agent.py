"""The 50-line loop from the lecture: it parks what needs a yes, and it stops."""
import json

import pytest

from src import memory
from src.simple_agent import PENDING, confirm, run
from src.tools import _rsvps


@pytest.fixture(autouse=True)
def week_seven(monkeypatch):
    monkeypatch.setenv("CAMPUSPULSE_TODAY", "2026-11-18")
    memory.remember_interest("s123", "tech talks")
    memory.remember_interest("s123", "free food")
    PENDING.clear()


def test_the_gate_blocks_until_a_person_says_yes():
    plan = run("Plan my week", "s123")
    assert plan["status"] == "needs_confirmation" and len(plan["proposed"]) == 4
    assert _rsvps() == {}                                  # proposed is not done
    done = confirm("s123", ["a1"])                         # yes to the first one only
    assert [d["ok"] for d in done] == [True]
    assert list(_rsvps()) == ["ev-206"]                    # exactly what was approved
    assert confirm("s123", ["a1", "a2"]) == []             # and a plan works once


def test_the_loop_stops_after_max_steps():
    def never_done(messages, schemas):                     # a model that always wants one more look
        return {"content": None, "tool_calls": [
            {"id": f"c{len(messages)}", "name": "list_events", "arguments": json.dumps({"from_date": "2026-11-18"})}]}

    plan = run("Plan my week", "s123", llm=never_done, max_steps=4)
    assert plan["status"] == "stopped" and "4 steps" in plan["text"]
    assert _rsvps() == {}


def test_the_loop_only_gets_the_tools_on_its_list():
    seen = []

    def model(messages, schemas):
        seen.extend(s["function"]["name"] for s in schemas)
        return {"content": "done", "tool_calls": []}

    run("Plan my week", "s123", llm=model)
    assert sorted(seen) == ["list_events", "make_calendar_file", "rsvp"]
