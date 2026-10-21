# CampusPulse · tools and MCP (Week 5 reference)

Week 4's grounded `/ask`, unchanged, plus four tools the model can ask for: `check_room`, `list_events`, `make_calendar_file` (reads) and `rsvp` (adds, never removes). The same contracts are served two ways: function calling inside `POST /act`, and an MCP server any MCP host can launch. Every line of code shown in the Week 5 lecture is in these files.

## Run it

```
pip install -r requirements.txt

# offline: no key, no network, no cost. Tests, CI and the classroom demo use this.
export CAMPUSPULSE_OFFLINE=1 CAMPUSPULSE_TODAY=2026-10-21
pytest                                   # 99 offline tests: 37 from Week 4, 62 new
python -m evals.run_tool_golden          # 5 model-level tool cases, one adversarial
python -m demo.tool_demo naive           # the lab demo: three bad calls, no contract
python -m demo.tool_demo contract        # the same three calls through src/act.py
python -m demo.tool_demo mcp             # the MCP door, and a spoofed student that changes nothing

# the MCP server
CAMPUSPULSE_STUDENT=s123 python -m src.mcp_server          # stdio: what Claude Code, Cursor, VS Code launch
python -m src.mcp_server --http                            # Streamable HTTP on 127.0.0.1:8000/mcp

# live: the real model decides which tool to call
export CAMPUSPULSE_OFFLINE=0 OPENROUTER_API_KEY=...
unset CAMPUSPULSE_TODAY
python -m src.index && uvicorn src.app:app --reload
curl -s localhost:8000/act -H 'content-type: application/json' -H 'X-Student-Id: s123' \
     -d '{"question": "Save me a seat at Open Build Night"}'
python -m evals.run_tool_golden          # live: costs well under a cent
```

Logs: `logs/usage.jsonl` (every model call), `logs/answers.jsonl` (every grounded answer), `logs/tools.jsonl` (every tool call: tool, arguments, ok or the error, a hash of the student, latency). RSVPs are written to `state/rsvps.json`.

## Where things are

| File | What it does | Lecture slide |
|---|---|---|
| `src/contracts.py` | the four input contracts and the shared types; `extra="forbid"`, patterns, fixed room list; no identity field anywhere | 8 |
| `src/tools.py` | the four tools, their result models, `ToolFailure`, the registry and `tools_for()` | 8, 24 |
| `src/llm.py` | Week 4's file plus `complete_tools()`, which returns the model's request and its `reasoning_details` | 7 |
| `src/act.py` | the loop: offered? valid? run with identity from us; errors go back to the model; three rounds at most; one log line per call | 9, 10, 14 |
| `src/mcp_server.py` | the MCP door: `MCPServer`, annotations, `Resolve` for the student, `ToolError` for expected failures | 19, 24 |
| `src/offline.py` | Week 4's stand-ins plus a keyword "model" that picks a tool and copies arguments from the question | |
| `src/app.py` | `POST /ask` (Week 4) and `POST /act` | |
| `data/campus/` | three rooms, the bookings that cause clashes, five events (one full, one cancelled) | |
| `evals/tools_golden.yaml` · `evals/run_tool_golden.py` | five model-level cases (the real model picks the tool); run by hand, like Week 4; exit 1 below 0.8 | |
| `evals/tools/*.yaml` · `tests/test_tool_golden.py` | HW2-style golden cases, one file per student; no model, so they run in CI and block a merge | |
| `docs/decisions/0003`, `0004` | calendar file instead of calendar access; identity never an argument | 23, 24 |
| `demo/tool_demo.py` | the lab's live demo: naive executor, then the contract, then MCP | |

## Two things that surprise people

- **The MCP SDK drops unknown arguments; our function-calling door rejects them.** Neither lets them reach a tool. `tests/test_mcp.py` checks that both doors describe every tool's arguments identically.
- **Gemini 3-class models need their `reasoning_details` echoed back between tool turns**, or the next call fails. `as_assistant()` in `src/act.py` does it. Other models ignore the field.

Model and price, verified on openrouter.ai on 19 October 2026: `google/gemini-3.8-flash` lists `tools`, `tool_choice` and structured outputs as supported, $0.75 in / $3.75 out per million tokens (50% promotional). MCP Python SDK 2.3.0, protocol revision 2026-07-28.
