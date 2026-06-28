# Engram

**An Engineering Memory System — not a note-taking app.**

Engram preserves *your* understanding over the years. It reduces the friction between
learning something and writing it down, without ever replacing your thinking. Every
design decision answers one question:

> **"Will Future Me understand what Present Me understood?"**

The AI is a **scribe, never an author**: it captures your explanation in your own words,
files it well, and connects it to what you already know — but it never rewrites your
voice, invents knowledge, or expands concepts you didn't write.

---

## How it works

Engram is two cooperating halves with a hard boundary between them:

```
┌─────────────────────────────────────┐         ┌──────────────────────────────┐
│  Reasoning  (the "engram" skill,     │  calls  │  engram-mcp  (the hands)     │
│  governed by the Constitution)       │ ──────► │  • filesystem operations     │
│  • decides placement & dedupe        │  tools  │  • deterministic parsing     │
│  • fills the note from YOUR words    │         │    (frontmatter / headings / │
│  • suggests links, asks 1 mentor Q   │ ◄────── │     wiki-links)              │
│  • NEVER touches the filesystem      │  data   │  • NEVER reasons or generates│
└─────────────────────────────────────┘         └──────────────────────────────┘
                                                          │ reads / writes
                                                          ▼
                                       engram-data/  (an Obsidian Markdown vault)
                                       plain .md files — hand-editable, no lock-in
```

- **`engram-mcp`** — a Python [MCP](https://modelcontextprotocol.io) server (stdio,
  FastMCP) exposing **15 deterministic tools** over a Markdown vault. It does filesystem
  work and structure parsing; it never reasons or generates content.
- **The `engram` skill** (`.claude/skills/engram/SKILL.md`) — the reasoning layer that
  drives a learning session and calls the tools. It never writes files directly.
- **The [Constitution](docs/CONSTITUTION.md)** — the principles that govern everything.
  *The skill provides the workflow; the Constitution provides the principles; when they
  conflict, the Constitution wins.*

Your notes live as plain `.md` files in an Obsidian-compatible vault — readable and
editable by hand, with or without AI.

---

## A learning session

```
You:  /engram  → "Today I learned how Tokio's work-stealing scheduler rebalances
                  tasks across worker threads…"

Engram:
  1. reasons about intent & placement, then searches to avoid duplicates
  2. fills the note template STRICTLY from your words (formatting only)
  3. write_note(...) into Engineering/Languages/Rust/ (created lazily)
  4. rebuild_index(...) for the touched folders
  5. proposes REAL [[Related Topics]] via search / get_backlinks
  6. asks exactly ONE mentor question — never a lecture
```

The whole point: you focus on *understanding and explaining*; Engram removes the
Markdown-and-filing friction.

---

## The tool surface (15 tools)

