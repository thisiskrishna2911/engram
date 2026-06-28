import pytest

from engram_mcp import constitution


def test_read_constitution_reads_configured_path(tmp_path, monkeypatch):
    f = tmp_path / "C.md"
    f.write_text("# Engram Constitution\nbe a scribe", encoding="utf-8")
    monkeypatch.setenv("ENGRAM_CONSTITUTION", str(f))
    assert "be a scribe" in constitution.read_constitution()


def test_constitution_path_defaults(monkeypatch):
    monkeypatch.delenv("ENGRAM_CONSTITUTION", raising=False)
    assert str(constitution.constitution_path()) == "docs/CONSTITUTION.md"


def test_read_constitution_missing_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("ENGRAM_CONSTITUTION", str(tmp_path / "nope.md"))
    with pytest.raises(FileNotFoundError):
        constitution.read_constitution()
