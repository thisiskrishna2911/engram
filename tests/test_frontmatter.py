from engram_mcp.frontmatter import parse, serialize, title_of


def test_parse_roundtrip():
    text = "---\ntitle: Foo\ntags:\n- rust\n---\n\n# Body\ntext"
    p = parse(text)
    assert p.frontmatter["title"] == "Foo"
    assert p.frontmatter["tags"] == ["rust"]
    assert "# Body" in p.body
    assert p.frontmatter_error is None


def test_parse_no_frontmatter():
    p = parse("# Just a heading\n")
    assert p.frontmatter == {}
    assert p.body == "# Just a heading\n"
    assert p.frontmatter_error is None


def test_parse_malformed_frontmatter_does_not_crash():
    text = "---\nfoo: [unclosed\nbar: : :\n---\n\nbody"
    p = parse(text)
    assert p.frontmatter == {}
    assert p.frontmatter_error is not None
    assert p.body.strip() == "body"
    assert "unclosed" in p.raw_frontmatter


def test_serialize_emits_frontmatter():
    out = serialize({"title": "Foo"}, "# Body")
    assert out.startswith("---\ntitle: Foo\n---\n\n# Body")


def test_serialize_no_frontmatter_returns_body():
    assert serialize({}, "# Body") == "# Body"


def test_title_of_prefers_frontmatter():
    assert title_of({"title": "Real Title"}, "filename") == "Real Title"
    assert title_of({}, "filename") == "filename"
