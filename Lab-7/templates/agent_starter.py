"""Lab 7 starter: a supervised loop in about 50 lines. It is the file from lecture slide 8.

Copy this file to src/agent.py in your team repo. It already works. Change the lines marked
ADAPT (there are three, plus the imports if your Lab 5 names differ), then run the test in
templates/test_agent.py.

Three ideas, and nothing else:
  the loop    ask the model "what next?", run the tool it asks for, show it the result, repeat
  the stop    at most MAX_STEPS model turns, then the loop ends and says so
  the yes     a tool in NEEDS_YES is never run by the loop. It is parked. confirm() runs it
              when a person says yes, and no model is involved in that.

The CampusPulse version of this file: Lab-7/examples/campuspulse-agent/src/simple_agent.py
"""
from __future__ import annotations

import json
from datetime import date

# Your Lab 5 code. If your functions have other names, change these three imports only.
from src.act import as_assistant, call_tool     # echo the model's turn; run one tool safely
from src.llm import complete_tools              # one model call that may ask for tools
from src.tools import tools_for                 # your tool registry: {name: tool} for this user

# ADAPT 1: what is this loop for? One or two sentences, then how to finish.
GOAL_PROMPT = """You help a student plan their week of campus events.
Work in steps: look things up first, then propose actions.
A proposed action is NOT done: a person must confirm it. Never say it is done.
Finish with two or three sentences: what you proposed and why."""

LOOP_TOOLS = ("list_events", "rsvp")    # ADAPT 2: only the tools this goal needs. Leave the rest out.
NEEDS_YES = {"rsvp"}                    # ADAPT 3: tools that book, send, pay or delete. They wait for a person.
MAX_STEPS = 6                           # the stop

PENDING: dict[str, list[dict]] = {}     # user -> parked actions. A dict is enough for today.


def facts(user: str) -> str:
    """Facts your code already knows go into the prompt. The model is not asked to guess them."""
    return f"Today is {date.today():%A %Y-%m-%d}."      # optional: add the user's settings, their saved preferences


def describe(call: dict) -> str:
    """One line a person can read before saying yes. Optional: make it friendlier for your product."""
    return f"{call['name']} {call['arguments']}"


def run(goal: str, user: str, llm=complete_tools, max_steps: int = MAX_STEPS) -> dict:
    allowed = {name: tool for name, tool in tools_for(user).items() if name in LOOP_TOOLS}
    schemas = [tool.schema() for tool in allowed.values()]
    messages = [{"role": "system", "content": GOAL_PROMPT + "\n" + facts(user)}, {"role": "user", "content": goal}]
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
    print(json.dumps({"status": status, "steps": len({t["step"] for t in trace}), "proposed": len(proposed)}))
    return {"status": status, "text": text, "proposed": proposed, "trace": trace}


def confirm(user: str, approved_ids: list[str]) -> list[dict]:
    """The person said yes. Run exactly what was parked, once. No model here."""
    actions = PENDING.pop(user, [])                                   # pop: a plan works once
    allowed = tools_for(user)
    return [call_tool({"id": a["id"], "name": a["tool"], "arguments": a["arguments"]}, allowed, user)
            for a in actions if a["id"] in approved_ids]
