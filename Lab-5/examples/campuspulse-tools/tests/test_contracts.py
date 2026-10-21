"""The contract rejects bad input before any tool code runs."""
import pytest
from pydantic import ValidationError

from src.contracts import CalendarFile, CheckRoom, ListEvents, Rsvp


def test_valid_check_room_parses_types():
    args = CheckRoom.model_validate_json('{"room": "B204", "date": "2026-10-29", "start": "15:00"}')
    assert args.date.isoformat() == "2026-10-29" and args.minutes == 60


@pytest.mark.parametrize("bad, field", [
    ('{"room": "Lab B204; DROP TABLE bookings", "date": "2026-10-22", "start": "18:00"}', "room"),
    ('{"room": "Auditorium", "date": "2026-10-22", "start": "18:00"}', "room"),
    ('{"room": "B204", "date": "2026-02-30", "start": "18:00"}', "date"),
    ('{"room": "B204", "date": "next Thursday", "start": "18:00"}', "date"),
    ('{"room": "B204", "date": "2026-10-22", "start": "6pm"}', "start"),
    ('{"room": "B204", "date": "2026-10-22", "start": "18:00", "minutes": 600}', "minutes"),
    ('{"room": "B204", "date": "2026-10-22"}', "start"),
])
def test_bad_check_room_arguments_are_rejected(bad, field):
    with pytest.raises(ValidationError) as e:
        CheckRoom.model_validate_json(bad)
    assert field in {str(err["loc"][0]) for err in e.value.errors()}


def test_truncated_json_is_rejected():
    with pytest.raises(ValidationError):
        CheckRoom.model_validate_json('{"room": "B204", "date": ')


def test_unknown_argument_is_an_error_not_ignored():
    with pytest.raises(ValidationError):
        Rsvp.model_validate_json('{"event_id": "ev-201", "student": "s999"}')


def test_event_id_has_a_pattern():
    with pytest.raises(ValidationError):
        CalendarFile.model_validate_json('{"event_id": "../../etc/passwd"}')


def test_look_ahead_is_bounded():
    with pytest.raises(ValidationError):
        ListEvents.model_validate_json('{"from_date": "2026-10-21", "days": 365}')


def test_no_contract_names_the_caller():
    for model in (CheckRoom, ListEvents, CalendarFile, Rsvp):
        assert not {"student", "user", "user_id", "student_id"} & set(model.model_fields)
