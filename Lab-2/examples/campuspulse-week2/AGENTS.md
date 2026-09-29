# AGENTS.md · CampusPulse
FastAPI service answering questions about KIU campus events. Spec: docs/spec.md

## Commands
install:  pip install -r requirements.txt
run:      uvicorn src.app:app --reload
test:     pytest -q

## Conventions
- Model id comes from env CAMPUSPULSE_MODEL (default google/gemini-3.8-flash)
- Every model call goes through src/llm.py, which logs usage
- Times are ISO 8601 with offset, timezone Asia/Tbilisi
- Errors return {"error": ..., "field": ...} with a 4xx status
- New endpoint = new test in tests/ + one golden question in evals/

## Always
- Run pytest before saying you are done, and paste the result

## Ask first
- Adding a dependency · changing a response shape · editing .github/workflows/

## Never
- Read or write .env, or print a key
- Delete, skip, or weaken a test to make it pass
