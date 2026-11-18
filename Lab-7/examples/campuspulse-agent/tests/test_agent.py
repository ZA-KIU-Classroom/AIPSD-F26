"""The Supervised Autonomy Loop (Week 7): it finishes a plan, it stays inside its budget,
it survives a flaky model, and it never books anything on its own."""
import json
import os

import pytest

from src import memory
from src.agent import Budget, ModelUnavailable, call_model, perceive, run
from src.tools import _rsvps


@pytest.fixture(autouse=True)
def week_seven(monkeypatch):
    monkeypatch.setenv("CAMPUSPULSE_TODAY", "2026-11-18")          # Wednesday of Week 7
    memory.remember_interest("s123", "tech talks")
    memory.remember_interest("s123", "free food")


def call(name, **args):
    return {"id": f"c-{name}-{len(json.dumps(args))}", "name": name, "arguments": json.dumps(args)}


def reply(text=None, calls=(), cost=0.001):
    return {"content": text, "tool_calls": list(calls), "usage": {"tokens_in": 900, "tokens_out": 40, "cost_usd": cost}}


def test_perceive_reads_facts_with_code_not_a_model():
    seen = perceive("s123")
    assert seen["interests"] == ["tech talks", "free food"] and len(seen["classes"]) == 5
    assert perceive(None) == {"today": seen["today"], "interests": [], "classes": []}


def test_the_loop_completes_a_plan_and_books_nothing():
    r = run("Plan my week", student="s123")
    assert r.status == "needs_confirmation" and r.stop == "done" and r.steps == 3
    assert [a["arguments"] for a in r.proposed] == ['{"event_id":"ev-206"}', '{"event_id":"ev-209"}']
    assert _rsvps() == {}                                           # the gate: proposed is not booked


def test_the_gates_checks_refuse_what_the_model_did_not_check():
    r = run("Plan my week", student="s123")
    reasons = " | ".join(x["error"] for x in r.rejected)
    assert "ev-207" in reasons and "clashes with the student's class: Algorithms lab" in reasons
    assert "ev-210" in reasons and "is full" in reasons


def test_a_visitor_gets_suggestions_and_no_plan():
    r = run("Plan my week", student=None)
    assert r.status == "answered" and r.plan_id is None and r.proposed == []


def test_the_planner_is_never_offered_a_tool_outside_its_world():
    offered = []

    def model(messages, schemas, timeout=None):
        offered.extend(s["function"]["name"] for s in schemas)
        return reply("done")

    run("Plan my week", student="s123", llm=model)
    assert sorted(offered) == ["list_events", "make_calendar_file", "rsvp"]      # no remember_interest


def test_step_budget_stops_a_loop_that_never_finishes():
    days = iter(range(1, 99))

    def restless(messages, schemas, timeout=None):                  # always one more read
        return reply(calls=[call("list_events", from_date="2026-11-18", days=next(days) % 14 + 1)])

    r = run("Plan my week", student="s123", llm=restless, budget=Budget(max_steps=4))
    assert r.status == "stopped" and r.stop == "step budget (4)" and r.steps == 4
    assert "Nothing was booked" in r.text


def test_cost_budget_stops_the_loop():
    days = iter(range(1, 99))

    def pricey(messages, schemas, timeout=None):
        return reply(calls=[call("list_events", from_date="2026-11-18", days=next(days) % 14 + 1)], cost=0.009)

    r = run("Plan my week", student="s123", llm=pricey, budget=Budget(max_cost_usd=0.02))
    assert r.stop == "cost budget ($0.02)" and r.steps == 3         # 0.027 spent: stopped before a fourth turn


def test_the_same_call_twice_is_refused_not_repeated():
    turns = []

    def stuck(messages, schemas, timeout=None):
        turns.append(json.loads(messages[-1]["content"]) if messages[-1]["role"] == "tool" else None)
        return reply(calls=[call("list_events", from_date="2026-11-18")]) if len(turns) < 3 else reply("done")

    run("Plan my week", student="s123", llm=stuck)
    assert "events" in turns[1] and "already made this exact call" in turns[2]["error"]


def test_a_timeout_is_retried_with_backoff_and_then_succeeds():
    attempts, waits = [], []

    def flaky(messages, schemas, timeout=None):
        attempts.append(timeout)
        if len(attempts) < 3:
            raise TimeoutError("no reply in 12 s")
        return reply("done")

    out = call_model(flaky, [], [], Budget(), sleep=waits.append)
    assert out["content"] == "done" and attempts == [12.0, 12.0, 12.0]
    assert len(waits) == 2 and 0.5 <= waits[0] < 0.75 and 1.0 <= waits[1] < 1.25


def test_a_dead_model_stops_the_run_cleanly():
    def dead(messages, schemas, timeout=None):
        raise TimeoutError

    with pytest.raises(ModelUnavailable):
        call_model(dead, [], [], Budget(attempts=2), sleep=lambda s: None)
    r = run("Plan my week", student="s123", llm=dead, sleep=lambda s: None)
    assert r.status == "stopped" and "model unavailable" in r.stop and _rsvps() == {}


def test_a_bad_request_is_not_retried():
    attempts = []

    def wrong(messages, schemas, timeout=None):
        attempts.append(1)
        raise ValueError("400: malformed tool schema")

    with pytest.raises(ValueError):
        call_model(wrong, [], [], Budget(), sleep=lambda s: None)
    assert len(attempts) == 1


def test_every_step_is_in_the_trace_and_the_log_has_no_student_id():
    log = os.environ["CAMPUSPULSE_AGENT_LOG"]
    before = open(log).read().count("\n") if os.path.exists(log) else 0
    r = run("Plan my week", student="s123")
    lines = [json.loads(x) for x in open(log).read().splitlines()[before:]]
    assert [x["phase"] for x in lines] == ["reason", "act", "reason", "act", "act", "act", "act", "reason", "finish"]
    assert lines[-1]["status"] == "needs_confirmation" and lines[-1]["proposed"] == 2 and lines[-1]["rejected"] == 2
    assert all(x["run"] == r.id for x in lines) and "s123" not in open(log).read()
