"""CampusPulse's four tools: the code that acts, behind the contracts in src/contracts.py.

Three read and one adds. Nothing here deletes, edits someone else's data, or writes to a
student's real calendar: that is the least-privilege decision, made by what we chose NOT to build.

Every tool takes a validated contract object (never raw model output) and returns a pydantic
result. A failure we expected (unknown event, full event) raises ToolFailure with a message
written for the model to read and act on. Anything else is a bug and is allowed to crash.

The data lives in data/campus/. RSVPs are written to $CAMPUSPULSE_STATE_DIR/rsvps.json.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Callable, Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from .contracts import CalendarFile, CheckRoom, Contract, ListEvents, Rsvp

TBILISI = ZoneInfo("Asia/Tbilisi")
DATA = Path(os.environ.get("CAMPUSPULSE_CAMPUS_DATA", Path(__file__).resolve().parents[1] / "data" / "campus"))


class ToolFailure(Exception):
    """An expected failure. The message goes back to the model, so make it say what to do next."""


def today() -> date:
    """Today in Kutaisi. CAMPUSPULSE_TODAY pins it for tests and the demo."""
    pinned = os.environ.get("CAMPUSPULSE_TODAY")
    return date.fromisoformat(pinned) if pinned else datetime.now(TBILISI).date()


def _load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def _state_file() -> Path:
    return Path(os.environ.get("CAMPUSPULSE_STATE_DIR", "state")) / "rsvps.json"


def student_key(student: str) -> str:
    """We store and log a hash of the student id, not the id itself."""
    return hashlib.sha256(student.encode()).hexdigest()[:12]


# ---------------------------------------------------------------- results

class RoomStatus(BaseModel):
    room: str
    date: date
    start: str
    end: str
    capacity: int
    free: bool                 # no clash and no rule broken
    clashes: list[str]         # bookings that overlap the slot
    rules: list[str]           # booking rules the slot breaks, in the regulation's words
    notice_ok: bool            # enough working days' notice for Student Affairs


class EventSummary(BaseModel):
    id: str
    title: str
    club: str
    start: str
    room: str
    seats_left: int
    status: str


class EventList(BaseModel):
    events: list[EventSummary]


class IcsFile(BaseModel):
    filename: str
    content: str


class RsvpResult(BaseModel):
    event_id: str
    title: str
    status: Literal["added", "already registered"]
    seats_left: int


# ---------------------------------------------------------------- check_room

def _working_days_between(start: date, end: date) -> int:
    """Mon to Fri strictly after `start` and strictly before `end`."""
    d, n = start + timedelta(days=1), 0
    while d < end:
        n += d.weekday() < 5
        d += timedelta(days=1)
    return n


def check_room(args: CheckRoom) -> RoomStatus:
    rooms = _load("rooms.json")
    begin = datetime.combine(args.date, time.fromisoformat(args.start))
    end = begin + timedelta(minutes=args.minutes)
    rules = []
    if args.date < today():
        rules.append("That date has already passed.")
    if args.date.weekday() == 6:
        rules.append("Rooms are not bookable on Sundays except with written approval "
                     "from the Head of Student Affairs.")
    if args.date.weekday() == 5 and end.time() > time(18, 0):
        rules.append("Buildings close at 18:00 on Saturdays.")
    if end.date() != args.date or end.time() > time(21, 45):
        rules.append("Events must end and the room must be cleared by 21:45.")
    clashes = [f"{b['what']}, {b['start'][11:]} to {b['end'][11:]}" for b in _load("bookings.json")
               if b["room"] == args.room
               and datetime.fromisoformat(b["start"]) < end and begin < datetime.fromisoformat(b["end"])]
    needed = 5 if begin.time() >= time(17, 0) else 2
    return RoomStatus(room=args.room, date=args.date, start=args.start, end=end.strftime("%H:%M"),
                      capacity=rooms[args.room]["capacity"], free=not clashes and not rules,
                      clashes=clashes, rules=rules,
                      notice_ok=_working_days_between(today(), args.date) >= needed)


# ---------------------------------------------------------------- events

def _events() -> dict[str, dict]:
    return {e["id"]: e for e in _load("events.json")}


def _rsvps() -> dict[str, list[str]]:
    f = _state_file()
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def _seats_left(event: dict, rsvps: dict[str, list[str]]) -> int:
    return event["capacity"] - event["seats_taken"] - len(rsvps.get(event["id"], []))


def _event(event_id: str) -> dict:
    event = _events().get(event_id)
    if event is None:
        raise ToolFailure(f"There is no event {event_id}. Call list_events to find the right id.")
    return event


def list_events(args: ListEvents) -> EventList:
    rsvps, until = _rsvps(), args.from_date + timedelta(days=args.days)
    found = [EventSummary(id=e["id"], title=e["title"], club=e["club"], start=e["start"], room=e["room"],
                          seats_left=max(0, _seats_left(e, rsvps)), status=e["status"])
             for e in _events().values()
             if args.from_date <= date.fromisoformat(e["start"][:10]) < until]
    return EventList(events=sorted(found, key=lambda e: e.start))


def make_calendar_file(args: CalendarFile) -> IcsFile:
    event = _event(args.event_id)
    if event["status"] == "cancelled":
        raise ToolFailure(f"{event['title']} ({event['id']}) was cancelled. Do not offer a calendar file.")
    start = datetime.fromisoformat(event["start"]).replace(tzinfo=TBILISI).astimezone(timezone.utc)
    stamp = "%Y%m%dT%H%M%SZ"
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//CampusPulse//KIU//EN", "BEGIN:VEVENT",
             f"UID:{event['id']}@campuspulse.kiu.example",
             f"DTSTAMP:{datetime.combine(today(), time(0), timezone.utc).strftime(stamp)}",
             f"DTSTART:{start.strftime(stamp)}",
             f"DTEND:{(start + timedelta(minutes=event['minutes'])).strftime(stamp)}",
             f"SUMMARY:{event['title']}", f"LOCATION:{event['room']}, KIU",
             "END:VEVENT", "END:VCALENDAR"]
    return IcsFile(filename=f"{event['id']}.ics", content="\r\n".join(lines) + "\r\n")


def rsvp(args: Rsvp, student: str) -> RsvpResult:
    """`student` comes from the signed-in session. The model cannot set it: Rsvp has no such field."""
    event = _event(args.event_id)
    if event["status"] == "cancelled":
        raise ToolFailure(f"{event['title']} ({event['id']}) was cancelled.")
    if datetime.fromisoformat(event["start"]).date() < today():
        raise ToolFailure(f"{event['title']} has already happened.")
    rsvps, key = _rsvps(), student_key(student)
    taken = rsvps.setdefault(event["id"], [])
    if key in taken:                                         # idempotent: asking twice is safe
        return RsvpResult(event_id=event["id"], title=event["title"], status="already registered",
                          seats_left=_seats_left(event, rsvps))
    if _seats_left(event, rsvps) <= 0:
        raise ToolFailure(f"{event['title']} is full ({event['capacity']} of {event['capacity']} seats). "
                          "Tell the student; do not try again.")
    taken.append(key)
    f = _state_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(rsvps, indent=1), encoding="utf-8")
    tmp.replace(f)                                            # all or nothing, never half a file
    return RsvpResult(event_id=event["id"], title=event["title"], status="added",
                      seats_left=_seats_left(event, rsvps))


# ---------------------------------------------------------------- the registry

@dataclass(frozen=True)
class Tool:
    name: str
    args: type[Contract]
    run: Callable[..., BaseModel]
    writes: bool = False                  # True: changes the world, needs a signed-in student

    def schema(self) -> dict:
        """What the model sees: name, description and JSON Schema, all from the contract."""
        return {"type": "function", "function": {
            "name": self.name, "description": self.args.__doc__.strip(),
            "parameters": self.args.model_json_schema()}}


TOOLS = {t.name: t for t in [
    Tool("check_room", CheckRoom, check_room),
    Tool("list_events", ListEvents, list_events),
    Tool("make_calendar_file", CalendarFile, make_calendar_file),
    Tool("rsvp", Rsvp, rsvp, writes=True),
]}


def tools_for(student: str | None) -> dict[str, Tool]:
    """Least privilege by construction: a visitor who is not signed in is never offered a write tool."""
    return {n: t for n, t in TOOLS.items() if student or not t.writes}
