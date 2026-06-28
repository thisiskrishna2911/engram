from dataclasses import dataclass

import yaml

DELIM = "---"


@dataclass
class ParsedNote:
    frontmatter: dict
    body: str
    raw_frontmatter: str
    frontmatter_error: str | None


def parse(text: str) -> ParsedNote:
    lines = text.splitlines(keepends=True)
    if lines and lines[0].strip() == DELIM:
        for i in range(1, len(lines)):
            if lines[i].strip() == DELIM:
                raw = "".join(lines[1:i])
                body = "".join(lines[i + 1:]).lstrip("\n")
                try:
                    data = yaml.safe_load(raw)
                except yaml.YAMLError as e:
                    return ParsedNote({}, body, raw, str(e))
                if data is None:
                    return ParsedNote({}, body, raw, None)
                if not isinstance(data, dict):
                    return ParsedNote({}, body, raw, "frontmatter is not a mapping")
                return ParsedNote(data, body, raw, None)
    return ParsedNote({}, text, "", None)


def serialize(frontmatter: dict, body: str) -> str:
    if frontmatter:
        raw = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
        return f"{DELIM}\n{raw}\n{DELIM}\n\n{body}"
    return body


def title_of(frontmatter: dict, stem: str) -> str:
    title = frontmatter.get("title")
    return str(title) if title else stem
