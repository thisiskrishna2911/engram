import shutil

from . import frontmatter as fm
from .vault import NotFoundError, Vault


def create_folder(vault: Vault, path: str) -> dict:
    p = vault.resolve(path)
    created = not p.exists()
    p.mkdir(parents=True, exist_ok=True)
    return {"path": vault.relpath(p), "created": created}


def list_dir(vault: Vault, path: str = ".") -> dict:
    p = vault.resolve(path)
    if not p.is_dir():
        raise NotFoundError(path)
    folders_out, notes_out = [], []
    for child in sorted(p.iterdir(), key=lambda c: c.name.lower()):
        if child.name.startswith("."):
            continue
        if child.is_dir():
            folders_out.append({"name": child.name, "path": vault.relpath(child)})
        elif child.suffix == ".md":
            parsed = fm.parse(child.read_text(encoding="utf-8"))
            notes_out.append({
                "name": child.name,
                "title": fm.title_of(parsed.frontmatter, child.stem),
                "path": vault.relpath(child),
            })
    return {"path": vault.relpath(p), "folders": folders_out, "notes": notes_out}


def rename_folder(vault: Vault, path: str, new_name: str) -> dict:
    p = vault.resolve(path)
    if not p.is_dir():
        raise NotFoundError(path)
    target = p.parent / new_name
    p.rename(target)
    return {"old_path": vault.relpath(p), "new_path": vault.relpath(target)}


def move(vault: Vault, src: str, dest: str) -> dict:
    s = vault.resolve(src)
    if not s.exists():
        raise NotFoundError(src)
    d = vault.resolve(dest)
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(s), str(d))
    return {"src": vault.relpath(s), "dest": vault.relpath(d)}
