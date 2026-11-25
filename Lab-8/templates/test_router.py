"""Lab 8 tests: copy to tests/test_router.py. Three tests, all offline: the "provider" is a small
function written here, so each test decides exactly which model is down. No key, no cost.

Nothing to adapt unless your CHAINS has no "chat" job: then change JOB.
The CampusPulse versions, with four more tests: Lab-8/examples/campuspulse-router/tests/test_router.py
"""
import pytest

from src import router
from src.router import CACHE, CHAINS, SORRY, complete, summary

JOB = "chat"                                            # ADAPT only if your CHAINS has other job names
QUESTION = [{"role": "user", "content": "a question your product gets every day"}]
FIRST, SECOND = CHAINS[JOB][0], CHAINS[JOB][1]          # fails here? your chain needs two models


class Down(Exception):
    status_code = 503


class OurBug(Exception):
    status_code = 400


def models(down=(), error=Down):
    """A fake provider. Models named in `down` raise; the others answer with their own name."""
    def call(messages, tools, timeout=None, model=None):
        if model in down:
            raise error(f"{model} is down")
        return {"content": f"answered by {model}", "tool_calls": [], "usage": {"cost_usd": 0.001}}
    return call


@pytest.fixture(autouse=True)
def clean(tmp_path, monkeypatch):
    CACHE.clear()
    monkeypatch.setattr(router, "LOG", tmp_path / "router.jsonl")     # tests never touch your real log


def test_the_second_model_answers_when_the_first_is_down():
    answer = complete(QUESTION, job=JOB, call=models(down=[FIRST]))
    assert answer["content"] == f"answered by {SECOND}"
    assert summary()["answered_by_a_fallback"] == 1               # and the log says so


def test_everything_down_gives_a_sentence_not_a_stack_trace():
    answer = complete(QUESTION, job=JOB, call=models(down=CHAINS[JOB]))
    assert answer["content"] == SORRY and answer["degraded"] and answer["tool_calls"] == []
    assert not CACHE                                              # an apology is never cached


def test_our_own_bug_is_raised_not_hidden_by_the_next_model():
    with pytest.raises(OurBug):
        complete(QUESTION, job=JOB, call=models(down=[FIRST], error=OurBug))
