"""Streaming and the chat turn: tokens arrive as pieces, usage is logged once, tools go through the gates."""
import json
import os

from src import memory
from src.chat import build_messages, chat_turn
from src.llm import stream
from src.tools import tools_for


def schemas(student=None):
    return [t.schema() for t in tools_for(student).values()]


def test_stream_yields_pieces_and_logs_time_to_first_token():
    log = os.environ["CAMPUSPULSE_USAGE_LOG"]
    before = open(log).read().count("\n") if os.path.exists(log) else 0
    s = stream([{"role": "user", "content": "what's on this week?"}], schemas())
    pieces = list(s)
    assert len(pieces) > 3 and "".join(pieces) == s.text and "Open Build Night" in s.text
    assert s.tool_calls == [] and s.usage.prompt_tokens > 0
    lines = open(log).read().splitlines()
    assert len(lines) == before + 1
    last = json.loads(lines[-1])
    assert last["kind"] == "stream" and last["ttft_ms"] is not None and last["ttft_ms"] >= 0


def test_stream_collects_tool_call_fragments():
    s = stream([{"role": "user", "content": "remember that I like tech talks"}], schemas("s123"))
    assert list(s) == []                                        # a tool turn carries no text
    assert s.tool_calls == [{"id": "call_1", "name": "remember_interest",
                             "arguments": json.dumps({"topic": "tech talks"})}]


def test_chat_turn_remembers_only_when_asked_and_only_for_a_student():
    events = list(chat_turn("remember that I like tech talks", session="sess-a", student="s123"))
    kinds = [k for k, _ in events]
    assert kinds.count("tool") == 1 and kinds[-1] == "done"
    tool = next(p for k, p in events if k == "tool")
    assert tool == {"tool": "remember_interest", "ok": True, "error": None}
    assert memory.interests("s123") == ["tech talks"]
    assert "Remembered" in "".join(p for k, p in events if k == "token")
    assert events[-1][1]["calls"] == 1 and events[-1][1]["remembered"] is True


def test_a_visitor_cannot_write_memory_even_by_asking():
    events = list(chat_turn("remember that I like tech talks", session="sess-v", student=None))
    assert not any(k == "tool" for k, _ in events)
    assert "sign in" in "".join(p for k, p in events if k == "token")


def test_remembered_interests_shape_the_next_answer():
    memory.remember_interest("s123", "tech talks")
    msgs = build_messages("sess-a", "s123", "what's on?")
    assert "Known interests: tech talks" in msgs[0]["content"]
    text = "".join(p for k, p in chat_turn("what's on this week?", "sess-a", "s123") if k == "token")
    assert text.startswith("Since you like tech talks")


def test_another_students_interests_are_not_in_my_prompt():
    memory.remember_interest("s999", "chess")
    msgs = build_messages("sess-a", "s123", "what's on?")
    assert "chess" not in msgs[0]["content"] and "Known interests: none" in msgs[0]["content"]


def test_turns_are_written_back_and_fed_forward():
    list(chat_turn("what's on this week?", session="sess-a", student=None))
    msgs = build_messages("sess-a", None, "and the day after?")
    roles = [m["role"] for m in msgs]
    assert roles == ["system", "user", "assistant", "user"]
    assert msgs[1]["content"] == "what's on this week?"


def test_done_event_carries_cost_and_tokens():
    done = list(chat_turn("what's on this week?"))[-1][1]
    assert done["tokens_in"] > 0 and done["tokens_out"] > 0 and done["cost_usd"] == 0.0   # offline model is free
