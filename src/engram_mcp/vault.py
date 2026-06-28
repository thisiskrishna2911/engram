import os
from pathlib import Path

DEFAULT_VAULT = "engram-data"
TRASH_DIRNAME = ".trash"


class VaultError(Exception):
    """Base class for vault operation errors."""


class PathEscapeError(VaultError):
    """A path resolved outside the vault root."""


class NotFoundError(VaultError):
    """A target note or folder does not exist."""


class NoteExistsError(VaultError):
    """Writing would clobber an existing note without overwrite=True."""


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
        return Path(p).resolve().relative_to(self.root).as_posix()
