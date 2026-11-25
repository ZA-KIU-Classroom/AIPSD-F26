# HW2 · "Tool Contract" · write-up template

This page becomes the three files in `hw2/<your-github-username>/`. It adds nothing to HW2: the brief is `Lab-5/HOMEWORK.md`. Replace every `<...>`. Each prompt asks for something only your own repo can supply, so an answer that would fit any team's project is not an answer. A finished page: `examples/hw2-writeup-campuspulse.md`.

---

## Part 1 · save as `contract.md` (one page)

**Tool:** `<tool_name>` · **Owner:** `<your-github-username>` · **Team repo:** `<link>`
**Code on `main`:** contract class `<ClassName>` in `<file>` line `<n>` · function in `<file>` line `<n>` · registry entry in `<file>` · MCP registration in `<file>`
**Product pull request:** `#<number>` · merged commit `<short SHA>`

**In one sentence, for the model:** `<the docstring the model reads, copied from your code, not rewritten>`

| | |
|---|---|
| **Effect** | reads · adds · changes (pick one, and name what) |
| **Undo** | how a person reverses it in your product, or "nothing to undo" |
| **Idempotent?** | what happens on the second identical call: paste the actual second result |
| **Offered to** | which callers see this tool, and the line of code that decides it |
| **Identity from** | where the caller comes from in your code. Never an argument |
| **Touches** | the one table, folder or API scope it needs, by its real name |
| **Must never** | the one thing it must never do, even if asked |

**Inputs.** One row per argument, copied from your contract class.

| Argument | Type | Constraint (pattern, set or bounds, as written in code) | Description the model reads |
|---|---|---|---|
| | | | |

**Expected failures.** The exact message strings from your code.

| When | Message the model reads |
|---|---|
| | |

**The decision I had to make.** Three to five sentences: one thing the first version of this tool could do that the final version cannot, why you removed it, and where the removal is visible (a diff, a decision record, a deleted scope).

---

## Part 2 · save as `evidence.md`

**Where the cases live:** `evals/tools/<your-github-username>.yaml`, run by `<test file>` in CI job `<job name>`

| # | Type | Call, exactly as in the yaml | Expected | Actual result, pasted from the test output | Pass? |
|---|---|---|---|---|---|
| | normal | | | | |
| | normal | | | | |
| | normal | | | | |
| | bad-input | | | | |
| | adversarial | | | | |

**The adversarial case, in one sentence:** what an attacker or a confused model is trying to get your tool to do, in terms of your product's own data.

**The red run.** Branch `<name>` · what you weakened, as a one-line diff · pull request `#<number>` (closed, not merged) · run link `<url>` · the names of the tests that failed, pasted · the exact text GitHub showed on the merge button.

**What the red run taught me.** One paragraph. It must name something you did not know before the run: a case that failed for a different reason than you expected, a rule that turned out not to be the one protecting you.

**The green run.** Product pull request `#<number>` · run link `<url>` · the last line of the pytest output, pasted (the count of passed tests).

**Through the MCP door.** The client you used, the sentence you typed, and the tool calls it made, in order.

---

## Part 3 · save as `journal.md`

Copied from `docs/journal/<your-github-username>.md`. Three entries. Each one names a file, a test or a pull request in your repo.

### Week 5 · Tool Contract
**Where I used it:** `<file or pull request>`. **What I noticed:** `<one thing that went differently from what you expected>`. **Do differently:** `<one change to how you work>`.

### Week 6 · Session State
**Where I used it:** `<the thing your product remembers, its scope and its lifetime, and the file that sets them>`. **What I noticed:** `< >`. **Do differently:** `< >`.

### Week 7 · Supervised Autonomy Loop
**Where I used it:** `<the goal your loop takes, and the one tool in NEEDS_YES>`. **What I noticed:** `< >`. **Do differently:** `< >`.

---

## Before the form

- [ ] Both pull requests merged to `main`
- [ ] Every `<...>` on this page replaced; no line would be true of another team's repo
- [ ] No key, no `.env`, no personal data
- [ ] Form filled once, with your full name and your KIU email
