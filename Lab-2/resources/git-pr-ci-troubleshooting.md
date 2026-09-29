# Git, pull requests and CI: troubleshooting

*Not a concept guide. Read it when something breaks. The rules themselves are in your repo's `docs/TEAM-REPO.md`.*

## The Lab 2 flow in commands

```
git switch main && git pull
git switch -c slice-4-events-endpoint      # slice-<issue>-<two words>
# ... agent builds, you review, tests pass locally ...
git add -A && git commit -m "Add events endpoint with 422 for bad week (AC2, AC3)"
git push -u origin slice-4-events-endpoint
# open the pull request on GitHub (or: gh pr create --web, which opens the form with the checklist), "Closes #4" in the description
# teammate reviews and merges with Squash and merge when CI is green
git switch main && git pull
git tag lab2-agentic && git push origin lab2-agentic
```

## Common problems

| You see | Cause | Fix |
|---|---|---|
| CI never runs | workflow file not at `.github/workflows/*.yml`, or it is only on your branch and the PR is from a fork | check the path; push the workflow to `main` first |
| CI fails with `No module named src` | tests run from a different folder than on your laptop | keep `tests/conftest.py` from the example, or set `pythonpath` in pytest config |
| CI fails with `KeyError: OPENROUTER_API_KEY` | a test calls the real model | tests must mock model calls (see `tests/test_chat.py`); never put the key in CI for unit tests |
| Tests pass locally, fail in CI | a file only exists on your machine, or an unpinned dependency changed | `git status` for untracked files; add missing packages to requirements.txt |
| `ZoneInfoNotFoundError` on Windows | no timezone database | `pip install tzdata` |
| `rejected: non-fast-forward` on push | your branch changed on GitHub (a teammate pushed to it) | `git pull` on your branch, re-run tests, push again |
| Pull request says it has conflicts with `main` | `main` moved while you worked | on your branch: `git fetch origin && git merge origin/main`, resolve, re-run tests, push |
| Merge button greyed out | no approval yet, or CI not green | a teammate approves (Files changed → Review changes → Approve); wait for the `test` check |
| Tag already exists | tagged too early | `git tag -d lab2-agentic && git push origin :refs/tags/lab2-agentic`, then tag again on the right commit |
| Pull request template not showing | file not on `main` yet | commit `.github/pull_request_template.md` to `main` in Part 2 |
| `push declined` / `protected branch` when pushing to `main` | the ruleset is working | push your branch and open a pull request instead |
| Ruleset needs the `test` check but it is not in the list | CI has not run on `main` yet | merge or push one change that triggers CI, then add the check |
| Rules greyed out on a private repo | owner has GitHub Free | Student Developer Pack (GitHub Pro is free for students), or make the repo public |
| ZA-KIU says it cannot open your repo | invitation not accepted yet, or sent to the wrong name | Settings → Collaborators: check the username is exactly `ZA-KIU` and the invite is pending; tell me in Teams |
| A teammate cannot push their branch | not a collaborator | repo keeper: Settings → Collaborators → Add people |
| The agent committed to `main` | no branch before delegating | `git switch -c slice-<issue>-<words>` to keep the work, then reset `main` to `origin/main` with a teammate watching |

## Rules that save you

- The agent never pushes. You push, after review.
- CI configuration changes are made by a person, in their own commit ("ask first" in AGENTS.md).
- If a key ever lands in a commit, tell me the same day. Deleting the file does not remove it from history; we revoke the key.