| Group | Tools |
|---|---|
| **Folders** | `create_folder` · `list_dir` · `rename_folder` · `move` |
| **Notes** | `read_note` · `write_note` · `append_note` · `rename_note` · `delete_note` *(soft → `.trash/`)* |
| **Structure / queries** | `search` *(ranked: title › alias › tag › heading › content › linked)* · `find_by_metadata` · `get_backlinks` · `list_headings` · `get_metadata` |
| **Index** | `rebuild_index` *(regenerates `index.md` from a folder's contents)* |

**Safety is built into the server, not bolted on:**

- `write_note` is `overwrite=False` by default — **no silent clobber**.
- `rename_note`, `move`, and `rename_folder` refuse to overwrite an existing target.
- `delete_note` is a **soft delete** to `.trash/` — nothing is ever irrecoverable.
- Every path is resolved under the vault root; `..` and absolute escapes are rejected.
- Frontmatter parsing is **lenient** — a hand-edited YAML typo never crashes a query.
- Errors carry stable codes (`note_exists` / `not_found` / `path_escape`) so the agent
  can recover deliberately.

---

## Vault structure

Folders are created **lazily** — the vault only ever contains topics you've actually
touched. The tree below is the *placement map* the skill reasons over:

```
Engineering/
  Foundations/      DSA · Operating Systems · Networking · Databases · Concurrency
  Languages/        Rust · Python · Go
  AI/               LLMs · Agents · STT · TTS · RAG · Evaluation
  Infrastructure/   Docker · Kubernetes · Linux · Cloud · CI-CD
  Distributed Systems/   Performance/   System Design/   Projects/   Career/
```

Every folder may hold an `index.md` (navigation only), regenerated deterministically by
`rebuild_index`.

---

## Getting started

**Prerequisites:** Python 3.13+.

```bash
# From the repo root — installs the package and test deps
pip install -e ".[dev]"
```

**Register the MCP server.** `.mcp.json` (already in the repo) points your MCP client at
the server:

```json
{
  "mcpServers": {
    "engram": {
      "command": "python3",
      "args": ["-m", "engram_mcp.server"],
      "env": { "ENGRAM_VAULT": "engram-data", "PYTHONPATH": "src" }
    }
  }
}
```

- `ENGRAM_VAULT` — the vault directory (default `engram-data/`).
- `PYTHONPATH=src` lets the server run from a fresh checkout without the editable install.

**Use it.** In an MCP-capable client (e.g. Claude Code) with the `engram` skill installed,
type `/engram` and explain something you learned. A note appears in your vault, the index
updates, and you get one mentor question. See
[`docs/engram-verification.md`](docs/engram-verification.md) for the end-to-end check.

---

## The note template

Every note is plain Markdown with YAML frontmatter, filled **only** from your explanation:

```markdown
---
title: Work Stealing
category: Engineering/Languages/Rust
status: seedling | growing | evergreen
confidence: 0-5
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [rust, concurrency]
source:
---

# Summary
<one concise summary, only from your explanation>

# Explanation
<your explanation — wording preserved, formatting only>

# Examples
<your examples, if any>

# Related Topics
[[Tokio]]

# Questions I Still Have
<only genuine gaps inferred from what you said>

# Revision Questions
<2-5 active-recall questions>
```

Confidence scale: `0` never seen · `1` recognize the term · `2` understand basics ·
`3` can explain · `4` have built with it · `5` can teach it.

---

## Project layout

```
engram/
├── src/engram_mcp/        # the MCP server
│   ├── vault.py           # path safety + ENGRAM_VAULT config + error types
│   ├── frontmatter.py     # lenient YAML parse/serialize
│   ├── markdown.py        # heading + wiki-link extraction (fence-aware)
│   ├── notes.py           # read / write / append / rename / soft-delete
│   ├── folders.py         # create / list / rename / move
│   ├── links.py           # backlinks
│   ├── search.py          # ranked search + metadata queries
│   ├── index.py           # deterministic index.md rebuild
│   └── server.py          # FastMCP app — registers the 15 tools
├── tests/                 # pytest suite (golden-vault fixture, contract tests)
├── .claude/skills/engram/SKILL.md   # the reasoning workflow
├── docs/
│   ├── CONSTITUTION.md    # the governing principles
│   └── superpowers/       # design spec, DX overview, implementation plan
└── .mcp.json              # MCP server registration
```

---

## Development

```bash
python3 -m pytest -q        # run the full suite
```

The codebase follows a strict separation: **the server is deterministic and never
reasons** (it only does filesystem work and parsing), while all judgment lives in the
skill. New providers/behaviors are added by composition, not by leaking logic into the
server.

---

## Principles & scope

Engram is governed by the [**Engram Constitution**](docs/CONSTITUTION.md). Read it first
if you plan to extend the system — it is the authority on what Engram may and may not do.

**Intentionally out of scope for now** (the Constitution's "Extensibility" section — build
only when explicitly requested): flashcards, spaced repetition, semantic/vector search,
knowledge-graph visualization, interview generation, learning analytics, hosted agents.
Today's design is meant to absorb these later without an architectural rewrite.

---

> **Engram exists to preserve my thinking, not replace it.**
