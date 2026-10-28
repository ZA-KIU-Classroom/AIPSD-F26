"""The four tools, called directly with validated contracts."""
import pytest

from src import tools
from src.contracts import CalendarFile, CheckRoom, ListEvents, Rsvp


def room(**kw):
    return tools.check_room(CheckRoom(**{"room": "B204", "start": "15:00", **kw}))


def test_free_slot_is_free():
    s = room(date="2026-10-29", minutes=90)
    assert s.free and s.end == "16:30" and s.capacity == 30 and s.notice_ok


def test_clash_with_a_booking():
    s = room(date="2026-10-22", start="18:00")
    assert not s.free and "Open Build Night" in s.clashes[0]


def test_sunday_rule_from_the_regulations():
    s = tools.check_room(CheckRoom(room="A112", date="2026-10-25", start="10:00"))
    assert not s.free and "Sundays" in s.rules[0]


def test_saturday_closes_at_18():
    s = room(date="2026-10-24", start="17:00", minutes=90)
    assert not s.free and any("Saturdays" in r for r in s.rules)


def test_must_end_by_2145():
    s = room(date="2026-10-29", start="21:00", minutes=60)
    assert not s.free and any("21:45" in r for r in s.rules)


def test_past_date_is_refused():
    assert not room(date="2026-10-01").free


def test_evening_needs_five_working_days_notice():
    assert room(date="2026-10-26", start="18:00").notice_ok is False   # 3 working days away
    assert room(date="2026-10-29", start="18:00").notice_ok is True    # 6 working days away


def test_list_events_window_and_seats():
    found = tools.list_events(ListEvents(from_date="2026-10-21", days=7)).events
    assert [e.id for e in found] == ["ev-201", "ev-205", "ev-202"]
    assert found[0].seats_left == 4


def test_calendar_file_is_valid_ics_in_utc():
    ics = tools.make_calendar_file(CalendarFile(event_id="ev-201")).content
    assert ics.startswith("BEGIN:VCALENDAR\r\n") and "DTSTART:20261022T140000Z" in ics
    assert "DTEND:20261022T170000Z" in ics


def test_cancelled_event_has_no_calendar_file():
    with pytest.raises(tools.ToolFailure, match="cancelled"):
        tools.make_calendar_file(CalendarFile(event_id="ev-205"))


def test_unknown_event_says_what_to_do_next():
    with pytest.raises(tools.ToolFailure, match="list_events"):
        tools.rsvp(Rsvp(event_id="ev-999"), student="s123")


def test_rsvp_adds_once_and_is_idempotent():
    first = tools.rsvp(Rsvp(event_id="ev-201"), student="s123")
    again = tools.rsvp(Rsvp(event_id="ev-201"), student="s123")
    assert (first.status, first.seats_left) == ("added", 3)
    assert (again.status, again.seats_left) == ("already registered", 3)


def test_full_event_refuses():
    with pytest.raises(tools.ToolFailure, match="full"):
        tools.rsvp(Rsvp(event_id="ev-204"), student="s123")


def test_rsvp_stores_a_hash_not_the_student_id():
    tools.rsvp(Rsvp(event_id="ev-202"), student="s123")
    stored = tools._state_file().read_text()
    assert "s123" not in stored and tools.student_key("s123") in stored


def test_no_tool_deletes_anything():
    assert not any(w in name for name in tools.TOOLS for w in ("delete", "cancel", "remove", "update"))


def test_visitor_is_offered_read_tools_only():
    assert set(tools.tools_for(None)) == {"check_room", "list_events", "make_calendar_file"}
    assert "rsvp" in tools.tools_for("s123")


def test_schema_comes_from_the_contract():
    s = tools.TOOLS["check_room"].schema()["function"]
    assert s["parameters"]["additionalProperties"] is False
    assert s["parameters"]["properties"]["room"]["enum"] == ["A015", "A112", "B204"]
