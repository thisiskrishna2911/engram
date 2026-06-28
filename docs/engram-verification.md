## Prerequisites

From the repo root, install the package and test deps once:

    pip install -e ".[dev]"

The `.mcp.json` also sets `PYTHONPATH=src`, so the server runs from a fresh
checkout (run from the repo root) as long as `mcp` and `pyyaml` are installed.

# Engram end-to-end verification

With the `engram` MCP server registered (`.mcp.json`) and the `engram` skill installed:

1. In Claude, say: `/engram` then "Today I learned how Tokio's work-stealing scheduler
   rebalances tasks across worker threads."
2. Confirm:
   - [ ] A note appears under `engram-data/Engineering/Languages/Rust/` (or `Concurrency/`).
   - [ ] The **Explanation** section preserves your wording (no textbook rewrite).
   - [ ] `index.md` in that folder was updated.
   - [ ] Exactly ONE mentor question was asked.
3. Say: "find my note on work stealing" → Claude calls `search` and returns the note
   without reading the whole vault.
