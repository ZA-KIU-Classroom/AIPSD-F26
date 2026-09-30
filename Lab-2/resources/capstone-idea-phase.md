# Choosing Your Capstone: From Zero Ideas to One Spec-Ready Idea

**Lab 2 resource · CS6920 · Agentic Engineering**

## Before you start

Lab 1 asked you to write spec v0. Lab 2 assumes spec v0 exists. Nothing in between taught you how to arrive at the idea. This document is that step, and it is built as a journey: six steps, each with a time budget, something you do, and something you have at the end. CampusPulse, the example that runs through the whole course, walks the same six steps beside you so you can see each move before you make it.

Do the steps in order. If you walked in with an idea already, good: it becomes one card among many in Step 1, and it has to earn its place like the others. Most teams that write their idea down next to seven alternatives either find a better one or find the better version of it.

| Step | What you do | Time | What you have after |
|---|---|---|---|
| 1 · Collect | Log real friction from your own life | 8 min | Ten seeds |
| 2 · Sharpen | Learn what makes a seed an AI product | 5 min | The model-job lens |
| 3 · Expand | Run the grid and the teardown; write idea cards | 17 min | Eight or more idea cards |
| 4 · Gate | Six yes/no checks per card | 5 min | The survivors |
| 5 · Score | Weighted scorecard, comparison, pre-mortem | 8 min | One leading idea, and why |
| 6 · Commit | Turn the winner into spec v0 material | 7 min | Spec bridge, golden questions, first slice |

Fifty minutes alone, about sixty as a team. Blank templates for every step are in the appendix.

---

## Step 1 · Collect: log the friction

**Goal:** get raw material on the page before any theory gets in the way.
**Time:** 8 minutes.

List ten moments from the last two weeks where you, or someone you watched, did information work by hand. Searching three channels for one fact. Retyping something from a photo or a PDF. Answering the same question for the fifth time. Sorting a pile of messages into what matters. Deciding where a request should go. Working out whether something is still on.

Write each one as a single line: *who* was doing it, *what* they were trying to find out or produce, and *how* they did it by hand. Do not judge them. Do not think about AI yet. If you cannot reach ten, widen the circle: a family member's job, a club you are in, a part-time job, a course you TA.

**Output:** ten seeds.

> **CampusPulse at this step.** Seed: *A first-year student wanted to know if the hackathon was still on; checked four Telegram groups and the noticeboard, found two different times, went to the wrong room.*

---

## Step 2 · Sharpen: the model-job lens

**Goal:** learn the one test that turns a seed into a CS6920 idea, so you can apply it in Step 3.
**Time:** 5 minutes of reading.

### Three layers, two required

Students conflate three things when they hear "AI project." Separate them.

| Layer | What it means | Required? |
|---|---|---|
| Built **with** agents | You delegate the coding to an agent under a spec and AGENTS.md, and review what comes back. This is the method Week 2 taught. | Yes. Every capstone is built this way. |
| Has a model **inside** | The product itself calls a model to do a job plain code cannot do. The user gets value from that job. | Yes. This is the AI-embedded element. |
| Is itself **agentic** | The product's model calls tools, takes actions, or runs multi-step plans on the user's behalf, behind gates. | Optional. Rung 4. Week 5 gives you tools (MCP), Week 7 gives you the confirmation gate. Earn it. |

A capstone built with agents but with no model inside is a software engineering project. A capstone with a model inside that you hand-coded is a Week 1 project. You need both of the first two.

### The model-job test

For any seed, write one sentence: **"The model's job in this product is to ______ from ______."**

Then ask: could the blank be done by a SQL query, a regex, or an if/else over structured fields? If yes, there is no AI element yet. You have a CRUD app with a model bolted on. Push until the model is doing work plain code cannot.

Signals that a real model job exists:

- The input is unstructured: free text, a photo, a voice note, a PDF someone formatted by hand.
- The mapping from input to output is fuzzy, needs world knowledge, or must handle phrasings nobody anticipated.
- The right answer depends on reading a context (documents, a calendar, a thread) and reasoning over it.
- Part of the job is knowing when it does not know, and saying so.

**Garnish versus engine.** A to-do app with a "summarize my tasks" button is garnish: remove the model and the product still works. CampusPulse without its model is a JSON file nobody can ask anything. That is an engine. Your capstone must be an engine. Step 5 scores this as *model necessity*.

### The five model jobs

Almost every viable capstone has its model doing one of these as its core job. Naming yours tells you which later weeks you will lean on.

