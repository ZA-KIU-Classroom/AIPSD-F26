from types import SimpleNamespace

import numpy as np
from fastapi.testclient import TestClient

from src import llm


class FakeClient:
    """Stands in for the OpenAI SDK client. Records what we sent."""
    def __init__(self):
        self.sent = {}
        usage = SimpleNamespace(prompt_tokens=1000, completion_tokens=200)
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._chat))
        self.embeddings = SimpleNamespace(create=self._embed)
        self._usage = usage

    def _chat(self, **kw):
        self.sent["chat"] = kw
        msg = SimpleNamespace(content='{"answer": "ok [1].", "citations": [1], "grounded": true}')
        return SimpleNamespace(model="google/gemini-3.8-flash", usage=self._usage,
                               choices=[SimpleNamespace(message=msg)])

    def _embed(self, **kw):
        self.sent["embed"] = kw
        data = [SimpleNamespace(embedding=[3.0, 4.0]) for _ in kw["input"]]
        return SimpleNamespace(model="openai/text-embedding-3-small",
                               usage=SimpleNamespace(prompt_tokens=12, completion_tokens=0), data=data)


def live(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr(llm, "OFFLINE", False)
    monkeypatch.setattr(llm, "_client", fake)
    return fake


def test_cost_uses_the_verified_prices():
    assert llm.cost_usd("google/gemini-3.8-flash", 1_000_000, 0) == 0.75
    assert llm.cost_usd("google/gemini-3.8-flash", 0, 1_000_000) == 3.75
    assert llm.cost_usd("openai/text-embedding-3-small", 1_000_000, 0) == 0.02


def test_text_only_call_sends_no_image_part(monkeypatch):
    fake = live(monkeypatch)
    out = llm.complete_json("question", schema={"type": "object"})
    content = fake.sent["chat"]["messages"][0]["content"]
    assert [p["type"] for p in content] == ["text"]
    assert fake.sent["chat"]["temperature"] == 0
    assert out["grounded"] is True


def test_lab3_style_image_call_still_works(monkeypatch):
    fake = live(monkeypatch)
    llm.complete_json("read this poster", image=b"\xff\xd8", schema={"type": "object"})
    content = fake.sent["chat"]["messages"][0]["content"]
    assert content[1]["image_url"]["url"].startswith("data:image/jpeg;base64,")


def test_embed_returns_unit_vectors_and_logs_cost(monkeypatch):
    fake = live(monkeypatch)
    v = llm.embed(["a", "b"])
    assert fake.sent["embed"]["model"] == llm.EMBED_MODEL
    assert v.shape == (2, 2) and np.allclose(v[0], [0.6, 0.8])


def test_ask_endpoint(index, monkeypatch):
    from src import app as app_module
    app_module.index.cache_clear()
    monkeypatch.setattr(app_module, "load", lambda: index)
    client = TestClient(app_module.app)
    r = client.post("/ask", json={"question": "What is the Wi-Fi password for the library?"})
    assert r.status_code == 200 and r.json()["status"] == "refused"
    assert client.post("/ask", json={"question": ""}).status_code == 422
