# 0001 · Hybrid retrieval (vectors + BM25) as the default

**Context.** Students ask about rooms and clubs by exact names: "B204", "A112", "Debate Society". Embeddings blur rare strings like room codes into their neighbours, and pure vector search ranked an event page in B204 above the rule about food in labs.

**Decision.** Retrieve with `hybrid()` in `src/retrieve.py`: the top 20 by cosine and the top 20 by BM25, merged with Reciprocal Rank Fusion (constant 60), then the top k. The refusal threshold still uses the cosine score of the retrieved chunks.

**Alternatives.** Vector only (simpler, misses exact codes). BM25 only (no model, but "cost" never finds "fee"). A reranking model (better ordering, one more model call per question; revisit in Week 10).

**Consequences.** One extra pure-Python scoring pass per question, about a millisecond for 52 chunks. No extra model cost. Thirty lines of code to own (`src/bm25.py`).