| Model job | What the model does | Course weeks that build it |
|---|---|---|
| **Answer** | Takes a natural-language question and answers it from a context | Week 4 retrieval design and golden set; Week 11 evaluation gates |
| **Extract** | Turns messy input into a structured record | Week 3 multimodal I/O |
| **Classify / route** | Sorts input into categories and says how confident it is | Week 4 golden set; Week 11 audit |
| **Draft** | Produces a first version a human then edits | Week 7 confirmation gate |
| **Act with tools** | Calls tools and takes actions on the user's behalf, behind a gate | Week 5 MCP tools; Week 7 gate; Week 12 red team |

Cross-cutting, and required for all five: **abstain when unsure.** Week 3 introduces it and Week 11 grades it. If your model job has no "I do not know" path, add one.

**Output:** you can state the model-job test from memory, and you can name the five jobs.

> **CampusPulse at this step.** Take the seed from Step 1 and write the sentence: *The model's job is to answer natural-language questions from the events data.* Not a regex: "is the hackathon still on?", "what's happening Thursday?", and "where's the CS club thing?" are all the same query in different words. Model job: **Answer**. Engine, not garnish.

---

## Step 3 · Expand: from seeds to eight idea cards

**Goal:** widen the pool so Step 5 has real alternatives to compare, and force the AI element into every candidate.
**Time:** 17 minutes. Two generators, then the card.

### 3a · The access × model-job grid (12 minutes)

Rows are groups of people you can actually reach before Week 15: your cohort, a student club, a family business, an employer, a community you belong to. Pick three. Columns are the five model jobs from Step 2.

| | Answer | Extract | Classify / route | Draft | Act with tools |
|---|---|---|---|---|---|
| Group 1: ______ | | | | | |
| Group 2: ______ | | | | | |
| Group 3: ______ | | | | | |

Fill at least eight cells, one line each: what would the model do for that group in that job. Use your Step 1 seeds to fill the first cells; the empty columns will pull ideas out of you that the friction log did not. Empty cells are fine. A whole **row** you cannot fill means you do not know that group's information work well enough to build for them; swap the row.

The grid does two things at once. Every cell is a model job, so every idea has the AI element by construction. And every row is a group you can put a product in front of, which is what golden questions and Demo Day both need.

### 3b · Process teardown (5 minutes)

Take the one seed from Step 1 you find most annoying. Write its steps, five to eight. Label each: **code** (deterministic, a script does it), **model** (fuzzy, needs a model), **human** (judgment, stays with a person).

Every *model* step is a candidate. The best first slices are model steps sitting between code steps, because the inputs and outputs are already structured and the acceptance criterion writes itself.

### 3c · Write the idea cards

Every candidate from the grid or the teardown goes into this exact shape. If you cannot fill a slot, the idea is not specific enough yet; that is information, not a formatting problem.

> **[Specific user]** needs to **[outcome]**. Today they **[manual friction]**. The model's job is to **[model job verb]** from **[context or data source]**. A wrong answer costs **[consequence]**. The first slice is **[one endpoint or flow]**.

**Output:** eight or more idea cards. Fewer than eight, run the grid again with a different third row.

> **CampusPulse at this step.** One row of the grid, group: KIU students.
>
> | | Answer | Extract | Classify / route | Draft | Act with tools |
> |---|---|---|---|---|---|
> | KIU students | Answer questions about campus events from the events data | Turn a photo of a poster into an event record | Sort Telegram messages into announcement / cancellation / noise | Write the weekly digest for a club admin to approve | Book a room once the admin confirms |
>
> Five cards from one row. The *Answer* cell became CampusPulse's core. The *Extract* cell is what Week 3 adds. *Act with tools* is rung 4 and stays out of scope until Week 7.
>
> The Answer card, written out: *KIU students need to know what is happening on campus this week. Today they check four Telegram groups and a noticeboard. The model's job is to answer natural-language questions from the events data. A wrong answer costs a missed event or a walk to an empty room. The first slice is `GET /events?week=N` returning confirmed events.*

---

## Step 4 · Gate: six yes/no checks

**Goal:** remove the cards that cannot work, fast, without argument.
**Time:** 5 minutes for the whole sheet.

Every card must pass all six. Any "no" parks the card.

| Gate | Question |
|---|---|
| G1 · Real user | Can you name a specific person or group and put the product in front of three of them before Week 15? |
| G2 · Model job | Does "the model's job is to ___" pass the not-a-regex test from Step 2? |
| G3 · Scriptable check | Can you write one acceptance criterion a script could grade pass or fail with no human in the loop? |
| G4 · Context exists | Does the data the model needs exist today, and can you get it into a repo legally and practically? No personal data you cannot handle. |
| G5 · Lab 2 slice | Can one slice be specified, delegated, reviewed, and merged inside Lab 2 plus studio time? |
| G6 · Recoverable | If the model is wrong, is the cost embarrassment or wasted time, not money, health, legal exposure, or safety? |

