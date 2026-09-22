# AGENTS.md · [Product name]

*Instructions for AI coding agents working in this repo. Keep it current; agents read this first.*

## What this project is
One paragraph: what we are building and for whom.

## Stack
- Language: [Python 3.11 / Node 20]
- Framework: [FastAPI / Next.js / ...]
- Model access: OpenRouter · default model: [google/gemini-3.8-flash]
- Data: [where it lives]

## How to run
```
[install command]
[run command]
[test command]
```

## Conventions
- Secrets come from environment variables. Never write a key into a file.
- Every model call reads and logs `usage`.
- New features ship with at least one golden question in `/evals`.

## You may
- Create and edit files in `src/`, `tests/`, `docs/`
- Propose dependency changes (ask before adding)

## You may not
- Touch `.env`, CI config, or anything in `secrets/`
- Delete tests to make them pass
- Call paid APIs in loops without a cap
