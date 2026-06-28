import re

_WIKILINK = re.compile(r"\[\[([^\]\|#]+)(?:[#\|][^\]]*)?\]\]")
_HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def _content_lines(body: str):
    in_fence = False
    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield line


def extract_headings(body: str) -> list[dict]:
    out = []
    for line in _content_lines(body):
        m = _HEADING.match(line)
        if m:
            out.append({"level": len(m.group(1)), "text": m.group(2)})
    return out


def extract_wikilinks(body: str) -> list[str]:
    seen: list[str] = []
    for line in _content_lines(body):
        for m in _WIKILINK.finditer(line):
            target = m.group(1).strip()
            if target and target not in seen:
                seen.append(target)
    return seen
