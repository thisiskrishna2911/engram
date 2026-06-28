# tests/test_search.py
from engram_mcp import search


def test_search_ranks_title_above_tag(golden):
    # "tokio" appears in tokio.md's title (tier 6); no other note's title matches.
    hits = search.search(golden, "tokio")["hits"]
    assert hits[0]["path"] == "Engineering/Languages/Rust/tokio.md"
    assert hits[0]["field"] == "title"


def test_search_tag_match(golden):
    hits = search.search(golden, "concurrency")["hits"]
    assert hits[0]["path"] == "Engineering/Languages/Rust/work-stealing.md"
    assert hits[0]["field"] == "tag"


def test_search_alias_match(golden):
    hits = search.search(golden, "tokio-rs")["hits"]
    assert hits[0]["field"] == "alias"


def test_search_orders_title_before_content(vault):
    from engram_mcp import notes
    notes.write_note(vault, "match-title.md", "---\ntitle: Backpressure\n---\n\nunrelated body")
    notes.write_note(vault, "match-body.md", "---\ntitle: Other\n---\n\nthis mentions backpressure")
    hits = search.search(vault, "backpressure")["hits"]
    assert [h["field"] for h in hits[:2]] == ["title", "content"]
    assert hits[0]["path"] == "match-title.md"


def test_find_by_metadata_matches_list_member(golden):
    out = search.find_by_metadata(golden, "tags", "rust")
    assert [n["path"] for n in out["notes"]] == ["Engineering/Languages/Rust/tokio.md"]


def test_search_excludes_index_md(vault):
    from engram_mcp import index, notes, search

    notes.write_note(vault, "Folder/a.md", "---\ntitle: Apple\n---\n\nx")
    index.rebuild_index(vault, "Folder")  # index.md contains [[Apple]]
    paths = [h["path"] for h in search.search(vault, "Apple")["hits"]]
    assert "Folder/a.md" in paths
    assert "Folder/index.md" not in paths
