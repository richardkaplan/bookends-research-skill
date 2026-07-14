# Bookends home — groups, import, attach, deep-link, Vancouver, and the bridge quirks

Source-specific detail for running the Bookends Research Skill. Drive Bookends through
its MCP (`mcp__bookends-mcp__*`) — the MCP server bundled inside Bookends.app — never
through screen automation.

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

## 1. Retrieve references + PDFs — Bookends-first, Firecrawl only as fallback

**Try Bookends for each article first; fall back to Firecrawl only when Bookends cannot
retrieve it, then import the result back into Bookends.** Log each article's path
(Bookends vs Firecrawl-fallback) so the run is auditable.

### 1a. PRIMARY — Bookends' own retrieval (verified features)

Confirmed against the Bookends User Guide and the AppleScript dictionary — do not assume
features beyond these:

- **Online Search / Bookends Browser.** Bookends searches literature databases directly:
  built-in **PubMed, Google Scholar, Semantic Scholar, Google Books, Library of Congress,
  JSTOR, arXiv**, plus Z39.50/SRU catalogs. Its **"Attempt PDF download"** option (same as
  *Refs → Get PDF → From Internet (If Available)*) auto-downloads and attaches the PDF on
  import when the article is open-access or the IP has access.
- **Identifier add:** `mcp__bookends-mcp__bookends_quick_add` (DOI/PMID/arXiv) — pulls
  metadata and, where available, full text.
- **Automatic PDF download for existing references:** Bookends' native **`download pdfs`**
  command fetches and attaches the full-text PDF using a reference's stored **PMID, DOI,
  or arXiv id** (it also tries to resolve a DOI first when only some ids are present). It
  is the scriptable form of *Get PDF → From Internet (If Available)*. Drive it via
  `mcp__bookends-mcp__bookends_add_pdf` (identifier retrieval / direct PDF URL / local
  file); when only AppleScript fits, run it with
  `mcp__bookends-mcp__bookends_applescript_run`:

  ```
  tell application "Bookends"
    tell front library window
      set r to download pdfs {publication item id "<refID>"}
    end tell
  end tell
  -- returns JSON, one result per publication item
  ```

  Then confirm the attachment with `mcp__bookends-mcp__bookends_get_attachment_paths`.
- **Local PDF / folder:** attach an on-disk PDF with
  `mcp__bookends-mcp__bookends_add_pdf { items:[{ id, path }] }`, or bulk-import a
  folder with `mcp__bookends-mcp__bookends_import_pdf_folder` (resolve `metadata_required`
  items by DOI/PMID/ISBN/arXiv through `bookends_quick_add`).
- De-duplicate first: `mcp__bookends-mcp__bookends_search` by DOI/PMID/title
  (`sqlWhere` accepts bare `doi` / `pmid` aliases) so a re-run never duplicates a ref.

An article counts as **Bookends-retrieved** when Bookends located the reference AND
attached a usable PDF (or a deliberately-flagged abstract-only PDF) via the above.

### 1b. FALLBACK — Firecrawl (only when Bookends can't)

Only when the Bookends path fails for a given article — no match, unresolvable DOI/PMID,
or no retrievable PDF — fall back to the **`firecrawl-research-index`** skill /
`mcp__mcp-server-firecrawl__firecrawl_research_*` (and/or PubMed) to find and fetch it,
then **import the result back into Bookends**: create/locate the reference
(`bookends_quick_add`) and attach the fetched PDF (`bookends_add_pdf`). Mark the article
**Firecrawl-fallback**. Firecrawl costs money and is
less private than the native Bookends path — reserve it for this fallback and for
genuinely external-website research.

### 1c. Abstract-only + id/provenance bookkeeping

- Attach an abstract-only PDF when no full text exists (either path): render the citation +
  abstract as HTML, print it to PDF with headless Chrome, attach with
  `mcp__bookends-mcp__bookends_add_pdf` — and flag the article abstract-only in the report
  (its quote is not a full-text deep link).
