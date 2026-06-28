from . import frontmatter as fm
from . import markdown as md
from .links import _iter_notes
from .vault import Vault

_TITLE, _ALIAS, _TAG, _HEADING, _CONTENT, _LINKED = 6, 5, 4, 3, 2, 1
_FIELD = {6: "title", 5: "alias", 4: "tag", 3: "heading", 2: "content", 1: "linked"}


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value]
    return [str(value)]


def _snippet(body: str, query: str) -> str:
    i = body.lower().find(query.lower())
    if i < 0:
        return ""
    start, end = max(0, i - 30), min(len(body), i + len(query) + 30)
    return body[start:end].replace("\n", " ").strip()


def search(vault: Vault, query: str, limit: int = 20) -> dict:
    q = query.lower().strip()
    notes_list = list(_iter_notes(vault))
    parsed = {p: fm.parse(p.read_text(encoding="utf-8")) for p in notes_list}
    title = {p: fm.title_of(parsed[p].frontmatter, p.stem) for p in notes_list}

    title_match = {p for p in notes_list if q in title[p].lower()}
    match_keys = {title[p].lower() for p in title_match} | {p.stem.lower() for p in title_match}

    hits = []
    for p in notes_list:
        f = parsed[p].frontmatter
        body = parsed[p].body
        aliases = _as_list(f.get("aliases"))
        tags = _as_list(f.get("tags"))
        headings = [h["text"] for h in md.extract_headings(body)]
        links = {link.lower() for link in md.extract_wikilinks(body)}
        if q in title[p].lower():
            score = _TITLE
        elif any(q in a.lower() for a in aliases):
            score = _ALIAS
        elif any(q in t.lower() for t in tags):
            score = _TAG
        elif any(q in h.lower() for h in headings):
            score = _HEADING
        elif q in body.lower():
            score = _CONTENT
        elif links & match_keys:
            score = _LINKED
        else:
            continue
        hits.append({
            "path": vault.relpath(p),
            "field": _FIELD[score],
            "snippet": _snippet(body, query),
            "score": score,
        })
    hits.sort(key=lambda h: (-h["score"], h["path"]))
    return {"query": query, "hits": hits[:limit]}


def find_by_metadata(vault: Vault, field: str, value) -> dict:
    out = []
    for p in _iter_notes(vault):
        f = fm.parse(p.read_text(encoding="utf-8")).frontmatter
        v = f.get(field)
        if v is None:
            continue
        if isinstance(v, list):
            match = any(str(x).lower() == str(value).lower() for x in v)
        else:
            match = str(v).lower() == str(value).lower()
        if match:
            out.append({"path": vault.relpath(p), "title": fm.title_of(f, p.stem), "value": v})
    return {"field": field, "value": value, "notes": out}
