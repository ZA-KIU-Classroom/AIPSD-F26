# Streaming, explained

*Optional reading for Lab 6, Part 2. Read it if you want to know why streaming works the way it does, not just how to switch it on.*

## 1. The concept, in plain language

A model writes its answer one token at a time. Without streaming, your server waits for the last token, then sends the whole answer. With streaming, the provider sends each token (or small group of tokens) as soon as it exists, your server forwards it, and the browser shows it. The total time does not change. What changes is when the person sees the first word: from "when everything is done" to "about a third of a second in".

That number has a name: **time to first token**, TTFT. It is the number people feel. A reply that takes four seconds and shows nothing feels broken; the same reply that starts at 300 milliseconds and finishes at four seconds feels fast. Nothing about the model changed.

The transport most apps use is **Server-Sent Events** (SSE): an ordinary HTTP response that stays open and is written to in pieces. Each piece is a few lines of text, `event: token`, `data: {...}`, then a blank line. The browser reads the body as it arrives and splits on the blank lines. That is the whole protocol. No WebSockets, no binary framing, no library on either side.

## 2. Why it matters in production

Two reasons, and the second one is the one people miss.

**Perceived latency is the product.** Users abandon slow interfaces, and "slow" is judged by the first sign of life, not the last. Every major chat product streams for this reason alone.

**Streaming changes where your accounting happens.** When the answer arrived as one object, usage (tokens, cost) came with it. In a stream, usage arrives in the last chunk, after the text. If your logging code runs when the first token arrives, or when the HTTP handler returns the response object, it logs nothing. CampusPulse's `Stream` class logs after the loop ends, when `usage` has been seen, and it records `ttft_ms` alongside the usual numbers. Lab 6 checks that log line.

**A failure story.** A team shipped streaming in a support chatbot and their cost dashboard dropped to near zero overnight. They celebrated for a week. The bill was the same: the usage callback had been attached to the non-streaming path only, so every streamed call logged zero tokens. The fix was two lines. The lesson is the Evidence Rule: a feature is not shipped until its log entry is proven, and the proof for a streamed call is a log line with real token counts written after the last chunk.

## 3. Worked example on CampusPulse

**The server side.** `src/llm.py` adds a `Stream` class. Iterating it calls the model with `stream=True` and yields each text delta:

```python
s = stream(messages, tools)
for piece in s:
    yield "token", piece          # the endpoint turns this into an SSE event
```

After the loop, `s.text` is the full answer, `s.usage` the token counts from the last chunk, `s.ttft_ms` the time to the first text delta, and `s.tool_calls` any tool the model asked for. The log line is written inside `__iter__`, after the last chunk, so it has every number.

**Tool calls in a stream.** The model may decide to call a tool while streaming. The call arrives in fragments: one chunk carries the id and the name, later chunks carry the arguments a few characters at a time, all tagged with the same `index`. `Stream` stitches them into the same dict shape Week 5's `call_tool()` expects. `src/chat.py` only decides what to run after the stream ends, through the same three gates as Week 5.

**The endpoint.** `src/app.py` wraps the generator in a `StreamingResponse` with `media_type="text/event-stream"`. Each event is three lines: `event: <kind>`, `data: <json>`, blank. Three kinds: `token`, `tool` (one per tool call, with `ok` and the error if any), `done` (ttft, tokens, cost, how many calls ran).

**The browser.** `static/index.html` uses `fetch` and reads `r.body.getReader()`. `EventSource` would be simpler, but it only does GET and cannot send headers, and the session and student ids travel as headers. The loop appends chunks to a buffer and splits on `\n\n`. It also measures its own first-token time, which is usually 20 to 80 ms more than the server's: that gap is the network, and it is worth seeing once.

**Try it:** `python -m demo.state_demo latency`. The scripted model sleeps per word so the shape is visible: same total, first word from 3.2 s to 0.1 s.

## 4. Common mistakes and how to spot them

- **Logging before the stream ends.** Symptom: `tokens_in: 0` on every stream line, or no stream lines at all. Fix: log after the loop, from the last chunk's usage.
- **Buffering in the middle.** A reverse proxy (nginx, some PaaS routers) buffers the whole response and delivers it at once. Symptom: it streams on localhost, not in production. Fix: `X-Accel-Buffering: no` and `Cache-Control: no-cache` headers (CampusPulse sets both), and check your host's docs for proxy buffering.
- **Splitting on `\n` instead of `\n\n`.** JSON in `data:` can be long; an event is terminated by a blank line, not a newline. Symptom: `JSON.parse` errors on long answers.
- **Forgetting the assistant turn before a tool result.** When the model asked for a tool mid-stream, you must append its own turn (with the tool calls, and `reasoning_details` for Gemini 3) before the tool message, exactly as Week 5's `as_assistant()` does. Symptom: a 400 from the provider on the second call.
- **Streaming the wrong thing.** Streaming a tool's JSON result to the user is noise. Stream model text; send tool outcomes as one event each.
- **Treating TTFT as the only number.** A stream with a 200 ms first token and a 40-second tail is still a bad experience. Log both, and watch the tail in your usage log.

## 5. Check yourself

1. Your usage log shows a stream line with `ttft_ms: 310` and `tokens_out: 0`. What went wrong, and where in the code?
2. A teammate proposes WebSockets "because streaming needs them". What would you say, and when would they be right?
3. The browser's first-token time is 900 ms but the server logs `ttft_ms: 280`. Name two places the 620 ms could be, and how you would tell them apart.