- Record each reference's Bookends **id** and its **retrieval provenance** (Bookends vs
  Firecrawl-fallback) — the id is the locator for highlighting, linking, and filing into
  a subtopic; the provenance feeds the run's audit tally.

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

## 3. Highlight a quote + build a RESOLVABLE deep link (Bookends MCP only — no PDF library)

**Check the attachment belongs to the reference FIRST** (§3c). Bookends annotates the
*first* attachment; a stray one gives you a flawless link to the wrong paper.

```
# 1. write the persistent highlight, in place, into the attached PDF
mcp__bookends-mcp__bookends_annotate_pdf {
  bookends_reference_id: "<refID>",
  annotation: "highlight",
  mode: "exact",        # ALWAYS pass it — the tool's OWN DEFAULT IS "semantic"
  query: "<the verbatim sentence>",
  idempotent: true      # default: re-runs reuse the highlight (created:0, reused:1)
}
-> { annotations_created, annotations_reused, disk_verified, page, … }

# 2. read the annotation back — its `link` IS the page-accurate citation URL
mcp__bookends-mcp__bookends_get_pdf_content { id: "<refID>", mode: "annotations" }
-> { annotations: [ { page, text, link: "bookends://…/pdf/<Lib>/<id>/<attID>/<page0>" } ] }
```

The deep link is **annotation-anchored** and generated by Bookends. **There is no PyMuPDF /
`fitz` dependency in this skill — do not add one back.**

**⛔ `mode` is `exact`, always. `semantic` is BANNED.** One paraphrased sentence produced
**20 highlights across 11 pages** — it is a different operation, not a looser match.
`regex` / `key_points` are unused too.

**⛔ FABRICATED-QUOTE GUARD.** `exact` writes nothing when the text is not verbatim (or is
ambiguous). **A quote that will not match is a quote that is WRONG.** Go back to the PDF and
take a real sentence; **never** loosen the mode. Line breaks and end-of-line hyphenation
already match; a repeated sentence is disambiguated with `page` (1-based) / `occurrence`.

**Two MCP quirks (neither is a blocker):**

- **No `.bak`.** Annotations are applied **in place** — there is **no rollback** on a
  malformed write. `disk_verified` confirms the saved file; `idempotent: true` means a
  repeat call does not even rewrite the file.
- **`bookends_get_pdf_content` echoes highlight text with the line-break hyphen retained**
  (`"first mobi-lized"`). *Matching* is correct; only the echo is un-dehyphenated. Quote
  from **your own source string**. If you must quote from the annotation list, strip the
  join hyphen with a regex — `re.sub(r"(\w)-\s+(\w)", r"\1\2", text)` — **not** with a PDF
  library.

**⛔ R-BOOKENDS-PDF-DEEPLINK-02: never emit a `…/selection/…` link.** Bookends implements
no `selection` route; it dereferences a nil object and raises the modal **"An error has
occurred: nil object."** Never string-template a citation URL — take it from the annotation.

**The bare `bookends://sonnysoftware.com/<refID>` form is BANNED.** It selects the
reference inside the FULL marked library, dropping the reader into unrelated citations
("soup"). Never emit it for anything.

Supported forms, and what each is for:

- **Group link** — `bookends://sonnysoftware.com/group/<LibraryName>/<URL-encoded group name>` —
  opens that group. This is the **`Bookends Group`** link required on every source
  (R-BOOKENDS-DUAL-LINK-01): point it at the source's **subtopic child group**.
  `<LibraryName>` (e.g. `Library1`, from AppleScript `name of front library window` minus
  `.bdb`) is REQUIRED; percent-encode the name (space→`%20`, em dash→`%E2%80%94`, `&`→`%26`).
