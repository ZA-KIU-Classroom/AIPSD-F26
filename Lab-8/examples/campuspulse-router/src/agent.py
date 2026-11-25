"""The week planner: a Supervised Autonomy Loop (Week 7).

One goal in ("plan my week"), many steps, and a person at the one point where a wrong step
has a cost. The loop is Perceive, Reason, Act, Observe:

  PERCEIVE   code reads what is true right now: today, the student's interests (Week 6 memory),
             their timetable. No model is asked for anything code already knows.
  REASON     one model turn: given everything so far, which tool next, or are we done?
  ACT        a read runs through Week 5's call_tool(). A consequential action (rsvp) does NOT
             run: src/gate.py checks it and parks it in a plan for the student to confirm.
  OBSERVE    the result, the refusal, or "parked" goes back to the model as a tool message.

Four guardrails keep the loop honest:
  budget     steps, seconds and dollars, checked before every model turn
  timeout    one model call may take 12 seconds, not the SDK's default 10 minutes
  retry      only failures worth retrying (timeouts, 429, 5xx), with backoff and jitter
  gate       nothing consequential runs without a yes from the student

Every step writes one line to logs/agent.jsonl. That trace is the log half of the Evidence
Rule for a loop: you can replay what the agent saw, asked for, and was refused.
"""
from __future__ import annotations

import json
import os
import random
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from openai import APIConnectionError, APITimeoutError, InternalServerError, RateLimitError

from .act import as_assistant, call_tool
from .gate import propose
from .llm import complete_tools, ms_since
from .memory import interests, put_plan
from .tools import student_key, timetable, today, tools_for

AGENT_LOG = Path(os.environ.get("CAMPUSPULSE_AGENT_LOG", "logs/agent.jsonl"))
PLANNER_TOOLS = ("list_events", "make_calendar_file", "rsvp")      # the planner's whole world

SYSTEM = """You are CampusPulse's week planner for Kutaisi International University.
Goal: propose events in the student's next 7 days that match their interests and do not clash with their classes.
Work in steps. Call list_events first. Then call rsvp once for each event you recommend.
An rsvp call books nothing: it adds the event to a plan that the student must confirm.
If a tool returns an error, read it, then drop or replace that event. Never repeat the same call.
Finish with two or three sentences: what you proposed, what you left out and why. Never say an event is booked.
Known interests: {interests}
Classes this week:
{classes}
Today is {today}. Times are Kutaisi time."""


@dataclass
class Budget:
    max_steps: int = 6             # model turns in one run
    max_seconds: float = 45.0      # wall clock for the whole run
    max_cost_usd: float = 0.02     # two cents: about thirty ordinary chat turns
    call_timeout: float = 12.0     # one model call
    attempts: int = 3              # tries per model call

    def exceeded(self, steps: int, seconds: float, cost: float) -> str | None:
        if steps >= self.max_steps:
            return f"step budget ({self.max_steps})"
        if seconds >= self.max_seconds:
            return f"time budget ({self.max_seconds:.0f} s)"
        if cost >= self.max_cost_usd:
            return f"cost budget (${self.max_cost_usd})"
        return None


@dataclass
class Run:
    id: str
    goal: str
    status: str = "running"        # answered · needs_confirmation · stopped
    stop: str = ""                 # why the loop ended
    text: str = ""
    steps: int = 0
    cost_usd: float = 0.0
    plan_id: str | None = None
    proposed: list[dict] = field(default_factory=list)    # parked, waiting for a yes
    rejected: list[dict] = field(default_factory=list)    # refused by the gate's checks
    trace: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class ModelUnavailable(Exception):
    pass


RETRYABLE = (TimeoutError, APITimeoutError, APIConnectionError, RateLimitError, InternalServerError)


def call_model(llm, messages: list[dict], schemas: list[dict], budget: Budget, sleep=time.sleep) -> dict:
    """REASON, with a timeout, and retries only for failures that a retry can fix."""
    for attempt in range(1, budget.attempts + 1):
        try:
            return llm(messages, schemas, timeout=budget.call_timeout)
        except RETRYABLE as e:
            if attempt == budget.attempts:
                raise ModelUnavailable(f"{type(e).__name__}, {attempt} attempts") from e
            sleep(0.5 * 2 ** (attempt - 1) + random.uniform(0, 0.25))     # 0.5 s, 1 s, 2 s, plus jitter


