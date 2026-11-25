"""The MCP door: same contracts, annotations, identity from the server, in-memory client."""
import asyncio

import pytest
from mcp import Client

from src import tools
from src.mcp_server import mcp


def run(coro):
    return asyncio.run(coro)


async def listed():
    async with Client(mcp) as c:
        return {t.name: t for t in (await c.list_tools()).tools}


async def call(name, args):
    async with Client(mcp) as c:
        return await c.call_tool(name, args)


def strip(schema):
    return {k: {kk: vv for kk, vv in v.items() if kk != "title"} for k, v in schema["properties"].items()}


def test_same_tools_through_both_doors():
    assert set(run(listed())) == set(tools.TOOLS)


@pytest.mark.parametrize("name", sorted(tools.TOOLS))
def test_both_doors_describe_the_arguments_identically(name):
    mcp_schema = run(listed())[name].input_schema
    fc_schema = tools.TOOLS[name].schema()["function"]["parameters"]
    assert strip(mcp_schema) == strip(fc_schema)
    assert set(mcp_schema.get("required", [])) == set(fc_schema.get("required", []))


def test_annotations_mark_reads_and_the_one_additive_write():
    t = run(listed())
    assert all(t[n].annotations.read_only_hint for n in ("check_room", "list_events", "make_calendar_file"))
    assert t["rsvp"].annotations.read_only_hint is False and t["rsvp"].annotations.destructive_hint is False


def test_bad_arguments_are_rejected_by_the_sdk():
    r = run(call("check_room", {"room": "B204", "date": "2026-02-30", "start": "18:00"}))
    assert r.is_error


def test_expected_failure_reaches_the_model_as_text():
    r = run(call("make_calendar_file", {"event_id": "ev-205"}))
    assert r.is_error and "cancelled" in r.content[0].text


def test_rsvp_needs_a_signed_in_student():
    r = run(call("rsvp", {"event_id": "ev-201"}))
    assert r.is_error and "Not signed in" in r.content[0].text


def test_student_comes_from_the_server_not_the_model(monkeypatch):
    monkeypatch.setenv("CAMPUSPULSE_STUDENT", "s123")
    assert "student" not in run(listed())["rsvp"].input_schema["properties"]
    r = run(call("rsvp", {"event_id": "ev-201", "student": "s999"}))
    assert not r.is_error and r.structured_content["status"] == "added"
    stored = tools._state_file().read_text()
    assert tools.student_key("s123") in stored and tools.student_key("s999") not in stored
