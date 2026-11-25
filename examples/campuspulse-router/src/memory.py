"""Session State: everything CampusPulse remembers across turns, in one place, with a contract.

Three things are remembered. Each has a scope (who can read it), a lifetime (when it dies on
its own) and a deletion path (how a person kills it early). docs/state-contract.md is the
human-readable version of this table; the two must agree.

  kind        scope         lifetime          deleted by
  turn        one session   24 hours          expiry, or DELETE /me/memory
  interest    one student   180 days          DELETE /me/memory (a button, never a tool)
  plan        one student   15 minutes        confirmed, declined, expiry, or DELETE /me/memory   (Week 7)

Rules that hold everywhere in this file:
  * the key is the student HASH (tools.student_key), never the id. Logs, rows and
    backups never contain the id itself.
  * nothing is stored unless a function here is called with a student or a session.
    A visitor with neither leaves nothing behind.
  * every read filters by key AND by expiry. There is no "all rows" read in the product.
  * deletion is one call and it is total: forget() removes every row for that student.

Storage: SQLite through the standard library, one file next to Lab 5's rsvps.json.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import json
import uuid

from .tools import student_key

TURN_LIFETIME = timedelta(hours=24)        # a conversation is a day, then it is gone
INTEREST_LIFETIME = timedelta(days=180)    # a semester; refreshed when the student repeats it
MAX_TURNS = 6                              # the context budget for history (Week 1): 3 exchanges
MAX_INTERESTS = 10
PLAN_LIFETIME = timedelta(minutes=15)      # Week 7: a yes is only valid while the plan is fresh


def _db_path() -> Path:
    return Path(os.environ.get("CAMPUSPULSE_STATE_DIR", "state")) / "memory.db"


def now() -> datetime:
    """UTC now. CAMPUSPULSE_NOW pins it for the expiry tests."""
    pinned = os.environ.get("CAMPUSPULSE_NOW")
    return datetime.fromisoformat(pinned) if pinned else datetime.now(timezone.utc)


@contextmanager
def _conn():
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY, key TEXT NOT NULL, kind TEXT NOT NULL,
            role TEXT, value TEXT NOT NULL, created_at TEXT NOT NULL, expires_at TEXT NOT NULL)""")
        conn.execute("CREATE INDEX IF NOT EXISTS memory_key ON memory(key, kind, expires_at)")
        yield conn
        conn.commit()
    finally:
        conn.close()


def _put(key: str, kind: str, value: str, lifetime: timedelta, role: str | None = None) -> None:
    t = now()
    with _conn() as c:
        c.execute("INSERT INTO memory (key, kind, role, value, created_at, expires_at) VALUES (?,?,?,?,?,?)",
                  (key, kind, role, value, t.isoformat(), (t + lifetime).isoformat()))


def _get(key: str, kind: str, limit: int) -> list[sqlite3.Row]:
    with _conn() as c:
        c.row_factory = sqlite3.Row
        return c.execute("SELECT role, value, created_at FROM memory WHERE key=? AND kind=? AND expires_at>? "
                         "ORDER BY id DESC LIMIT ?", (key, kind, now().isoformat(), limit)).fetchall()


# ---------------------------------------------------------------- turns (scope: one session)

def add_turn(session: str, role: str, text: str) -> None:
    _put(f"session:{session}", "turn", text[:2000], TURN_LIFETIME, role=role)


def recent_turns(session: str, limit: int = MAX_TURNS) -> list[dict]:
    """The last few turns, oldest first, ready to drop into a messages list."""
    rows = _get(f"session:{session}", "turn", limit)
    return [{"role": r["role"], "content": r["value"]} for r in reversed(rows)]


# ---------------------------------------------------------------- interests (scope: one student)

def remember_interest(student: str, topic: str) -> list[str]:
    """Store one interest for the signed-in student. Idempotent: repeating it only refreshes the clock."""
    key = f"student:{student_key(student)}"
    with _conn() as c:
        c.execute("DELETE FROM memory WHERE key=? AND kind='interest' AND lower(value)=lower(?)", (key, topic))
    _put(key, "interest", topic.strip(), INTEREST_LIFETIME)
    return interests(student)


def interests(student: str) -> list[str]:
    rows = _get(f"student:{student_key(student)}", "interest", MAX_INTERESTS)
    return [r["value"] for r in reversed(rows)]


# ---------------------------------------------------------------- pending plans (Week 7; scope: one student)

def put_plan(student: str, actions: list[dict]) -> str:
    """Park what the planner proposed until the student answers. One pending plan per student:
    a new plan replaces the old one, so a stale card can never be confirmed."""
    key, plan_id = f"student:{student_key(student)}", uuid.uuid4().hex[:8]
    with _conn() as c:
        c.execute("DELETE FROM memory WHERE key=? AND kind='plan'", (key,))
    _put(key, "plan", json.dumps({"id": plan_id, "actions": actions}), PLAN_LIFETIME)
    return plan_id


def take_plan(student: str, plan_id: str) -> dict | None:
    """Read and delete in one step: a plan can be confirmed once. None if it is not this student's
    plan, was already used, or is older than PLAN_LIFETIME."""
    key = f"student:{student_key(student)}"
    rows = _get(key, "plan", 1)
    plan = json.loads(rows[0]["value"]) if rows else None
    if plan is None or plan["id"] != plan_id:
        return None
    with _conn() as c:
        c.execute("DELETE FROM memory WHERE key=? AND kind='plan'", (key,))
    return plan


def drop_plans(student: str) -> int:
    with _conn() as c:
        return c.execute("DELETE FROM memory WHERE key=? AND kind='plan'",
                         (f"student:{student_key(student)}",)).rowcount


# ---------------------------------------------------------------- deletion and expiry

@dataclass
class Forgotten:
    interests: int
    turns: int
    plans: int = 0                         # Week 7: the contract gained a row, so forgetting did too

    def to_dict(self) -> dict:
        return {"interests": self.interests, "turns": self.turns, "plans": self.plans}


def forget(student: str | None, session: str | None) -> Forgotten:
    """Everything, now. Not 'mark as deleted': the rows are gone. Called by DELETE /me/memory."""
    with _conn() as c:
        n_i = n_t = n_p = 0
        if student:
            n_i = c.execute("DELETE FROM memory WHERE key=? AND kind='interest'",
                            (f"student:{student_key(student)}",)).rowcount
            n_p = c.execute("DELETE FROM memory WHERE key=? AND kind='plan'",
                            (f"student:{student_key(student)}",)).rowcount
        if session:
            n_t = c.execute("DELETE FROM memory WHERE key=? AND kind='turn'", (f"session:{session}",)).rowcount
    return Forgotten(interests=n_i, turns=n_t, plans=n_p)


def expire() -> int:
    """Delete every row past its lifetime. Run at startup and on a timer; reads already ignore them."""
    with _conn() as c:
        return c.execute("DELETE FROM memory WHERE expires_at<=?", (now().isoformat(),)).rowcount
