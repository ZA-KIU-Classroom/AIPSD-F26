# 0005 · Memory writes are explicit: the student asks, a tool runs, the reply says so

**Context.** CampusPulse could learn interests silently: run an extraction after every turn and store whatever the model infers ("the student asked about robotics twice, store 'robotics'").

**Decision.** Interests are stored only when the student asks. The model is offered `remember_interest(topic)`, a write tool under the Week 5 rules (signed-in callers only, validated topic, identity from the session). The reply to a successful write names what was stored and how to delete it. There is no `forget` tool: forgetting is `DELETE /me/memory`, a button in the app.

**Why.** A silent store is a store the student cannot audit and did not consent to. It also turns every turn into a write, which is a budget problem (Week 1) and a leakage surface: a poisoned event description could make the model "remember" instructions (Week 12). An explicit write is a small, visible, idempotent action the student can undo.

**Evidence.** `tests/test_stream_chat.py::test_chat_turn_remembers_only_when_asked_and_only_for_a_student`, `::test_a_visitor_cannot_write_memory_even_by_asking`, `tests/test_memory.py::test_a_visitor_leaves_nothing_behind`.

**Consequences.** The product remembers less than it could. Students who never say "remember" get no personalisation; the UI hint in the input box tells them the phrase.
