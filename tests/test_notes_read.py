import pytest

from engram_mcp import notes
from engram_mcp.vault import NotFoundError


def _seed(vault, rel, text):
    p = vault.resolve(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return rel


def test_read_note_returns_parsed_fields(vault):
    rel = _seed(vault, "a/n.md", "---\ntitle: N\ntags:\n- x\n---\n\n# H\n[[Other]]\n")
    out = notes.read_note(vault, rel)
    assert out["path"] == "a/n.md"
    assert out["frontmatter"]["title"] == "N"
    assert out["headings"] == [{"level": 1, "text": "H"}]
    assert out["links"] == ["Other"]
    assert out["frontmatter_error"] is None


def test_read_note_missing_raises(vault):
    with pytest.raises(NotFoundError):
        notes.read_note(vault, "nope.md")


def test_list_headings(vault):
    rel = _seed(vault, "h.md", "# One\n## Two\n")
    assert notes.list_headings(vault, rel)["headings"] == [
        {"level": 1, "text": "One"},
        {"level": 2, "text": "Two"},
    ]


def test_get_metadata_reports_error_on_bad_yaml(vault):
    rel = _seed(vault, "bad.md", "---\nfoo: [unclosed\n---\n\nbody")
    out = notes.get_metadata(vault, rel)
    assert out["frontmatter"] == {}
    assert out["frontmatter_error"] is not None
