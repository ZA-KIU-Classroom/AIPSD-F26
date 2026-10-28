"""Four tests every Week 6 slice needs. Copy into tests/, rename the imports to your modules.

They prove the three columns of your state contract and the streaming log line. Keep them
offline: no key, no network. CI runs them on every pull request.
"""
import json
import os


def test_stream_yields_pieces_and_logs_time_to_first_token():
    """Your streaming function yields more than one piece, the pieces join into the answer,
    and exactly one usage log line is written with a ttft_ms field."""
    from src.llm import stream                                   # your module
    log = os.environ["<YOUR_USAGE_LOG_ENV>"]                     # the path your log_usage writes to
    before = open(log).read().count("\n") if os.path.exists(log) else 0
    s = stream([{"role": "user", "content": "<a question your product answers>"}])
    pieces = list(s)
    assert len(pieces) > 1 and "".join(pieces) == s.text
    lines = open(log).read().splitlines()
    assert len(lines) == before + 1 and "ttft_ms" in json.loads(lines[-1])


def test_scope_one_users_memory_never_reaches_another():
    """Store something for user A. Read as user B. B sees nothing, and A's data is not in B's prompt."""
    from src.memory import remember, recall                      # your names
    from src.chat import build_messages
    remember("user-a", "<something>")
    assert recall("user-b") == []
    assert "<something>" not in build_messages(session="sess-b", user="user-b", question="hello")[0]["content"]


def test_lifetime_is_enforced(monkeypatch):
    """Pin the clock, write, move the clock past the lifetime, read: gone. Then expire() removes it."""
    from src import memory
    monkeypatch.setenv("<YOUR_NOW_ENV>", "2026-10-28T09:00:00+00:00")
    memory.remember("user-a", "<something>")
    monkeypatch.setenv("<YOUR_NOW_ENV>", "<a time past the lifetime>")
    assert memory.recall("user-a") == []
    assert memory.expire() >= 1


def test_deletion_is_total_and_immediate():
    """forget() returns the counts, the reads come back empty, and the rows are really gone."""
    from src import memory
    memory.remember("user-a", "<something>")
    gone = memory.forget("user-a", session="sess-a")
    assert gone["<your count field>"] >= 1
    assert memory.recall("user-a") == []
    # open the store directly and check there are no rows for user-a, flagged or otherwise
