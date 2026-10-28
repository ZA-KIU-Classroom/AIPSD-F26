"""Find the k chunks most likely to answer a question.

search()  vector only: meaning. Shown on screen in Week 4, Chapter 2.
hybrid()  vectors and BM25 together, merged with Reciprocal Rank Fusion. The default.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .chunk import Chunk
from .index import Index
from .llm import embed

RRF_K = 60   # the constant from Cormack et al. (2009); it dampens the top ranks


@dataclass
class Hit:
    chunk: Chunk
    score: float       # cosine similarity between the question and this chunk


def search(index: Index, query: str, k: int = 5) -> list[Hit]:
    q = embed([query])[0]
    scores = index.vectors @ q            # cosine, because every row is unit length
    top = np.argsort(-scores)[:k]
    return [Hit(index.chunks[i], float(scores[i])) for i in top]


def rrf(rankings: list[list[int]], k: int = RRF_K) -> list[int]:
    """Merge several rankings of chunk positions. Rank 1 in any list counts most."""
    fused: dict[int, float] = {}
    for ranking in rankings:
        for rank, i in enumerate(ranking, start=1):
            fused[i] = fused.get(i, 0.0) + 1.0 / (k + rank)
    return sorted(fused, key=lambda i: -fused[i])


def hybrid(index: Index, query: str, k: int = 5, pool: int = 20) -> list[Hit]:
    q = embed([query])[0]
    cos = index.vectors @ q
    by_vector = list(np.argsort(-cos)[:pool])
    kw = np.array(index.bm25.scores(query))
    by_keyword = [i for i in np.argsort(-kw)[:pool] if kw[i] > 0]
    return [Hit(index.chunks[i], float(cos[i])) for i in rrf([by_vector, by_keyword])[:k]]
