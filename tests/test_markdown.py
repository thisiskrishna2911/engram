from engram_mcp.markdown import extract_headings, extract_wikilinks


def test_extract_headings_skips_code_fences():
    body = "# Title\n```\n# not a heading\n```\n## Sub"
    assert extract_headings(body) == [
        {"level": 1, "text": "Title"},
        {"level": 2, "text": "Sub"},
    ]


def test_extract_wikilinks_handles_alias_and_section():
    body = "See [[Tokio]] and [[Scheduler|the scheduler]] and [[Note#Heading]]."
    assert extract_wikilinks(body) == ["Tokio", "Scheduler", "Note"]


def test_extract_wikilinks_dedups_in_order():
    assert extract_wikilinks("[[A]] [[A]] [[B]]") == ["A", "B"]


def test_extract_wikilinks_skips_code_fences():
    body = "[[Real]]\n```\n[[NotALink]]\n```\n"
    assert extract_wikilinks(body) == ["Real"]
