# CampusPulse · streaming, voice and state (Week 6 reference)

Week 5's grounded `/ask`, the four tools and the MCP server, unchanged, plus three things from Week 6: answers that stream as they are written, a voice path (a clip in, a spoken answer out), and session state with a contract: what is remembered, for whom, for how long, and how a student deletes it. Every line of code shown in the Week 6 lecture is in these files.

## Run it

```
pip install -r requirements.txt

# offline: no key, no network, no cost. Tests, CI and the classroom demos use this.
export CAMPUSPULSE_OFFLINE=1 CAMPUSPULSE_TODAY=2026-10-28
pytest                                   # 122 offline tests: 100 from Weeks 4 and 5, 22 new
python -m demo.state_demo latency        # the same answer, whole then streamed: first word 3.2 s → 0.1 s
python -m demo.state_demo leak           # a naive memory leaks one student's interest into another's answer
python -m demo.state_demo forget         # remember, look, forget, look; the rows in memory.db

# the app, offline (the scripted model answers; the page streams, remembers and forgets)
python -m src.index && uvicorn src.app:app --reload     # then open http://127.0.0.1:8000/

# live: the real model streams, transcribes and speaks
export CAMPUSPULSE_OFFLINE=0 OPENROUTER_API_KEY=...
unset CAMPUSPULSE_TODAY
python -m src.index && uvicorn src.app:app --reload
curl -N localhost:8000/chat -H 'content-type: application/json' -H 'X-Session-Id: demo' \
     -H 'X-Student-Id: s123' -d '{"question": "remember that I like tech talks"}'
curl -X DELETE localhost:8000/me/memory -H 'X-Session-Id: demo' -H 'X-Student-Id: s123'
```

Logs: `logs/usage.jsonl` (every model call; `stream` lines carry `ttft_ms`, `transcribe` and `speak` lines carry the audio size), `logs/answers.jsonl`, `logs/tools.jsonl` (every tool call, `remember_interest` included). State: `state/memory.db` (turns and interests) next to `state/rsvps.json`.

## Where things are

| File | What it does | Lecture slide |
|---|---|---|
| `src/llm.py` | Week 5's file plus `Stream` (text as it arrives, tool-call fragments collected, usage from the last chunk, `ttft_ms` logged), `transcribe()` (an `input_audio` part to the chat model) and `speak()` (`/audio/speech`, PCM wrapped as WAV) | 7, 13, 14 |
| `src/memory.py` | the state store: turns scoped by session (24 h), interests scoped by hashed student (180 days), `forget()` that deletes rows, `expire()` | 19, 22 |
| `src/chat.py` | one turn: context from memory, stream, run any tool through Week 5's `call_tool()`, stream the result, write the two turns back | 21 |
| `src/app.py` | `POST /chat` as Server-Sent Events, `GET` and `DELETE /me/memory`, `POST /voice` | 8, 22 |
| `src/contracts.py` · `src/tools.py` · `src/mcp_server.py` | Week 5's contracts and tools plus `remember_interest` (a write, adds only); registered through both doors | 20 |
| `src/offline.py` | Week 5's stand-ins plus a chunked `stream()`, `transcribe()` and `speak()` | |
| `static/index.html` | the page: streams with `fetch`, shows first-token time and cost, a Forget me button, hold-to-talk that records, resamples to 16 kHz WAV in the browser and posts it | 9, 15 |
| `docs/state-contract.md` | the table of everything remembered: scope, lifetime, written when, deleted by | 18 |
| `docs/decisions/0005`, `0006` | memory writes are explicit; lifetimes and the forget button | 20, 25 |
| `tests/test_memory.py` · `test_stream_chat.py` · `test_voice_and_endpoints.py` | the 22 new tests: pieces arrive and ttft is logged; scope, lifetime, deletion; a visitor leaves nothing; the clip is never written to disk | 26 |
| `demo/state_demo.py` | the lab's three live demos | |

## Three things that surprise people

- **OpenRouter puts `usage` in the last streamed chunk on its own.** No `stream_options`, no second call; the `cost` field is there too. `Stream` reads it after the loop ends, so the log line has real numbers, not estimates.
- **A tool call can arrive in fragments mid-stream:** the id and name first, then the arguments a few characters at a time. `Stream` stitches them by index. Only after the stream ends does `chat.py` decide whether anything runs, through the same three gates as Week 5.
- **`DELETE /me/memory` needs no model at all.** Forgetting is the one memory operation that must work even when the model is down, so it is an endpoint and a button, never a tool the model holds.

Models and prices, verified on openrouter.ai on 26 October 2026: `google/gemini-3.8-flash` $0.75 in / $3.75 out per million tokens (50% promotional), audio input at 32 tokens per second of audio; `google/gemini-3.8-flash-lite-tts` $0.50 in / $6 out per million tokens, returns 24 kHz 16-bit mono PCM. Verify both before you ship.
