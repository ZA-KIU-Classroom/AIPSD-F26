# Lab 2 · Agentic Build · `lab2-agentic`

**Week 2 · live online · right after the lecture · 2 hours · pattern: Spec Before Code**
You leave with: a team repo set up the way it will run until Demo Day, spec v1, AGENTS.md v2, and the first real slice of your capstone built by an agent and merged through three gates. Tagged `lab2-agentic`.

**Where this sits in your capstone.** Your repo grows one tagged lab at a time: `lab1-spec` → **`lab2-agentic` (today)** → `lab3-multimodal` → one tag per lab. Those tags are the history your Design Review, Safety Audit and Repository Review look back on. Today's slice is the first piece of your own core feature, not an exercise.

**Before lab:** the team repo from Lab 1 is cloned on every member's machine, your agentic tool is signed in, and the team OpenRouter key is exported in your shell, not saved in a file.

---

## Part 1 · Spec v0 → v1 · 12 min

1. Open `docs/spec.md` next to `templates/spec-v1-upgrade.md`. Fill every section.
2. Rewrite each acceptance criterion until a script could decide pass or fail without asking you. At least one covers an error case, one covers cost or latency. Stuck? `resources/writing-testable-specs.md`.
3. Add a **First slice** section: the smallest piece of your spec's core feature that runs end to end. At most three criteria.
4. Commit: `spec v1`. Model answer: `examples/campuspulse-week2/docs/spec.md`.

## Part 2 · The team repo for the whole capstone · 15 min

`templates/team-repo-guide.md` is your team's rulebook until Demo Day.

1. Copy it to `docs/TEAM-REPO.md`. Fill section 1 together: members, GitHub usernames, roles. Read section 3 once: where every milestone and homework lives.
2. Match the structure in section 2. Copy in what you are missing from `templates/capstone-repo/` (README skeleton, `.env.example`, `.gitignore`, `pytest.ini`, issue template, `docs/decisions/`, `docs/journal/`). Never overwrite a file you already have.
3. Rewrite `AGENTS.md` from `templates/AGENTS-v2.md`: exact commands, conventions, Always / Ask first / Never, your three Never lines. Claude Code users: `CLAUDE.md` with one line, `@AGENTS.md`. Why: `resources/agents-md-that-works.md`.
4. Make the test command real (a smoke test is fine). A person, not the agent, checks `.github/workflows/ci.yml` against `templates/ci.yml` (the job must be named `test`) and copies `templates/pull_request_template.md` to `.github/`. Push once so CI runs.
5. **Repo keeper, last:** give **ZA-KIU** access (collaborator, or make the repo public) and protect `main` (section 5). From now on, every change arrives by pull request.

**✅ Checkpoint 1 (around minute 57):** `docs/TEAM-REPO.md` with roles, the structure in place, ZA-KIU has access, `main` protected, spec v1 and AGENTS.md v2 on `main`, CI green.

## Part 3 · Delegate the slice · 28 min

The Week 2 loop, now your permanent workflow (guide section 4). One person drives the agent; another reviews and merges.

1. Open an issue from the **Slice** template: criteria, done-when, not in this slice.
2. `git switch main && git pull && git switch -c slice-<issue>-<two-words>`
3. Prompt: *"Implement the First slice in docs/spec.md. Propose a plan first. Do not write any files until I approve the plan."*
4. **Gate 1, the plan.** Check it against each criterion. Fix the plan, not the code later.
5. Let it build. **Read `tests/` before `src/`.** Could each test fail if the feature broke? `resources/reviewing-agent-code.md`.
6. **Gate 2, the tests.** Run them yourself; read the output, not the agent's summary.
7. Push, open a pull request with `Closes #<issue>`, tick only what you actually did.
8. **Gate 3, CI green.** Your teammate reviews, clicks **Approve**, and merges with **Squash and merge**.
9. Add your entry to `docs/delegation-log.md` (`templates/delegation-log.md`), including what you checked.

Failed review? Good: log it, fix the spec or AGENTS.md, delegate again. Why: `resources/gates-and-the-ladder.md`.

**✅ Checkpoint 2 (around minute 85):** slice merged, CI green, log entry written. Then:

```
git switch main && git pull
git tag lab2-agentic && git push origin lab2-agentic
```

## Part 4 · Studio · 20 min

- Board and labels (guide section 8); first README fill: problem, how to run.
- One decision record in `docs/decisions/` for a choice you made today.
- `TEAM-CONTRACT.md` from `Lab-1/templates/team-contract.md`, due end of Week 3. Your Week 2 journal entry in `docs/journal/<username>.md`.

Last 15 minutes: HOMEWORK.md together, then a look at next week.

---

## Folder map

- `templates/` · team repo guide, capstone repo starter files, spec v1 checklist, AGENTS.md v2, delegation log, PR checklist, CI.
- `examples/campuspulse-week2/` · the lecture's service, with the rejected slide 20 diff in `demo/`.
- `resources/` · optional depth: four concept guides and a Git and CI troubleshooting guide.

---

## Homework

**No new homework this week.** Two things are due, and nothing new is graded.
**1. HW1 keeps going (unchanged since Lab 1):**
**HW1 · "Spec to Ship" · 5 points · individual**
**Due: Thursday of Week 4, 23:59 (Tbilisi time)**
**Submit: push to `hw1/<your-github-username>/` in your team repo, then fill the submission form (link on Teams)**
**Deliver: a one-page spec, the working feature it describes, 3 golden questions with results, a half-page delegation log, and your Pattern Journal for Weeks 1 to 4**
**2. Team contract · due end of Week 3 · part of your Design Review (10 points, Week 4)**
**Submit: `TEAM-CONTRACT.md` at your team repo root, from `Lab-1/templates/team-contract.md`, every member's name typed in**

Full notes: [HOMEWORK.md](HOMEWORK.md)
