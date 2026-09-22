# Lab 1 · Instructor Guide

**Week 2 · live online · run twice (Group A, Group B) · outcome: teams formed, repos live with AGENTS.md, spec v0 tagged `lab1-spec`**

## Before lab (day before)

- Post the Teams announcement (bottom of this file) with: meeting link, Classroom invite link, this lab folder link.
- Verify the Classroom template repo: CI stub green, folders present (`src/`, `docs/`, `evals/`, `hw1/`), template `AGENTS.md` absent (students bring their own from templates/).
- Prepare the team tracker sheet (team name, members, GitHub handles, idea one-liner, key issued Y/N).
- Have 4 to 6 OpenRouter team keys pre-generated with budgets; issue as teams confirm at Checkpoint 1.
- Breakout rooms enabled; ability to broadcast messages to rooms.

## Minute plan (120 min)

| Min | Segment | Notes |
|---|---|---|
| 0-10 | Recap + Q&A on Week 1 and 2 lectures | No watch-check reveal (W1-2 were in person). Ask the two questions cold: what did we say you should ask of every tool? |
| 10-15 | Lab overview | Share README, walk the folder map once. Say it explicitly: this structure repeats every week, HOMEWORK.md always at the root. |
| 15-40 | Part 1 · Teams | Chat idea lines → breakout by affinity (5-6 rooms) → 10 min → report back. Record in tracker. Free agents stay with you; place them by interest, not leftovers. |
| 40-70 | Part 2 · Repo + AGENTS.md | One member accepts Classroom link, adds the rest. Broadcast the two commands they always fumble: cloning with SSH vs HTTPS, and inviting collaborators. |
| ~55 | **Checkpoint 1** | Call 3 random teams: screen-share the repo with AGENTS.md pushed. Issue team API keys to confirmed teams (DM, never in shared chat). |
| 70-95 | Part 3 · Spec v0 + agentic drill | The drill matters more than spec polish. Push teams to actually reject one AI suggestion and write down why. |
| ~85 | **Checkpoint 2** | Broadcast the tag commands. Watch tags land: `git ls-remote --tags <repo-url>` from your side, or refresh the repo page. |
| 95-108 | Part 4 · Studio + random demos | Rotate rooms. Pick 2-3 individuals for 2-minute screen shares of their team's current state. |
| 108-118 | Homework walkthrough | Share HOMEWORK.md on screen. Read the top block out loud, word for word. Point at the due line twice. |
| 118-120 | Close | Next week: recording drops 48h before lab, first watch-check goes live, teams lock with contract. |

## Checkpoint verification

- C1 pass: repo under the Classroom org, ≥2 collaborators, `AGENTS.md` at root with project-specific content (not the raw template).
- C2 pass: `docs/spec.md` committed with every section attempted, tag `lab1-spec` visible on origin.
- Teams that miss C2 in-lab: 24 hours to push and tag, note it in the tracker. Chronic pattern starts the early-warning record.

## Common failure modes

1. **Classroom link creates a personal repo, not team.** They clicked before entering a team name. Delete, redo, join existing team.
2. **Collaborator invites lost.** Invitees must check GitHub notifications or email; the repo is invisible until accepted.
3. **AGENTS.md pasted verbatim from template.** Ask one question: "what is your test command?" If the file says `[test command]`, it is not done.
4. **The agentic drill produces worship.** Teams accept all AI critique uncritically. Force the rejection: "show me one suggestion you turned down." If they cannot, the drill has not happened.
5. **Free agents ghost after Part 1.** Message them directly in the room; unplaced students by end of lab get an email same day and a slot in a team before Week 3 lock.
6. **Key leakage.** If any team pastes a key into shared chat, revoke immediately, reissue by DM, and say why in front of everyone. Teachable moment, zero shame, one sentence.

## Cross-group teams
Allowed only if every member can attend one common slot. Record which slot; that is where their checkpoints happen.

## Teams announcement (post day before; homework block below is verbatim from HOMEWORK.md, do not paraphrase)

---

**Lab 1 is this week · live online**

Link: [MEETING LINK] · Group A [TIME] · Group B [TIME]
Before lab: finish the Week 1 checklist (runtime, GitHub, one OpenRouter call, agentic tool). Lab folder: [REPO LINK]/Lab-1 · read README.md, it is two pages.
You leave with: a team, a live repo with AGENTS.md, and spec v0 tagged `lab1-spec`.

**HW1 · "Spec to Ship" · 5 points · individual**
**Due: Thursday of Week 4, 23:59 (Tbilisi time)**
**Submit: push to `hw1/<your-github-username>/` in your team repo, then fill the submission form (link on Teams)**
**Deliver: a one-page spec, the working feature it describes, 3 golden questions with results, a half-page delegation log, and your Pattern Journal for Weeks 1 to 4**

Full brief: [REPO LINK]/Lab-1/HOMEWORK.md

---
