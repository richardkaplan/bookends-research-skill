# Bookends home — groups, import, attach, deep-link, Vancouver, and the bridge quirks

Source-specific detail for running the Bookends Research Skill. Drive Bookends through
its MCP (`mcp__bookends-mcp__*`) and the pdf-highlight MCP
(`mcp__pdf-highlight-and-deep-link__*`) — never through screen automation.

## 0. Create the topic group + subtopic child groups

- Create groups with `mcp__bookends-mcp__bookends_groups`:
  - Parent: `{ action: "create", name: "<Topic> — Deep-Linked Report" }`
  - Each child: `{ action: "create", name: "<Topic> — <Subtopic>", parent: "<Topic> — Deep-Linked Report" }`
  - Always create a `<Topic> — Reports` child for the finished report.
- **Global-unique-name error.** Bookends group names are unique across the WHOLE
  library. A bare `Diagnosis` / `Reports` will collide with another project and error.
  **Always project-qualify** the name (`<Topic> — Diagnosis`). If a create still
  errors on uniqueness, disambiguate further (append a year or short id).
- **Verify real nesting.** After creating, call `{ action: "get" }` and confirm each
  child reports the parent as its container. A flat list of same-named groups means the
  nesting failed — recreate the child with the correct `parent`.
- File references later with
  `{ action: "add_references", name: "<Topic> — <Subtopic>", reference_ids: [ ... ] }`.

## 1. Get references and attach PDFs

- De-duplicate first: `mcp__bookends-mcp__bookends_search` by DOI/PMID/title
  (`sqlWhere` accepts bare `doi` / `pmid` aliases).
- Add by identifier: `mcp__bookends-mcp__bookends_quick_add` (DOI/PMID/arXiv) — pulls
  metadata and, where available, full text.
- Attach a downloaded full-text PDF:
  `mcp__pdf-highlight-and-deep-link__bookends_attach_pdf { id, pdfPath }`
  (or `mcp__bookends-mcp__bookends_add_pdf` for local files / direct PDF URLs /
  identifier retrieval).
- Attach an abstract-only PDF when no full text exists:
  `mcp__pdf-highlight-and-deep-link__bookends_attach_abstract_pdf` — and flag the
  article abstract-only in the report (its quote is not a full-text deep link).
- Record each reference's Bookends **id** — the locator for highlighting, linking, and
  filing into a subtopic.

## 2. The AppleScript-bridge quirks (bake in)

The Bookends AppleScript bridge is fussy on write:

- **It rejects the `volume` field on write.** Do not try to set `volume` through the
  bridge — the write fails.
- **It rejects any value containing parentheses.** A value like `25(2)` fails.

Workarounds:

- Store the issue in a **parenthesis-free** form (e.g. keep volume `25` and issue `2`
  as separate plain values in accepting fields; never write a `(`/`)` value).
- Prefer the dedicated tools (`bookends_set_field`, `bookends_quick_add`) over raw
  AppleScript; fall back to `bookends_applescript_run` only when nothing else fits, and
  keep every written value parenthesis-free.
- **Citations in the report must still be correct.** Reconstruct the full
  `volume(issue)` string in the report body and in the Vancouver References list from
  the stored parts. Only the value written *through the bridge* is parenthesis-free;
  what the reader sees is a correct `25(2)`.
- **Bad DOI → repurpose in place.** If a DOI/PMID resolved to the wrong paper,
  overwrite that record's fields with the correct metadata and re-attach the correct
  PDF. Never trash it and make a new one — editing in place avoids orphaned
  attachments and preserves the id/links.

## 3. Highlight a quote + get the deep link

```
mcp__pdf-highlight-and-deep-link__pdf_link_for_quote
  params: { "locator": "<bookends id or bookends:// URL>", "quote": "<verbatim fragment>" }
```

Writes a persistent highlight into the attached PDF and returns a `deepLink`:

```
bookends://…/selection/<Library>/<id>/0/<page>/0/0/0/0
```

This is **page-accurate**. Bookends ignores fabricated sentence-level selection
coordinates, so the link resolves to the correct page of the correct attachment — that
is expected. Use the returned `bookends://…` link verbatim as the quote's `href`.

`mcp__pdf-highlight-and-deep-link__bookends_get_selection_link` is the server-side
equivalent of Bookends' native "link to selected text of displayed PDF" if you need to
capture a current manual selection instead.

## 4. Vancouver References (the one format change)

The report ends with a section titled **`References`** (NOT "Works Cited"), formatted in
**Vancouver** style: numbered in citation order, plain text, no hyperlinks (Word-ready).

- Generate with `mcp__bookends-mcp__bookends_get_formatted_reference` using a Vancouver
  output style, or compose by hand.
- Reconstruct `volume(issue)` from the parenthesis-free stored parts so the printed
  Vancouver citation is correct even though the bridge stored the parts separately.
- The Academic Summary (just above References) keeps its in-text `(Author, Year)`
  citations as **plain text**, not hyperlinks, so it pastes into Microsoft Word cleanly.

## 5. Save the report — Bookends + iCloud

- **Bookends:** attach the finished HTML/PDF to a report reference filed in the
  `<Topic> — Reports` subgroup, and set the record's **AI-content label (label 3)**.
  **Never** add tags to the report; **never** trash anything. When regenerating, add the
  new report alongside the old one (do not move the old one to trash). Name it with an
  ` (AI)` suffix, e.g. `<Topic> — Deep-Linked Report (AI)`.
- **iCloud / `RESEARCH_DIR`:** save the SAME HTML under the configured `RESEARCH_DIR`
  (defined in SKILL.md → *Configuration*; default
  `$HOME/Library/Mobile Documents/com~apple~CloudDocs/Research`, resolved from `$HOME`
  — never a hardcoded username or absolute personal path):
  `<RESEARCH_DIR>/<Topic> — Deep-Linked Report/<Topic> — Deep-Linked Report (AI) <date>.html`
  (create the folder if needed). If iCloud Drive is not present, fall back to a
  documented default (`$HOME/Research`) or ask the user, and report the path used.
