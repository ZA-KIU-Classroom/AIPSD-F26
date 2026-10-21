"""The vector index: chunks, their vectors, and which model made the vectors.

For a few thousand chunks a NumPy array is the right database: it loads in milliseconds and
there is nothing to run. When you outgrow it (tens of thousands of chunks, many writers,
filtering by metadata), move to pgvector or a vector store. The interface stays the same.

Build it:   python -m src.index            (reads data/corpus/, writes data/index/)
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .bm25 import BM25
from .chunk import Chunk, load_corpus
from .llm import embed, embed_model_name

CORPUS = Path("data/corpus")
INDEX_DIR = Path("data/index")
BATCH = 64


class IndexMismatch(RuntimeError):
    """The index was built with a different embedding model than the one queries use."""


@dataclass
class Index:
    chunks: list[Chunk]
    vectors: np.ndarray          # shape (n_chunks, dims), every row unit length
    model: str
    bm25: BM25 | None = None

    def __post_init__(self):
        if self.bm25 is None:
            self.bm25 = BM25([c.embed_text() for c in self.chunks])


def build(chunks: list[Chunk]) -> Index:
    texts = [c.embed_text() for c in chunks]
    parts = [embed(texts[i:i + BATCH]) for i in range(0, len(texts), BATCH)]
    return Index(chunks, np.vstack(parts).astype(np.float32), embed_model_name())


def save(index: Index, out: Path = INDEX_DIR) -> None:
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "vectors.npy", index.vectors)
    (out / "chunks.json").write_text(json.dumps([c.to_dict() for c in index.chunks], indent=1), encoding="utf-8")
    meta = {"embed_model": index.model, "dims": int(index.vectors.shape[1]), "chunks": len(index.chunks),
            "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (out / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")


def load(src: Path = INDEX_DIR) -> Index:
    meta = json.loads((src / "meta.json").read_text(encoding="utf-8"))
    if meta["embed_model"] != embed_model_name():
        raise IndexMismatch(f"index built with {meta['embed_model']}, queries use {embed_model_name()}. "
                            "Vectors from different models are not comparable: rebuild with python -m src.index")
    chunks = [Chunk(**d) for d in json.loads((src / "chunks.json").read_text(encoding="utf-8"))]
    return Index(chunks, np.load(src / "vectors.npy"), meta["embed_model"])


if __name__ == "__main__":
    chunks = load_corpus(CORPUS)
    index = build(chunks)
    save(index)
    print(f"indexed {len(chunks)} chunks from {CORPUS} with {index.model} -> {INDEX_DIR}", file=sys.stderr)
