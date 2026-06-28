import pytest

from engram_mcp import folders, notes
from engram_mcp.vault import NotFoundError


def test_create_folder_is_lazy_and_nested(vault):
    res = folders.create_folder(vault, "Engineering/Languages/Rust")
    assert res["created"] is True
    assert vault.resolve("Engineering/Languages/Rust").is_dir()
    again = folders.create_folder(vault, "Engineering/Languages/Rust")
    assert again["created"] is False


def test_list_dir_separates_folders_and_notes(vault):
    folders.create_folder(vault, "Sub")
    notes.write_note(vault, "a.md", "---\ntitle: Alpha\n---\n\nx")
    out = folders.list_dir(vault, "")
    assert [f["name"] for f in out["folders"]] == ["Sub"]
    assert out["notes"][0]["title"] == "Alpha"


def test_list_dir_skips_hidden(vault):
    (vault.resolve(".trash")).mkdir()
    out = folders.list_dir(vault, "")
    assert out["folders"] == []


def test_list_dir_missing_raises(vault):
    with pytest.raises(NotFoundError):
        folders.list_dir(vault, "nope")


def test_move_note(vault):
    notes.write_note(vault, "a.md", "x")
    folders.create_folder(vault, "dest")
    res = folders.move(vault, "a.md", "dest/a.md")
    assert res["dest"] == "dest/a.md"
    assert vault.resolve("dest/a.md").exists()
    assert not vault.resolve("a.md").exists()


def test_rename_folder(vault):
    folders.create_folder(vault, "old")
    res = folders.rename_folder(vault, "old", "new")
    assert res["new_path"] == "new"
    assert vault.resolve("new").is_dir()
