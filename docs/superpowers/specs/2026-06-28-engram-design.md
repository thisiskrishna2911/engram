# Engram v0.1 — Design Spec

- **Date:** 2026-06-28
- **Status:** Approved (brainstorming) — pending implementation plan
- **Author:** Krishna (vision) · captured via brainstorming

---

## 1. Mission

Engram is an **Engineering Memory System**, not a note-taking app. Its purpose is to
**preserve the user's understanding, not generate knowledge**. Every design decision
answers one question:

> "Will Future Krishna understand what Present Krishna understood?"

Engram reduces the friction between *learning* and *documenting* so the user can focus
on understanding rather than writing Markdown.

**Final principle (overrides everything else):**

> Engram exists to preserve my thinking, not replace it.

## 2. Core Principles (Guardrails)

1. **AI is a scribe, not an author.**
2. Preserve the user's understanding and **voice** — format only, never rewrite into
   textbook language.
3. Never hallucinate or inject knowledge unless explicitly requested.
4. Prefer simple, hand-editable Markdown over complex abstractions.
5. Reduce friction. Organize automatically. Encourage active recall.
6. The AI helps the user think — it never thinks *for* the user.
7. **Strict separation:** the MCP server never reasons, decides, or generates content;
   the AI never touches the filesystem except through MCP.

## 3. Architecture

Two deliverables, one principle — **Claude is the scribe, the MCP server is the hands.**

```
┌─────────────────────────────┐         ┌──────────────────────────────┐
│  engram skill  (REASONING)  │  calls  │  engram-mcp  (HANDS)          │
│  • placement decisions      │ ──────► │  • filesystem operations      │
│  • fills template from the  │  tools  │  • deterministic parsing      │
│    user's words (format)    │         │    (frontmatter/headings/     │
│  • [[links]], mentor Qs     │ ◄────── │     [[wikilinks]])            │
│  • NEVER writes files       │  data   │  • NEVER reasons/generates    │
└─────────────────────────────┘         └──────────────────────────────┘
                                                   │ reads/writes
                                                   ▼
                                    engram-data/  (Obsidian Markdown vault)
                                    plain .md files — hand-editable, no lock-in
```

- **`engram-mcp`** — Python MCP server, **stdio** transport. Vault root configured via
  `ENGRAM_VAULT` (default `engram-data/`). Deterministic only. Registered in the user's
  Claude config so this Claude can call it.
- **`engram` skill** — `.claude/skills/engram/SKILL.md`. All reasoning. Invoked via
  `/engram` (and/or auto-triggers on "I learned…"). Calls MCP tools; never touches the
  filesystem.

**The boundary is the product.** The server returns *data*; Claude makes *decisions*.
Parsing existing structure (frontmatter, headings, links) is **not** reasoning — it does
not decide, generate, or hallucinate — so the server can be smart about *lookups* while
remaining a pure scribe's tool.

### Key decisions (with rationale)

| Decision | Choice | Why |
|---|---|---|
| What the "AI Agent" is | **Claude + `engram` skill** (build only the server) | Captures the carefully-specified workflow in one version-controlled artifact; fits the user's existing skill+MCP setup; no separate app, LLM key, or cost. |
| Vault folder tree | **Lazy creation** | Folders + `index.md` created only when a note needs them. Vault only ever contains touched topics. The `Engineering/` tree becomes a *placement map* the skill reasons over, not pre-created empty folders. |
| Server depth | **Structure-aware indexer** | Deterministically parses frontmatter/headings/wikilinks to power ranked search, metadata queries, backlinks, index rebuild. Token-cheap for Claude; realizes the full spec; no cache complexity. Interface is forward-compatible with a future persistent index. |

## 4. Component 1 — `engram-mcp` (the server)

Python package, `src/` layout:

```
engram/
  pyproject.toml
  src/engram_mcp/
    __init__.py
    server.py        # FastMCP app + tool registrations
    vault.py         # path safety (resolve under root, reject ..), ENGRAM_VAULT config
    notes.py         # read / write / append / rename / move / soft-delete
    folders.py       # create (lazy nested) / list / rename
    frontmatter.py   # parse + serialize YAML frontmatter (lenient on hand-edit typos)
    markdown.py      # extract # headings and [[wikilinks]] from a body
    search.py        # ranked search + find_by_metadata
    links.py         # backlink resolution (scan vault for [[target]])
    index.py         # rebuild_index(folder) -> deterministic index.md
  tests/
```

### Tool surface (v0.1)

**Folders**

