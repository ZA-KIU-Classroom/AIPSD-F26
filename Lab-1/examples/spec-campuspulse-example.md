# Spec v0 · CampusPulse (example)

*A filled example at the level we expect for Lab 1. Yours can be rougher.*

## Problem
Students find out about campus events from posters and group chats, usually after the event. There is no single place to ask "what is happening" and get a current answer.

## Users
KIU students who want to attend events but do not follow every club channel. Secondary: club organizers who want turnout.

## Success criteria
1. A student gets a correct answer about this week's events in under 3 seconds.
2. Cost per answer stays under $0.005.
3. In testing, 9 of 10 golden questions pass.

## Core feature (Weeks 2 to 4 scope)
Ask a question about campus events in plain language, get an answer grounded in the events dataset. No accounts, no booking yet.

## Context list
- `events.json` (title, time, place, category, status, week) · in the repo
- Current week number · computed server-side
- Nothing else. User history and club descriptions come later.

## Acceptance criteria
1. "What is happening Friday?" returns only confirmed events for this week's Friday.
2. A question about a week with no events says so instead of inventing one.
3. Every response logs prompt tokens, completion tokens, and latency.

## Napkin math
500 req/day × (5,200 × $0.75 + 210 × $3.75) / 1M × 30 ≈ $70/month on gemini-3.8-flash.

## Risks and safety
- Stale `events.json` makes confident wrong answers. Mitigation: show data freshness in the reply.
- Latency spikes at peak times. Mitigation: measure now, cache in W10.
- Misuse: someone asks it non-event questions. Mitigation: system prompt scopes refusals.

## Out of scope (for now)
Bookings, accounts, voice, posters, Georgian language (planned W6+).
