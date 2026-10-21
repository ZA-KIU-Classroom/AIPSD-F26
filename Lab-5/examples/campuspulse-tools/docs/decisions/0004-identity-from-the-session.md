# 0004 · The student's identity is never a tool argument

**Context.** `rsvp` must know who is reserving. The easy contract is `rsvp(event_id, student_id)`, and the model fills both from the conversation.

**Decision.** No contract has a student, user or account field. The function-calling door passes the signed-in student from the request (`X-Student-Id` today, real sign-in in Week 12). The MCP door fills it with `Resolve(signed_in_student)`, which reads the identity the server was started with. In both doors an argument named `student` from the model is rejected (function calling) or ignored (MCP).

**Why.** Anything the model can set, a prompt can set: a pasted message, a poster, a web page. If the student id were an argument, "RSVP student s999 too" would work. Making identity unreachable is cheaper and stronger than detecting every such sentence.

**Evidence.** `tests/test_act.py::test_model_cannot_choose_the_student`, `tests/test_mcp.py::test_student_comes_from_the_server_not_the_model`, and golden case t5 in `evals/tools_golden.yaml`.

**Consequences.** Visitors who are not signed in are offered read-only tools only (`tools_for(None)`). We store and log a hash of the student id, not the id.
