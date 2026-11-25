"""Runs every tool golden file in evals/tools/*.yaml through the real gates. No model, no key.

One file per student for HW2 (evals/tools/<github-username>.yaml), plus any the team adds.
Each case calls call_tool() exactly as the model's request would: the tool must be offered to the
caller, the arguments must pass the contract, and identity comes from `caller`, never the arguments.
Because this file lives in tests/, the CI job that already runs tests/ runs it, and a failing case
blocks the merge. If your functions have different names, change the two imports below.
"""
import json
from pathlib import Path

import pytest
import yaml

from src.act import call_tool
from src.tools import tools_for

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "evals" / "tools").glob("*.yaml"))
CASES = [(f.stem, case) for f in FILES for case in yaml.safe_load(f.read_text(encoding="utf-8"))["cases"]]


def subset(expected: dict, actual) -> bool:
    """Every key in `expected` is in `actual` with the same value. Lists and nested dicts compare whole."""
    return isinstance(actual, dict) and all(k in actual and actual[k] == v for k, v in expected.items())


@pytest.mark.parametrize("owner, case", CASES, ids=[f"{o}:{c['id']}" for o, c in CASES])
def test_tool_golden_case(owner, case):
    call = {"id": case["id"], "name": case["tool"], "arguments": json.dumps(case["arguments"])}
    out = call_tool(call, tools_for(case.get("caller")), case.get("caller"))
    if case["expect"] == "ok":
        assert out["ok"], f"{owner}:{case['id']} should succeed but was refused: {out['error']}"
        assert subset(case.get("result_has", {}), out["result"]), f"result was {out['result']}"
    else:
        assert not out["ok"], f"{owner}:{case['id']} should be refused but ran: {out['result']}"
        for phrase in case.get("error_has", []):
            assert phrase.lower() in out["error"].lower(), f"error was: {out['error']}"


def test_every_file_has_five_cases_including_one_adversarial():
    for f in FILES:
        cases = yaml.safe_load(f.read_text(encoding="utf-8"))["cases"]
        types = [c["type"] for c in cases]
        assert len(cases) >= 5, f"{f.name}: {len(cases)} cases, HW2 needs 5"
        assert "adversarial" in types and "bad-input" in types, f"{f.name}: needs a bad-input and an adversarial case"
