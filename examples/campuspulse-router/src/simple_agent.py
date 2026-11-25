"""The supervised loop in about 50 lines (Week 7). This is the version shown in the lecture
and the one Lab 7 starts from: Lab-7/templates/agent_starter.py is this file with ADAPT marks.

Three ideas, and nothing else:
  the loop    ask the model "what next?", run the tool it asks for, show it the result, repeat
  the stop    at most MAX_STEPS model turns, then the loop ends and says so
  the yes     a tool in NEEDS_YES is never run by the loop. It is parked. confirm() runs it
              when a person says yes, and no model is involved in that.

src/agent.py and src/gate.py are the same loop grown up: checks before parking, a budget in
seconds and dollars, timeouts and retries, a plan that expires. Read them when this one is clear.
"""
from __future__ import annotations

import json

from .act import as_assistant, call_tool        # Lab 5: echo the model's turn; run one tool safely
from .agent import SYSTEM, perceive             # the planner's prompt and the facts code reads
from .llm import complete_tools                 # Lab 5: one model call that may ask for tools
from .tools import _event, tools_for            # Lab 5: the tool registry

LOOP_TOOLS = ("list_events", "make_calendar_file", "rsvp")    # the only tools this loop may use
NEEDS_YES = {"rsvp"}                                          # tools that wait for a person
MAX_STEPS = 6                                                 # the stop

PENDING: dict[str, list[dict]] = {}     # user -> parked actions. A dict is enough for today.


def prompt(user: str) -> str:
    seen = perceive(user)
    classes = "\n".join(f"- {c['day']} {c['start']} to {c['end']}: {c['what']}" for c in seen["classes"])
    return SYSTEM.format(interests=", ".join(seen["interests"]) or "none", classes=classes or "- none",
                         today=seen["today"].strftime("%A %Y-%m-%d"))


def describe(call: dict) -> str:
    """One line a person can read before saying yes."""
    try:
        e = _event(json.loads(call["arguments"])["event_id"])
        return f"RSVP: {e['title']} · {e['start'].replace('T', ' ')} · {e['room']}"
    except Exception:
        return f"{call['name']} {call['arguments']}"


def run(goal: str, user: str, llm=complete_tools, max_steps: int = MAX_STEPS) -> dict:
    allowed = {name: tool for name, tool in tools_for(user).items() if name in LOOP_TOOLS}
    schemas = [tool.schema() for tool in allowed.values()]
    messages = [{"role": "system", "content": prompt(user)}, {"role": "user", "content": goal}]
    proposed, trace = [], []
    for step in range(1, max_steps + 1):
        msg = llm(messages, schemas)                                  # REASON: what next?
        if not msg["tool_calls"]:                                     # the model says it is done
            return finish("needs_confirmation" if proposed else "answered", msg["content"], user, proposed, trace)
        messages.append(as_assistant(msg))
        for call in msg["tool_calls"]:
            if call["name"] in NEEDS_YES:                             # ACT, needs a yes: park it
                action = {"id": f"a{len(proposed) + 1}", "tool": call["name"],
                          "arguments": call["arguments"], "summary": describe(call)}
                proposed.append(action)
                observation = {"status": "added to the plan; NOT done. A person will confirm.",
                               "summary": action["summary"]}
            else:                                                     # ACT, a read: run it
                outcome = call_tool(call, allowed, user)
                observation = outcome.get("result") or {"error": outcome["error"]}
            trace.append({"step": step, "tool": call["name"], "parked": call["name"] in NEEDS_YES})
            messages.append({"role": "tool", "tool_call_id": call["id"],              # OBSERVE
                             "content": json.dumps(observation)})
    return finish("stopped", f"I stopped after {max_steps} steps. Nothing was done.", user, proposed, trace)


def finish(status: str, text: str, user: str, proposed: list[dict], trace: list[dict]) -> dict:
    PENDING[user] = proposed                                          # parked until a person answers
    return {"status": status, "text": text, "proposed": proposed, "trace": trace}


def confirm(user: str, approved_ids: list[str]) -> list[dict]:
    """The person said yes. Run exactly what was parked, once. No model here."""
    actions = PENDING.pop(user, [])                                   # pop: a plan works once
    allowed = tools_for(user)
    return [call_tool({"id": a["id"], "name": a["tool"], "arguments": a["arguments"]}, allowed, user)
            for a in actions if a["id"] in approved_ids]
