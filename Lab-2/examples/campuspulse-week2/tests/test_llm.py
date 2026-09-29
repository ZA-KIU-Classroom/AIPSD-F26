import json
import logging
from types import SimpleNamespace

from src import llm


def test_every_model_call_logs_usage(monkeypatch, caplog):            # AC4
    fake_resp = SimpleNamespace(
        usage=SimpleNamespace(prompt_tokens=1000, completion_tokens=200),
        choices=[SimpleNamespace(message=SimpleNamespace(content="Two events this week."))],
    )
    fake_client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kw: fake_resp)))
    monkeypatch.setattr(llm, "client", lambda: fake_client)

    with caplog.at_level(logging.INFO, logger="campuspulse.llm"):
        answer, usage = llm.chat("system", "question")

    assert answer == "Two events this week."
    logged = json.loads(caplog.records[-1].getMessage().split("model_call ", 1)[1])
    assert set(logged) == {"model", "tokens_in", "tokens_out", "cost_usd", "latency_ms"}
    assert logged["tokens_in"] == 1000 and logged["tokens_out"] == 200
    assert logged["cost_usd"] == round((1000 * llm.PRICE_IN_PER_M + 200 * llm.PRICE_OUT_PER_M) / 1_000_000, 6)
