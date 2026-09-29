# CampusPulse · Spec v1

## Goal
Turn the Week 1 script into a FastAPI service. Users: KIU students checking what is on, from a phone.

## Acceptance criteria
- AC1  POST /chat {question} returns {answer, event_ids, usage}
- AC2  GET /events?week=N returns only confirmed events in ISO week N
- AC3  week outside 1..53 returns 422 with {"error": ..., "field": "week"}
- AC4  every model call logs model, tokens in/out, cost_usd, latency_ms
- AC5  p95 latency of /chat under 4 s with the 30-event shortlist

## Context the agent needs
data/events.json · src/format.py (Week 1 compact formatter) · AGENTS.md

## Constraints
Python 3.11 · FastAPI · OpenRouter via openai SDK · model id from env

## Out of scope
auth · database · front end · RSVP (that is Week 5)

## Verification
pytest green locally and in GitHub Actions · 3 golden questions pass (evals/golden.md)

## First slice (Lab 2)
Criteria: AC2, AC3
Done when: tests/test_events.py passes locally and in CI
Not in this slice: AC1, AC4, AC5 (next slice)
