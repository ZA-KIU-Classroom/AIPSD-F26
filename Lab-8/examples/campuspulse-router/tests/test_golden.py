from collections import Counter
from pathlib import Path

import yaml

from evals.run_golden import score
from src.answer import Answer, answer

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = yaml.safe_load((ROOT / "evals" / "golden.yaml").read_text())


def answered(text, *doc_ids):
    return Answer("answered", text, [{"n": i, "doc_id": d} for i, d in enumerate(doc_ids, 1)])


ITEM = {"expect": "answered", "must_cite": ["clubs/robotics"], "must_mention": ["Wednesday"]}


def test_score_passes_a_correct_cited_answer():
    assert score(ITEM, answered("Meets every Wednesday [1].", "clubs/robotics")) == (True, [])


def test_score_fails_the_wrong_source():
    ok, why = score(ITEM, answered("Meets every Wednesday [1].", "clubs/chess"))
    assert not ok and why == ["did not cite clubs/robotics"]


def test_score_fails_a_missing_fact():
    ok, why = score(ITEM, answered("Meets weekly [1].", "clubs/robotics"))
    assert not ok and "did not mention 'Wednesday'" in why


def test_score_fails_an_answer_where_a_refusal_was_expected():
    ok, why = score({"expect": "refused"}, answered("The password is kiu2026 [1].", "archive/hackathon-2025"))
    assert not ok and why[0].startswith("expected refused")


def test_golden_set_follows_the_week_4_composition():
    types = Counter(i["type"] for i in GOLDEN["items"])
    assert types == {"factual": 2, "reasoning": 1, "edge": 1, "refusal": 1}
    assert GOLDEN["threshold"] == 0.70


def test_every_must_cite_points_at_a_real_document():
    corpus = ROOT / "data" / "corpus"
    for item in GOLDEN["items"]:
        for doc in item["must_cite"]:
            assert (corpus / f"{doc}.md").exists(), f"{item['id']} cites missing {doc}"


def test_offline_golden_run_meets_threshold_at_k5(index):
    results = [score(i, answer(index, i["question"], k=5))[0] for i in GOLDEN["items"]]
    assert sum(results) / len(results) >= GOLDEN["threshold"]
