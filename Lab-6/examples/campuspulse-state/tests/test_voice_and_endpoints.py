"""The Week 6 endpoints through FastAPI's test client, and the voice path offline."""
import base64
import io
import json
import os
import wave

from fastapi.testclient import TestClient

from src import memory
from src.app import app
from src.llm import pcm_to_wav, speak, transcribe

client = TestClient(app)
HDRS = {"X-Session-Id": "sess-t", "X-Student-Id": "s123"}


def parse_sse(body: str) -> list[tuple[str, dict]]:
    events = []
    for block in body.strip().split("\n\n"):
        lines = dict(l.split(": ", 1) for l in block.split("\n"))
        events.append((lines["event"], json.loads(lines["data"])))
    return events


def test_chat_streams_server_sent_events():
    with client.stream("POST", "/chat", json={"question": "what's on this week?"}, headers=HDRS) as r:
        assert r.status_code == 200 and r.headers["content-type"].startswith("text/event-stream")
        body = "".join(r.iter_text())
    events = parse_sse(body)
    assert events[0][0] == "token" and events[-1][0] == "done"
    assert sum(1 for k, _ in events if k == "token") > 3
    assert "ttft_ms" in events[-1][1]


def test_memory_can_be_seen_and_deleted_by_its_owner():
    client.post("/chat", json={"question": "remember that I like tech talks"}, headers=HDRS)
    assert client.get("/me/memory", headers=HDRS).json()["interests"] == ["tech talks"]
    other = client.get("/me/memory", headers={"X-Session-Id": "sess-o", "X-Student-Id": "s999"}).json()
    assert other["interests"] == [] and other["recent_turns"] == 0
    gone = client.delete("/me/memory", headers=HDRS).json()
    assert gone["interests"] == 1 and gone["turns"] == 2
    assert client.get("/me/memory", headers=HDRS).json() == {"interests": [], "recent_turns": 0,
                                                              "lifetimes": {"turns": "24 hours", "interests": "180 days"}}


def test_forget_without_identity_deletes_nothing():
    memory.remember_interest("s123", "tech talks")
    assert client.delete("/me/memory").json() == {"interests": 0, "turns": 0}
    assert memory.interests("s123") == ["tech talks"]


def test_transcribe_and_speak_offline():
    clip = b"RIFF....fake....TEXT: what's on this week"
    assert transcribe(clip) == "what's on this week"
    wav = speak("Open Build Night is on Thursday.")
    with wave.open(io.BytesIO(wav)) as w:
        assert w.getframerate() == 24000 and w.getnchannels() == 1 and w.getsampwidth() == 2
    assert pcm_to_wav(b"\x00\x00" * 10)[:4] == b"RIFF"


def test_voice_endpoint_returns_transcript_answer_and_audio_without_storing_the_clip():
    clip = b"RIFF....fake....TEXT: what's on this week"
    r = client.post("/voice", files={"clip": ("q.wav", clip, "audio/wav")}, headers=HDRS)
    assert r.status_code == 200
    body = r.json()
    assert body["transcript"] == "what's on this week" and "Open Build Night" in body["answer"]
    assert base64.b64decode(body["audio_wav_base64"])[:4] == b"RIFF"
    state_dir = os.environ["CAMPUSPULSE_STATE_DIR"]
    on_disk = [p for p in os.listdir(state_dir)] if os.path.exists(state_dir) else []
    assert all(not p.endswith((".wav", ".mp3", ".webm")) for p in on_disk)
    lines = [json.loads(l) for l in open(os.environ["CAMPUSPULSE_USAGE_LOG"])]
    kinds = [l["kind"] for l in lines[-4:]]
    assert "transcribe" in kinds and "speak" in kinds and "stream" in kinds
