# Final Whole-Branch Review Fix Report — Engram v0.1

Branch: `feature/engram-v0.1`
Date: 2026-06-28

## Changes Applied

### FIX 1 — Code-tagged vault exceptions (`src/engram_mcp/vault.py`)

- `VaultError` base class now has a `code` class attribute and `__init__` that prefixes every exception message with the stable token (e.g. `note_exists: path/to/file`).
- Subclasses: `PathEscapeError` (`code = "path_escape"`), `NotFoundError` (`code = "not_found"`), `NoteExistsError` (`code = "note_exists"`).
- `Vault.relpath` now raises `PathEscapeError` instead of a bare `ValueError` when the path is outside the vault root.
- New test in `tests/test_vault.py`: `test_errors_carry_code_token` — verifies all three codes appear in `str(exc)`.

### FIX 2 — Self-bootstrapping repo (`.mcp.json` + `docs/engram-verification.md`)

- Added `"PYTHONPATH": "src"` to `.mcp.json` env, so the server runs from a fresh checkout without a system-installed package.
- Prepended a **Prerequisites** section to `docs/engram-verification.md` documenting `pip install -e ".[dev]"`.

### FIX 3 — `list_dir` skips generated `index.md` (`src/engram_mcp/folders.py`)

- Changed the skip condition from `child.name.startswith(".")` to also exclude `child.name == "index.md"`.
- New test in `tests/test_folders.py`: `test_list_dir_skips_index_md` — writes a note, rebuilds the index, and asserts `index.md` is absent from the listing.

## Verification Outputs

### 1. Full test suite

```
$ python3 -m pytest -q
.........................................................   [100%]
57 passed in 0.67s
```

All 57 tests pass (was 55; 2 new tests added).

### 2. Server boot check

```
$ ENGRAM_VAULT=engram-data python3 -m engram_mcp.server < /dev/null
# (started, no traceback, exited cleanly on SIGTERM with code 0)
exit: 0
```

No Python traceback observed.

### 3. `.mcp.json` env validation

```
$ python3 -c "import json; d=json.load(open('.mcp.json')); print(d['mcpServers']['engram']['env'])"
{'ENGRAM_VAULT': 'engram-data', 'PYTHONPATH': 'src'}
```

Both `ENGRAM_VAULT` and `PYTHONPATH` present.
