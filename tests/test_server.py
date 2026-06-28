import pytest

from engram_mcp.server import build_server


def test_build_server_returns_app(vault):
    app = build_server(vault)
    assert app is not None


EXPECTED_TOOLS = {
    "create_folder", "list_dir", "rename_folder", "move",
    "read_note", "write_note", "append_note", "rename_note", "delete_note",
    "search", "find_by_metadata", "get_backlinks", "list_headings", "get_metadata",
    "rebuild_index",
}


async def test_all_fifteen_tools_registered(vault):
    app = build_server(vault)
    tools = await app.list_tools()
    assert {t.name for t in tools} == EXPECTED_TOOLS


def test_learning_session_tool_sequence(vault):
    # Mirrors the data-flow in the spec, exercised through the module layer the tools wrap.
    from engram_mcp import folders, index, links, notes, search
    folders.create_folder(vault, "Engineering/Languages/Rust")
    notes.write_note(
        vault,
        "Engineering/Languages/Rust/work-stealing.md",
        "---\ntitle: Work Stealing\ntags:\n- rust\ncreated: 2026-06-28\n---\n\n"
        "# Summary\nA scheduler strategy. Related to [[Tokio]].\n",
    )
    idx = index.rebuild_index(vault, "Engineering/Languages/Rust")
    assert "Work Stealing" in idx["notes"]
    hits = search.search(vault, "work stealing")["hits"]
    assert hits[0]["field"] == "title"
    # a later note that links here shows up as a backlink
    notes.write_note(
        vault,
        "Engineering/Languages/Rust/tokio.md",
        "---\ntitle: Tokio\n---\n\nUses [[Work Stealing]].\n",
    )
    back = links.get_backlinks(vault, "Engineering/Languages/Rust/work-stealing.md")
    assert [b["title"] for b in back["backlinks"]] == ["Tokio"]
