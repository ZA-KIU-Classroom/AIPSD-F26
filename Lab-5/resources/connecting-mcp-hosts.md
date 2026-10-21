# Connecting an MCP host · setup and troubleshooting

*Optional reference for Lab 5, Part 3. Setup help, not a concept guide. Configuration formats checked on 19 October 2026; hosts change them, so if a key name does not work, check the host's own MCP documentation.*

## Before any host: run the server by hand

From your repo root, with your virtual environment active:

```
python -c "import mcp.server; print('ok')"     # SDK 2.x installed?
pytest tests/test_mcp.py -q                     # the server works in memory?
python -m src.mcp_server                        # starts, prints nothing, waits: correct. Ctrl+C to stop
```

If the third command prints a traceback, fix that first. No host can show you a clearer error than your own terminal.

Every host needs the same three things: the **command** (`python`, ideally the full path to your virtual environment's Python), the **arguments** (`-m`, `src.mcp_server`), and the **environment** (the identity variable your server's `Resolve(...)` reads, for example `CAMPUSPULSE_STUDENT=s123`; never a real student's id, never an API key you would not want in a config file).

## Claude Code

From the repo root:

```
claude mcp add --env CAMPUSPULSE_STUDENT=s123 --transport stdio campuspulse -- python -m src.mcp_server
```

Everything after `--` is the command the host runs. Then inside Claude Code type `/mcp`: the server should show as connected with its tools. `claude mcp list` shows the status of every server from the terminal; `claude mcp remove campuspulse` removes it.

To share the setup with your team, a project-scoped `.mcp.json` at the repo root:

```json
{
  "mcpServers": {
    "campuspulse": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "env": { "CAMPUSPULSE_STUDENT": "s123" }
    }
  }
}
```

## Cursor

`.cursor/mcp.json` in the project (or `~/.cursor/mcp.json` for every project):

```json
{
  "mcpServers": {
    "campuspulse": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "env": { "CAMPUSPULSE_STUDENT": "s123" }
    }
  }
}
```

## VS Code

`.vscode/mcp.json` in the workspace. Note the different top-level key and the `type` field:

```json
{
  "servers": {
    "campuspulse": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "env": { "CAMPUSPULSE_STUDENT": "s123" }
    }
  }
}
```

## Streamable HTTP, for testing another host or a teammate's machine

```
python -m src.mcp_server --http        # serves http://127.0.0.1:8000/mcp
```

Keep it on `127.0.0.1` until Week 12: there is no authentication yet, and anyone who can reach the port can call your tools. A Python client can connect with `Client("http://127.0.0.1:8000/mcp")` from the `mcp` package.

## The five usual causes when it does not connect

| Symptom | Cause | Fix |
|---|---|---|
| Host says failed, no detail | the host runs a different Python without `mcp` installed | use the full path to `.venv/bin/python` (Windows: `.venv\Scripts\python.exe`) as the command |
| `ModuleNotFoundError: src` | the host started the server from another folder | open the project folder in the host, or add `"cwd"` if your host supports it, or use an absolute path |
| Connects, then drops immediately | something prints to standard output | remove `print()`; log to standard error |
| `ModuleNotFoundError: No module named 'mcp.server.fastmcp'` | code copied from an SDK version 1 tutorial | `from mcp.server import MCPServer` |
| Write tool says "Not signed in" | the `env` block is missing or misspelled | set the identity variable in the host config, then restart the server from the host |

## Windows notes

Use `python` or `py -3.11` as the command, whichever runs your virtual environment. In JSON, write Windows paths with forward slashes (`C:/Users/you/project/.venv/Scripts/python.exe`) or doubled backslashes. If PowerShell blocks activating the virtual environment, `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

## Checking which protocol revision you speak

`pip show mcp` should say 2.3.0 or later; that SDK speaks the 2026-07-28 revision and still serves older clients. If a host is very old and refuses to connect, update the host before you debug your server.
