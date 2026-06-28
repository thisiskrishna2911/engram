import os
from pathlib import Path

DEFAULT_VAULT = "engram-data"
TRASH_DIRNAME = ".trash"


class VaultError(Exception):
    """Base class for vault operation errors. The message is prefixed with a
    stable `code` token so callers (and Claude, after the MCP framework
    flattens the exception to its string form) can branch on the failure
    mode."""

    code = "vault_error"

    def __init__(self, detail: str = "") -> None:
        self.detail = str(detail)
        super().__init__(f"{self.code}: {self.detail}" if self.detail else self.code)


class PathEscapeError(VaultError):
    """A path resolved outside the vault root."""

    code = "path_escape"


class NotFoundError(VaultError):
    """A target note or folder does not exist."""

    code = "not_found"


class NoteExistsError(VaultError):
    """Writing, renaming, or moving would clobber an existing path without overwrite."""

    code = "note_exists"


class Vault:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    @classmethod
    def from_env(cls) -> "Vault":
        return cls(os.environ.get("ENGRAM_VAULT", DEFAULT_VAULT))

    def resolve(self, rel: str) -> Path:
        candidate = (self.root / (rel or "")).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise PathEscapeError(rel)
        return candidate

    def relpath(self, p: Path) -> str:
        try:
            return Path(p).resolve().relative_to(self.root).as_posix()
        except ValueError:
            raise PathEscapeError(str(p)) from None
