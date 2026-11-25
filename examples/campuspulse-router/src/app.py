"""CampusPulse: grounded answers (Week 4), tool use (Week 5), streaming, voice and state (Week 6),
and the week planner behind a confirmation gate (Week 7).

Run:  python -m src.index && uvicorn src.app:app --reload   then open http://127.0.0.1:8000/

Week 6 endpoints:
  POST   /chat         streams the answer as Server-Sent Events: token, tool, done
  GET    /me/memory    what we hold for this caller (interests, number of recent turns)
  DELETE /me/memory    forget it all, now. A button in the UI; never a tool the model holds
  POST   /voice        an audio clip in, the transcript, the answer and a WAV of it spoken, out

Week 7 endpoints:
  POST   /plan                   run the planner. It proposes; nothing is booked
  POST   /plan/{id}/confirm      the student's yes: runs the approved actions. No model involved
  DELETE /plan/{id}              the student's no: the parked plan is deleted

Identity and session come from headers (X-Student-Id, X-Session-Id): a stand-in for real
sign-in until Week 12. The model never sees either and cannot change them.
"""
from __future__ import annotations

import base64
import json
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from . import agent, gate, memory
from .act import act
from .answer import answer
from .chat import answer_text, chat_turn
from .index import load
from .llm import speak, transcribe

STATIC = Path(__file__).resolve().parents[1] / "static"


@asynccontextmanager
async def lifespan(_app):
    memory.expire()                      # lifetimes are enforced, not just declared
    yield


app = FastAPI(title="CampusPulse", lifespan=lifespan)


class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=500)


@lru_cache(maxsize=1)
def index():
    return load()


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.post("/ask")
def ask(body: Ask) -> dict:
    return answer(index(), body.question).to_dict()


@app.post("/act")
def act_endpoint(body: Ask, x_student_id: str | None = Header(default=None)) -> dict:
    return act(body.question, student=x_student_id).to_dict()


def sse(events) -> StreamingResponse:
    """Server-Sent Events: one 'event:' line, one 'data:' line, a blank line. Text, not binary."""
    def gen():
        for kind, payload in events:
            data = json.dumps(payload if kind != "token" else {"text": payload})
            yield f"event: {kind}\ndata: {data}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/chat")
def chat(body: Ask, x_session_id: str | None = Header(default=None),
         x_student_id: str | None = Header(default=None)) -> StreamingResponse:
    return sse(chat_turn(body.question, session=x_session_id, student=x_student_id))


@app.get("/me/memory")
def my_memory(x_session_id: str | None = Header(default=None),
              x_student_id: str | None = Header(default=None)) -> dict:
    return {"interests": memory.interests(x_student_id) if x_student_id else [],
            "recent_turns": len(memory.recent_turns(x_session_id)) if x_session_id else 0,
            "lifetimes": {"turns": "24 hours", "interests": "180 days"}}


@app.delete("/me/memory")
def forget_me(x_session_id: str | None = Header(default=None),
              x_student_id: str | None = Header(default=None)) -> dict:
    return memory.forget(x_student_id, x_session_id).to_dict()


@app.post("/voice")
async def voice(clip: UploadFile = File(...), x_session_id: str | None = Header(default=None),
                x_student_id: str | None = Header(default=None)) -> dict:
    audio = await clip.read()                       # in memory for this request only; never written
    fmt = (clip.filename or "clip.wav").rsplit(".", 1)[-1].lower()
    question = transcribe(audio, fmt=fmt if fmt in {"wav", "mp3", "m4a", "ogg", "flac", "aac"} else "wav")
    text = answer_text(question, session=x_session_id, student=x_student_id)
    return {"transcript": question, "answer": text,
            "audio_wav_base64": base64.b64encode(speak(text)).decode("ascii")}


# ---------------------------------------------------------------- Week 7: the planner and its gate

class Goal(BaseModel):
    goal: str = Field(min_length=3, max_length=300)


class Approval(BaseModel):
    approve: list[str] = Field(max_length=10)       # the action ids the student ticked


@app.post("/plan")
def plan(body: Goal, x_student_id: str | None = Header(default=None)) -> dict:
    return agent.run(body.goal, student=x_student_id).to_dict()


@app.post("/plan/{plan_id}/confirm")
def confirm_plan(plan_id: str, body: Approval, x_student_id: str | None = Header(default=None)) -> dict:
    if not x_student_id:
        raise HTTPException(401, "Sign in to confirm a plan.")
    done = gate.confirm(x_student_id, plan_id, body.approve)
    if done is None:                                 # expired, already used, or not this student's
        raise HTTPException(410, "That plan is no longer valid. Ask for a new one.")
    return done


@app.delete("/plan/{plan_id}")
def decline_plan(plan_id: str, x_student_id: str | None = Header(default=None)) -> dict:
    return {"dropped": memory.drop_plans(x_student_id) if x_student_id else 0}
