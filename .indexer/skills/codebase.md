---
name: codebase
description: Navigate this codebase. Load this before reading any source file or answering any code question.
---

# Codebase Navigation Instructions

This repo is indexed. **Do not read source files until you have checked the wiki.** The wiki gives you structure, relationships, and constraints in a fraction of the tokens.

## Stats

- **8 symbols** across **7 files** — indexed 2026-04-21 @ `a3c6c8f7`
- Wiki: `wiki/` — 1 page(s)
- Manifest: `.indexer/manifest.json` — maps every file to its wiki page and component IDs

## Wiki Pages

| Page | Covers | Key Entry Points |
|------|--------|-----------------|
| [root](../wiki/root.md) | activate_slots.js, app.ts | runDryRun, runLive, addNumbers |

## How to Answer Questions About This Codebase

**Step 1 — Orient:** Read `wiki/INDEX.md` first. It has the system overview and cross-cutting flows.

**Step 2 — Find the module:** Match the question to a wiki page from the table above. Read that page only.

**Step 3 — Look up symbols:** Component IDs follow `relative/path.py::ClassName.method_name`. Find them in the wiki page's Key Symbols table.

**Step 4 — Trace calls:** Use `## Relationships → Called by` on the wiki page to trace callers without reading source.

**Step 5 — Read source only if needed:** Once you know exactly which file and line range, read the source. Prefer the wiki for everything else.

## When to Read Source vs Wiki

| Question type | Use |
|--------------|-----|
| What does X do? | Wiki — Key Symbols table |
| Who calls X? | Wiki — Relationships → Called by |
| What does this module own? | Wiki — Modules table |
| How does a request flow end-to-end? | Wiki — Data Flows section (if --deep indexed) |
| What are the gotchas? | Wiki — Design Constraints section (if --deep indexed) |
| What's the exact implementation? | Source file — use line_start/line_end from manifest |
| Is X tested? | Source — check test files directly |

## Component ID Format

```
relative/path.py::ClassName.method_name   ← method
relative/path.py::ClassName               ← class
relative/path.py::function_name           ← top-level function
```

## Manifest Lookup

To find which wiki page covers a file:
```
.indexer/manifest.json → files["path/to/file.py"] → wiki_page
```

To find all symbols in a file:
```
.indexer/manifest.json → files["path/to/file.py"] → component_ids
```