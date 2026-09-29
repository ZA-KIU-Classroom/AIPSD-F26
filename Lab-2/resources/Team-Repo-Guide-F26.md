# Team Repo Guide · [Team name]

*Your team's GitHub rulebook for the whole capstone, from Lab 2 to Demo Day. Copy this file to `docs/TEAM-REPO.md`, fill in section 1 together in Lab 2, and keep it true. Sections 2 to 11 are the course standard: they change only with my agreement (last section).*

**Why it matters.** Half your course grade depends on this repo: the Design Review (10), the Safety and Evaluation Audit (10), Demo Day (20, a live demo of what is on `main`) and the Repository Review (10). HW1 (5) and HW2 (5) live here too. The repo is also your evidence trail: who built what, what was delegated to AI, and how it was verified. Keep it the way this guide says, and every milestone becomes a matter of pointing at what is already there.

---

## 1 · Our team (fill in together, Lab 2)

| Member | GitHub username | Standing role |
|---|---|---|
| | | Repo keeper |
| | | Spec keeper |
| | | Eval keeper (from Week 4) |
| | | |

- **Repo keeper:** owns the repo; access, settings, branch rules, CI, tags. Makes the "ask first" changes to `.github/`.
- **Spec keeper:** `docs/spec.md` and `AGENTS.md` stay true and current.
- **Eval keeper:** `evals/`, the golden set and the evaluation results in the README, from Week 4.

Teams of two: each person holds two roles. Roles decide who keeps a file honest, not who may touch it. At Demo Day any member answers any question about any part.

**Slice rota (recommended):** the person who drives the agent rotates every slice, and the reviewer is the next person in the rota, so everyone drives at least one slice before Week 4.

Our capstone in one sentence: [product, for whom, why]
Repo: [link] · Instructor access: [ZA-KIU collaborator / public] · Team OpenRouter key issued to: [name] (never paste the key here)

---

## 2 · The structure

One repo per team, for the whole semester. Create missing folders now; an empty folder needs a `.gitkeep` file to be committed.

```
<team-repo>/
├── README.md                    the product's front page (section 10): judges and graders open this first
├── AGENTS.md                    how agents work here (v2 from Lab 2); CLAUDE.md contains "@AGENTS.md"
├── TEAM-CONTRACT.md             signed by every member, end of Week 3
├── .env.example                 every variable name the app needs, with non-secret defaults only
├── .gitignore                   .env, .venv, __pycache__, node_modules, data you must not share
├── requirements.txt             or package.json (Node teams: adapt ci.yml in Lab 2 and show me)
├── pytest.ini                   tells pytest to collect tests/ only
├── .github/
│   ├── workflows/ci.yml         runs tests/ on every push and pull request; HW2 adds a check (Weeks 5 to 7), evals join in Week 11
│   ├── pull_request_template.md the review checklist
│   └── ISSUE_TEMPLATE/slice.md  one issue per slice
├── src/                         product code (the Week 5 tools and MCP server live here too)
├── tests/                       tests that run in CI: no API calls, no keys
├── evals/                       golden sets and eval results (section 7)
├── data/                        sample and seed data only; never personal data
├── docs/
│   ├── TEAM-REPO.md             this file
│   ├── spec.md                  the living spec: v0 (Lab 1), v1 (Lab 2), then it grows
│   ├── delegation-log.md        the team's shared delegation log
│   ├── decisions/               one short record per decision a newcomer would question
│   ├── journal/<username>.md    each member's Pattern Journal, all semester
│   └── ...                      lab and milestone working files (section 3)
├── hw1/<username>/              HW1, individual, due Thursday of Week 4
└── hw2/<username>/              HW2 write-up, individual, due end of Week 7 (paths confirmed in the HW2 brief)
```

Later labs add to this, never replace it: HW2's CI check in Weeks 5 to 7, evaluation steps in CI in Week 11, a Dockerfile in Week 12. Each lab README names the exact paths.

