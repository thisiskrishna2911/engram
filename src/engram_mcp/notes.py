from . import frontmatter as fm
from . import markdown as md
from .vault import NotFoundError, Vault


def _require_file(vault: Vault, path: str):
    p = vault.resolve(path)
    if not p.is_file():
        raise NotFoundError(path)
    return p


def read_note(vault: Vault, path: str) -> dict:
    p = _require_file(vault, path)
    text = p.read_text(encoding="utf-8")
    parsed = fm.parse(text)
    return {
        "path": vault.relpath(p),
        "content": text,
        "frontmatter": parsed.frontmatter,
        "headings": md.extract_headings(parsed.body),
        "links": md.extract_wikilinks(parsed.body),
        "frontmatter_error": parsed.frontmatter_error,
    }


def list_headings(vault: Vault, path: str) -> dict:
    p = _require_file(vault, path)
    parsed = fm.parse(p.read_text(encoding="utf-8"))
    return {"path": vault.relpath(p), "headings": md.extract_headings(parsed.body)}


def get_metadata(vault: Vault, path: str) -> dict:
    p = _require_file(vault, path)
    parsed = fm.parse(p.read_text(encoding="utf-8"))
    return {
        "path": vault.relpath(p),
        "frontmatter": parsed.frontmatter,
        "frontmatter_error": parsed.frontmatter_error,
    }
