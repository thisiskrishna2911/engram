# tests/test_index.py
from engram_mcp import index


def test_rebuild_index_lists_notes_and_is_idempotent(golden):
    res = index.rebuild_index(golden, "Engineering/Languages/Rust")
    assert res["path"] == "Engineering/Languages/Rust/index.md"
    body = golden.resolve(res["path"]).read_text(encoding="utf-8")
    assert "## Notes" in body
    assert "[[Tokio]]" in body
    assert "[[Work Stealing]]" in body
    # idempotent: a second rebuild produces identical bytes
    first = body
    index.rebuild_index(golden, "Engineering/Languages/Rust")
    assert golden.resolve(res["path"]).read_text(encoding="utf-8") == first


def test_rebuild_index_lists_subfolders(golden):
    res = index.rebuild_index(golden, "Engineering/Languages")
    body = golden.resolve(res["path"]).read_text(encoding="utf-8")
    assert "## Folders" in body
    assert "[Rust](Rust/index.md)" in body


def test_recently_added_orders_by_created_desc(golden):
    res = index.rebuild_index(golden, "Engineering/Languages/Rust")
    body = golden.resolve(res["path"]).read_text(encoding="utf-8")
    recent = body.split("## Recently Added", 1)[1]
    # work-stealing (created 2026-01-03) is newer than tokio (2026-01-02)
    assert recent.index("Work Stealing") < recent.index("Tokio")
