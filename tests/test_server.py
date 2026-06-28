from engram_mcp.server import build_server


def test_build_server_returns_app(vault):
    app = build_server(vault)
    assert app is not None
