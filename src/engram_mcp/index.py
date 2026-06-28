from . import frontmatter as fm
from .vault import NotFoundError, Vault

_RECENT_LIMIT = 5


def _created(parsed: fm.ParsedNote) -> str:
    value = parsed.frontmatter.get("created")
    return str(value) if value else ""


def rebuild_index(vault: Vault, folder: str) -> dict:
    d = vault.resolve(folder)
    if not d.is_dir():
        raise NotFoundError(folder)

    subfolders: list[str] = []
    notes: list[tuple[str, str]] = []      # (title, created)
    for child in sorted(d.iterdir(), key=lambda c: c.name.lower()):
        if child.name.startswith(".") or child.name == "index.md":
            continue
        if child.is_dir():
            subfolders.append(child.name)
        elif child.suffix == ".md":
            parsed = fm.parse(child.read_text(encoding="utf-8"))
            notes.append((fm.title_of(parsed.frontmatter, child.stem), _created(parsed)))

    notes.sort(key=lambda n: n[0].lower())
    recent = sorted(notes, key=lambda n: n[1], reverse=True)[:_RECENT_LIMIT]

    heading = d.name if d != vault.root else "Engram"
    lines = [f"# {heading}", ""]
    if subfolders:
        lines.append("## Folders")
        lines += [f"- [{name}]({name}/index.md)" for name in subfolders]
        lines.append("")
    if notes:
        lines.append("## Notes")
        lines += [f"- [[{title}]]" for title, _ in notes]
        lines.append("")
    if recent:
        lines.append("## Recently Added")
        lines += [f"- [[{title}]]" + (f" — {created}" if created else "") for title, created in recent]
        lines.append("")
    content = "\n".join(lines).rstrip() + "\n"

    (d / "index.md").write_text(content, encoding="utf-8")
    return {
        "path": vault.relpath(d / "index.md"),
        "folders": subfolders,
        "notes": [title for title, _ in notes],
    }
