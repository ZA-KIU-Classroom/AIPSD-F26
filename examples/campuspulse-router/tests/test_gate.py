"""The confirmation gate (Week 7): proposed is not done; a yes runs exactly what was shown,
once, for the student who was shown it, while it is fresh."""
import json
import os
import sqlite3

import pytest
from fastapi.testclient import TestClient

from src import memory
from src.agent import run
from src.app import app
from src.gate import confirm, propose
from src.tools import TOOLS, _rsvps, student_key, timetable

client = TestClient(app)
NINO = {"X-Student-Id": "s123"}


@pytest.fixture(autouse=True)
def week_seven(monkeypatch):
    monkeypatch.setenv("CAMPUSPULSE_TODAY", "2026-11-18")
    memory.remember_interest("s123", "tech talks")
    memory.remember_interest("s123", "free food")


def ask(event_id, student="s123"):
    return propose({"id": "c1", "name": "rsvp", "arguments": json.dumps({"event_id": event_id})},
                   TOOLS["rsvp"], student, timetable(student))


def test_propose_describes_the_action_and_writes_nothing():
    action, seen = ask("ev-206")
    assert action["tool"] == "rsvp" and action["arguments"] == '{"event_id":"ev-206"}'
    assert "Thu 19 Nov, 18:00 to 19:30" in action["summary"] and "NOT booked" in seen["status"]
    assert _rsvps() == {}


def test_propose_refuses_a_clash_a_full_event_and_bad_arguments():
    assert "clashes with the student's class" in ask("ev-207")[1]["error"]
    assert "is full" in ask("ev-210")[1]["error"]
    assert "invalid arguments: event_id" in ask("ev-206; drop")[1]["error"]
    assert all(ask(e)[0] is None for e in ("ev-207", "ev-210", "ev-999"))


def test_the_gate_blocks_until_the_student_says_yes():
    r = run("Plan my week", student="s123")
    assert _rsvps() == {}                                            # blocked
    done = confirm("s123", r.plan_id, [r.proposed[0]["id"]])         # yes to one of two
    assert [x["ok"] for x in done["ran"]] == [True] and len(done["skipped"]) == 1
    assert _rsvps() == {"ev-206": [student_key("s123")]}             # exactly what was approved


def test_scope_another_student_cannot_confirm_my_plan():
    r = run("Plan my week", student="s123")
    assert confirm("s999", r.plan_id, [a["id"] for a in r.proposed]) is None
    assert _rsvps() == {}


def test_lifetime_a_plan_cannot_be_confirmed_after_15_minutes(monkeypatch):
    monkeypatch.setenv("CAMPUSPULSE_NOW", "2026-11-18T09:00:00+00:00")
    r = run("Plan my week", student="s123")
    monkeypatch.setenv("CAMPUSPULSE_NOW", "2026-11-18T09:15:01+00:00")
    assert confirm("s123", r.plan_id, [a["id"] for a in r.proposed]) is None
    assert _rsvps() == {} and memory.expire() == 1


def test_a_plan_is_single_use_and_a_new_plan_replaces_the_old_one():
    first = run("Plan my week", student="s123")
    second = run("Plan my week", student="s123")
    assert confirm("s123", first.plan_id, [first.proposed[0]["id"]]) is None      # stale card
    assert confirm("s123", second.plan_id, []) == {"ran": [], "skipped": [a["summary"] for a in second.proposed]}
    assert confirm("s123", second.plan_id, [second.proposed[0]["id"]]) is None    # already used


def test_deletion_forget_me_removes_a_pending_plan():
    r = run("Plan my week", student="s123")
    assert memory.forget("s123", None).to_dict() == {"interests": 2, "turns": 0, "plans": 1}
    assert confirm("s123", r.plan_id, [a["id"] for a in r.proposed]) is None
    db = sqlite3.connect(os.path.join(os.environ["CAMPUSPULSE_STATE_DIR"], "memory.db"))
    assert db.execute("SELECT count(*) FROM memory").fetchone()[0] == 0


def test_endpoints_plan_confirm_decline():
    r = client.post("/plan", json={"goal": "Plan my week"}, headers=NINO).json()
    assert r["status"] == "needs_confirmation" and len(r["proposed"]) == 2 and len(r["rejected"]) == 2
    ids = [a["id"] for a in r["proposed"]]
    assert client.post(f"/plan/{r['plan_id']}/confirm", json={"approve": ids}).status_code == 401
    ok = client.post(f"/plan/{r['plan_id']}/confirm", json={"approve": ids}, headers=NINO)
    assert ok.status_code == 200 and [x["ok"] for x in ok.json()["ran"]] == [True, True]
    assert client.post(f"/plan/{r['plan_id']}/confirm", json={"approve": ids}, headers=NINO).status_code == 410
    again = client.post("/plan", json={"goal": "Plan my week"}, headers=NINO).json()
    assert again["proposed"] == [] and "already registered" in again["rejected"][0]["error"]
    third = client.post("/plan", json={"goal": "Plan my week"}, headers={"X-Student-Id": "s999"}).json()
    assert third["plan_id"] is None                                  # s999 has no interests on file
    assert client.delete("/plan/whatever", headers=NINO).json() == {"dropped": 0}
