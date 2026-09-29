"""CampusPulse service · built from docs/spec.md v1 by an agent, reviewed by a human.

Run:  uvicorn src.app:app --reload
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from . import llm
from .format import format_event_compact

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
TBILISI = ZoneInfo("Asia/Tbilisi")
DATA = Path(__file__).resolve().parent.parent / "data" / "events.json"
SYSTEM = "You are CampusPulse, a campus events assistant at KIU. Answer in at most three short sentences, from the events listed only."

app = FastAPI(title="CampusPulse")


def error(status: int, message: str, field: str) -> JSONResponse:
    """The one error shape from AGENTS.md: {"error": ..., "field": ...}. Never FastAPI's default."""
    return JSONResponse(status_code=status, content={"error": message, "field": field})


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    return error(422, first["msg"], str(first["loc"][-1]))       # e.g. week=abc -> field "week"


def load_events() -> list[dict]:
    return json.loads(DATA.read_text(encoding="utf-8"))


def confirmed_in_week(week: int) -> list[dict]:
    return [e for e in load_events() if e["week"] == week and e["status"] == "confirmed"]


@app.get("/events")
def events(week: int):
    # AC3: our error shape, not FastAPI's default, so every client handles one format
    if not 1 <= week <= 53:
        return error(422, "week must be between 1 and 53", "week")
    return confirmed_in_week(week)                                   # AC2: confirmed only, no other filters


class Question(BaseModel):
    question: str


@app.post("/chat")
def chat(body: Question):
    week = datetime.now(TBILISI).isocalendar().week                  # aware "now", in Tbilisi
    shortlist = confirmed_in_week(week)
    context = "\n".join(format_event_compact(e) for e in shortlist)
    answer, usage = llm.chat(SYSTEM, f"Events this week:\n{context}\n\nQuestion: {body.question}")
    return {"answer": answer, "event_ids": [e["id"] for e in shortlist], "usage": usage}   # AC1
