from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_week_39_returns_only_confirmed_events():             # AC2
    r = client.get("/events?week=39")
    assert r.status_code == 200
    assert [e["id"] for e in r.json()] == ["ev-101", "ev-102"]   # not tentative ev-103, not cancelled ev-104


def test_week_with_no_events_returns_empty_list():
    r = client.get("/events?week=12")
    assert r.status_code == 200 and r.json() == []


def test_week_out_of_range_is_422_with_field():                 # AC3
    r = client.get("/events?week=54")
    assert r.status_code == 422
    assert r.json() == {"error": "week must be between 1 and 53", "field": "week"}


def test_week_not_a_number_uses_our_error_shape():             # AC3, and the AGENTS.md error convention
    r = client.get("/events?week=abc")
    assert r.status_code == 422
    assert set(r.json()) == {"error", "field"} and r.json()["field"] == "week"
