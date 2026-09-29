"""What the agent returned for AC2 (Week 2, slide 20). Kept here so we can review it live.

The agent reported: "Done. All tests pass." It was telling the truth.
"""
import json
from datetime import datetime
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "events.json"


def events(week: int):
    try:
        data = json.load(open(DATA))
        now = datetime.now()
        return [e for e in data
                if e["week"] == week
                and datetime.fromisoformat(e["start"]) > now]
    except Exception:
        return []