Failing **G2** is the most common outcome and the most fixable: the idea is real but the model is garnish. Rewrite the model job before you park it. Failing **G4** is the most dangerous to ignore, because you will not find out until Week 6 that the data does not exist.

**Output:** the survivors, usually three to five cards.

> **CampusPulse at this step.** G1: KIU students, reachable daily. G2: open-ended phrasings, not a regex. G3: `GET /events?week=39` returns only confirmed events for that week. G4: events live in a JSON file in the repo. G5: one endpoint. G6: a wrong answer is a missed event. Six passes. The *Act with tools* card from the same row fails G6 at this stage (booking the wrong room costs someone else their booking), which is exactly why it waits for Week 7's gate.

---

## Step 5 · Score: pick one, and know why

**Goal:** choose between the survivors on evidence, not on which one you thought of first.
**Time:** 8 minutes.

### 5a · Weighted scorecard

Score each surviving card 1 to 5 on every dimension, multiply by the weight. The weights are not arbitrary. Verifiability is heaviest because the course's central claim is that autonomy is earned by verifiability, and a capstone you cannot verify cannot climb the ladder.

| Dimension | What a 5 looks like | Weight |
|---|---|---|
| Verifiability | You could write ten golden questions with known-correct answers today | ×3 |
| Model necessity | Remove the model and the product is worthless | ×2 |
| Context availability | The data is in a file you already have | ×2 |
| User access | You can talk to real users this week | ×2 |
| Scope fit | Ten build weeks, one slice per week, and you can name the first six slices | ×2 |
| Demo-ability | A judge sees it work in 90 seconds on Demo Day | ×1 |
| Learning fit | It exercises at least two of: multimodal (W3), retrieval (W4), tools (W5), gates (W7) | ×1 |
| Motivation | You will still care about this in Week 12 | ×1 |

Maximum 70. **52 to 70:** commit. **38 to 51:** narrow and rescore; the usual fix is a sharper model job or a smaller first slice, rarely a different idea. **Below 38:** park it, but keep the card; it may become a Week 6 feature of the idea you do pick.

### 5b · Compare the top three

Put the three highest side by side and look at where they *differ*, not at the totals. Two ideas at 58 and 55 are a coin flip on the numbers; one has a 5 on verifiability and the other a 3, and that is the decision.

Then place each on the grid from the Week 2 lecture: cost of a wrong answer against ease of verification. A first capstone belongs on the right half, easy to verify. Top-right (expensive if wrong, easy to verify) is fine; that is rung 3 behind gates and it makes a strong Demo Day story. Bottom-left is where capstones go to die.

### 5c · Pre-mortem

For your leading card, write one sentence in the past tense: *"This project failed in Week 14 because ______."* Then act on it now.

- About scope ("we were still building X"): move X to out-of-scope today.
- About data ("the calendar export never worked"): verify the data access this week, before spec v1.
- About the model ("the answers were never reliable"): that is verifiability; write the golden questions before committing.
- About the team ("nobody wanted to work on it by November"): the motivation score is being honest with you. Listen.

### 5d · Decision rule

Highest weighted total that survives its pre-mortem. On a tie, the card with the stronger three golden questions wins, because it will be easier to prove on Demo Day.

**Output:** one leading idea, its scorecard, and the pre-mortem action you already took.

> **CampusPulse at this step.**
>
> | Dimension | Score | Weight | Weighted |
> |---|---|---|---|
> | Verifiability | 5 | ×3 | 15 |
> | Model necessity | 4 | ×2 | 8 |
> | Context availability | 4 | ×2 | 8 |
> | User access | 5 | ×2 | 10 |
> | Scope fit | 5 | ×2 | 10 |
> | Demo-ability | 5 | ×1 | 5 |
> | Learning fit | 5 | ×1 | 5 |
> | Motivation | 4 | ×1 | 4 |
> | **Total** | | | **65 / 70** |
>
> Model necessity is a 4, not a 5, and that is worth noticing: a week filter over structured JSON is nearly a query. What makes it a model job is the open-ended phrasing of questions and the Week 3 extraction from posters. Scoped as "filter events by week," it would have failed G2.
>
> Grid placement: cheap to be wrong, easy to verify. Bottom-right. Climb.
>
> Pre-mortem: *"This project failed in Week 14 because we spent three weeks building RSVPs and payments instead of making the answers correct."* Action taken: RSVPs and payments go to out-of-scope now. That sentence is why the CampusPulse out-of-scope list is longer than its feature list.

