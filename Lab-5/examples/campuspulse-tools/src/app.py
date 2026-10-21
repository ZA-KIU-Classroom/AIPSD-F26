"""CampusPulse: grounded answers (Week 4) and tool use (Week 5).

Run:  python -m src.index && uvicorn src.app:app --reload
"""
from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, Header
from pydantic import BaseModel, Field

from .act import act
from .answer import answer
from .index import load

app = FastAPI(title="CampusPulse")


class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=500)


@lru_cache(maxsize=1)
def index():
    return load()


@app.post("/ask")
def ask(body: Ask) -> dict:
    return answer(index(), body.question).to_dict()


@app.post("/act")
def act_endpoint(body: Ask, x_student_id: str | None = Header(default=None)) -> dict:
    # Stand-in for real sign-in (Week 12). Whoever this header names is the caller; the model
    # never sees it and cannot change it. No header: read-only tools only.
    return act(body.question, student=x_student_id).to_dict()
