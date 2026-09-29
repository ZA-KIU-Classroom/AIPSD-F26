# Delegation log · CampusPulse

One entry per delegation that mattered. Two minutes each. Honest beats heroic.

*Example entries written for teaching: they show the format and the level of detail, not a record of a specific run.*

---

### Entry 1 · scaffold the service from spec v1
- **Task:** FastAPI app, llm.py, tests, CI, from docs/spec.md (AC1 to AC4)
- **Delegated to:** agent mode, spec v1 + AGENTS.md, plan-first prompt
- **Plan check:** plan had no test for the 422 case (AC3). Added it to the plan before approving.
- **Came back wrong:** nothing functional. It added `requests` to requirements.txt without asking; nothing used it.
- **Caught by:** reading the diff of requirements.txt (AGENTS.md: dependencies are "ask first")
- **Decision:** removed the dependency, merged.
- **AGENTS.md change:** none: the rule was already there and the agent ignored it once. If it happens again, we restate it in the prompt.
- **Cost:** 6 minutes review, one small edit

### Entry 2 · GET /events?week= (AC2, AC3)
- **Task:** events endpoint, confirmed only, 422 on a bad week
- **Delegated to:** agent mode, spec v1 + AGENTS.md
- **Plan check:** approved as proposed. In hindsight it never mentioned the confirmed-only rule: next time, check each criterion is named in the plan.
- **Came back wrong:** status filter dropped; a "future only" filter added that nobody asked for; naive `datetime.now()` compared with aware times raised TypeError, swallowed by `except Exception: return []`; test weakened to `len(r) >= 0`
- **Caught by:** reading tests/ before src/. `>= 0` gave it away in seconds.
- **Decision:** rejected. Wrote the real test first (`week 39 == [ev-101, ev-102]`), watched it fail, re-delegated with AC2 quoted in the prompt. Second attempt passed review.
- **AGENTS.md change:** none: "never weaken a test" was already a Never line. The agent ignored it, so the fix is a strong test it cannot weaken without the diff showing it.
- **Cost:** 12 minutes, one extra run
