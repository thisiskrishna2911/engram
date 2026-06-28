import pytest


@pytest.fixture
def vault(tmp_path):
    """An empty vault rooted at a fresh temp dir."""
    from engram_mcp.vault import Vault  # imported lazily; vault.py lands in Task 2
    return Vault(tmp_path)


@pytest.fixture
def golden(tmp_path):
    """A tiny known vault for search / backlink / index assertions."""
    from engram_mcp.vault import Vault
    root = tmp_path
    rust = root / "Engineering" / "Languages" / "Rust"
    rust.mkdir(parents=True)
    (rust / "tokio.md").write_text(
        "---\ntitle: Tokio\naliases:\n- tokio-rs\ntags:\n- rust\n- async\n"
        "created: 2026-01-02\n---\n\n"
        "# Summary\nTokio is an async runtime. It uses [[Work Stealing]].\n",
        encoding="utf-8",
    )
    (rust / "work-stealing.md").write_text(
        "---\ntitle: Work Stealing\ntags:\n- concurrency\ncreated: 2026-01-03\n---\n\n"
        "# Summary\nA scheduler strategy for balancing tasks.\n",
        encoding="utf-8",
    )
    return Vault(root)
