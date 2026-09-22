# Building AI-Powered Applications

**CS6920 · Fall 2026 · Kutaisi International University**
**Instructor: Zeshan Ahmad · zeshan.ahmad@kiu.edu.ge · announcements on Teams · office hours over Google Meet, booked by email**

You are training to be an operator: an engineer who directs AI with specifications, delegates real work to models and agents, verifies everything with tests and measurements, and owns the outcome. Two questions run through all fifteen weeks: **what did I delegate, and how do I verify it?**

---

## How this course runs

- **Lectures are recorded** and released at least 48 hours before your lab. Weeks 1 and 2 were delivered in person (recordings posted).
- **Labs are live online**, weekly from Week 2, in two groups. We code live, break things live, and build your capstone. Links and times are posted on Teams.
- **Before each lab** (from Week 3): a 3-question watch-check on the recording. Two minutes, auto-graded, best 8 of 10 count.
- **Weeks 8 and 9**: on-campus midterm period, no classes. One exam, and protected capstone build time.
- **One rule from Lab 3 onward, the Evidence Rule**: every feature ships with a test and a log entry. "It works" is a measurement.

## Finding your way

Every lab folder has the same skeleton. Learn it once, use it all semester:

```
Lab-N/
  README.md       ← the lab itself, two pages
  HOMEWORK.md     ← always here, always this name, deadline in the first lines
  templates/      ← copy these into your repo
  examples/       ← the same documents, filled in for CampusPulse
  resources/      ← optional, never required
```

CampusPulse is the running example we build forward in every lecture; the reference repo tags a release per week. Your capstone is your own product, built to the same standard.

## The semester

| Wk | Lecture | Pattern | In the lab |
|---|---|---|---|
| 1 | The operator's landscape, tokens, cost | Context as Budget | no lab |
| 2 | Agentic engineering, specs, AGENTS.md | Spec Before Code | Lab 1 · teams, repo, spec v0 |
| 3 | Vision, documents, image generation | Uncertainty-Aware UX | Lab 2 · multimodal · **teams lock** |
| 4 | Embeddings and RAG | Grounded Generation | Lab 3 · RAG + golden set · **Design Review · HW1 due** |
| 5 | Function calling, structured outputs, MCP | Tool Contract | Lab 4 · tools + MCP · **Quiz 1** |
| 6 | Streaming, voice, state, governance | Session State | Lab 5 · streaming + memory |
| 7 | Agents and orchestration | Supervised Autonomy Loop | Lab 6 · agent loop · **HW2 due** |
| 8-9 | **Midterm period · no classes** |  | on-campus exam, weeks 1-7 |
| 10 | Model routing, caching, optimization | Fallback Chain | Lab 7 · optimization |
| 11 | Evaluation and observability | Golden Set Gate | Lab 8 · evals in CI · **Safety & Eval Audit** |
| 12 | Production, security, red teaming | Least-Privilege Deployment | Lab 9 · deploy + harden · **Quiz 2** |
| 13 | Portability, OSS models, fine-tuning survey | Portable Core | Lab 10 · three-path benchmark |
| 14 | Consolidation, case study, pitch craft | pattern review | Lab 11 · Demo Day rehearsal |
| 15 | Demo Day |  | Lab 12 · **Demo Day + Repository Review** |

## Grading · 100 points

| Interim · 70 · minimum 25 | pts | Final · 30 · minimum 16 | pts |
|---|---|---|---|
| Midterm exam (on campus) | 25 | Demo Day · investor pitch, industry judges | 20 |
| Design Review · W4 | 10 | Repository Review | 10 |
| Safety & Evaluation Audit · W11 | 10 |  |  |
| Participation: HW1 5 + HW2 5 + watch-checks 3 + peer form 2 | 15 |  |  |
| Quiz 1 · W5 + Quiz 2 · W12, in lab | 5 + 5 |  |  |

Your capstone is 50 of the 100, across four milestones. Capstone tags, in order: `lab1-spec → lab2-multimodal → lab3-rag-goldenset → lab4-tools-mcp → lab5-streaming-state → lab6-agent-loop → lab7-optimization → lab8-eval-ci → lab9-production → lab10-portability → lab11-rehearsal → lab12-demo-day`.

## AI use, in one paragraph

Using AI tools on labs, homework, and the capstone is encouraged; it is the subject of the course. Every submission logs what was delegated and how it was verified (your Pattern Journal covers weekly work). Submitting output you cannot explain is misconduct, and oral defense of any work can be required. Quizzes and the midterm are AI-free.

## Getting help

Ask in your lab first, on Teams second, by email third. Post exact errors, not "it doesn't work." Full policies, rubrics, and the reading list live in the syllabus on Teams.
