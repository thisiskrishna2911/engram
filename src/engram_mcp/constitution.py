import os
from pathlib import Path

DEFAULT_CONSTITUTION = "docs/CONSTITUTION.md"
CONSTITUTION_URI = "engram://constitution"


def constitution_path() -> Path:
    """Path to the governing Constitution, configurable via ENGRAM_CONSTITUTION
    (default: docs/CONSTITUTION.md, relative to the server's working directory)."""
    return Path(os.environ.get("ENGRAM_CONSTITUTION", DEFAULT_CONSTITUTION))


def read_constitution() -> str:
    """Return the full text of the Engram Constitution.
    Raises FileNotFoundError if the configured path does not exist."""
    path = constitution_path()
    if not path.is_file():
        raise FileNotFoundError(f"constitution not found at {path}")
    return path.read_text(encoding="utf-8")
