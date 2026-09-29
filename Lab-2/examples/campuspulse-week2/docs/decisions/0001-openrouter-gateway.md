# 0001 · Call models through OpenRouter, model id from the environment

**Date:** Week 2 · **Decided by:** CampusPulse team (example)

**Context.** We want to compare and switch models during the semester (Week 10 routing, Week 13 second provider) without rewriting code, and every model call must log cost.

**Decision.** All model calls go through `src/llm.py` using the OpenAI SDK pointed at OpenRouter. The model id comes from `CAMPUSPULSE_MODEL`, default `google/gemini-3.8-flash`.

**Alternatives.** Each provider's own SDK: more features, but one code path per provider. Hardcoded model string: simpler today, a rewrite every time prices change.

**Consequences.** One place to log usage and one place to add fallbacks later. We depend on OpenRouter's availability; Week 10's fallback chain addresses that.
