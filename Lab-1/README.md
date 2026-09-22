# Lab 1 · Team, Repo, Spec

**Week 2 · live online · 2 hours · tag by end of lab: `lab1-spec`**

You leave this lab with three things: a locked-in team, a live capstone repository with an `AGENTS.md`, and version zero of your product spec, written and pushed. That spec becomes your Design Review in Week 4, so nothing today is throwaway.

Before lab, you completed the Week 1 checklist (runtime installed, GitHub ready, one free OpenRouter call made, agentic tool installed). If something failed, say so in the first 10 minutes, not at minute 90.

---

## Part 1 · Teams · 25 min

Teams are 2 to 4 people and lock at the end of Week 3 with a signed team contract. Today you form a working team; you have one week to change your mind.

1. Everyone posts one line in the meeting chat: an idea you would build, or "free agent."
2. We form breakout rooms around ideas. Talk. Ten minutes.
3. Report back: team name, members, one-sentence idea. I record it.

No team by the end of Part 1? Stay in the main room; I will place you. Cross-group teams are allowed only if every member can attend one common lab slot; ask me first.

## Part 2 · Repo + AGENTS.md · 30 min

One repo per team, from the course template. It comes with a CI stub and empty folders you will fill all semester.

1. One member accepts the Classroom link (on Teams) and creates the team repo. Everyone else joins it.
2. Copy `templates/AGENTS.md` into the repo root. Fill it in for your project: stack, run commands, conventions, what an agent may and may not touch.
3. Commit and push.

`AGENTS.md` is how coding agents learn your project's rules. You saw it in Tuesday's lecture; today it becomes real. Yours will be thin now and grow every week.

**✅ Checkpoint 1 (around minute 55):** repo exists, everyone has access, `AGENTS.md` is pushed. Show it when I call on you.

## Part 3 · Spec v0, the agentic way · 40 min

Copy `templates/spec-v0.md` into your repo as `docs/spec.md` and fill it in as a team. One page. Every section, even roughly.

Then the drill: open your agentic tool, point it at your repo, and ask it to critique your spec. Two prompts, in this order:

1. "Read docs/spec.md and AGENTS.md. List the three biggest ambiguities an engineer would hit building this."
2. "Rewrite our success criteria so each one is measurable."

Take what is good, reject what is not, and note one thing you rejected and why. That note goes in your Pattern Journal this week. Delegate, then verify. That is the whole course in one exercise.

**✅ Checkpoint 2 (around minute 85):** spec v0 pushed, tagged `lab1-spec`:

```
git tag lab1-spec && git push origin lab1-spec
```

## Part 4 · Studio + homework · 25 min

Studio time: keep improving the spec, start the team contract (`templates/team-contract.md`, due with team lock next week), or start your `pattern-journal.md` from the template. I rotate rooms. Random demos: I will pick two or three people to share a screen for two minutes.

Last 10 minutes: we open HOMEWORK.md together and walk it.

---

## Folder map

- `templates/` · spec, AGENTS.md, team contract, pattern journal. Copy these into your repo.
- `examples/` · the same documents, filled in for CampusPulse. Read before writing yours.
- `resources/` · optional. Tool setup help and further reading. Nothing in there is required.

## Homework

**HW1 · "Spec to Ship" · 5 points · individual**
**Due: Thursday of Week 4, 23:59 (Tbilisi time)**
**Submit: push to `hw1/<your-github-username>/` in your team repo, then fill the submission form (link on Teams)**
**Deliver: a one-page spec, the working feature it describes, 3 golden questions with results, a half-page delegation log, and your Pattern Journal for Weeks 1 to 4**

Full brief in `HOMEWORK.md`, one folder up from wherever you are standing. It is one page. Read it today, not in Week 4.
