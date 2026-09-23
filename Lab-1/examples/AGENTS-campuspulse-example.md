# AGENTS.md · CampusPulse (example)

## What this project is
An AI assistant that answers student questions about campus events, grounded in a curated events dataset. Course reference build for CS6920.

## Stack
- Language: Python 3.11
- Framework: FastAPI
- Model access: OpenRouter · default model: google/gemini-3.8-flash
- Data: `data/events.json`, checked into the repo

## How to run
```
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

## Conventions
- Secrets come from environment variables (`OPENROUTER_API_KEY`). Never write a key into a file.
- Every model call reads and logs `usage` to `logs/usage.jsonl`.
- Context is filtered before every call: only this week's confirmed events. See docs/spec.md, Context list.
- New features ship with at least one golden question in `/evals`.

## You may
- Create and edit files in `app/`, `tests/`, `docs/`, `evals/`
- Propose dependency changes (ask before adding)

## You may not
- Touch `.env`, `.github/`, or `data/events.json` (data changes go through a human)
- Delete tests to make them pass
- Call paid APIs in loops without a cap
