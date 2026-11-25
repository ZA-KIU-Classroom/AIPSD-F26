"""The confirmation gate (Week 7): an agent proposes, a person confirms, code runs what was seen.

Two functions, on either side of a human:

  propose()   called by the loop when the model asks for a consequential tool. It validates the
              arguments against the contract, runs every check the real tool would run plus the
              timetable, and returns an ACTION: a description to show the student and the exact
              arguments to run later. It writes nothing and books nothing.

  confirm()   called by POST /plan/{id}/confirm when the student presses the button. No model is
              involved. It takes the parked plan (single use, this student only, 15 minutes),
              and runs the approved actions through Week 5's call_tool(): offered? valid?
              identity from the session. What the student approved is exactly what runs.

The plan is parked in the Week 6 store as a third kind of state. docs/state-contract.md has
its row; decision record 0007 says why the gate is here and not in the prompt.
"""
from __future__ import annotations

import hashlib

from pydantic import ValidationError

from .act import brief, call_tool
from .memory import take_plan
from .tools import Tool, ToolFailure, rsvp_preview, tools_for

PREVIEW = {"rsvp": rsvp_preview}       # one preview per consequential tool: "would this work, and should it?"


def propose(call: dict, tool: Tool, student: str | None, classes: list[dict]) -> tuple[dict | None, dict]:
    """Returns (action, observation). action is None when the gate's checks refuse the call;
    the observation is what the model reads next, either way."""
    try:
        args = tool.args.model_validate_json(call["arguments"] or "{}")        # the contract, checked
    except ValidationError as e:
        return None, {"error": f"invalid arguments: {brief(e)}"}
    try:
        summary = PREVIEW[tool.name](args, student, classes)                   # checked by code, now
    except ToolFailure as e:
        return None, {"error": str(e)}
    stored = args.model_dump_json()                                            # exactly what will run
    action = {"id": "a-" + hashlib.sha256(f"{tool.name}{stored}".encode()).hexdigest()[:6],
              "tool": tool.name, "arguments": stored, "summary": summary}
    return action, {"status": "added to the plan; NOT booked. The student will confirm or decline.",
                    "summary": summary}


def confirm(student: str, plan_id: str, approve: list[str]) -> dict | None:
    """The student said yes to some of it. None means there is no such plan for this student:
    it expired, was already used, or was never theirs."""
    plan = take_plan(student, plan_id)                                         # read and delete: once
    if plan is None:
        return None
    allowed, ran, skipped = tools_for(student), [], []
    for action in plan["actions"]:
        if action["id"] not in approve:
            skipped.append(action["summary"])
            continue
        outcome = call_tool({"id": action["id"], "name": action["tool"], "arguments": action["arguments"]},
                            allowed, student)                                  # the same three gates
        ran.append({"summary": action["summary"], "ok": outcome["ok"], "error": outcome["error"]})
    return {"ran": ran, "skipped": skipped}
