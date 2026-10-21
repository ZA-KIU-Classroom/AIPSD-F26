"""Offline stand-ins for the two model calls, used when CAMPUSPULSE_OFFLINE=1.

They exist so tests, CI and the classroom demo run with no key and no network.
They are deliberately simple and they are NOT a model:

  embed()          hashes character trigrams into 512 numbers. It catches typos and shared
                   words ("robtics" still lands near "robotics"). It does not understand
                   meaning: "fee" and "cost" are unrelated to it. Real embeddings are.
  complete_json()  reads the SOURCES block of a grounded-answer prompt and copies the first
                   sentences of the sources that share most of the question's words. If none
                   do, it answers grounded=false. It never writes anything new.

  complete_tools() picks a tool by keywords and copies arguments it can see in the question
                   (a room code, a YYYY-MM-DD date, an HH:MM time, an ev-NNN id). After a tool
                   result it reports that result in one plain sentence. It never plans.

Golden-set numbers from offline mode measure retrieval and the citation checks, not answer
quality. Run the golden set live before you trust a number.
"""
from __future__ import annotations

import hashlib
import json
import re
from types import SimpleNamespace

import numpy as np

MODEL = "offline/trigram-hash"
DIMS = 512

STOP = set("""a an and are as at be by can do does for from has have how i if in is it me my
of on or the there this to was what when where which who will with you your our we any about
after before into than that then them they these those up""".split())


def words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP]


def _vector(text: str) -> np.ndarray:
    v = np.zeros(DIMS, dtype=np.float32)
    for w in words(text):
        padded = f" {w} "
        for i in range(len(padded) - 2):
            h = int(hashlib.md5(padded[i:i + 3].encode()).hexdigest(), 16)
            v[h % DIMS] += 1.0
    n = np.linalg.norm(v)
    return v / n if n else v


def embed(texts: list[str], log) -> np.ndarray:
    tokens = sum(len(t.split()) for t in texts)
    log(SimpleNamespace(model=MODEL, usage=SimpleNamespace(prompt_tokens=tokens, completion_tokens=0)),
        latency_ms=0, kind="embed")
    return np.stack([_vector(t) for t in texts])


_SOURCE = re.compile(r"^\[(\d+)\] (.*?)\n(.*?)(?=^\[\d+\] |\Z)", re.S | re.M)


def stems(text: str) -> set[str]:
    """Crude stemming: the first four letters. 'booked', 'booking' and 'book' all become 'book'."""
    return {w[:4] for w in words(text)}


def complete_json(prompt: str) -> tuple[dict, SimpleNamespace]:
    head, question = prompt.split("QUESTION:", 1)
    q = stems(question)
    cited, parts = [], []
    for n, header, body in _SOURCE.findall(head):
        overlap = len(q & stems(header + " " + body)) / max(1, len(q))
        if overlap >= 0.6 and len(cited) < 2:
            sentences = re.split(r"(?<=[.!?])\s+", body.strip())
            ranked = sorted(sentences, key=lambda s: -len(q & stems(s)))[:2]
            cited.append(int(n))
            parts += [f"{s.rstrip('.')} [{n}]." for s in sentences if s in ranked]
    out = ({"answer": " ".join(parts), "citations": cited, "grounded": True} if cited else
           {"answer": "The sources do not say.", "citations": [], "grounded": False})
    resp = SimpleNamespace(model=MODEL, usage=SimpleNamespace(
        prompt_tokens=len(prompt.split()), completion_tokens=len(out["answer"].split())))
    return out, resp


# ------------------------------------------------------------------ Week 5: tools

_ROOM = re.compile(r"\b([abAB]\d{3})\b")
_DATE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_TIME = re.compile(r"\b(\d{1,2}:\d{2})\b")
_EVENT = re.compile(r"\b(ev-\d{3})\b", re.I)
_MINUTES = re.compile(r"\b(\d{2,3}) ?min", re.I)


def _say(result: dict) -> str:
    if "error" in result:
        return f"I couldn't do that: {result['error']}"
    if "free" in result:
        if result["free"]:
            return f"{result['room']} is free on {result['date']} from {result['start']} to {result['end']}."
        why = result["clashes"] + result["rules"]
        return f"{result['room']} is not available then: {'; '.join(why)}"
    if "events" in result:
        if not result["events"]:
            return "There are no events in that window."
        return "Coming up: " + "; ".join(f"{e['title']} ({e['id']}, {e['start'].replace('T', ' ')}"
                                         f"{', cancelled' if e['status'] == 'cancelled' else ''})"
                                         for e in result["events"]) + "."
    if "content" in result:
        return f"Here is your calendar file: {result['filename']}."
    if "seats_left" in result:
        verb = "You're registered for" if result["status"] == "added" else "You were already registered for"
        return f"{verb} {result['title']}. Seats left: {result['seats_left']}."
    return "Done."


def complete_tools(messages: list[dict], tools: list[dict]) -> tuple[dict, SimpleNamespace]:
    names = {t["function"]["name"] for t in tools}
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    q = messages[last_user]["content"]
    results = [json.loads(m["content"]) for m in messages[last_user + 1:] if m["role"] == "tool"]
    call = None
    if results:
        content = " ".join(_say(r) for r in results)
    else:
        content, low = None, q.lower()
        event, day = _EVENT.search(q), _DATE.search(q)
        if event and any(w in low for w in ("rsvp", "sign me up", "save me a seat", "register me")):
            if "rsvp" in names:
                call = ("rsvp", {"event_id": event.group(1).lower()})
            else:
                content = "Please sign in first: I can only RSVP for a signed-in student."
        elif event and "calendar" in low:
            call = ("make_calendar_file", {"event_id": event.group(1).lower()})
        elif _ROOM.search(q) and day and _TIME.search(q):
            args = {"room": _ROOM.search(q).group(1).upper(), "date": day.group(1),
                    "start": _TIME.search(q).group(1).zfill(5)}
            if _MINUTES.search(q):
                args["minutes"] = int(_MINUTES.search(q).group(1))
            call = ("check_room", args)
        elif "event" in low or "what's on" in low or "whats on" in low:
            call = ("list_events", {"from_date": day.group(1) if day else _today(messages)})
        else:
            content = "I can check rooms, list events, make calendar files and RSVP. Which would you like?"
    calls = [] if call is None else [{"id": f"call_{len(messages)}", "name": call[0],
                                      "arguments": json.dumps(call[1])}]
    out = {"content": content, "tool_calls": calls, "reasoning_details": None}
    resp = SimpleNamespace(model=MODEL, usage=SimpleNamespace(
        prompt_tokens=sum(len(str(m.get("content") or "").split()) for m in messages)
        + 40 * len(tools), completion_tokens=len((content or json.dumps(calls)).split())))
    return out, resp


def _today(messages: list[dict]) -> str:
    found = _DATE.search(messages[0]["content"]) if messages and messages[0]["role"] == "system" else None
    return found.group(1) if found else "2026-10-21"
