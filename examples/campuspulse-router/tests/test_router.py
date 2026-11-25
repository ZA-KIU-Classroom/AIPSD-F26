"""Week 8: the fallback chain, tested offline. The "models" are small functions written here,
so each test decides exactly who is down. Lab-8/templates/test_router.py is this file with ADAPT marks."""
import pytest

from src import router
from src.router import CACHE, CHAINS, SORRY, complete, summary

QUESTION = [{"role": "user", "content": "What is on this week?"}]
FIRST, SECOND = CHAINS["chat"][0], CHAINS["chat"][1]


class Down(Exception):
    status_code = 503


class OurBug(Exception):
    status_code = 400


def models(down=(), error=Down):
    """A fake provider. Models named in `down` raise; the others answer with their own name."""
    asked = []

    def call(messages, tools, timeout=None, model=None):
        asked.append(model)
        if model in down:
            raise error(f"{model} is down")
        return {"content": f"answered by {model}", "tool_calls": [], "usage": {"cost_usd": 0.001}}
    call.asked = asked
    return call


@pytest.fixture(autouse=True)
def clean(tmp_path, monkeypatch):
    CACHE.clear()
    monkeypatch.setattr(router, "LOG", tmp_path / "router.jsonl")


def test_the_first_model_answers_when_it_is_up():
    call = models()
    assert complete(QUESTION, call=call)["content"] == f"answered by {FIRST}"
    assert call.asked == [FIRST]                                  # the second model was never paid


def test_the_second_model_answers_when_the_first_is_down():
    call = models(down=[FIRST])
    assert complete(QUESTION, call=call)["content"] == f"answered by {SECOND}"
    assert summary()["answered_by_a_fallback"] == 1               # and the log says so


def test_everything_down_gives_a_sentence_not_a_stack_trace():
    answer = complete(QUESTION, call=models(down=CHAINS["chat"]))
    assert answer["content"] == SORRY and answer["degraded"] and answer["tool_calls"] == []
    assert not CACHE                                              # an apology is never cached


def test_our_own_bug_is_raised_not_hidden_by_the_next_model():
    call = models(down=[FIRST], error=OurBug)
    with pytest.raises(OurBug):
        complete(QUESTION, call=call)
    assert call.asked == [FIRST]


def test_the_same_question_is_paid_for_once():
    call = models()
    first, second = complete(QUESTION, call=call), complete(QUESTION, call=call)
    assert first == second and len(call.asked) == 1
    other = [{"role": "user", "content": "What is on next week?"}]
    complete(other, call=call)
    assert len(call.asked) == 2                                   # a different question is a different key
    assert summary()["answered_from_cache"] == 1 and summary()["saved_by_cache_usd"] == 0.001


def test_a_turn_that_offers_tools_is_never_cached():
    call, tools = models(), [{"type": "function", "function": {"name": "rsvp"}}]
    complete(QUESTION, tools, call=call)
    complete(QUESTION, tools, call=call)
    assert len(call.asked) == 2


def test_the_week_7_loop_runs_through_the_chain():
    """One argument changes: llm=complete. The planner now survives its first model being down."""
    from src import memory
    from src.llm import complete_tools
    from src.simple_agent import run
    memory.remember_interest("s123", "tech talks")

    def first_is_down(messages, tools, timeout=None, model=None):
        if model == FIRST:
            raise TimeoutError("no reply in 12 s")
        return complete_tools(messages, tools, timeout=timeout, model=model)

    plan = run("Plan my week", "s123", llm=lambda m, s: complete(m, s, call=first_is_down))
    assert plan["status"] == "needs_confirmation" and plan["proposed"]
    assert summary()["answered_by_a_fallback"] >= 2 and summary()["sorry_message"] == 0
