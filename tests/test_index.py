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


def test_recently_added_falls_back_to_mtime(vault):
    import os

    from engram_mcp import index, notes

    notes.write_note(vault, "Folder/old.md", "---\ntitle: Old\n---\n\nx")
    notes.write_note(vault, "Folder/new.md", "---\ntitle: New\n---\n\ny")
    # No 'created' frontmatter -> mtime fallback. Set explicit, far-apart mtimes.
    os.utime(vault.resolve("Folder/old.md"), (1_000_000_000, 1_000_000_000))
    os.utime(vault.resolve("Folder/new.md"), (2_000_000_000, 2_000_000_000))
    res = index.rebuild_index(vault, "Folder")
    body = vault.resolve(res["path"]).read_text(encoding="utf-8")
    recent = body.split("## Recently Added", 1)[1]
    assert recent.index("New") < recent.index("Old")
