"""The Week 6 live demos. Offline, no key, deterministic. Run from the example root.

    python -m demo.state_demo latency   the same answer twice: whole reply after 3.6 s, then streamed
                                        with the first word at 0.3 s. Watch the clock, not the words.
    python -m demo.state_demo leak      a naive memory (one list for everyone) leaks Nino's interest
                                        into Giorgi's answer; then the same two chats through src/memory.py
    python -m demo.state_demo forget    remember, look, forget, look: and the row count in the database

The "model" is the scripted one in src/offline.py, with a sleep per word in the latency demo so
the timing on screen is honest about the shape of the problem (the real model is faster per
word and slower to the first one).
"""
from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
import time

os.environ.setdefault("CAMPUSPULSE_OFFLINE", "1")
os.environ.setdefault("CAMPUSPULSE_TODAY", "2026-10-28")
_tmp = tempfile.mkdtemp(prefix="campuspulse-demo-")
os.environ.setdefault("CAMPUSPULSE_STATE_DIR", _tmp)
os.environ.setdefault("CAMPUSPULSE_USAGE_LOG", os.path.join(_tmp, "usage.jsonl"))
os.environ.setdefault("CAMPUSPULSE_TOOL_LOG", os.path.join(_tmp, "tools.jsonl"))

from src import memory  # noqa: E402
from src.chat import chat_turn  # noqa: E402
from src.llm import stream  # noqa: E402

Q = "what's on this week?"
DELAY = 0.12          # seconds per word, so a 30-word answer takes about 3.6 s either way


def latency() -> None:
    msgs = [{"role": "user", "content": Q}]
    print("\n1 · no streaming: the student sees nothing until the whole answer exists\n")
    t0 = time.perf_counter()
    s = stream(msgs)
    words = []
    for piece in s:
        time.sleep(DELAY)
        words.append(piece)
    print(f"   {time.perf_counter() - t0:4.1f} s  {''.join(words).strip()}")
    print("\n2 · streaming: the same words, shown as they arrive\n")
    t0 = time.perf_counter()
    first = None
    for piece in stream(msgs):
        time.sleep(DELAY)
        if first is None:
            first = time.perf_counter() - t0
            print(f"   {first:4.1f} s  ", end="", flush=True)
        print(piece, end="", flush=True)
    print(f"\n   {time.perf_counter() - t0:4.1f} s  done")
    print(f"\n   Same total. The first word moved from {time.perf_counter() - t0:.1f} s to {first:.1f} s. "
          "That is the whole feature.\n")


NAIVE_MEMORY: list[str] = []          # one list, for everyone: the bug most first versions ship with


def naive_chat(student: str, question: str) -> str:
    if "i like" in question.lower():
        NAIVE_MEMORY.append(question.lower().split("i like", 1)[1].strip(" .!"))
        return f"Noted: {NAIVE_MEMORY[-1]}."
    hint = f"Since you like {NAIVE_MEMORY[0]}, " if NAIVE_MEMORY else ""
    return f"{hint}Open Build Night is on Thursday."


def leak() -> None:
    print("\n1 · the naive version: memory is a list, and there is only one list\n")
    for who, q in [("Nino", "Remember that I like chess."), ("Giorgi", "What's on this week?")]:
        print(f"   {who:<7} {q}\n           → {naive_chat(who, q)}")
    print("\n   Giorgi never said a word about chess. Nino's interest just crossed into his answer.")
    print("   Nothing crashed. Nothing was logged. This is the bug you find in a screenshot on Teams.\n")
    print("2 · through src/memory.py: scope is part of the key, and the key is a hash\n")
    for session, student, q in [("sess-n", "nino", "remember that I like chess"),
                                ("sess-g", "giorgi", "what's on this week?")]:
        text = "".join(p for k, p in chat_turn(q, session, student) if k == "token").strip()
        print(f"   {student:<7} {q}\n           → {text}")
    print("\n   Giorgi gets the plain answer. Nino's row is keyed 'student:<hash>' and his read never touches it.")
    _rows()


def forget() -> None:
    print("\n1 · remember\n")
    text = "".join(p for k, p in chat_turn("remember that I like tech talks", "sess-n", "nino") if k == "token")
    print("   →", text.strip())
    print("\n2 · look\n")
    print("   interests('nino') =", memory.interests("nino"))
    _rows()
    print("\n3 · forget: DELETE /me/memory, which calls memory.forget()\n")
    print("   forget('nino', 'sess-n') =", memory.forget("nino", "sess-n").to_dict())
    print("\n4 · look again\n")
    print("   interests('nino') =", memory.interests("nino"))
    _rows()
    print("\n   Not 'deleted: true' on a row that still exists. The rows are gone. That is what 'forget' means.\n")


def _rows() -> None:
    db = sqlite3.connect(os.path.join(_tmp, "memory.db"))
    rows = db.execute("SELECT key, kind, value, expires_at FROM memory").fetchall()
    print(f"\n   memory.db · {len(rows)} row(s)")
    for key, kind, value, exp in rows:
        print(f"     {key:<22} {kind:<9} {value[:40]:<42} expires {exp[:10]}")


if __name__ == "__main__":
    {"latency": latency, "leak": leak, "forget": forget}[sys.argv[1] if len(sys.argv) > 1 else "latency"]()
