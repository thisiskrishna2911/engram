import pytest

from engram_mcp import notes
from engram_mcp.vault import NoteExistsError, NotFoundError, TRASH_DIRNAME


def test_write_then_read_roundtrip(vault):
    res = notes.write_note(vault, "a/n.md", "hello")
    assert res["created"] is True
    assert notes.read_note(vault, "a/n.md")["content"] == "hello"


def test_write_refuses_clobber_by_default(vault):
    notes.write_note(vault, "n.md", "one")
    with pytest.raises(NoteExistsError):
        notes.write_note(vault, "n.md", "two")
    assert notes.read_note(vault, "n.md")["content"] == "one"


def test_write_overwrite_true_replaces(vault):
    notes.write_note(vault, "n.md", "one")
    res = notes.write_note(vault, "n.md", "two", overwrite=True)
    assert res["created"] is False
    assert notes.read_note(vault, "n.md")["content"] == "two"


def test_append_requires_existing(vault):
    with pytest.raises(NotFoundError):
        notes.append_note(vault, "missing.md", "x")


def test_append_adds_content(vault):
    notes.write_note(vault, "n.md", "one")
    notes.append_note(vault, "n.md", "\ntwo")
    assert notes.read_note(vault, "n.md")["content"] == "one\ntwo"


def test_rename_note(vault):
    notes.write_note(vault, "a/old.md", "x")
    res = notes.rename_note(vault, "a/old.md", "New Title")
    assert res["new_path"] == "a/New Title.md"
    assert notes.read_note(vault, "a/New Title.md")["content"] == "x"


def test_delete_note_moves_to_trash(vault):
    notes.write_note(vault, "n.md", "x")
    res = notes.delete_note(vault, "n.md")
    assert res["trashed_to"].startswith(TRASH_DIRNAME + "/")
    assert not vault.resolve("n.md").exists()
    assert vault.resolve(res["trashed_to"]).exists()