- **Page-accurate PDF link — the ONLY valid Citation/quote link** —
  `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>` — opens the
  attached PDF at `<page0>` (0-based). **Take it from the annotation** you just wrote:
  `bookends_get_pdf_content { id: "<refID>", mode: "annotations" }` returns it in each
  annotation's `link` field, already page-accurate. The `<attachmentID>` is OPAQUE — it
  only ever comes from Bookends, and it **churns whenever an attachment is rebuilt**, so
  re-read every link after any re-attach.

  Do **not** harvest the page from AppleScript `link to displayed PDF`: that reports
  whichever page Bookends happens to be showing (page 0 for a freshly-opened PDF). It stays
  useful for exactly one thing — **after** firing a URL, reading back which PDF/page
  Bookends actually navigated to, which is the only accepted proof a link lands where it
  claims.

Note on passage-level links: Bookends can produce a true selection link via the
`link to selected text of displayed PDF` property, but only for an ACTIVE manual text
selection in the viewer — it cannot be fabricated from coordinates. So for automated
reports, the annotation-anchored page link (`pdf/…`) is the tightest reliably-resolvable
target; the persistent highlight supplies passage-level precision on that page.

## 3c. R-BOOKENDS-ATTACHMENT-PROVENANCE-01 — the first attachment must be the right paper

A citation link can be well-formed, carry a real attachmentID, resolve with no error, pass
observed navigation — **and still open the WRONG PAPER**, because the reference carries a
**stray first attachment** (a PDF belonging to another article: a bad download, a
mis-resolved DOI, an attach against the wrong record). Bookends displays *and annotates*
the FIRST attachment, so the highlight, the page and the link are all faithfully computed
against the wrong PDF. Link-level validation cannot see this — it validates the link, not
the paper.

**Before highlighting any source, verify its first attachment belongs to it:** list the
attachments (`bookends_get_attachment_paths`), read the first attachment's opening pages
(`bookends_get_pdf_content { id, mode: "text" }`), and confirm the reference's **title**
(and author/year) appears there. Run
`python3 scripts/validate_bookends_attachment.py --sources --group "<Topic> — <Subtopic>"`
as a fatal pre-ship gate. On a mismatch: re-attach the correct PDF **first**, never delete
the stray (detach/supersede it), and **re-read every deep link for that reference** — the
attachmentID has churned.

## 3d. R-BOOKENDS-VERIFY-EVERY-01 — check the artifact, not a cousin of it

