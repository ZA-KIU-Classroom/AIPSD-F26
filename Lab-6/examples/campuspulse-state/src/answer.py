"""Grounded generation: answer from retrieved sources, cite them, or refuse.

The contract (docs/retrieval-spec.md in the CampusPulse example):
  1. Nothing relevant retrieved      -> refuse, and never call the model.
  2. The model says "not in sources" -> refuse.
  3. Any citation that does not check out -> refuse. An uncited claim is never shown.
  4. Otherwise answer, with every sentence pointing at a numbered source the user can open.
Every call writes one line to logs/answers.jsonl: the log entry half of the Evidence Rule.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from .index import Index
from .llm import complete_json, embed_model_name
from .retrieve import Hit, hybrid

# Below this cosine score nothing retrieved is about the question. Tune it on your golden set.
DEFAULT_MIN_SCORE = {"openai/text-embedding-3-small": 0.25, "offline/trigram-hash": 0.25}
ANSWER_LOG = Path(os.environ.get("CAMPUSPULSE_ANSWER_LOG", "logs/answers.jsonl"))
REFUSAL = "I can't answer that from CampusPulse's sources."


def min_score() -> float:
    env = os.environ.get("CAMPUSPULSE_MIN_SCORE")
    return float(env) if env else DEFAULT_MIN_SCORE.get(embed_model_name(), 0.25)


class Reply(BaseModel):              # what we ask the model for
    model_config = ConfigDict(extra="forbid")
    answer: str                      # every sentence ends with [n]
    citations: list[int]             # the n's it used
    grounded: bool                   # false: the sources do not answer it


PROMPT = """Answer the QUESTION using only the SOURCES.
End every sentence with the number of the source it came from, like [2].
If the sources do not answer the question, set grounded to false
and say what is missing. Never use outside knowledge.

SOURCES:
{sources}

QUESTION: {question}"""


@dataclass
class Answer:
    status: str                      # "answered" or "refused"
    text: str
    sources: list[dict] = field(default_factory=list)   # {n, chunk_id, doc_id, title, section}
    reason: str = ""                 # why we refused, for logs and the review queue

    def to_dict(self) -> dict:
        return asdict(self)


def format_sources(hits: list[Hit]) -> str:
    return "\n\n".join(f"[{n}] {h.chunk.title} · {h.chunk.section}\n{h.chunk.text}"
                       for n, h in enumerate(hits, start=1))


def check_citations(reply: Reply, n_sources: int) -> str | None:
    """Return a reason the answer cannot be shown, or None if every citation checks out."""
    markers = {int(m) for m in re.findall(r"\[(\d+)\]", reply.answer)}
    if not reply.citations or not markers:
        return "answer has no citations"
    unknown = (markers | set(reply.citations)) - set(range(1, n_sources + 1))
    if unknown:
        return f"cites sources that were never retrieved: {sorted(unknown)}"
    if markers != set(reply.citations):
        return "citation list and [n] markers disagree"
    sentences = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", reply.answer.strip()) if s]
    uncited = [s for s in sentences if not re.search(r"\[\d+\]", s)]
    if uncited:
        return f"uncited sentence: {uncited[0][:60]!r}"
    return None


def refuse(reason: str) -> Answer:
    return Answer("refused", REFUSAL, reason=reason)


def cite(hits: list[Hit], citations: list[int]) -> list[dict]:
    """Turn the model's [n] numbers back into the documents the student can open."""
    return [{"n": n, "chunk_id": hits[n - 1].chunk.id, "doc_id": hits[n - 1].chunk.doc_id,
             "title": hits[n - 1].chunk.title, "section": hits[n - 1].chunk.section}
            for n in sorted(set(citations)) if 1 <= n <= len(hits)]


def answer(index: Index, question: str, k: int = 5, retrieve=hybrid, llm=complete_json,
           check: bool = True) -> Answer:
    hits = retrieve(index, question, k=k)
    def done(result: Answer) -> Answer:
        return _log(question, k, hits, result)
    best = max((h.score for h in hits), default=0.0)
    if best < min_score():                                    # 1 · nothing relevant
        return done(refuse(f"best match {best:.2f} below threshold"))
    raw = llm(PROMPT.format(sources=format_sources(hits), question=question),
              schema=Reply.model_json_schema())
    reply = Reply.model_validate(raw)                          # the shape, checked
    if not reply.grounded:                                     # 2 · the model says no
        return done(refuse("model: sources do not answer it"))
    problem = check_citations(reply, n_sources=len(hits)) if check else None
    if problem:                                                # 3 · a citation fails
        return done(refuse(problem))
    return done(Answer("answered", reply.answer, cite(hits, reply.citations)))   # 4


def _log(question: str, k: int, hits: list[Hit], result: Answer) -> Answer:
    line = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "question": question,
            "status": result.status, "reason": result.reason, "k": k,
            "best_score": round(max((h.score for h in hits), default=0.0), 3),
            "retrieved": [h.chunk.id for h in hits], "cited": [s["chunk_id"] for s in result.sources]}
    ANSWER_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ANSWER_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")
    return result
