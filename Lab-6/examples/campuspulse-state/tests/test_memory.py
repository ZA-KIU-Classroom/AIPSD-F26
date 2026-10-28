"""Session State: scope, lifetime and deletion, each proven, not promised."""
import os
import sqlite3

from src import memory


def test_interest_is_remembered_and_idempotent():
    assert memory.remember_interest("s123", "tech talks") == ["tech talks"]
    assert memory.remember_interest("s123", "Tech Talks") == ["Tech Talks"]       # refreshed, not doubled
    memory.remember_interest("s123", "free food")
    assert memory.interests("s123") == ["Tech Talks", "free food"]


def test_scope_one_students_memory_never_reaches_another():
    memory.remember_interest("s123", "tech talks")
    assert memory.interests("s999") == []


def test_scope_turns_belong_to_one_session():
    memory.add_turn("sess-a", "user", "what's on?")
    memory.add_turn("sess-a", "assistant", "Open Build Night.")
    memory.add_turn("sess-b", "user", "hello")
    assert [t["content"] for t in memory.recent_turns("sess-a")] == ["what's on?", "Open Build Night."]
    assert len(memory.recent_turns("sess-b")) == 1


def test_recent_turns_keep_the_context_budget():
    for i in range(10):
        memory.add_turn("sess-a", "user", f"turn {i}")
    turns = memory.recent_turns("sess-a")
    assert len(turns) == memory.MAX_TURNS and turns[-1]["content"] == "turn 9"


def test_lifetime_a_turn_is_gone_after_24_hours(monkeypatch):
    monkeypatch.setenv("CAMPUSPULSE_NOW", "2026-10-28T09:00:00+00:00")
    memory.add_turn("sess-a", "user", "hello")
    monkeypatch.setenv("CAMPUSPULSE_NOW", "2026-10-29T09:00:01+00:00")
    assert memory.recent_turns("sess-a") == []                                     # reads ignore it...
    assert memory.expire() == 1                                                    # ...and expire() removes it


def test_lifetime_an_interest_lasts_180_days(monkeypatch):
    monkeypatch.setenv("CAMPUSPULSE_NOW", "2026-10-28T09:00:00+00:00")
    memory.remember_interest("s123", "chess")
    monkeypatch.setenv("CAMPUSPULSE_NOW", "2027-04-25T09:00:00+00:00")           # day 179
    assert memory.interests("s123") == ["chess"]
    monkeypatch.setenv("CAMPUSPULSE_NOW", "2027-04-27T09:00:00+00:00")           # day 181
    assert memory.interests("s123") == []


def test_deletion_is_total_and_immediate():
    memory.remember_interest("s123", "tech talks")
    memory.add_turn("sess-a", "user", "hello")
    gone = memory.forget("s123", "sess-a")
    assert gone.to_dict() == {"interests": 1, "turns": 1}
    assert memory.interests("s123") == [] and memory.recent_turns("sess-a") == []
    db = sqlite3.connect(os.path.join(os.environ["CAMPUSPULSE_STATE_DIR"], "memory.db"))
    assert db.execute("SELECT count(*) FROM memory").fetchone()[0] == 0           # rows gone, not flagged


def test_the_student_id_is_never_stored():
    memory.remember_interest("s123", "tech talks")
    db = sqlite3.connect(os.path.join(os.environ["CAMPUSPULSE_STATE_DIR"], "memory.db"))
    keys = [r[0] for r in db.execute("SELECT key FROM memory")]
    assert keys and all("s123" not in k for k in keys)


def test_a_visitor_leaves_nothing_behind():
    from src.chat import chat_turn
    list(chat_turn("what's on this week?", session=None, student=None))
    path = os.path.join(os.environ["CAMPUSPULSE_STATE_DIR"], "memory.db")
    assert not os.path.exists(path)                                                # not even an empty file
