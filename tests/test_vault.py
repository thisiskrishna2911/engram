import os
from pathlib import Path

import pytest

from engram_mcp.vault import Vault, PathEscapeError, DEFAULT_VAULT


def test_resolve_within_root(tmp_path):
    v = Vault(tmp_path)
    assert v.resolve("Engineering/Rust/note.md") == (tmp_path / "Engineering/Rust/note.md").resolve()


def test_resolve_root_itself(tmp_path):
    v = Vault(tmp_path)
    assert v.resolve("") == tmp_path.resolve()


def test_resolve_rejects_parent_escape(tmp_path):
    v = Vault(tmp_path)
    with pytest.raises(PathEscapeError):
        v.resolve("../outside.md")


def test_resolve_rejects_absolute(tmp_path):
    v = Vault(tmp_path)
    with pytest.raises(PathEscapeError):
        v.resolve("/etc/passwd")


def test_relpath_roundtrip(tmp_path):
    v = Vault(tmp_path)
    p = v.resolve("a/b.md")
    assert v.relpath(p) == "a/b.md"


def test_from_env_default(monkeypatch):
    monkeypatch.delenv("ENGRAM_VAULT", raising=False)
    assert Vault.from_env().root == Path(DEFAULT_VAULT).resolve()


def test_errors_carry_code_token(vault):
    from engram_mcp import notes
    from engram_mcp.vault import NoteExistsError, NotFoundError

    notes.write_note(vault, "n.md", "x")
    with pytest.raises(NoteExistsError) as ei:
        notes.write_note(vault, "n.md", "y")
    assert "note_exists" in str(ei.value)

    with pytest.raises(NotFoundError) as ei2:
        notes.read_note(vault, "missing.md")
    assert "not_found" in str(ei2.value)

    with pytest.raises(PathEscapeError) as ei3:
        vault.resolve("../escape")
    assert "path_escape" in str(ei3.value)
