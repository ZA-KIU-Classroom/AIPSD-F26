# Lab 6 · setup and troubleshooting

*Not a concept guide. The things that go wrong on the day, with the fix. Check here before asking in the chat.*

## Before the lab

```
git switch main && git pull                     # your team repo at lab5-tools-mcp
pip install -r requirements.txt                 # python-multipart is new this week (file uploads)
export OPENROUTER_API_KEY=...                   # the team key, as in Labs 4 and 5
```

The reference, to run beside your own code:

```
cd Lab-6/examples/campuspulse-state
pip install -r requirements.txt
export CAMPUSPULSE_OFFLINE=1 CAMPUSPULSE_TODAY=2026-10-28
pytest -q                                       # 122 passed
python -m src.index && uvicorn src.app:app --reload   # http://127.0.0.1:8000/
```

Windows PowerShell: `$env:CAMPUSPULSE_OFFLINE="1"`, and `curl -N` is `curl.exe -N`.

## Streaming

| Symptom | Cause | Fix |
|---|---|---|
| The whole answer appears at once in the browser, but `curl -N` streams | a proxy or the dev server buffers | send `X-Accel-Buffering: no` and `Cache-Control: no-cache`; on Railway or Vercel check the platform's docs for response buffering; `uvicorn` itself does not buffer |
| `curl` prints nothing for seconds, then everything | missing `-N` (no buffer) | `curl -N ...` |
| `tokens_in: 0` on every `stream` log line | usage read before the last chunk, or the last chunk skipped because `choices` is empty | handle a chunk with no `choices` and read `chunk.usage` from it; log after the loop |
| `JSON.parse` error in the browser on long answers | splitting on `\n` instead of `\n\n` | an SSE event ends with a blank line |
| 400 from the provider on the second call after a tool | the assistant turn with `tool_calls` (and `reasoning_details` for Gemini 3) was not appended before the tool message | use `as_assistant()` from `src/act.py` |
| `EventSource` cannot send my headers | it only does GET with no custom headers | use `fetch` and read the body (`templates/sse-client.html`) |

## State

| Symptom | Cause | Fix |
|---|---|---|
| `sqlite3.OperationalError: unable to open database file` | the state folder does not exist | `path.parent.mkdir(parents=True, exist_ok=True)` before connecting; the reference does this in `_conn()` |
| `database is locked` under the test client | two connections open at once in one thread | open, use and close per call (the `_conn()` context manager); do not keep a global connection |
| Interests from one test leak into the next | the same state dir across tests | the `fresh_state` fixture in `tests/conftest.py` gives every test its own `CAMPUSPULSE_STATE_DIR` |
| Expiry test passes even with no expiry code | reads filter nothing | compare `expires_at > now()` in the query, and pin `now()` with an environment variable in the test |
| `forget()` returns 0 | the key was built from a different id (hashed vs raw, or session vs student) | build keys in one place and reuse it; print the key once |
| The model ignores "remember that I like…" | the tool is not offered (visitor), or the description does not say when to call it | sign in (set `X-Student-Id`); keep the contract docstring explicit: "only when they ask you to" |

## Voice (stretch)

| Symptom | Cause | Fix |
|---|---|---|
| `getUserMedia` fails with a permissions error | not HTTPS and not localhost, or no user gesture | open `http://127.0.0.1:8000/`, not an IP on the LAN; keep hold-to-talk |
| `decodeAudioData` throws | the blob has zero bytes (released too fast) or an unsupported container | hold the button for at least a second; the reference converts in the browser so the server always receives WAV |
| 422 from `/voice` | `python-multipart` not installed, or the form field is not named `clip` | `pip install python-multipart`; `fd.append("clip", wav, "clip.wav")` |
| The transcript is empty with the real model | a format the provider rejects, or audio too quiet | send WAV; check the `transcribe` log line's token count: under 40 tokens means the clip was under a second |
| `audio.speech.create` returns 404 or 400 | the TTS model id is wrong, or the voice name is not one this model has | `google/gemini-3.8-flash-lite-tts`, voice `Kore`; check the model page on openrouter.ai for voices |
| Playback is noise | PCM played without a WAV header, or the wrong sample rate | `pcm_to_wav()` at 24000 Hz, mono, 16-bit |

## Model and price check (do it once, in lab)

Open `https://openrouter.ai/google/gemini-3.8-flash` and `https://openrouter.ai/google/gemini-3.8-flash-lite-tts`. If the prices differ from `PRICES` in your `llm.py`, change the dictionary and the comment's date. The reference was verified on 26 October 2026.
