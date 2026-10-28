"""One conversational turn: remembered context in, streamed answer out, state written back.

The turn (Week 6, Chapters 2 and 4):
  1. build the context: the system prompt with this student's interests, the last few turns of
     THIS session, then the new question. Context as Budget: six turns, ten interests, no more.
  2. stream the model's reply to the caller as it arrives.
  3. if the model asked for a tool, run it through Week 5's call_tool() (offered? valid?
     identity from us) and stream one more round with the result. One round, not three: a
     chat turn is a conversation, not a plan.
  4. write back the two turns, and only the two turns. Interests are written only by the
     remember_interest tool, which the student has to ask for.

Every turn yields events the endpoint turns into SSE: ("token", text), ("tool", outcome),
("done", summary). The summary carries time to first token and cost so the UI can show them.
"""
from __future__ import annotations

import json
from typing import Iterator

from .act import as_assistant, call_tool
from .llm import cost_usd, stream
from .memory import add_turn, interests, recent_turns
from .tools import today, tools_for

SYSTEM = """You are CampusPulse, the events assistant for Kutaisi International University.
Answer in two or three short sentences. Use a tool when the question needs live data or an action.
If the student asks you to remember an interest and you have the remember_interest tool, call it
once with the interest in two or three plain words; never remember anything they did not ask you to.
Known interests: {interests}
Today is {today}. Times are Kutaisi time."""


def build_messages(session: str | None, student: str | None, question: str) -> list[dict]:
    known = ", ".join(interests(student)) if student else "none"
    msgs = [{"role": "system", "content": SYSTEM.format(interests=known or "none", today=today().isoformat())}]
    if session:
        msgs += recent_turns(session)                       # scope: this session only
    msgs.append({"role": "user", "content": question})
    return msgs


def chat_turn(question: str, session: str | None = None, student: str | None = None,
              llm=stream) -> Iterator[tuple[str, object]]:
    allowed = tools_for(student)
    schemas = [t.schema() for t in allowed.values()]
    messages = build_messages(session, student, question)
    calls: list[dict] = []
    s = llm(messages, schemas)
    for piece in s:
        yield "token", piece
    if s.tool_calls:                                        # the model asked; our code decides
        messages.append(as_assistant({"content": s.text or None, "tool_calls": s.tool_calls,
                                      "reasoning_details": s.reasoning_details}))
        for call in s.tool_calls:
            outcome = call_tool(call, allowed, student)
            calls.append(outcome)
            yield "tool", {"tool": outcome["tool"], "ok": outcome["ok"], "error": outcome["error"]}
            messages.append({"role": "tool", "tool_call_id": call["id"],
                             "content": json.dumps(outcome.get("result") or {"error": outcome["error"]})})
        s2 = llm(messages, schemas)
        for piece in s2:
            yield "token", piece
        answer, streams = s2.text, [s, s2]
    else:
        answer, streams = s.text, [s]
    if session:
        add_turn(session, "user", question)
        add_turn(session, "assistant", answer)
    usage = [(x.usage.prompt_tokens, x.usage.completion_tokens) for x in streams if x.usage]
    yield "done", {"ttft_ms": s.ttft_ms, "calls": len(calls),
                   "tokens_in": sum(u[0] for u in usage), "tokens_out": sum(u[1] for u in usage),
                   "cost_usd": round(sum(cost_usd(_model(), *u) for u in usage), 6),
                   "remembered": bool(student) and bool(interests(student))}


def _model() -> str:
    from . import llm
    return llm.CHAT_MODEL if not llm.OFFLINE else llm.offline.MODEL


def answer_text(question: str, session: str | None = None, student: str | None = None) -> str:
    """The non-streamed convenience used by the voice path: the whole answer as one string."""
    return "".join(piece for kind, piece in chat_turn(question, session, student) if kind == "token").strip()