def perceive(student: str | None) -> dict:
    """PERCEIVE: facts the code can read are read by code. The model is not asked to guess them."""
    return {"today": today(),
            "interests": interests(student) if student else [],
            "classes": timetable(student) if student else []}


def run(goal: str, student: str | None = None, llm=complete_tools, budget: Budget | None = None,
        sleep=time.sleep) -> Run:
    budget = budget or Budget()
    allowed = {n: t for n, t in tools_for(student).items() if n in PLANNER_TOOLS}
    schemas = [t.schema() for t in allowed.values()]
    seen = perceive(student)
    classes = "\n".join(f"- {c['day']} {c['start']} to {c['end']}: {c['what']}" for c in seen["classes"])
    messages = [{"role": "system", "content": SYSTEM.format(
                    interests=", ".join(seen["interests"]) or "none", classes=classes or "- none on file",
                    today=seen["today"].strftime("%A %Y-%m-%d"))},
                {"role": "user", "content": goal}]
    r, t0, asked = Run(id=uuid.uuid4().hex[:8], goal=goal), time.perf_counter(), set()
    while True:
        over = budget.exceeded(r.steps, time.perf_counter() - t0, r.cost_usd)
        if over:                                                       # a budget stop is a normal ending
            return _finish(r, "stopped", over, student)
        try:
            t1 = time.perf_counter()
            msg = call_model(llm, messages, schemas, budget, sleep)    # REASON
        except ModelUnavailable as e:
            return _finish(r, "stopped", f"model unavailable ({e})", student)
        r.steps += 1
        r.cost_usd = round(r.cost_usd + (msg.get("usage") or {}).get("cost_usd", 0.0), 6)
        _trace(r, "reason", ms=ms_since(t1), calls=len(msg["tool_calls"]), **(msg.get("usage") or {}))
        if not msg["tool_calls"]:                                      # the model says it is done
            r.text = msg["content"] or ""
            return _finish(r, "needs_confirmation" if r.proposed else "answered", "done", student)
        messages.append(as_assistant(msg))
        for call in msg["tool_calls"]:
            tool, key = allowed.get(call["name"]), (call["name"], call["arguments"])
            if key in asked:                                           # the same call twice is a loop
                seen_it = {"error": "You already made this exact call. Use the earlier result."}
                observation, ok, gated = seen_it, False, False
            elif tool is not None and tool.confirm:                    # ACT, consequential: park it
                action, observation = propose(call, tool, student, seen["classes"])
                ok, gated = action is not None, True
                (r.proposed if ok else r.rejected).append(action or {"call": call["arguments"], **observation})
            else:                                                      # ACT, a read: Week 5's gates
                outcome = call_tool(call, allowed, student)
                observation, ok, gated = outcome.get("result") or {"error": outcome["error"]}, outcome["ok"], False
            asked.add(key)
            _trace(r, "act", tool=call["name"], ok=ok, gated=gated)
            messages.append({"role": "tool", "tool_call_id": call["id"],           # OBSERVE
                             "content": json.dumps(observation)})


def _finish(r: Run, status: str, stop: str, student: str | None) -> Run:
    r.status, r.stop = status, stop
    if status == "stopped":
        r.text = (f"I stopped before finishing: {stop}. Nothing was booked."
                  + (" What I had proposed so far is below; confirm only what you want." if r.proposed else ""))
    if r.proposed and student:
        r.plan_id = put_plan(student, r.proposed)                      # parked for 15 minutes
    _trace(r, "finish", status=status, stop=stop, steps=r.steps, cost_usd=r.cost_usd,
           proposed=len(r.proposed), rejected=len(r.rejected),
           student=student_key(student) if student else None)
    return r


def _trace(r: Run, phase: str, **fields) -> None:
    line = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "run": r.id,
            "step": r.steps, "phase": phase, **fields}
    r.trace.append(line)
    AGENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AGENT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")
