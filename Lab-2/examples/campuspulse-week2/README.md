# CampusPulse · Week 2 reference build

The service from the Week 2 lecture: the product side of the structure in `templates/team-repo-guide.md` (a real team repo also has `TEAM-CONTRACT.md`, `docs/TEAM-REPO.md`, `docs/journal/` and `hw1/`).

```
pip install -r requirements.txt
export OPENROUTER_API_KEY=...      # team key, in your shell, never in a file
pytest -q                          # 6 tests, no API calls
uvicorn src.app:app --reload       # GET /events?week=39 · POST /chat
pytest demo -q                     # the agent's rejected attempt from slide 20: its test passes. That is the problem.
```

- `docs/spec.md` · slide 8, plus the First slice section Lab 2 asks for · `AGENTS.md`, `CLAUDE.md` · slide 14
- `src/app.py` · AC1 to AC3 · `src/llm.py` · AC4, the only place a model is called
- `tests/` · a test for each of AC1 to AC4 (AC5, latency, is checked from the logs) · `evals/golden.md` · 3 golden questions
- `docs/delegation-log.md` · example entries · `docs/decisions/0001-...` · an example decision record
- `demo/` · the diff we rejected in the lecture, kept for review practice (not run in CI)
- `.github/` · CI that runs pytest, the pull request checklist, the Slice issue template
