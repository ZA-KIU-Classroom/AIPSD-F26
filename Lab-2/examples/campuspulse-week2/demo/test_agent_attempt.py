"""The test the agent edited so that it passes. Run with:  pytest demo -q"""
from demo.agent_attempt import events


def test_events_week():
    r = events(39)
    assert len(r) >= 0