Verify **every distinct link actually shipped, enumerated from the SHIPPED FILE** (the
finished HTML; the attached PDF's `/Annots` URIs). Not a sample. Not a representative. Not a
related-but-different object. **N distinct links in the file → N probes**, and the run's
report-back states both numbers. "I checked one and it worked" is evidence about that one
link and nothing else.

**A passing check on the wrong object is worse than no check** — it manufactures false
confidence and ships the bug with a certificate attached. Three real instances, one shape:

- **A cousin.** A hardcoded module-level constant sent **all 88 per-source `Bookends Group`
  links across 29 sources to the report's own `Reports` folder** instead of each source's
  subtopic group. The pre-ship check fired the **report's own** group link — which correctly
  points at `Reports` — watched it land on `Reports`, and reported "group links verified."
  True, and worthless: the 29 citation links were never touched.
- **The wrong failure mode.** "Pre-ship check passed: 0 bare-id links, 0 `/selection/` links."
  Also true, also irrelevant — the broken links were **well-formed `/group/` links pointing at
  the wrong group**, a form the check never looked at.
- **The link vs the paper** (§3c, R-BOOKENDS-ATTACHMENT-PROVENANCE-01). A link that was
  well-formed, carried a real attachmentID, resolved without error and **passed observed
  navigation** — while opening the **wrong paper**, because of a stray first attachment.

Before running any check, ask: **could this pass while the actual defect is present?** If yes,
fix the check first. Same family as R-BOOKENDS-ATTACHMENT-PROVENANCE-01.

Enforcement: `scripts/validate_bookends_links.py` enumerates from the surfaces and probes every
distinct URL, and takes `--group-map` (refID → the subtopic group the source was filed into at
step 5). It FAILS on the fingerprints of this bug: **every per-source group link identical**, or
a per-source group link pointing at the **`Reports`** folder.

## 3e. R-BOOKENDS-NO-APPLESCRIPT-GROUP-VERIFY-01 — AppleScript cannot verify group navigation

**BANNED by name: verifying a `bookends://…/group/…` link with AppleScript.** Bookends'
AppleScript dictionary exposes **no property for the currently-displayed group** — there is
nothing to ask. Reading **`selected publication items`** after firing a `/group/` URL returns a
**stale selection from before the call**: it reports success no matter what the URL did, or
whether it did anything at all. It cannot tell "right group", "wrong group" and "nothing
happened" apart. It is a silently-lying verification path.

**Required procedure — read the window:**

1. **Park** Bookends on a known state with a **known reference count** (e.g. `All`, showing N
   refs). Never park on the group under test.
2. **Fire** the URL.
3. **READ THE WINDOW — screenshot it** and read back the **displayed group** and the
   **displayed reference count**.
4. **Correct navigation MUST change both.** The displayed group must be the one the URL named,
   and **the ref count must change from N. The count change is the proof.** Unchanged group or
   unchanged count = FAIL.
5. Log the observation (parked group + count → observed group + count + screenshot path) and
   pass it to `scripts/validate_bookends_links.py --group-nav-log`. The validator will not pass
   a `/group/` link without it. **"Fired it, no alert appeared" is not a pass.**

**PDF / citation links are a different case and AppleScript verification of them is SOUND —
keep it.** After firing a `…/pdf/…` link, `name of displayed PDF` and `link to displayed PDF`
report the PDF *and page* Bookends actually navigated to; after a `…/ref/…` link,
`selected publication items` reports the reference it actually selected. Those readbacks **are
refreshed by the action**. Group links have no such property — **do not analogise from one to
the other.**

**General rule: exit codes are never evidence.** `open` returns **0 even when Bookends throws
an error dialog** and does nothing at all. Every verification must read back **observed state
that could only be true if the action had succeeded** — and the reader must first prove that
the state it reads is **refreshed by the action**, not cached/stale from before it.

**The null test — run it once per verification channel before trusting it.** Park on a
known-wrong state and **read the channel without firing anything.** If it still reports the
expected/"success" value, the channel is stale and verifies nothing. `selected publication
items` fails this test for group links; `link to displayed PDF` passes it for PDF links.

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

## 3b. Three links per reference — web citation + the named Group link + Bookends Citation
## (R-BOOKENDS-DUAL-LINK-01)

Every reference in the report (Summary/Source-type table, per-article cards, AND the
Vancouver References list — **anywhere a per-source link is emitted**) carries **three
distinct affordances**:

- **Citation → the article on the web.** Hyperlink the citation text (and the shown title)
  to the article online, built from the Bookends record in priority order:
  1. **DOI** → `https://doi.org/<doi>`
  2. else **PMID** → `https://pubmed.ncbi.nlm.nih.gov/<pmid>/`
  3. else the reference's **stored URL / publisher link** (the `url` field).

  Pull `doi`, `pmid`, and `url` from the record (e.g. `bookends_get_properties`). If none of
  the three exist, leave the citation as **plain text** (no dead link) and say so.
- **"· <group name>" → the source's subtopic group.** Labelled with the GROUP'S OWN NAME, never
  the generic string "Bookends Group" (**R-BOOKENDS-GROUP-LINK-LABEL-01**) — the reader must be
  able to see where the link goes without clicking it. The library-qualified group link
  `bookends://sonnysoftware.com/group/<LibraryName>/<URL-encoded group name>` (§3). Lands the
  reader among that report's sibling sources.
- **"· Bookends Citation" → that specific reference / its PDF.** The Bookends-generated PDF
  deep link `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>` (§3),
  read back from `link to displayed PDF` with the highlight's page substituted. The
  `…/selection/…` form is BANNED (R-BOOKENDS-PDF-DEEPLINK-02) — it throws "nil object".

Render all three so they are visually distinct (rule 6). Label the two Bookends links
with the **group's own name** and **exactly** `Bookends Citation` — never one ambiguous "Open in
Bookends". Deliver as styled clickable text (§3a). This applies identically in the
Summary table, the Part I cards, and the References list; the Academic Summary stays
plain-text / Word-ready. Example rendering:

```html
<strong><a href="https://doi.org/10.1007/xxxxx">Source title</a></strong>
 · <a href="bookends://sonnysoftware.com/group/Library1/Topic%20%E2%80%94%20Subtopic">Topic — Subtopic</a>
 · <a href="bookends://sonnysoftware.com/pdf/Library1/8721/1783717403/3">Bookends Citation</a>
```

## 3f. R-BOOKENDS-NARRATIVE-CITE-STYLE-01 — in-narrative citation style

The Part II narrative's in-text citations have a **named style**; `author-date` is the
**default**.

- **`author-date` (APA-like, DEFAULT)** — `(Jones et al, 2015)` (3+ authors),
  `(Jones & Smith, 2015)` (two), `(Jones, 2015)` (one); several works in one parenthesis are
  **semicolon-separated**; a narrative mention reads *"Jones et al (2015) found…"*.
- **`numeric-superscript` (AMA)** — numbered superscripts keyed to the reference list. Only on
  explicit request.

**Naming, so nobody re-litigates it:** AMA *is* the numbered/superscript system;
`(Jones et al, 2015)` is **author-date (APA-like)**, not AMA. If a user asks for "AMA inline
author-date", build **author-date** and label it that way.

**Both styles keep the deep links.** Each in-text citation is itself an `<a>` whose href is the
annotation-anchored `bookends://…/pdf/…` link for that source (§3). Style is presentation; the
deep link is the point of the report. Dead author-date text = failed run.

**The References list does not move.** Numbered, in citation order, **not alphabetized and not
renumbered**, each entry keeping its web citation link plus both Bookends links (Group =
the source's own subtopic group; Citation = its PDF deep link). The style option touches the
**narrative only**. The Academic Summary keeps its plain-text `(Author, Year)` citations.

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

---

## 3g. R-BOOKENDS-GROUP-LINK-LABEL-01 — the group link is labelled with the group's name

The anchor text of a `…/group/…` link is **the group's own name**, on every surface: the
per-source cards, the section headers, the Summary / Source-type table, and the References list.

| | |
|---|---|
| ✅ | `<a href="bookends://sonnysoftware.com/group/Library1/Topic%20%E2%80%94%20Subtopic">Topic — Subtopic</a>` |
| ✅ | `<a href="bookends://sonnysoftware.com/group/Library1/Topic%20%E2%80%94%20Subtopic">Subtopic</a>` |
| ⛔ | `<a href="…">Bookends Group</a>` / `Open Bookends Group` / `Open in Bookends` / `Group` |

Either the full project-qualified name or the bare subtopic name is fine — be consistent within a
report. Two reasons this is a rule and not a preference:

1. **Legibility.** The reader sees the destination without clicking.
2. **It surfaces the hardcoded-constant bug.** When every group link renders as the same generic
   `Bookends Group` string, a generator that points all of them at one group (see 3e) looks
   identical to a correct one. Named labels make that defect visible on the page.

This changes the group link's **text only**. The dual-link standard (R-BOOKENDS-DUAL-LINK-01) is
untouched: every source still carries its web citation link AND its `Bookends Citation` link
alongside the group-named link. `Bookends Citation` keeps its literal label — it targets one
specific reference, which has no short human-meaningful name.

## 3h. R-BOOKENDS-LIBRARY-MUST-BE-OPEN-01 — the closed-library false alarm

**A `bookends://` link resolves against Bookends' FRONT LIBRARY WINDOW.** With Bookends running
but **no library open**, macOS hands the URL over successfully and Bookends resolves it against
nothing. The link appears dead. It is not.

On 2026-07-14 this cost real time twice in one day: once presenting as the *"An error has
occurred: nil object"* dialog, once as a group link that silently did nothing. **Both were a
closed library.** Neither was a bad link.

**Check it first — background-only, one call, before touching the generator:**

```
mcp__bookends-mcp__bookends_libraries { action: "list" }
→ {"count": 0, "libraries": []}   ← NO LIBRARY OPEN. That is the bug.
```

**The name-based group form is CORRECT — verified against Bookends itself.** Selecting a group in
the sidebar and using **Edit → Copy Link** emits exactly:

```
bookends://sonnysoftware.com/group/<LibraryName>/<percent-encoded group name>
```

byte-for-byte the form this skill generates. There is no full-path variant, no `.bdb`-suffixed
variant, and no id-based variant to switch to. (There is also **no AppleScript group-link
property** — the dictionary exposes `link to displayed PDF`, but nothing for groups. Copy Link is
the only authority.)

**Corollary — the expensive one.** An agent that "fixes" a correct link because it assumed the
link was at fault makes things strictly worse: it burns a regeneration cycle, supersedes good
records, and leaves the real cause in place to recur. **Confirm the form against Copy Link before
editing anything.** If what you emit already matches Copy Link, the generator is not the bug.

**Static triage order, before firing any URL:**

1. Is a library open? (`bookends_libraries { action: "list" }`)
2. Are the per-source group links **distinct**? Extract every `/group/` link from the SHIPPED
   file. All identical, or all ending in `Reports` → the hardcoded-constant bug (3e). A real defect.
3. Do the decoded group names match the **live** Bookends group names, character for character?
   (`bookends_groups { action: "get" }`; em dash must be U+2014 on both sides, `%E2%80%94` in the URL.)

1 ✓, 2 ✓, 3 ✓ → **the links are correct and the failure is environmental.** Say so plainly. Do not
invent a code fix to look productive.

## 3i. R-BOOKENDS-LIBRARY-NAME-ON-REPORT-01 — name the target library, once, in the header

Every report says which Bookends library its links resolve in. The library name is *in* every
`bookends://` URL (`…/pdf/<Library>/…`, `…/group/<Library>/…`) but the reader only ever sees the
anchor text, so without a statement in the report a user with several libraries cannot tell which
one to open — and a link into a closed library fails silently (3h).

**Say it once, at document scope, in three places:**

- the **header / cross-navigation block** — `Bookends library: Library1`;
- the **how-to-open callout**, paired with the closed-library warning;
- the **provenance footer**, alongside the link counts.

**Do not repeat it per citation.** Every link in a report targets the same library, so putting the
name on 31 cards adds 31 copies of a constant and crowds the per-link labels that actually carry
information — the group's name (3g) and the `Bookends Citation` affordance (3b). Per-link library
naming is only warranted for a report drawing sources from **more than one library**, which this
skill's one-library-per-run filing makes impossible.

### Can a URL open a library? No — but Bookends may auto-open one.

**There is no `bookends://` command to open or switch a library.** The documented URL destinations
are: a reference, a group/folder, a PDF, a PDF page, PDF-selected text, a PDF annotation. No
library verb. **AppleScript has no `open library` either** — the dictionary offers `create library`
and nothing for opening an existing one.

The User Guide does, however, document an automatic behaviour, verbatim:

> "Clicking on a Bookends hypertext link in another app will launch Bookends, if it is not running,
> and navigate to the link. **If the destination is in a closed library, it will be automatically
> opened if it is listed in the File → Open → Recents menu.**"

Two things follow:

1. **The auto-open is conditional**, not guaranteed. The target library must be on the Recents list,
   whose length is capped in Settings → *Number of recent libraries shown*. A library that has aged
   off Recents will not auto-open and the link will fail silently — correct URL, no destination.
2. **It explains the intermittency.** A `bookends://` link fired at a Bookends with no library open
   sometimes navigates fine and sometimes does nothing. That is not a flaky URL scheme; it is
   whether the target library happened to be in Recents.

**Therefore: do not try to solve the closed-library problem at the link level.** There is no link
form that opens a library. Name the library in the report (3i) and warn the reader (3h).