**Rules of thumb:** product code in `src/`; proof that it works in `tests/` and `evals/`; explanations and decisions in `docs/`; individual homework code and write-ups in `hw1/` and `hw2/` (HW2's product and CI changes are the one exception, section 4).

---

## 3 · Milestones and homework: what lives where

| When | What | Who | Points | Lives in the repo as | Built from |
|---|---|---|---|---|---|
| End of Week 3 | Team contract | team | part of the Design Review | `TEAM-CONTRACT.md`, from `Lab-1/templates/team-contract.md` | Lab 1 |
| Thursday of Week 4, 23:59 (Tbilisi time) | **HW1 · Spec to Ship** | individual | 5 | `hw1/<username>/`: `spec.md`, `golden.md` (3 golden questions with results), `delegation.md` (half a page), `journal.md` (your Weeks 1 to 4 entries, copied from `docs/journal/<username>.md`), `src/`. Then the submission form (link on Teams) | Labs 1 to 3 |
| Week 4 | **Design Review** | team | 10 | working files in `docs/`; the Week 4 brief sets the submission format; conducted in the Week 4 lab studio | spec (problem, users, success criteria), architecture, prompt and data flows, risks and safety threats, evaluation plan, token budget (the spec's napkin math), team contract |
| Released with the Week 5 lab, due end of Week 7 | **HW2 · Tool Contract** | individual | 5 | one capstone function wrapped as an MCP tool (in `src/`), a small golden set with one adversarial input, a CI check that blocks the merge when it fails, journal Weeks 5 to 7; exact paths in the HW2 brief (`hw2/<username>/` reserved for the write-up) | the Week 5 lab |
| Week 11 | **Safety and Evaluation Audit** | team | 10 | submitted against your Week 11 lab tag: golden set and regression tests running in CI, red-team results, bias and privacy checks, error taxonomy, telemetry plan | `evals/`, CI, `docs/` |
| Week 14 | Backup demo video | team | part of Demo Day readiness | video link committed to the README | the Week 14 lab |
| Week 15 | **Demo Day** | team; any member answers any question | 20 | the live product on your final tag | everything |
| Week 15, due the following Sunday 23:59 (Tbilisi time) | **Repository Review** | team, plus one individual journal line | 10 | the whole repo against the checklist in section 10 | everything, plus `docs/journal/<username>.md` Weeks 10 to 14 |

**Not in the repo:** watch-checks (Google Forms before each recorded lecture's lab), the peer assessment form (opens Week 14, due Week 15), both quizzes and the midterm.

**Weeks 8 and 9** (midterm period, no classes) are protected build time. The repo rules do not pause.

---

## 4 · How work flows

Every change, human or agent, takes the same path. It is the Week 2 loop, made permanent.

```
issue  →  branch  →  plan (agent proposes, a human approves)  →  build  →  tests read first, then run
       →  pull request with checklist  →  CI green  →  a teammate reviews and merges  →  log entry
```

1. **Issue.** One issue per slice, from the Slice template: acceptance criteria, done-when, not in this slice.
2. **Branch** from an up-to-date `main`: `slice-<issue>-<two-words>` (for example `slice-4-events-endpoint`), `fix-<issue>-<two-words>`, or `docs-<two-words>`.
3. **Build** with your agent, plan first. The agent never pushes and never merges.
4. **Pull request** into `main`, with `Closes #<issue>`. Tick only what you actually did in the checklist.
5. **Review and merge.** The person who drove the agent does not merge. A teammate reads tests first, then code, approves (Files changed → Review changes → Approve), and merges with **Squash and merge**.
6. **Log.** Add the entry to `docs/delegation-log.md`, in the same pull request or right after.

**Individual homework uses the same path, with one difference.** Branch `hw1-<username>`, pull request, CI green, a teammate approves and merges. The teammate checks only that the changes stay inside your own folder. They do not edit or improve your homework: it is individual work. Your `hw1/<username>/delegation.md` is your own log for HW1; the team's `docs/delegation-log.md` is for the product. HW1 tests run with `pytest hw1/<username>`; they are not part of team CI.

**HW2 is the exception.** It wraps a capstone function as a tool and adds a CI check, so it changes `src/` and `.github/workflows/ci.yml`. Put those changes in their own pull request, reviewed like any product change, with the repo keeper approving the CI edit. Only the write-up under `hw2/<username>/` is individual-only. The HW2 brief in Week 5 confirms the details.

**Own your commits.** Every member commits from their own GitHub account, on their own machine. No shared accounts, no committing on someone's behalf. Commit history and pull requests are part of the evidence of who built what, and the course reserves an oral defense to check it.

**AI use is permitted and logged.** Agents and AI tools are allowed for everything in this repo. Log significant delegations in the delegation log. AI is not allowed only in the quizzes and the midterm.

**`main` is always green and always demoable.** If `main` breaks, fixing it comes before any new slice.

**Commit messages:** short and specific, present tense: `Add 422 for out-of-range week (AC3)`. They do not need to mention AI; the delegation log does that.

---

## 5 · Access and protecting `main` (repo keeper, 10 minutes, Lab 2)

**Give your instructor access, one of two ways:**
- **Private repo:** Settings → Collaborators → Add people → **ZA-KIU**. (On a personal account every collaborator gets write access. That is fine: I review, I do not push.)
- **Public repo:** Settings → General → Danger Zone → Change visibility → Public. The Repository Review expects a clean public repo by Week 15 anyway.

Public means anyone can read every commit, forever, and other teams can read your HW1 and HW2 folders before the deadlines. **Recommended:** stay private with ZA-KIU as a collaborator until HW2 is graded, and go public by Week 14 for the Repository Review. Before you switch: no keys anywhere in the history, no personal data in `data/`, and every member agrees.

**Every member** is a collaborator with write access (Settings → Collaborators). The repo keeper stays the owner.

**Protect `main`:** Settings → Rules → Rulesets → New branch ruleset (older interface: Settings → Branches → Add rule). Target: `main`. Turn on:

- Require a pull request before merging, with **1 approval**
- Require status checks to pass: select **test** (it appears after CI has run once)
- Block force pushes
- Restrict deletions

**Settings → General → Pull Requests:** keep **Allow squash merging** ticked, untick "Allow merge commits" and "Allow rebase merging", and turn on "Automatically delete head branches."

A banner saying the rules are not enforced, on a private repo? Enforcing rules on private repos needs GitHub Pro, which is free for students with the GitHub Student Developer Pack (education.github.com; approval can take a few days). The owner applies for it, or the team makes the repo public. Until the rule is enforced, it still stands as a team rule: nobody pushes to `main`.

---

## 6 · Tags: the evidence trail

Each lab ends with a tag on `main`. Together they show how your product grew, week by week. The Audit is submitted against your Week 11 lab tag, and the Design Review and Repository Review look at the same history.

| When | Tag | What `main` contains |
|---|---|---|
| Lab 1 | `lab1-spec` | team, repo, spec v0, first AGENTS.md |
| Lab 2 | `lab2-agentic` | this guide adopted, spec v1, AGENTS.md v2, first slice merged through the gates, first log entries |
| Lab 3 | `lab3-multimodal` | one image-to-data feature with a low-confidence path |
| Later labs | announced in each lab README | one tag per lab, same rule |

```
git switch main && git pull
git tag <tag-name> && git push origin <tag-name>
```

Tag only on `main`, only when CI is green. Tagged the wrong commit? See `Lab-2/resources/git-pr-ci-troubleshooting.md`.

---

## 7 · Evidence: tests, golden sets and the Evidence Rule

**The Evidence Rule, from the Week 4 lab on:** every feature you merge carries at least one test (a unit test, a golden question or an eval case) and one log entry. Until the Week 4 lab says otherwise, read "log entry" as a line your running feature writes (for example the usage, cost and latency line every model call already logs). "It works" is a measurement, not a feeling. The pull request checklist asks for both.

**The golden set grows with the course:**

| When | Golden questions | Where |
|---|---|---|
| HW1 | 3, with results | `hw1/<username>/golden.md` |
| Week 4 | your first golden set, run against your pipeline (CampusPulse uses 5; the Week 4 lab sets yours) | `evals/` |
| Week 11 | 10, by the composition rule: 3 factual, 2 reasoning, 2 edge case, 2 refusal, 1 format; pass threshold 0.70; runs in CI and blocks a regressing merge | `evals/` and `.github/workflows/ci.yml` |

Unit tests in `tests/` never call a real model, so they run in CI without a key. HW2's check joins CI in Weeks 5 to 7. Evaluations that call a model join CI in Week 11, with the key stored as a repository secret (section 9).

---

## 8 · Issues, board and the weekly habit

- **Labels:** `slice`, `eval`, `blocked`, plus GitHub's default `bug` and `documentation`. Create the new three once, in Issues → Labels, or with the GitHub CLI:
  ```
  gh label create slice --color 1f6feb
  gh label create eval --color 8250df
  gh label create blocked --color d73a4a
  ```
- **Board:** a GitHub Project linked to the repo, columns Todo · In progress · In review · Done. Every slice issue goes on it.
- **After every lab, 15 minutes as a team:** move cards, pick the next slice and its driver from the rota, read the last three log entries. Anything that went wrong twice becomes a line in AGENTS.md or a test.

---

## 9 · Secrets and data

- The team OpenRouter key lives in each member's shell environment (`export OPENROUTER_API_KEY=...`). Never in code, commits, issues, screenshots or chat.
- A local `.env` file works only if your app loads it (for example with python-dotenv); if you use one, it is in `.gitignore` and never committed. `.env.example` lists the variable names with non-secret defaults only, for example `OPENROUTER_API_KEY=` and `CAMPUSPULSE_MODEL=google/gemini-3.8-flash`.
- When CI needs a key (Week 11 evals), the repo keeper adds it in Settings → Secrets and variables → Actions. Never print it in a workflow.
- A key in a commit, even for a minute: tell me the same day. Deleting the file does not remove it from history; we revoke the key.
- `data/` holds sample data you are allowed to share. No real students' names, photos, IDs or phone numbers, ever.

---

## 10 · The README and Repository Review readiness

The README is the first thing every grader and judge opens. Start from `Lab-2/templates/capstone-repo/README.md` and fill sections as they become true. The Repository Review (Week 15) checks, among other things:

- [ ] a clean public repo: no dead files, no secrets in history, the structure from section 2
- [ ] one-command setup, written in the README and working on a fresh clone
- [ ] a README with the problem, architecture and evaluation results
- [ ] CI evidence: green runs on `main`, and the evaluation gate from Week 11
- [ ] a 2-minute narrated video, YouTube Unlisted, linked in the README
- [ ] a case study: what you built, what you delegated, what you measured, what you would change
- [ ] every member's Pattern Journal, Weeks 10 to 14, in `docs/journal/`

The full checklist is walked line by line in Week 14. Build toward it weekly: a README that is true every week costs minutes; one written in Week 14 costs a weekend.

**Decision records:** when you choose something a newcomer would question (a model, a database, a library, dropping a feature), add `docs/decisions/NNNN-short-title.md` from the template: context, decision, alternatives, consequences. They are the backbone of your Design Review's architecture section and your case study.

---

## 11 · When things go wrong

| Situation | Do this |
|---|---|
| Someone pushed straight to `main` | Do not force-push over it. Open a pull request that reverts or fixes it, and check the branch rule is on |
| Your pull request conflicts with `main` | on your branch: `git fetch origin && git merge origin/main`, resolve, re-run tests, push |
| The agent committed to `main` locally | `git switch -c slice-<issue>-<words>` to keep the work, then `git switch main && git reset --hard origin/main` |
| CI red on `main` | Stop new slices. Whoever merged last fixes it first, with help |
| A teammate has not pushed anything for a week | Talk inside the team first, as your contract says; then email zeshan.ahmad@kiu.edu.ge |
| Lost or confused | `Lab-2/resources/git-pr-ci-troubleshooting.md`, then ask in lab or on Teams |

Section 1 is yours: update roles and the rota whenever they change. Sections 2 to 11 change only with my agreement: if a rule gets in your way, write a decision record arguing for the change and raise it in lab.
