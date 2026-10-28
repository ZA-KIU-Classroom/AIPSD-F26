"""The tool contracts: what each capability accepts, as types the code can check.

This file is the single source of truth for tool inputs. Two doors read it:
  * src/tools.py builds the function-calling schemas the model sees (Args models below)
  * src/mcp_server.py builds the MCP tools from the same type aliases
tests/test_mcp.py fails if the two doors ever describe a tool differently.

Rules that hold for every contract:
  * extra="forbid": an argument we did not ask for is an error, never ignored
  * every string that reaches a lookup or a file has a pattern or a fixed set of values
  * nothing here names WHO is calling. Identity comes from the server, never the model.
"""
from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

RoomCode = Annotated[Literal["A015", "A112", "B204"], Field(description="A bookable room")]
Day = Annotated[date, Field(description="Calendar date, YYYY-MM-DD")]
Clock = Annotated[str, Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$", description="Start, 24-hour HH:MM")]
Minutes = Annotated[int, Field(ge=15, le=240, description="Length in minutes, 15 to 240")]
EventId = Annotated[str, Field(pattern=r"^ev-\d{3}$", description="Event id, like ev-201")]
Days = Annotated[int, Field(ge=1, le=14, description="How many days to look ahead, 1 to 14")]
Topic = Annotated[str, Field(pattern=r"^[A-Za-z][A-Za-z0-9 &'-]{1,39}$",
                             description="An interest in plain words, 2 to 40 characters, like 'tech talks'")]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CheckRoom(Contract):
    """Is a room free for this slot, under KIU's booking rules? Reads only."""
    room: RoomCode
    date: Day
    start: Clock
    minutes: Minutes = 60


class ListEvents(Contract):
    """Upcoming events from a date, with ids and seats left. Reads only."""
    from_date: Day
    days: Days = 7


class CalendarFile(Contract):
    """An .ics file for one event that the student adds to their own calendar. Reads only."""
    event_id: EventId


class Rsvp(Contract):
    """Reserve one seat at an event for the signed-in student. Adds only, never removes."""
    event_id: EventId


class RememberInterest(Contract):
    """Remember one interest for the signed-in student, only when they ask you to. Adds only;
    forgetting is a button in the app, not a tool."""
    topic: Topic
