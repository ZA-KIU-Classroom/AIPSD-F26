from src.chunk import MAX_CHARS, chunk_markdown

DOC = """# KIU Chess Club

## About
Players of every level.

## Meetings
Mondays and Thursdays, 17:00 to 20:00.
"""


def test_one_chunk_per_section_with_title_and_section():
    chunks = chunk_markdown("clubs/chess", DOC)
    assert [c.section for c in chunks] == ["About", "Meetings"]
    assert all(c.title == "KIU Chess Club" for c in chunks)
    assert [c.id for c in chunks] == ["clubs/chess#1", "clubs/chess#2"]


def test_embed_text_carries_title_and_section():
    c = chunk_markdown("clubs/chess", DOC)[1]
    assert c.embed_text().startswith("KIU Chess Club · Meetings\n")


def test_long_section_splits_with_one_paragraph_overlap():
    paras = [f"Paragraph {i}. " + "word " * 60 for i in range(8)]
    doc = "# Long\n\n## Rules\n" + "\n\n".join(paras)
    chunks = chunk_markdown("regs/long", doc)
    assert len(chunks) > 1
    assert all(len(c.text) <= MAX_CHARS + 400 for c in chunks)
    last_para_of_first = chunks[0].text.split("\n\n")[-1]
    assert chunks[1].text.startswith(last_para_of_first)    # the overlap


def test_text_before_first_heading_is_kept():
    chunks = chunk_markdown("misc/note", "# Note\nJust one line, no headings.")
    assert chunks[0].section == "Overview"
    assert "one line" in chunks[0].text


def test_empty_sections_are_dropped():
    chunks = chunk_markdown("x/y", "# T\n\n## Empty\n\n## Full\nSomething.")
    assert [c.section for c in chunks] == ["Full"]


def test_real_corpus_loads(index):
    doc_ids = {c.doc_id for c in index.chunks}
    assert {"clubs/robotics", "regulations/room-booking", "archive/hackathon-2025"} <= doc_ids
