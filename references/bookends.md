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

## 3. Highlight a quote + build a RESOLVABLE deep link

```
mcp__pdf-highlight-and-deep-link__pdf_link_for_quote
  params: { "locator": "<bookends id or bookends:// URL>", "quote": "<verbatim fragment>" }
```

This writes a persistent highlight into the attached PDF and returns the match's **page
index**, a **`referenceLink`** (`bookends://sonnysoftware.com/<refID>`), and a legacy
`deepLink` of the form:

```
bookends://sonnysoftware.com/selection/<Library>/<id>/0/<page>/0/0/0/0
```

**Do NOT use that `selection` `deepLink` as the quote's `href`.** It is a *fabricated* URL:
the segment where Bookends expects a real attachment/annotation id is `0`. When the link is
followed, Bookends tries to resolve object id `0`, finds nothing, and shows **"An error has
occurred: nil object."** (The browser → macOS → Bookends hand-off itself works; the failure
is Bookends resolving the nil target.) `selection/…` is **not** one of Bookends' documented
link types.

Use one of Bookends' **supported, self-emitted** link forms instead:

- **Reference link** — `bookends://sonnysoftware.com/<refID>` — selects the reference. This
  is what Bookends' Edit → Copy Link produces and what the original "excellent" Priapism
  report used. Always resolves. Available directly as the MCP's `referenceLink`.
- **Page-accurate PDF link** —
  `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>` — opens the
  attached PDF at `<page0>` (0-based). This is exactly the string Bookends' PDF-viewer
  "Copy Link" and the AppleScript `link to displayed PDF` property emit. Get the real
  `<attachmentID>` from Bookends and substitute your page:

  ```
  tell application "Bookends"
    set selected publication items of front library window to ¬
      (publication items of front library window whose id is <refID>)
    delay 0.3
    return link to displayed PDF of front library window
    -- e.g. bookends://sonnysoftware.com/pdf/Library1/101722/1783086068/0
  end tell
  ```

  Take `<attachmentID>` (4th path segment) and replace the trailing page segment with the
  highlight's 0-based page index. The persistent highlight marks the exact passage on that
  page.

Note on passage-level links: Bookends can produce a true selection link via the
`link to selected text of displayed PDF` property, but only for an ACTIVE manual text
selection in the viewer — it cannot be fabricated from coordinates
(`mcp__pdf-highlight-and-deep-link__bookends_get_selection_link` reads that property when a
selection exists). So for automated reports, page-accurate (`pdf/…`) is the tightest
reliably-resolvable target; the persistent highlight supplies passage-level precision on
that page.

## 3a. Deliver the links into Bookends as STYLED, CLICKABLE text

`bookends://` links work perfectly *inside* Bookends — but only when they sit in a field as
**styled text carrying the live hyperlink**. Bookends' Notes field and User1–User4 fields
hold styled text and live links; User5–User20 are plain text (no links). Two facts from the
Bookends User Guide ("Hypertext links in reference fields"):

- **Only a plain Paste inserts a live hyperlink — Paste And Match Style strips it** to dead
  plain text. By default that plain Paste is `⌘V`. If you have remapped `⌘V` to
  Paste-and-Match-Style in Bookends → Settings, do the plain paste with **Edit → Paste** or
  **⇧⌥⌘V**. (Developer tutorial: https://www.youtube.com/watch?v=GCp8R_tUuD8 .)
- Setting a field with AppleScript writes **plain text only** (attributes/links are lost),
  so a live link must arrive via the **clipboard as rich text**, then a plain Paste. There
  is no supported AppleScript path to inject an attributed hyperlink directly into a field.

Reproducible clipboard method (`scripts/styled_links_to_clipboard.sh`): build an HTML
fragment of the styled link list, `textutil -convert rtf` it, and load it onto the clipboard
as RTF so a single plain Paste drops live links into the field:

```
# input: lines of  <label><TAB>bookends://…  on stdin
./scripts/styled_links_to_clipboard.sh < links.tsv
# then in Bookends: click the report record's Notes field and press ⌘V
#   (or Edit → Paste / ⇧⌥⌘V if ⌘V is mapped to match-style)
```

To fully automate the paste, the skill may (with the user's permission) click the Notes
field and send a plain-paste keystroke via System Events; otherwise leave the styled list on
the clipboard and tell the user to press ⌘V into the Notes field. Either way this is **in
addition to** the attached HTML report and the iCloud copy — those stay unchanged.

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
  ` (AI)` suffix, e.g. `<Topic> — Deep-Linked Report (AI)`. **Also deliver the report's
  `bookends://` link list into that record's Notes field as styled, clickable text (§3a) —
  plain Paste, never Paste and Match Style — so the deep links are followable inside
  Bookends.**
- **iCloud / `RESEARCH_DIR`:** save the SAME HTML under the configured `RESEARCH_DIR`
  (defined in SKILL.md → *Configuration*; default
  `$HOME/Library/Mobile Documents/com~apple~CloudDocs/Research`, resolved from `$HOME`
  — never a hardcoded username or absolute personal path):
  `<RESEARCH_DIR>/<Topic> — Deep-Linked Report/<Topic> — Deep-Linked Report (AI) <date>.html`
  (create the folder if needed). If iCloud Drive is not present, fall back to a
  documented default (`$HOME/Research`) or ask the user, and report the path used.
