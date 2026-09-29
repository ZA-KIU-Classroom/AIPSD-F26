# Spec v0 → v1 · upgrade checklist

*Work in your repo's `docs/spec.md`. Commit the upgrade as one commit: "spec v1".*

## 1 · Every section filled
Goal and users · Acceptance criteria · Context list · Constraints · Out of scope · Verification. Empty means the agent guesses.

## 2 · Every acceptance criterion testable
The test: **could a script decide pass or fail without asking you?** Rewrite each one in this table first, then copy the right-hand column into the spec.

| v0 wording | v1 wording (testable) | Checked by (unit test, golden question, log) |
|---|---|---|
| | | |
| | | |
| | | |

Include at least one criterion for an error case and one for cost or latency.

## 3 · Name the first slice
Pick the smallest piece that runs end to end. One endpoint or one function, at most three acceptance criteria.

```
## First slice (Lab 2)
Criteria: AC__, AC__
Done when: [the tests that must pass]
Not in this slice: [everything else, explicitly]
```

## 4 · Verification section says how
Which command runs the tests, and what counts as green. The agent reads this and can check itself before it says "done."