---

## Step 6 · Commit: turn the winner into spec v0 material

**Goal:** leave with the seven answers spec v0 needs, three golden questions, and a first slice you can hand to an agent.
**Time:** 7 minutes.

### 6a · The spec bridge

Answer each row in a sentence or two. These become the seven sections of spec v0. Slide 28 of the Week 2 deck shows where each one ends up later.

| Spec v0 section | Answer now | Where it goes later |
|---|---|---|
| Problem and users | The specific user from your card, and the friction | Week 4 Design Review; first 30 seconds of the Demo Day pitch |
| Success criteria | What number or observable fact changes if this works | Design Review; the numbers judges ask about in Week 15 |
| Acceptance criteria | Three checks a script could run, starting with the one from G3 | First golden set in Week 4; the CI gate in Week 11 |
| Context list | The data source from your card, and anything else the model must see | Retrieval design in Week 4 |
| Napkin math | Calls per use, rough tokens per call, rough cost per day at ten users | Token budget in the Design Review; measured in Week 10 |
| Risks and safety | The worst plausible wrong answer, and what the abstain path looks like | Safety and Evaluation Audit in Week 11; red team in Week 12 |
| Out of scope | Everything from the pre-mortem, plus every card you parked | The list that protects your Week 14 |

### 6b · Three golden questions

In the words a real user would use, not a developer's. For each, write what a correct answer contains. If you cannot say what a correct answer contains, it is not a golden question yet.

### 6c · The first slice, for Lab 2

One endpoint, one flow, or one function. Small enough that you can read every line of the diff. It must exercise the model job, not only the plumbing around it, or Lab 2's review loop has nothing interesting to catch. Write it as one sentence you could hand to an agent, the way the Week 2 demo did.

**Output:** spec bridge filled, three golden questions with expected answers, first slice as one sentence. You are ready for the spec v1 pass in Lab 2.

> **CampusPulse at this step.** Spec bridge filled from the card. Golden questions: "What's on this week?" (contains only confirmed events in the current ISO week, with room and time), "Where is the CS club meeting?" (contains the room from the confirmed record, or says it does not know), "Is the hackathon still happening?" (contains the status and, if cancelled, says so plainly). First slice: *"Add `GET /events?week=N` that returns only confirmed events for that week, times in Asia/Tbilisi with offset."*

---

## For facilitators: running this in Lab 2

The six steps fit a 50-minute block at the start of Lab 2, before the spec v1 pass. Students who bring a spec v0 write it as one card in Step 3 and score it honestly in Step 5. Most keep it; some find the better version; a few replace it. All three outcomes beat refining a spec for an idea that fails G2 in Week 4.

If this resource is used with a future cohort, the cleaner sequence is Steps 1 to 5 as pre-work before Lab 1, and Lab 1's spec-writing time for Step 6.

Either way the rule is the same: the idea is chosen before the spec is written, and it is chosen against alternatives, not by default.

---

## Appendix · Blank templates

### Step 1 · Seeds

| # | Who | What they needed | How they did it by hand |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| … | | | |
| 10 | | | |

### Step 3 · Grid

| | Answer | Extract | Classify / route | Draft | Act with tools |
|---|---|---|---|---|---|
| Group 1: | | | | | |
| Group 2: | | | | | |
| Group 3: | | | | | |

### Step 3 · Idea card

> **[Specific user]** needs to **[outcome]**. Today they **[manual friction]**. The model's job is to **[model job verb]** from **[context or data source]**. A wrong answer costs **[consequence]**. The first slice is **[one endpoint or flow]**.

### Step 4 · Gate check

| Card | G1 user | G2 model job | G3 scriptable | G4 context | G5 slice | G6 recoverable | Status |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |

### Step 5 · Scorecard

| Dimension | Weight | Card A | Card B | Card C |
|---|---|---|---|---|
| Verifiability | ×3 | | | |
| Model necessity | ×2 | | | |
| Context availability | ×2 | | | |
| User access | ×2 | | | |
| Scope fit | ×2 | | | |
| Demo-ability | ×1 | | | |
| Learning fit | ×1 | | | |
| Motivation | ×1 | | | |
| **Weighted total / 70** | | | | |

### Step 5 · Pre-mortem

*"This project failed in Week 14 because ________________________________."*
Action taken today: ________________________________

### Step 6 · Golden questions

| # | Question, in the user's words | A correct answer contains |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
