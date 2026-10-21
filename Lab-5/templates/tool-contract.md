# Tool contracts · [product name]

*One section per tool. Copy to `docs/tool-contracts.md` (Lab 5), or to `hw2/<your-github-username>/contract.md` for HW2 (one page). Fill every row; "n/a" is an answer, an empty cell is not. Every rule in this table must exist in code: the contract class, the tool body, or the registry.*

## `[tool_name]`

**In one sentence, for the model:** [this becomes the docstring the model reads: what it does, and whether it changes anything]

| | |
|---|---|
| **Effect** | reads · adds · changes · deletes (pick one; deletes needs my agreement) |
| **Undo** | how a person reverses it, or "nothing to undo" |
| **Idempotent?** | does calling it twice with the same arguments change anything more? |
| **Offered to** | which callers see this tool at all (visitor, signed-in user, admin) |
| **Identity from** | where the caller comes from: session, request header (stand-in), `Resolve(...)`. Never an argument |
| **Touches** | the smallest resource it needs: one table, one folder, one API scope. Name it |
| **Must never** | the one thing it must never do, even if asked |

**Inputs.** Every string has a pattern or a fixed set of values; every number has bounds; unknown fields are refused.

| Argument | Type | Constraint | Description the model reads |
|---|---|---|---|
| | | | |

**Result.** The fields it returns, with types. No internal ids the model does not need.

**Expected failures.** Each one raises your tool's failure type with a message the model can act on.

| When | Message the model reads (what happened, what to do next) |
|---|---|
| | |

**Tests and golden cases.** Name them, and the file each one lives in.

| Case | Expect | Where |
|---|---|---|
| a valid call | runs, result has ... | |
| invalid arguments | refused before the tool runs | |
| not offered to this caller | refused, nothing runs | |
| identity in the arguments | refused | |
| adversarial: [describe] | refused | |

**Log line.** What `logs/tools.jsonl` records for every call, and what it deliberately leaves out (personal data).
