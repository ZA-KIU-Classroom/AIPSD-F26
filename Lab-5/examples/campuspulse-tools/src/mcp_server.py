"""CampusPulse as an MCP server: the same four tools, now usable by any MCP host.

Run it over stdio (what Claude Code, Cursor and VS Code launch):
    CAMPUSPULSE_STUDENT=s123 python -m src.mcp_server
Or over Streamable HTTP (what you deploy):
    python -m src.mcp_server --http          # http://127.0.0.1:8000/mcp

MCP Python SDK 2.x (MCPServer, formerly FastMCP), speaking the 2026-07-28 protocol and
older clients from the same endpoint. The schema of every tool comes from the type hints,
which come from src/contracts.py. tests/test_mcp.py checks both doors stay identical.
"""
from __future__ import annotations

import os
import sys
from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver import Resolve
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from . import tools
from .contracts import CalendarFile, CheckRoom, Clock, Day, Days, EventId, ListEvents, Minutes, RoomCode, Rsvp

mcp = MCPServer("campuspulse", instructions="KIU campus events: rooms, events, calendar files, RSVPs.")
READS = ToolAnnotations(read_only_hint=True, open_world_hint=False)
ADDS = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=True)


def signed_in_student() -> str:
    """Who is calling. Set by whoever launches the server, never by the model."""
    student = os.environ.get("CAMPUSPULSE_STUDENT")
    if not student:
        raise ToolError("Not signed in: this server was started without CAMPUSPULSE_STUDENT.")
    return student


def _run(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except tools.ToolFailure as e:          # expected failures reach the model as readable errors
        raise ToolError(str(e)) from e


@mcp.tool(annotations=READS, description=CheckRoom.__doc__)
def check_room(room: RoomCode, date: Day, start: Clock, minutes: Minutes = 60) -> tools.RoomStatus:
    return _run(tools.check_room, CheckRoom(room=room, date=date, start=start, minutes=minutes))


@mcp.tool(annotations=READS, description=ListEvents.__doc__)
def list_events(from_date: Day, days: Days = 7) -> tools.EventList:
    return _run(tools.list_events, ListEvents(from_date=from_date, days=days))


@mcp.tool(annotations=READS, description=CalendarFile.__doc__)
def make_calendar_file(event_id: EventId) -> tools.IcsFile:
    return _run(tools.make_calendar_file, CalendarFile(event_id=event_id))


@mcp.tool(annotations=ADDS, description=Rsvp.__doc__)
def rsvp(event_id: EventId, student: Annotated[str, Resolve(signed_in_student)]) -> tools.RsvpResult:
    return _run(tools.rsvp, Rsvp(event_id=event_id), student=student)


if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run("streamable-http", host="127.0.0.1", port=8000)
    else:
        mcp.run()