| Tool | Purpose / Returns |
|---|---|
| `create_folder(path)` | Create nested folders lazily. Returns created path(s). |
| `list_dir(path)` | List child folders + notes with light metadata (name, type, mtime). |
| `rename_folder(path, new_name)` | Rename a folder. |
| `move(src, dest)` | Move a note or folder. |

**Notes**

| Tool | Purpose / Returns |
|---|---|
| `read_note(path)` | Full content + parsed metadata (frontmatter, headings, links). |
| `write_note(path, content, overwrite=False)` | Create or (explicitly) overwrite. **Default refuses to clobber.** |
| `append_note(path, content)` | Append text/section to an existing note. |
| `rename_note(path, new_title)` | Rename a note file. |
| `delete_note(path)` | **Soft delete** → moves to `.trash/` (recoverable). |

**Structure / queries** *(the structure-aware value)*

| Tool | Purpose / Returns |
|---|---|
| `search(query, limit)` | Ranked hits across the full priority order **title > alias > tag > heading > content > linked-notes** (see §10; linked-notes is the weakest signal). Each hit = path, matched field, snippet, score. |
| `find_by_metadata(field, value)` | Notes whose frontmatter `field` matches `value` (e.g. tag, status, confidence, project). |
| `get_backlinks(note)` | Notes containing `[[note]]`. |
| `list_headings(note)` | Heading outline of a note. |
| `get_metadata(note)` | Frontmatter as a structured dict. |

**Index**

| Tool | Purpose / Returns |
|---|---|
| `rebuild_index(folder)` | Regenerate `index.md` purely from directory contents: child folders, child notes, recently-added (by frontmatter `created`, falling back to file mtime). Deterministic, idempotent. |

### Design choices baked into the server

- **`overwrite=False` by default** — no silent clobber; forces Claude to be deliberate.
- **Soft-delete to `.trash/`** — nothing irrecoverable; honors the "preserve" ethos.
- **Lazy `create_folder`** — matches the vault-tree decision.
- **Path safety** — every path resolved under the vault root; reject `..`/absolute escapes.
- **Structured returns** — every tool returns a dict (path, title, mtime, …), not raw text.
- **Lenient frontmatter parsing** — a hand-edited YAML typo must never crash a query.

## 5. Component 2 — `engram` skill (the reasoning)

`.claude/skills/engram/SKILL.md` (+ reference files as needed) encodes, as
prompt/instructions **only** (no code, no filesystem access):

- **Learning-session workflow** — topic + explanation → decide placement (via the
  `Engineering/` placement map) → fill the **Standard Note Template** strictly from the
  user's words → `write_note` → lazy `create_folder` → `rebuild_index` → suggest *real*
  `[[Related Topics]]` → **one** Mentor question.
- **The exact note template, YAML frontmatter, and metadata block** (Section 8).
- **Hard guardrails** — never rewrite into textbook language, never add technical info,
  never expand concepts, preserve the user's voice, never invent "gaps."
- **Retrieval discipline** — use `search` / `find_by_metadata` / `get_backlinks` instead
  of reading the whole vault.
- **Mentor Mode** — exactly ONE follow-up question, or ONE pointed misunderstanding, or
  ONE next-topic suggestion. Never a lecture.

## 6. Data Flow — a learning session

```
You: /engram → "Today I learned how Tokio's work-stealing scheduler
                rebalances tasks across worker threads…"
  │
  ▼
1. Skill parses intent → topic, explanation, optional source/tags
2. Skill decides placement via the Engineering/ map → e.g. Languages/Rust/ or Concurrency/
3. Skill: search(query) + list_dir(folder)  ── dedupe: is there already a related note?
4. Skill fills the Standard Note Template  ── STRICTLY from the user's words (format only)
5. Skill: create_folder(...) if new  →  write_note(path, content, overwrite=False)
6. Skill: rebuild_index(folder) for the touched folder + parents
7. Skill: get_backlinks / search  →  proposes REAL [[Related Topics]] (user confirms)
8. Skill: emits ONE Mentor question
```

Every write crosses the MCP boundary. Claude decides; the server acts. Step 3
(dedupe-before-create) prevents duplicate-note sprawl and serves "build a connected
knowledge base over time."

## 7. Error Handling

