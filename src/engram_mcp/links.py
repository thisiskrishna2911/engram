# src/engram_mcp/links.py
from collections.abc import Iterator
from pathlib import Path

from . import frontmatter as fm
from . import markdown as md
from .vault import Vault


def _iter_notes(vault: Vault) -> Iterator[Path]:
    for p in sorted(vault.root.rglob("*.md")):
        rel = p.relative_to(vault.root)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if p.name == "index.md":
            continue
        yield p


def get_backlinks(vault: Vault, note: str) -> dict:
    target = vault.resolve(note)
    keys = {target.stem.lower()}
    if target.is_file():
        parsed = fm.parse(target.read_text(encoding="utf-8"))
        title = parsed.frontmatter.get("title")
        if title:
            keys.add(str(title).lower())
    backlinks = []
    for p in _iter_notes(vault):
        if p == target:
            continue
        parsed = fm.parse(p.read_text(encoding="utf-8"))
        linked = {link.lower() for link in md.extract_wikilinks(parsed.body)}
        if linked & keys:
            backlinks.append({"path": vault.relpath(p), "title": fm.title_of(parsed.frontmatter, p.stem)})
    return {"note": vault.relpath(target), "backlinks": backlinks}
