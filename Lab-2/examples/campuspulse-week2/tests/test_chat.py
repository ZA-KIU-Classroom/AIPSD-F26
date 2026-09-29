from datetime import datetime

from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
USAGE = {"model": "test", "tokens_in": 420, "tokens_out": 60, "cost_usd": 0.000540, "latency_ms": 900}


def test_chat_returns_answer_event_ids_and_usage(monkeypatch):         # AC1, AC4
    seen = {}

    def fake_chat(system, user, max_tokens=300):
        seen["user"] = user
        return "Two events this week: the AI reading group and a film screening.", USAGE

    class FixedNow(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 9, 29, 12, 0, tzinfo=tz)              # ISO week 40

    monkeypatch.setattr(app_module.llm, "chat", fake_chat)
    monkeypatch.setattr(app_module, "datetime", FixedNow)
    r = client.post("/chat", json={"question": "What is on this week?"})
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"answer", "event_ids", "usage"}
    assert body["event_ids"] == ["ev-105", "ev-106"]
    assert body["usage"]["cost_usd"] > 0
    assert "ev-105" in seen["user"] and "ev-101" not in seen["user"]   # only this week's events reach the model
