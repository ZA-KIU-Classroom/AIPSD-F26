# MCP in practice

*Optional reference for Lab 5, Part 3 and HW2. About 1,300 words. Read it if the roles, the transports, or the SDK's version 2 names are unclear, or if your server will not behave.*

## 1 · The idea in plain language

The Model Context Protocol is an open standard for connecting apps that want tools to systems that have them. Before it, every AI app wrote its own integration for every service: four apps and four services meant sixteen integrations. With MCP, each app speaks the protocol once and each service speaks it once: eight implementations, and any app can use any server.

Three roles. The **host** is the app a person uses: Claude Code, Cursor, VS Code, or your own product. It owns the model and the conversation. Inside the host, one **client** per connected server handles the protocol. The **server** exposes capabilities. A server can offer three kinds of thing: **tools** (the model decides to call them), **resources** (the app reads them by URI, like files), and **prompts** (templates a person picks). Lab 5 uses tools only.

Two transports. **stdio**: the host starts the server as a subprocess and talks through standard input and output. Local tools, your laptop, no network. **Streamable HTTP**: the server has a URL, and many hosts can connect. That is what you deploy.

The specification is versioned by date. The current revision is **2026-07-28**. Its headline change is a stateless core: no `initialize` handshake and no session id. Each request carries its protocol version and the client's capabilities in its own metadata, so any replica of a server can answer any request, behind an ordinary load balancer. The spec's advice for state is explicit handles passed as ordinary arguments, like CampusPulse's `event_id`. The same revision deprecates three older features (roots, sampling and protocol-level logging) with at least twelve months before any removal, and adopts full JSON Schema 2020-12 for tool input and output schemas.

## 2 · Why it matters in production

MCP makes a capability reusable, and that is exactly what makes it risky. Once your server speaks MCP, hosts you do not control can call it, with models you did not choose, reading conversations you never see. Your validation must not depend on your own model or your own provider's strict mode. It has to live in the server.

The cautionary story is Invariant Labs' May 2025 demonstration against the official GitHub MCP server. A malicious issue on a public repository contained instructions. A user asked their agent, connected to GitHub through MCP, to look at the open issues. The agent read the issue, followed it, pulled data from the user's private repositories and published it in a pull request on the public one. Invariant stressed that the server code had no bug to patch: the access token reached every repository, so the agent could too. The fix is architectural: scope access to what the task needs.

## 3 · Worked example: CampusPulse's server, line by line

`src/mcp_server.py`, Python SDK 2.3:

- `mcp = MCPServer("campuspulse", instructions=...)`. In SDK version 1 this class was `FastMCP`; version 2 renamed it and removed the old import. Many tutorials online still use the old name.
- `@mcp.tool(annotations=READS, description=CheckRoom.__doc__)` registers a function. The SDK reads the type hints (`RoomCode`, `Day`, `Clock`, `Minutes`, from `src/contracts.py`) and builds the input schema from them. It validates every incoming call against that schema before your function runs, so `2026-02-30` never reaches `check_room`.
- The return type `-> tools.RoomStatus` becomes an output schema, and the result goes back as structured content a host can use, not only text.
- `_run()` turns our `ToolFailure` into the SDK's `ToolError`. The SDK sends a `ToolError` message to the model. Any other exception is treated as a crash: the model sees only "Error executing tool check_room", and the server logs the traceback. Leaking nothing is the default.
- `rsvp(event_id: EventId, student: Annotated[str, Resolve(signed_in_student)])`. `Resolve` is new in version 2: the SDK fills `student` by running your function and removes it from the schema. The model cannot see the parameter, so it cannot fill it. If the model sends `"student": "s999"` anyway, the SDK ignores it.
- `mcp.run()` serves stdio; `mcp.run("streamable-http", host=..., port=8000)` serves HTTP at `/mcp`.

Testing needs no host at all:

```python
from mcp import Client
from src.mcp_server import mcp

async with Client(mcp) as c:
    tools = (await c.list_tools()).tools
    r = await c.call_tool("check_room", {"room": "B204", "date": "2026-10-29", "start": "15:00"})
    assert r.structured_content["free"] is True
```

`Client(server)` dispatches in memory: no subprocess, no network. The same `Client` takes a URL for HTTP or `StdioServerParameters(...)` to launch a real subprocess.

## 4 · Behaviours that surprise people

- **Unknown arguments are dropped, not rejected.** Send `{"from_date": "2026-10-21", "admin": true}` to `list_events` and the SDK silently ignores `admin`. Our function-calling door rejects it. Neither lets it reach your function, but know which your framework does.
- **Annotations are hints.** `read_only_hint=True` is a claim the server makes. The specification says clients must never base decisions on annotations from untrusted servers. Your own server must enforce what its annotations claim.
- **Sync tools run on a worker thread.** Fine for quick lookups. A tool that writes a file must still be safe if two calls arrive at once; Week 6 deals with shared state properly.
- **Version mismatch.** A host speaking an older revision still works: SDK 2 serves 2025-era clients from the same endpoint. When something does not connect, check both versions first.
- **stdio servers are silent.** `python -m src.mcp_server` prints nothing and waits for a host. That is correct. Anything your code prints to standard output corrupts the protocol; log to standard error.

## 5 · Common mistakes and how to spot them

| Mistake | Symptom | Fix |
|---|---|---|
| Copying a version 1 tutorial | `ModuleNotFoundError: No module named 'mcp.server.fastmcp'` | `from mcp.server import MCPServer` |
| Re-implementing the tool inside the server | the two doors disagree; both-doors test fails | call the same function with the same contract object |
| `print()` in a tool | the host disconnects with a parse error | `print(..., file=sys.stderr)` or the `logging` module |
| Raising `ValueError` for an expected failure | the model sees only "Error executing tool" | raise `ToolError` with a useful message |
| Identity from an environment variable read inside the tool body | the parameter still appears in the schema, or tests cannot vary it | `Resolve(signed_in_student)` |
| Serving HTTP on `0.0.0.0` with no auth | anyone on the network can call your tools | `127.0.0.1` until Week 12's deployment and auth |

## 6 · Check yourself

1. Your server works in the in-memory test but Claude Code shows it as failed. Name two things to check first.
2. Why does a stateless protocol suit CampusPulse's design with no changes?
3. A third-party MCP server marks its `delete_file` tool with `read_only_hint=True`. What should your host do with that hint, and why?

*Answers: (1) Run the exact command from the host config by hand to see import errors; check that the working directory and `env` are set in the config; look for `print()` writing to standard output. (2) Every CampusPulse call carries what it needs (`event_id`, the date) as arguments, and identity comes from the server's environment, so no request depends on a previous one. (3) Ignore it for any decision: hints from an untrusted server are claims, not guarantees. Confirm with the person before any call, or do not connect the server.*
