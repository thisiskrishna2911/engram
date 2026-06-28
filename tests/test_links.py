# tests/test_links.py
from engram_mcp import links


def test_backlinks_resolves_by_title(golden):
    out = links.get_backlinks(golden, "Engineering/Languages/Rust/work-stealing.md")
    paths = [b["path"] for b in out["backlinks"]]
    assert "Engineering/Languages/Rust/tokio.md" in paths


def test_backlinks_empty_when_unreferenced(golden):
    out = links.get_backlinks(golden, "Engineering/Languages/Rust/tokio.md")
    assert out["backlinks"] == []


def test_iter_notes_skips_trash(vault):
    from engram_mcp import notes
    notes.write_note(vault, "real.md", "x")
    notes.write_note(vault, "gone.md", "x")
    notes.delete_note(vault, "gone.md")
    found = [vault.relpath(p) for p in links._iter_notes(vault)]
    assert found == ["real.md"]
