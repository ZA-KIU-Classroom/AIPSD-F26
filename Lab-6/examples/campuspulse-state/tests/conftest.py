"""Every test runs offline: no key, no network, no cost. Logs and state go to a temp folder.
Today is pinned to Wednesday 21 October 2026, the day of the Week 5 lecture."""
import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="campuspulse-tests-")
os.environ["CAMPUSPULSE_OFFLINE"] = "1"
os.environ["CAMPUSPULSE_USAGE_LOG"] = os.path.join(_tmp, "usage.jsonl")
os.environ["CAMPUSPULSE_ANSWER_LOG"] = os.path.join(_tmp, "answers.jsonl")
os.environ["CAMPUSPULSE_TOOL_LOG"] = os.path.join(_tmp, "tools.jsonl")
os.environ["CAMPUSPULSE_TODAY"] = "2026-10-21"
os.environ.pop("CAMPUSPULSE_MIN_SCORE", None)
os.environ.pop("CAMPUSPULSE_STUDENT", None)

from pathlib import Path  # noqa: E402

import pytest  # noqa: E402

from src.chunk import load_corpus  # noqa: E402
from src.index import build  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def index():
    return build(load_corpus(ROOT / "data" / "corpus"))


@pytest.fixture(scope="session")
def tmpdir_session():
    return Path(_tmp)


@pytest.fixture(autouse=True)
def fresh_state(tmp_path, monkeypatch):
    """Every test starts with an empty RSVP list."""
    monkeypatch.setenv("CAMPUSPULSE_STATE_DIR", str(tmp_path / "state"))
