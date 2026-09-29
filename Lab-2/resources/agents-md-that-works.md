# An AGENTS.md that works

*Optional reading for Lab 2, Part 2. About 10 minutes.*

## The idea in plain language

A coding agent starts every session knowing nothing about your project. It sees the tool's own instructions, your task, whatever files it decides to open, and one file you control completely: `AGENTS.md`. That file is loaded every session, before the agent reads a single line of your code.

So AGENTS.md is your standing briefing to a very fast, very literal new teammate who has amnesia every morning. It should answer the questions that teammate would otherwise answer by guessing: how do I run this, how do I test it, what are the rules here, and what must I never touch.

Two properties decide whether it works.

**Short.** It is loaded into every session, so every line costs context every time (Week 1: Context as Budget). A 400-line AGENTS.md is not thorough; it pushes your code out of the agent's attention. Aim for 25 to 40 lines.

**True.** A command that no longer works is worse than no command: the agent runs it, fails, and improvises. When you change how the project runs, AGENTS.md changes in the same commit.

## Why it matters in production

Every team that works with agents meets the same surprise. The rule was written down, clearly, and the agent broke it anyway. It added a dependency the file said to ask about. It touched a file it was told to leave alone. Long sessions make it worse: as the context fills with code and test output, a rule read an hour ago gets less attention.

The lesson is not that AGENTS.md is useless. Our Week 2 experiment (slide 15) shows how much it changes behavior. The lesson is that **AGENTS.md is guidance, not enforcement.** It raises the chance the agent does the right thing. It does not guarantee it. So every rule that really matters gets a second line of defense that does not depend on the agent's attention:

| Rule in AGENTS.md | Enforced by |
|---|---|
| Run tests before saying done | CI runs them anyway on every push |
| Never weaken a test | tests are read first in review; a weakened assertion is visible in the diff |
| Never read `.env` | the key lives only in your environment; `.env` is in `.gitignore` |
| Ask before adding a dependency | `requirements.txt` changes are always reviewed line by line |
| Ask before editing CI | CI changes are made by a person, in their own commit |

Write the rule for the agent. Build the check for the day it ignores the rule.

## Worked example: the CampusPulse AGENTS.md, line by line

Open `examples/campuspulse-week2/AGENTS.md`. It is the file from slide 14.

**Line 1 · identity and pointer.** "FastAPI service answering questions about KIU campus events. Spec: docs/spec.md." The agent should not rediscover the project from file names, and the spec should be one hop away.

**Commands.** `pip install -r requirements.txt`, `uvicorn src.app:app --reload`, `pytest -q`. These are the most valuable lines in the file. With a working test command, the agent can check its own work before claiming it is done. Test them on a clean clone: if `pytest -q` fails on a fresh checkout, fix that before you delegate anything.

**Conventions.** Five rules a smart newcomer gets wrong in their first week:
- the model id comes from an environment variable, with a default, so nobody hardcodes a model string;
- every model call goes through `src/llm.py`, so usage logging happens in exactly one place;
- times are ISO 8601 with an offset, in Asia/Tbilisi, which prevents the naive-datetime bug from slide 20;
- errors have one shape, `{"error", "field"}`, so clients handle one format;
- every new endpoint ships with a test and a golden question.

Each convention answers one of the "silent guesses" from slide 6. If you cannot say which guess a convention prevents, it probably does not belong in the file.

**Always / Ask first / Never.** Three tiers, like a first-day briefing for an intern:
- *Always* is for habits: run the tests and paste the result.
- *Ask first* is for anything hard to undo or that affects other people: dependencies, response shapes, CI.
- *Never* is for damage: secrets, and weakening tests.

**`CLAUDE.md`.** One line, `@AGENTS.md`, so Claude Code reads the same file. One source of truth, whatever tool each teammate prefers.

## Common mistakes

- **Copying a template without editing it.** "[Your framework]" left in the file tells the agent nothing. So does a convention you do not actually follow.
- **Writing prose instead of rules.** "We value clean, well-tested code" changes nothing. "New endpoint = new test in tests/" changes behavior.
- **Commands that only work on one laptop.** Paths like `/Users/nino/...` or a virtualenv name only one person uses.
- **Growing it forever.** Every delegation log entry tempts you to add a line. Add a rule when a mistake happens twice, and delete rules that never fire.
- **Two sources of truth.** A `.cursorrules` file and an AGENTS.md that disagree. Point every tool at one file.
- **Trusting it as a lock.** It is a briefing. Keep the checks in the table above.

## Check yourself

1. Your AGENTS.md says `test: pytest`, but your tests only pass when run from the `backend/` folder. What will a new agent session probably do, and how do you fix the file?
2. Pick one of your Never lines. What is its second line of defense if the agent ignores it?
3. Why does a convention like "every model call goes through src/llm.py" matter more than a convention like "use descriptive variable names"?

*Answers to discuss in lab: (1) run it from the root, see failures, and start "fixing" code or tests; write the exact command, e.g. `cd backend && pytest -q`, and test it on a clean clone; (2) for example, keys never in the repo and `.env` git-ignored, or tests read first in every review; (3) it concentrates cost logging and model choice in one place, so a violation breaks measurement across the whole app; naming is useful but its failures are cheap and visible.*
