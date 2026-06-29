from mcp.server.fastmcp import FastMCP

from . import constitution, folders, index, links, notes
from .vault import Vault


def build_server(vault: Vault | None = None) -> FastMCP:
    vault = vault or Vault.from_env()
    app = FastMCP("engram")

    # --- Folders ---
    @app.tool()
    def create_folder(path: str) -> dict:
        return folders.create_folder(vault, path)

    @app.tool()
    def list_dir(path: str = ".") -> dict:
        return folders.list_dir(vault, path)

    @app.tool()
    def rename_folder(path: str, new_name: str) -> dict:
        return folders.rename_folder(vault, path, new_name)

    @app.tool()
    def move(src: str, dest: str) -> dict:
        return folders.move(vault, src, dest)

    # --- Notes ---
    @app.tool()
    def read_note(path: str) -> dict:
        return notes.read_note(vault, path)

    @app.tool()
    def write_note(path: str, content: str, overwrite: bool = False) -> dict:
        return notes.write_note(vault, path, content, overwrite)

    @app.tool()
    def append_note(path: str, content: str) -> dict:
        return notes.append_note(vault, path, content)

    @app.tool()
    def rename_note(path: str, new_title: str) -> dict:
        return notes.rename_note(vault, path, new_title)

    @app.tool()
    def delete_note(path: str) -> dict:
        return notes.delete_note(vault, path)

    # --- Structure / queries ---
    @app.tool()
    def search(query: str, limit: int = 20) -> dict:
        from . import search as search_mod
        return search_mod.search(vault, query, limit)

    @app.tool()
    def find_by_metadata(field: str, value: str) -> dict:
        from . import search as search_mod
        return search_mod.find_by_metadata(vault, field, value)

    @app.tool()
    def get_backlinks(note: str) -> dict:
        return links.get_backlinks(vault, note)

    @app.tool()
    def list_headings(path: str) -> dict:
        return notes.list_headings(vault, path)

    @app.tool()
    def get_metadata(path: str) -> dict:
        return notes.get_metadata(vault, path)

    # --- Index ---
    @app.tool()
    def rebuild_index(folder: str) -> dict:
        return index.rebuild_index(vault, folder)

    # --- Constitution (governing principles) ---
    @app.tool()
    def read_constitution() -> dict:
        return {
            "path": str(constitution.constitution_path()),
            "content": constitution.read_constitution(),
        }

    @app.resource(constitution.CONSTITUTION_URI)
    def constitution_resource() -> str:
        return constitution.read_constitution()

    return app


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
