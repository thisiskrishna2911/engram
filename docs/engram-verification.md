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
