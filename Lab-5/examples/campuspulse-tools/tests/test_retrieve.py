import json

import numpy as np
import pytest

from src.bm25 import BM25
from src.index import IndexMismatch, load, save
from src.retrieve import hybrid, rrf, search


def test_vectors_are_unit_length(index):
    norms = np.linalg.norm(index.vectors, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5)


def test_search_returns_k_hits_best_first(index):
    hits = search(index, "When does the chess club meet?", k=4)
    assert len(hits) == 4
    assert [h.score for h in hits] == sorted([h.score for h in hits], reverse=True)
    assert hits[0].chunk.doc_id == "clubs/chess"


def test_bm25_finds_exact_room_codes():
    docs = ["Room A112 seats 40 people.", "Lab B204 seats 30 people.", "The Auditorium seats 220."]
    s = BM25(docs).scores("capacity of B204")
    assert int(np.argmax(s)) == 1


def test_rrf_rewards_agreement_and_keeps_singletons():
    fused = rrf([[3, 1, 2], [1, 4]])
    assert fused[0] == 1            # high in both lists beats first in one
    assert set(fused) == {1, 2, 3, 4}


def test_hybrid_survives_a_typo(index):
    hits = hybrid(index, "when does the robtics club meet", k=5)
    assert "clubs/robotics" in {h.chunk.doc_id for h in hits}


def test_index_round_trip(index, tmp_path):
    save(index, tmp_path)
    again = load(tmp_path)
    assert len(again.chunks) == len(index.chunks)
    assert np.allclose(again.vectors, index.vectors)


def test_index_built_with_another_model_is_refused(index, tmp_path):
    save(index, tmp_path)
    meta = json.loads((tmp_path / "meta.json").read_text())
    meta["embed_model"] = "openai/text-embedding-3-small"
    (tmp_path / "meta.json").write_text(json.dumps(meta))
    with pytest.raises(IndexMismatch):
        load(tmp_path)