| Situation | Behavior |
|---|---|
| **Path escapes vault** (`..`, absolute) | Server rejects with a clear error; Claude surfaces it, does not retry blindly. |
| **Write to existing path** | `overwrite=False` default → server errors `note_exists`; Claude must choose append / new title / explicit overwrite. No silent clobber. |
| **Malformed frontmatter** (hand-edit typo) | Parser is **lenient**: on YAML failure, return raw frontmatter + `frontmatter_error` flag instead of crashing. Note still indexes by body/headings/links; only metadata queries skip it. Honors "everything editable by hand." |
| **Note not found** | Clear `not_found` error. |
| **Delete** | Soft → moves to `.trash/`, recoverable. Never hard-delete in v0.1. |
| **`rebuild_index`** | Idempotent — safe to call repeatedly; pure function of directory contents. |

Principle: the server fails **loudly and recoverably**, and never destroys user data.
Structured errors let Claude react deliberately rather than paper over them.

## 8. Standard Note Template

```markdown
---
title:
category:
status:
confidence:
created:
updated:
tags:
source:
---

# Summary
A concise summary based only on the user's explanation.

# Explanation
The user's explanation. Preserve wording. Improve formatting only.

# Examples
Examples provided by the user.

# Related Topics
[[Topic]]
[[Topic]]

# Questions I Still Have
Only genuine gaps inferred from the user's explanation. Do not invent gaps.

# Revision Questions
2–5 active-recall questions (e.g. "Explain this without looking.",
"What problem does this solve?", "When should it NOT be used?").
```

**Confidence scale:** `0` never seen · `1` recognize the term · `2` understand basics ·
`3` can explain · `4` have built with it · `5` can teach it.

**Metadata block (maintained per note):** `first_learned`, `last_reviewed`, `last_used`,
`projects`, `related`, `difficulty`, `status`.

**Relationships a note may reference:** Prerequisites · Related Topics · Used By ·
Projects · Books · Videos · Articles · Examples. The graph grows organically — never force
connections.

## 9. Vault Structure (placement map)

The skill reasons over this tree to place notes; folders are created lazily.

```
Engineering/
  Foundations/ {DSA, Operating Systems, Networking, Databases, Concurrency}
  Languages/   {Rust, Python, Go}
  AI/          {LLMs, Agents, STT, TTS, RAG, Evaluation}
  Infrastructure/ {Docker, Kubernetes, Linux, Cloud, CI-CD}
  Distributed Systems/
  Performance/
  System Design/
  Projects/
  Career/
```

Every directory may contain an `index.md` (navigation only): child folders, child notes,
quick links, recently added. The skill calls `rebuild_index` when notes are added or moved.

## 10. Search Philosophy

Ranking priority (implemented deterministically in `search.py`):
**1. exact titles · 2. aliases · 3. tags · 4. headings · 5. content · 6. linked notes.**
Goal: help Future Me rediscover knowledge quickly.

## 11. Testing Strategy

- **Unit (pytest)** against a temp-vault fixture, per module:
  - `vault.py` — traversal rejection, root resolution
  - `frontmatter.py` — parse/serialize round-trip **including malformed input** (no crash)
  - `markdown.py` — heading + `[[wikilink]]` extraction
  - `search.py` — **ranking order asserted** (title > tag > content), `find_by_metadata`
  - `links.py` — backlink resolution
  - `index.py` — `rebuild_index` golden output + idempotency
  - `notes.py` — overwrite-guard, soft-delete → `.trash/`
- **Tool-contract tests** — invoke each tool via FastMCP's in-process client; assert
  structured return shapes.
- **Golden vault fixture** — a tiny known vault (notes with deliberate links/tags) so
  search ranking + backlinks are asserted deterministically.
- **Skill verification (manual, documented)** — a scripted dry-run asserting the
  *tool-call sequence* of a learning session (placement → write → rebuild_index → mentor
  Q). Wording-preservation can't be unit-tested, so v0.1 ships a written end-to-end check:
  "learn X → note lands in the right folder, wording intact, index updated, exactly one
  mentor question."

## 12. Scope

**In scope (v0.1):** the `engram-mcp` server (structure-aware tools above) and the
`engram` skill (learning-session workflow + mentor mode).

**Explicitly OUT of scope** (deferred per the vision's "Future Features"): embeddings,
semantic/vector search, vector database, spaced repetition, knowledge-graph visualization,
AI memory, agentic planning, flashcards, GitHub integration, automatic project linking,
daily review, learning analytics. Do not implement unless explicitly requested.

## 13. Success Criteria

Engram succeeds if the user can: learn continuously without worrying about formatting;
explain concepts naturally; trust that the AI captured their understanding accurately;
retrieve their own thoughts easily months later; and watch the knowledge base grow
organically — friction removed, not complexity added.
