"""Week 1's compact formatter: only the fields a question needs. Context as Budget."""


def format_event_compact(e: dict) -> str:
    price = "free" if e.get("free") else "paid"
    return f'{e["id"]} | {e["title"]} | {e["start"]} | {e["location"]} | {price}'
