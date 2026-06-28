import shutil

from . import frontmatter as fm
from . import markdown as md
from .vault import NoteExistsError, NotFoundError, TRASH_DIRNAME, Vault


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


def write_note(vault: Vault, path: str, content: str, overwrite: bool = False) -> dict:
    p = vault.resolve(path)
    existed = p.is_file()
    if existed and not overwrite:
        raise NoteExistsError(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return {"path": vault.relpath(p), "created": not existed, "bytes": len(content.encode("utf-8"))}


def append_note(vault: Vault, path: str, content: str) -> dict:
    p = _require_file(vault, path)
    with p.open("a", encoding="utf-8") as f:
        f.write(content)
    return {"path": vault.relpath(p), "bytes": p.stat().st_size}


def rename_note(vault: Vault, path: str, new_title: str) -> dict:
    p = _require_file(vault, path)
    new_name = new_title if new_title.endswith(".md") else f"{new_title}.md"
    target = p.parent / new_name
    p.rename(target)
    return {"old_path": vault.relpath(p), "new_path": vault.relpath(target)}


def delete_note(vault: Vault, path: str) -> dict:
    p = _require_file(vault, path)
    trash = vault.root / TRASH_DIRNAME
    trash.mkdir(parents=True, exist_ok=True)
    dest = trash / p.name
    i = 1
    while dest.exists():
        dest = trash / f"{p.stem}.{i}{p.suffix}"
        i += 1
    shutil.move(str(p), str(dest))
    return {"path": vault.relpath(p), "trashed_to": vault.relpath(dest)}
