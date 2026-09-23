# Lab 1 · Team, Repo, Spec

**Week 2 · live online · 2 hours · tag by end of lab: `lab1-spec`**

You leave this lab with three things: a working team, a live capstone repository with an `AGENTS.md`, and version zero of your product spec, written and pushed. That spec becomes your Design Review in Week 4, so nothing today is throwaway.

This lab needs only the Week 1 lecture. Two things here, `AGENTS.md` and spec writing, are first contact: the templates carry you today, and the Week 2 lecture, Agentic Engineering, goes deep on both.

Before lab, you completed the Week 1 checklist (runtime installed, GitHub ready, one free OpenRouter call made, agentic tool installed). If something failed, say so in the first 10 minutes, not at minute 90.

---

## Part 1 · Teams · 25 min

Teams are 2 to 4 people and lock at the end of Week 3 with a signed team contract. Today you form a working team; you have one week to change your mind.

1. Everyone posts one line in the meeting chat: an idea you would build, or "free agent."
2. We form breakout rooms around ideas. Talk. Ten minutes.
3. Report back: team name, members, one-sentence idea. I record it.

No team by the end of Part 1? Stay in the main room; I will place you. Cross-group teams are allowed only if every member can attend one common lab slot; ask me first.

## Part 2 · Team repo setup · 35 min

One repo per team, created through GitHub Classroom from the course template. It comes with a CI stub and the semester folders (`src/ docs/ evals/ hw1/`). Follow the order exactly; the classic failure is two people creating two teams.

1. **One member only** opens the Classroom invite (pinned on Teams), clicks **Create a new team**, and names it `team-<your-team-name>` (lowercase, hyphens). This creates the repo.
2. **Everyone else** opens the same link and **joins that existing team**. Do not create a second one. The repo appears for you after joining.
3. Everyone clones and sets identity:

```
git clone https://github.com/ZA-KIU-Classroom/<your-team-repo>.git
git config user.name "Your Name"
git config user.email "you@student.kiu.edu.ge"
```

4. **Prove everyone can push.** Each member adds one line with their name to `docs/team.md`, commits, pushes. Four members, four commits. This catches invite problems now instead of homework night.
5. Copy `templates/AGENTS.md` into the repo root and fill it in: stack, run commands, conventions, what an agent may and may not touch.

What is `AGENTS.md`? A plain file that AI coding agents read first: what your project is, how to run it, and what they are allowed to touch. Yours will be thin today and grow every week; the Week 2 lecture explains the method behind it.

**✅ Checkpoint 1 (around minute 55):** repo exists under the course org, every member has a commit in `docs/team.md`, `AGENTS.md` is filled in and pushed. Show it when I call on you.

## Part 3 · Spec v0, the agentic way · 35 min

Copy `templates/spec-v0.md` into your repo as `docs/spec.md` and fill it in as a team. One page. Every section, even roughly.

Then the drill: open your agentic tool, point it at your repo, and ask it to critique your spec. Two prompts, in this order:

1. "Read docs/spec.md and AGENTS.md. List the three biggest ambiguities an engineer would hit building this."
2. "Rewrite our success criteria so each one is measurable."

Take what is good, reject what is not, and note one thing you rejected and why. That note goes in your Pattern Journal this week. Delegate, then verify: that is the whole course in one exercise, and the Week 2 lecture gives it a name and a method.

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
