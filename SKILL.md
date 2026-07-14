---
name: bookends-research-skill
description: "Produce a Bookends-native, deep-linked, highlighted research report on any topic, parameterized so only the topic changes each run. Creates a Bookends group with subtopic child groups plus a Reports folder, retrieves sources (guidelines, systematic reviews, key studies) Bookends-first — via Bookends' search, identifier retrieval and PDF download, with candidate papers first enumerated by a ROUTINE Firecrawl Research / PubMed search per subtopic (verified PMIDs/DOIs), falling back to a Firecrawl fetch only when Bookends cannot attach — attaches full-text PDFs, writes one persistent highlight and page-accurate bookends:// deep link per source, and assembles ONE combined HTML report (highlighted deep-linked quotes, stance table, narrative synthesis, Vancouver references). Use whenever the user asks for a Bookends research report, deep-linked or highlighted literature review, evidence synthesis or annotated bibliography in Bookends, or says 'run the Bookends research skill' or 'bookends:// deep-linked quotes'. Depends on the Bookends MCP server that ships inside Bookends.app."
---

# Bookends Research Skill

This skill produces a deep-linked, highlighted Bookends research report, **parameterized
so that only the RESEARCH TOPIC changes from run to run.** Everything else — the pipeline,
the report structure, the link forms — is fixed. The citation list at the end is titled
**"References"** and is formatted in **Vancouver** style.

Every claim in the finished report is traceable: each verbatim quotation is a
hyperlink that opens the source PDF **in Bookends at the exact highlighted passage**
(page-accurate `bookends://` deep link), with a persistent highlight already written
into the PDF. The report fuses a **literature package** (executive summary, stance
table, per-article summary cards each embedding 1–3 highlighted, deep-linked quotes)
with an **academic narrative synthesis** (a navigable, multi-section argument whose
quotations deep-link to their highlights), closing with a **Word-ready Academic
Summary** and a **Vancouver References** list.

**By default everything is COMBINED into one HTML document.** Only split into
separate deliverables if the user explicitly asks for it.

---

## What you can use this for

The topic is the only variable, so this skill works for **any question that has a
literature** — clinical or not. Invoke it as **`Run the Bookends Research Skill on
<your question>`**. Ready examples:

- **Clinical evidence syntheses / treatment-efficacy reviews** — *"Is surgery effective
  for chronic low back pain?"*, *"Efficacy of epidural steroid injections for lumbar
  radiculopathy"*, *"Does physical therapy prevent recurrent ankle sprains?"*
- **Drug / therapy comparisons** — *"Suzetrigine vs opioids for acute pain"*, *"SGLT2
  inhibitors vs GLP-1 receptor agonists for CKD outcomes"*, *"DOACs vs warfarin in
  atrial fibrillation"*.
- **Prognosis / natural-history / life-expectancy questions** — *"Life expectancy after
  severe TBI with disorders of consciousness"*, *"Influence of level of nursing care on
  life expectancy after stroke"*, *"Natural history of untreated lumbar disc
  herniation"*.
- **Diagnosis / work-up reviews** — *"Work-up of secondary hypertension"*, *"Diagnostic
  accuracy of D-dimer for pulmonary embolism"*.
- **Complication / adverse-event profiles** — *"Adverse-event profile of long-term PPI
  use"*, *"Complication rates of lumbar fusion"*.
- **Standard-of-care questions** — *"Standard of care for diabetic foot ulcer
  management"*, *"Guideline-recommended management of sepsis"*.
- **Medical-legal / life-care-planning evidence packs & expert-report support** — build a
  deep-linked evidence pack whose quotes cite the exact source passage, ready to drop into
  an expert report or life care plan (e.g. *"Evidence for attendant-care needs after high
  cervical spinal cord injury"*).
- **Occupational, aviation, and toxicology medicine** — *"Return-to-work outcomes after
  rotator-cuff repair"*, *"Neurocognitive effects of chronic organic-solvent exposure"*,
  *"Cardiovascular fitness standards for commercial pilots"*.
- **Non-clinical scholarly topics** — any field with a literature: *"Effectiveness of
  congestion pricing on urban traffic"*, *"Seismic design standards for base-isolated
  buildings"*, *"Efficacy of active-learning methods in undergraduate STEM"*.
- **Annotated bibliographies / literature reviews** where every quote must link to the
  exact passage in its source — the deep-linked, highlighted output is built for exactly
  this.

Whatever the question, the deliverable is the same: one combined HTML report with an
executive summary, a stance/source-type table, per-article cards with highlighted,
deep-linked verbatim quotes, a navigable narrative synthesis, a Word-ready Academic
Summary, and a Vancouver References list — saved into Bookends and to your iCloud
`RESEARCH_DIR`.

---

## Configuration

`RESEARCH_DIR` — where the HTML report is written to disk (in addition to Bookends).
It is defined **once, here**, and is the only path setting in the skill. **Never
hardcode a username or an absolute personal path anywhere** — resolve everything from
`$HOME` so the skill works for any macOS user and is safe to share publicly.

- **Default:**
  `RESEARCH_DIR = "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Research"`
  — the iCloud Drive root resolved generically from the current user's home directory
  (`$HOME/Library/Mobile Documents/com~apple~CloudDocs/`), then a `Research` subfolder.
  When the current user runs the skill this resolves to their own iCloud automatically;
  no personal path is baked in.
- **Override:** any user may set `RESEARCH_DIR` to their own folder name/path (e.g. a
  differently-named iCloud folder, or a non-iCloud location).
- **Fallback:** if iCloud Drive is **not** present at
  `$HOME/Library/Mobile Documents/com~apple~CloudDocs/`, do not assume any specific
  account — either use a documented local default (`$HOME/Research`) or ask the user
  where to save. Always report the path actually used.

The finished report's iCloud HTML copy is always written **inside a `Bookends Research`
subfolder** of `RESEARCH_DIR` (created if missing):
`<RESEARCH_DIR>/Bookends Research/<Topic> — Deep-Linked Report/<Topic> — Deep-Linked Report (AI) <date>.html`.

---

## Home is Bookends (always)

This skill is Bookends-native. The PDFs live as **attachments on Bookends
references**; deep links are **`bookends://…` page links**. Drive Bookends through its
MCP (`mcp__bookends-mcp__*`) — the MCP server bundled inside Bookends.app — **never**
through screen automation.

**Dependencies.**

```
pip install pyobjc-framework-Quartz    # so the validator can SEE a Bookends modal alert
pip install pypdf                      # link-annotation audit of the rendered report PDF
```

Plus **Google Chrome** (headless), used to render the finished HTML report to a
link-preserving PDF.

**No PDF library is used to highlight or to find a page. There is no PyMuPDF /
`fitz` dependency anywhere in this skill — do not reintroduce one.** The highlight,
the page, and the deep link all come from the **Bookends MCP itself**:

- `mcp__bookends-mcp__bookends_annotate_pdf` (**always `mode: "exact"`**) writes the
  persistent highlight into the attached PDF, in place;
- `mcp__bookends-mcp__bookends_get_pdf_content { mode: "annotations" }` reads that
  annotation back and returns its **annotation-anchored, page-accurate `bookends://`
  deep link** in the annotation's `link` field.

The deep link is therefore **generated by Bookends**, anchored to the annotation, and
never string-templated. Page-accuracy is verified by observed navigation, not assumed.

---

## Reading the deep links (Bookends link scheme + how to follow them)

Every highlighted quote is a `bookends://` link to its source PDF. **The `bookends://`
URL scheme works perfectly INSIDE Bookends** — clicking such a link that sits in a
Bookends field (Notes or User1–User4, which hold styled text) opens the PDF at the right
place. Two requirements make this reliable:

1. **Use Bookends' supported link forms (never a fabricated one).** Bookends resolves:
   - a **GROUP link** → `bookends://sonnysoftware.com/group/<LibraryName>/<URL-encoded group name>`,
     pointing at the group that holds that source. **NEVER the bare
     `bookends://sonnysoftware.com/<refID>` form** — it drops the reader into the full
     marked-library list;
   - a **page-accurate PDF deep link** →
     `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>` — the ONLY
     supported form for a citation/quote link. It opens **that specific reference and its
     attached PDF** at `page0` (a 0-based page index). `<attachmentID>` is an opaque
     per-attachment identifier that CANNOT be derived, guessed or templated — it must be
     read back from Bookends itself.

   **Every citation in the report carries BOTH a Group link and a Citation link — see
   R-BOOKENDS-DUAL-LINK-01 below.**

   ### R-BOOKENDS-PDF-DEEPLINK-02 (hard rule — supersedes the old selection form)

   **The `…/selection/<Library>/<refID>/…` form is BANNED. Never emit it, under any
   circumstance.** Bookends does not
   implement a `selection` route with a nil (`0`) attachment/annotation id: it dereferences
   a nil object and throws the modal **"An error has occurred: nil object."** dialog.

   **Citation links must be GENERATED BY BOOKENDS, never string-templated.** Take each one
   from the **annotation** the skill just wrote — the Bookends MCP hands back an
   annotation-anchored, page-accurate deep link:

   ```
   mcp__bookends-mcp__bookends_annotate_pdf {
     bookends_reference_id: "<refID>", annotation: "highlight",
     mode: "exact",            # ALWAYS. never "semantic" — see below
     query: "<verbatim sentence from the PDF>",
     idempotent: true          # default; a re-run reuses the highlight, adds no duplicate
   }
   -> { annotations_created, annotations_reused, disk_verified, … }

   mcp__bookends-mcp__bookends_get_pdf_content { id: "<refID>", mode: "annotations" }
   -> { annotations: [ { page, text, link: "bookends://sonnysoftware.com/pdf/…", … } ] }
   ```

   The annotation's `link` **is** the citation/quote link: it opens that reference's PDF at
   the highlighted passage. Build a `refID → deepLink` map from the annotation readback
   BEFORE emitting any HTML. A reference for which no annotation can be written has no usable
   PDF attachment (or a wrong quote — see the guard below): fix it, or drop the citation link.
   **Do not fabricate a URL.** The `bookends://sonnysoftware.com/<refID>` bare form remains
   banned (R-BOOKENDS-DUAL-LINK-01). Run `scripts/validate_bookends_links.py` before shipping;
   it fails the build on any selection-form, bare-id, zero-attachmentID or out-of-range-page
   link, and on any card missing either of its two links.

   ### R-BOOKENDS-EXACT-ONLY-01 (hard rule — `mode: "exact"`, never `semantic`)

   **`bookends_annotate_pdf` is called with `mode: "exact"` on EVERY call, without
   exception.** Note that the tool's own DEFAULT is `semantic` — so `mode` must be passed
   explicitly every single time; omitting it silently gets you the wrong mode.

   **`semantic` is UNUSABLE for this skill and must never be turned on.** Tested: a single
   paraphrased sentence produced **20 highlights spread across 11 pages** — it highlights
   whatever blocks it thinks are related, so the PDF is defaced and the "page" the link
   anchors to is meaningless. `regex` and `key_points` are likewise not used. If someone
   later proposes enabling `semantic` "just as a fallback", the answer is no: it is not a
   looser match, it is a different (and wrong) operation.

   **FABRICATED-QUOTE GUARD — `exact` failing is a FEATURE, not a bug.** `exact` writes
   nothing when the text is not present verbatim in the PDF (and writes nothing on an
   ambiguous match). **A quote that fails to match is a quote that is WRONG** — paraphrased,
   mis-transcribed, or hallucinated. The correct response is to go back to the PDF and take
   a genuinely verbatim sentence, **never** to loosen the mode. Falling back to `semantic`
   (or to any fuzzy matcher) would turn the skill's one automatic defense against a
   fabricated quotation into a rubber stamp. Do not do it.

   Practical notes that save reruns: the matcher already tolerates line breaks and
   end-of-line hyphenation, so a sentence that spans a line break still matches. If a
   sentence genuinely will not match, it is not in the PDF — pick another verbatim sentence
   that makes the same point. If the same sentence appears more than once, disambiguate with
   `page` (1-based) and/or `occurrence`, not with a looser mode.

   ### Two Bookends-MCP quirks to know (neither is a blocker)

   - **No `.bak` is written.** Annotations are applied **in place**, so there is **no
     rollback** if a write goes wrong. `disk_verified` in the response confirms the saved
     file; `idempotent: true` (the default) means a repeat call reuses the existing
     annotation (`annotations_created: 0, annotations_reused: 1`) and does not even rewrite
     the file. Do not rely on a backup copy existing — there isn't one.
   - **`bookends_get_pdf_content` echoes highlight text with the line-break hyphen
     retained** (e.g. `"first mobi-lized"`). The *matching* is correct; only the echoed text
     is un-dehyphenated. So **quote from your own source string**, not from the annotation
     echo. If you ever must quote back from the annotation list, strip the join hyphen with
     a small regex — `re.sub(r"(\w)-\s+(\w)", r"\1\2", text)` — and **do NOT reintroduce a
     PDF library to solve this.**

2. **Insert the link as STYLED (rich) text with a live hyperlink.** A `bookends://` link is
   clickable only if it lands in the field as styled text carrying the live URL. When
   pasting a link into a Bookends field, use a **normal (styled) Paste — `⌘V`** — **NOT
   "Paste and Match Style"** (which strips the hyperlink to dead plain text). If your `⌘V`
   is remapped to Paste-and-Match-Style in Bookends → Settings, use **Edit → Paste** or
   **⇧⌥⌘V** to do a plain styled paste. (Bookends developer tutorial:
   https://www.youtube.com/watch?v=GCp8R_tUuD8 ; corroborated by the Bookends User Guide,
   "Hypertext links in reference fields": *only Paste inserts a live hypertext link, not
   Paste And Match Style*.) Step 7 delivers the report's links into Bookends this way.

**Browser path (also works, keep it).** You can still follow any link by opening the HTML
report in a web browser — the Bookends attachment is now a hyperlink-preserving PDF, so
open the iCloud HTML copy in Safari/Chrome. The browser hands the
`bookends://` scheme to macOS, which routes it to Bookends. Ordinary web links (PMC /
open-access URLs) work everywhere.

Because of this, **every generated report must carry a short version of this note near
the top** — see the "How to open the deep links" line in step 6.

---

## Interpreting the invocation — parse, then expand

Treat the user request as a terse one-liner to parse and auto-expand. The user
normally types ONE line, e.g. `Run the Bookends Research Skill on Adhesive Capsulitis`
or `Bookends deep-link report on Efficacy of Epidural Steroid Injections`.

**Parse ONE thing: the TOPIC.** Everything else is fixed by this skill.

- **TOPIC / question** — the subject of the report. This is the only variable. If no
  topic is given, that is the single field you cannot guess — ask for it. Otherwise
  **do not ask permission to proceed**; run the whole pipeline end-to-end.
- **SOURCE DISCOVERY is Firecrawl-PubMed-first (ROUTINE); RETRIEVAL is Bookends-first.**
  For EVERY report, begin by running a **Firecrawl Research / PubMed search per subtopic**
  (`mcp__mcp-server-firecrawl__firecrawl_research_search_papers` / `_related_papers`, and/or
  the PubMed MCP `search_articles` -> `get_article_metadata`) to enumerate candidate
  peer-reviewed papers and capture each one's **PMID / DOI / exact article URL**. This
  discovery step is ROUTINE for every run, NOT merely a fallback for when Bookends can't
  resolve an identifier. THEN retrieve each discovered paper **Bookends-first** (identifier
  add + native PDF download); reach for a Firecrawl fetch only when Bookends cannot attach
  the PDF (see step 2). **SOURCE IS KING:** every citation/URL must be the exact verified
  article link (never a bare domain or section page), and you must **NEVER fabricate a
  quote** for a paper whose abstract/full text cannot be retrieved — drop it and note it.
  Honor an explicitly named alternative if the user gives one.
- **STORAGE** is always **Bookends** (plus the iCloud copy in step 7). Non-negotiable
  for this skill.
- If the user names a specific reference count, honor it; otherwise target **≥25**
  quality sources when the literature supports it (see step 2).

Having parsed the TOPIC, execute the numbered **End-to-end workflow** below in order.

---

## Standing rules (honor on every run)

- **Create-new, never-trash.** Never delete or trash any reference, attachment,
  group, or prior report. When regenerating, save the new report as a new record and
  leave the prior one in place.
- **Label = AI content.** The finished report record carries the user's **AI-content
  label** (label 3 / "AI Content"). Never tag the report.
- **Repurpose-in-place on a bad DOI.** If a DOI/PMID resolves to the WRONG paper,
  **repurpose that record in place** — overwrite its fields with the correct metadata
  and re-attach the correct PDF. **Never trash it** and create a fresh one; editing in
  place avoids orphaned attachments and preserves ids/links.
- **Bookends AppleScript bridge quirks (bake these in).** The Bookends AppleScript
  bridge **rejects the `volume` field** on write and **rejects any value containing
  parentheses**. Therefore: store the issue number in a parenthesis-free way (e.g. put
  `25` and `2` where the model expects `25(2)`, or place the issue in a field that
  accepts it) and **never** write a value that contains `(` or `)` through the bridge.
  The **citations in the report itself must still render correctly** — reconstruct the
  full `volume(issue)` in the report text and in the Vancouver References list from the
  stored parts; only the write-through-the-bridge value is parenthesis-free. Prefer the
  dedicated `bookends_set_field` / `bookends_quick_add` tools over raw AppleScript; fall
  back to `bookends_applescript_run` only when no dedicated tool fits, and keep every
  written value parenthesis-free.
- **Idempotent + resumable.** Every step is idempotent — on a transient error retry the
  failed item; never start over and never create duplicates (look a record up by
  DOI/PMID/title before adding).

---

## The six format rules (canonical — reproduce exactly every run)

The report MUST follow these six rules exactly.

1. **Per-article summaries carry 1–3 highlighted, hyperlinked quotes woven INLINE.**
   Each article's summary card embeds 1–3 exact verbatim quotes from *that* article.
   Each quote is (a) highlighted in the attached PDF by `bookends_annotate_pdf`
   (`mode: "exact"`; the call is idempotent — an identical highlight is reused, never
   duplicated) and (b) rendered as an active hyperlink to the **annotation-anchored**
   `bookends://` deep link that `bookends_get_pdf_content` returns for that highlight. **Weave each quoted phrase
   directly into the running sentence** so reading the paragraph carries you through
   the quote (e.g. *…the panel concluded the condition is "a compartment syndrome"
   requiring emergent decompression [link], which is why…*). **Never** stack quotes as
   detached block-quotes. This inline-weave rule applies to BOTH the Part I summary
   cards and the Part II narrative. Style the span as both a highlight (light
   background) and a bold link.
2. **In-report source links are NATIVE `bookends://` links (Bookends' supported forms),
   never a web proxy, and always the DUAL PAIR.** Link every source inside the report with
   **both** a `…/group/<Library>/<encoded group>` link (labeled `Bookends Group`) **and** a
   `…/pdf/<Library>/<refID>/<attachmentID>/<page0>` link (labeled `Bookends Citation`) — see
   R-BOOKENDS-DUAL-LINK-01 (rule 6). **The bare reference-id form
   `bookends://sonnysoftware.com/<refID>` is BANNED** (it dumps the reader into the whole
   marked library). The report opens on the Mac, so these native links resolve. Web-only
   sources → the article URL (e.g. PMC).
3. **Source links are typographically obvious.** Render every link-to-source
   (`bookends://`, PMC / open-access URL) **bold** and visibly link-styled (color +
   underline). Apply consistently to inline quote links, per-article citation links,
   and the summary table.
4. **Close with a Word-ready "Academic Summary," then a "References" list.** The
   **Academic Summary** is a high-level but detailed narrative that synthesizes ALL
   positions (supportive, equivocal, and not-supportive findings across every article)
   in flowing scholarly prose, using **in-text parenthetical author–year citations** as
   **plain text — NOT hyperlinks** (so nothing breaks when pasted into Microsoft Word).
   It must be clean Rich Text (normal paragraphs/headings, plain bold/italic).
   **Immediately after it, include a section titled `References` (NOT "Works Cited")
   formatted in Vancouver style** — numbered, in citation order. Per **rule 6**, each References entry
   carries the web citation link (DOI → PMID → stored URL) **plus BOTH Bookends links —
   "· Bookends Group · Bookends Citation"** (R-BOOKENDS-DUAL-LINK-01). The **Academic Summary
   above stays plain text** (Word-ready); only the References list is linked.
5. **The narrative synthesis is internally navigable.** Open Part II with a short table
   of contents whose items are **internal in-document links** (`<a href="#sec-N">`) to
   numbered sections, each carrying a **stable anchor id** (`<h2 id="sec-N">N. …</h2>`).
   These `#sec-N` links live only in the narrative — distinct from the external quote
   deep links (rule 1) and the native source links (rule 2). Do **not** put internal
   section links in the Academic Summary or References; the Academic Summary stays Word-ready plain text, while the References list carries only the rule-6 links (web citation + Bookends Group + Bookends Citation), not `#sec-N` anchors.

6. **R-BOOKENDS-DUAL-LINK-01 — every citation carries THREE affordances: a web citation
   link plus TWO clearly-labeled Bookends links.** The single ambiguous "Open in Bookends"
   tag is **RETIRED** (user request, 2026-07-11). In BOTH the Part I per-article cards, the
   Summary / Source-type table, and the References (Vancouver) list — **anywhere a
   per-source link is emitted** — render each source with:

   - **(a) The citation text / article title hyperlinked to the article on the WEB** — a
     click opens the paper online. Build the URL from the Bookends record in priority order:
     **DOI → `https://doi.org/<doi>`**, else **PMID →
     `https://pubmed.ncbi.nlm.nih.gov/<pmid>/`**, else the reference's **stored URL /
     publisher link** (`url` field). Pull `doi` / `pmid` / `url` via
     `bookends_get_properties`. If the reference has NO DOI, PMID, or URL, leave the
     citation as **plain text (no dead link)** — but the two Bookends links below are still
     MANDATORY.
   - **(b) The GROUP link — labelled with the group's OWN NAME**
     (**R-BOOKENDS-GROUP-LINK-LABEL-01**, see below) → the **library-qualified GROUP link**
     `bookends://sonnysoftware.com/group/<LibraryName>/<URL-encoded group name>` for the
     **subtopic child group that actually holds that source**. Lands the reader among that
     report's sibling sources. `<LibraryName>` is REQUIRED (e.g. `Library1`); percent-encode
     the group name (space→`%20`, em dash “—”→`%E2%80%94`, `&`→`%26`). The anchor **text** is
     the subtopic group's name — never the generic string `Bookends Group`, `Open Bookends
     Group`, or `Open in Bookends`.
   - **(c) A link labeled exactly `Bookends Citation`** → a link that opens **THAT SPECIFIC
     reference / its PDF**, never the whole library. It MUST be the Bookends-generated PDF
     deep link `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>`,
     read back from Bookends via the AppleScript `link to displayed PDF` property
     (R-BOOKENDS-PDF-DEEPLINK-02). **Never string-template a citation URL, and never emit the
     `…/selection/…` form** — Bookends has no such route and throws
     "An error has occurred: nil object." The same Bookends-generated `/pdf/` URL is used for
     the quote links inside the card.

   **Render them as a visibly distinguishable trio**, e.g.:

   ```html
   <strong><a href="https://doi.org/10.xxxx/yyy">Source title</a></strong>
   <span class="be-links"> · <a class="be-group" href="bookends://sonnysoftware.com/group/Library1/Topic%20%E2%80%94%20Subtopic">Topic — Subtopic</a>
   · <a class="be-cite" href="bookends://sonnysoftware.com/pdf/Library1/8721/1783717403/2">Bookends Citation</a></span>
   ```

   So: **citation → the article's web page; the group-named link → the subtopic group;
   "Bookends Citation" → that reference/PDF itself.** The two Bookends links must be
   distinguishable **at a glance** — never collapsed into one ambiguous "Open in Bookends".
   The group link is identifiable *by its own name*: the reader can see where it goes
   without clicking it (R-BOOKENDS-GROUP-LINK-LABEL-01).
   Style all links per rule 3. **The bare reference-id form
   `bookends://sonnysoftware.com/<id>` remains BANNED for every link** (see the standing
   rule and the pre-ship check).

   ### R-BOOKENDS-GROUP-LINK-LABEL-01 (hard rule — label the group link with the group's name)

   **A group link's anchor text is the GROUP'S OWN NAME.** Never a generic string.

   - ✅ `Rib Fractures & Chest Wall` · ✅ `Topic — Rib Fractures and Chest Wall`
   - ⛔ `Bookends Group` · ⛔ `Open Bookends Group` · ⛔ `Open in Bookends` · ⛔ `Group`

   Either the **full project-qualified group name** (`Topic — Subtopic`) or the **subtopic
   portion alone** (`Subtopic`) is acceptable — pick one and use it consistently through the
   report. The point of the rule is that **a reader can see where the link goes without
   clicking it**, and can tell two different group links apart on sight. A page full of
   identical `Bookends Group` labels hides exactly the bug R-BOOKENDS-VERIFY-EVERY-01 exists
   to catch: every source's group link silently pointing at the same group.

   **Applies on every surface** — the per-source cards, the section headers, the Summary /
   Source-type table, and the References (Vancouver) list. It changes the group link's
   **TEXT only**: the dual-link standard is untouched, so every source still carries BOTH its
   web citation link AND its `Bookends Citation` link alongside the group-named link.

   The `Bookends Citation` link keeps its literal label — it points at one specific reference,
   for which there is no short human-meaningful name, and the contrast between a *named* group
   link and a *labelled* citation link is what makes the pair readable at a glance.

---

## R-BOOKENDS-NARRATIVE-CITE-STYLE-01 — in-narrative citation style (a named, stated option)

The **in-text citations inside the Part II Scholarly Synthesis** have a **named style**. Two
are defined; **`author-date` is the DEFAULT.** State which one a run used.

**Terminology — get this right, it is routinely conflated.** People often ask for "AMA style"
while describing `(Jones et al, 2015)`. Those are **two different systems**:

- **AMA** = **numbered / superscript** citations keyed to a numbered reference list
  (`…a compartment syndrome.¹²`). Nothing parenthetical, no author, no year in the body.
- **author-date** = the **APA-like** parenthetical form `(Jones et al, 2015)`.

`(Jones et al, 2015)` is **author-date (APA-like)**, **not AMA**. When a user asks for "AMA
with inline author-date citations", implement **author-date** and label it `author-date` in
the run's report-back. Do not argue the naming — just do not mislabel it in the skill.

### Style `author-date` (DEFAULT — APA-like parenthetical)

- **Three or more authors:** `(Jones et al, 2015)`
- **Two authors:** `(Jones & Smith, 2015)`
- **One author:** `(Jones, 2015)`
- **Multiple works in one parenthesis:** separated by **semicolons** —
  `(Jones et al, 2015; Smith & Patel, 2019; Okafor, 2021)`
- **Narrative mention** (author as the sentence's subject) reads naturally, with only the year
  parenthesised: *"Jones et al (2015) found …"*, *"Jones & Smith (2015) reported …"*
- No comma before the ampersand; no period after "et al" (`et al, 2015`, as written here).

### Style `numeric-superscript` (AMA — the prior behavior, still available on request)

Numbered superscripts in citation order, keyed to the References list. Use only when the user
explicitly asks for numbered/superscript/AMA citations.

### Invariants that hold under BOTH styles (non-negotiable)

- **Every in-text citation stays a LIVE HYPERLINK to its highlighted passage** — the
  annotation-anchored `bookends://…/pdf/<Library>/<refID>/<attachmentID>/<page0>` deep link
  (R-BOOKENDS-PDF-DEEPLINK-02). **Changing the citation style must not cost the deep link.**
  The `(Jones et al, 2015)` text itself is the anchor. A narrative whose author-date citations
  are dead text is a FAILED run, however correct the style looks.
- **The end-of-report References list DOES NOT CHANGE with the style.** It stays exactly as
  the skill already builds it: **numbered, in citation order — NOT alphabetized, NOT reordered,
  NOT renumbered** — each entry carrying its **web citation link** plus **BOTH** Bookends links
  (`· Bookends Group · Bookends Citation`, R-BOOKENDS-DUAL-LINK-01), with the Group link
  pointing at **that source's own subtopic group**, never the Reports folder
  (R-BOOKENDS-VERIFY-EVERY-01). **The style option governs the in-narrative citations ONLY.**
- **The Academic Summary is unaffected**: it keeps its plain-text, Word-ready
  `(Author, Year)` citations with **no hyperlinks** (format rule 4).
- Inline **quotes** keep their rule-1 treatment (highlighted span, woven into the sentence,
  bold link to the exact-passage deep link). An author-date citation may sit alongside the
  quote link; it does not replace it.

---

## End-to-end workflow

Do these in order. Idempotent and resumable throughout.

### 1. Create the Bookends group + topic-appropriate subtopic child groups

Create a **NEW Bookends group named for the topic**, e.g. `<Topic> — Deep-Linked
Report`. Inside it, create **subtopic child groups that are natural for THIS topic** —
derive them from the topic's own structure.
**Always include a `Reports` child group** (the finished report is filed there).

**Derive the subtopics from the topic.** Look at how the literature on the topic is
actually organized and mirror it. Produce the natural breakdown for the topic at hand
(typically some mix of *Etiology/Pathophysiology*,
*Diagnosis/Assessment*, one or more *Treatment/Management* buckets split by the axis
that matters for that topic, *Special populations / subtypes*, *Prognosis / Outcomes*,
plus **Reports**). Aim for ~4–8 subtopics.

**Bookends group mechanics (do not skip):**
- Create with `mcp__bookends-mcp__bookends_groups { action: "create", name, parent }`.
- **Bookends group names are GLOBALLY UNIQUE.** A bare subtopic name like `Diagnosis`
  or `Reports` will collide with another project's group and raise a
  global-unique-name error. **Project-qualify every name**, e.g.
  `<Topic> — Diagnosis`, `<Topic> — Reports`, so it is unique across the whole library.
- Create the parent group first, then each child with `parent` set to the parent's
  unique name. **Verify real nesting/containment** afterwards with
  `bookends_groups { action: "get" }` — confirm each child actually reports the parent
  as its container (a flat set of same-named groups is a failure; fix it before moving
  on).
- Record each group's id.

### 2. Discover & retrieve authoritative sources — Firecrawl-PubMed discovery (routine), then Bookends-first retrieval

Assemble a stance-balanced set of authoritative sources on the topic — **clinical
practice guidelines, systematic reviews / meta-analyses, and key primary studies** —
spanning supportive, equivocal, and critical findings. **Target ≥25 references** when
that many quality sources exist; favor reviews, meta-analyses, and guidelines first.
Gather fewer only when the literature genuinely does not support 25 — and say so
explicitly. Honor an explicit user count if given.

**Retrieval order is Bookends-first, per article.** Bookends can itself search the
literature databases and download full-text PDFs, so use it as the PRIMARY retrieval
engine and reach for Firecrawl only when Bookends comes up empty. For EACH candidate
article, try the Bookends path first; only if it fails do you fall back to Firecrawl.
**Log which path each article came through** (Bookends vs Firecrawl-fallback) and carry
that provenance through the run so a completed run is auditable (surface the tally in
the step-8 report-back).

**Step 0 — ROUTINE Firecrawl-PubMed discovery (do this FIRST on every run).** Before
touching Bookends, enumerate the candidate literature per subtopic with
`mcp__mcp-server-firecrawl__firecrawl_research_search_papers` (+ `_related_papers`) and/or
the **PubMed MCP** (`search_articles` -> `get_article_metadata`). For each candidate capture
its **PMID / DOI / exact article URL** and verify it resolves to the real article page
(never a bare domain or section page). This produces an auditable, stance-balanced candidate
set — reliably surfacing the guideline / RCT / systematic-review anchors that a Bookends-only
identifier resolver frequently cannot pull. Discovery is ROUTINE, not a fallback. Only after
this step do you retrieve the papers, per A below. **Never fabricate a quote for a paper you
cannot actually retrieve — drop it and say so.**

**A. PRIMARY — retrieve via Bookends itself.** Use Bookends' own, verified retrieval
features (confirmed against the Bookends User Guide + AppleScript dictionary; see
`references/bookends.md` §1):

1. **Identifier-based add + metadata.** When you have (or can find) a DOI / PMID / arXiv
   id, add the reference with `mcp__bookends-mcp__bookends_quick_add` — it pulls the
   metadata (and full text where Bookends can retrieve it).
2. **Bookends online search.** Bookends searches literature databases directly — built-in
   **PubMed, Google Scholar, Semantic Scholar, Google Books, the Library of Congress,
   JSTOR, arXiv**, plus Z39.50/SRU catalogs — via its Online Search / Bookends Browser.
   Use it to locate an article and import its reference. Bookends' **"Attempt PDF
   download"** option (equivalent to *Refs → Get PDF → From Internet (If Available)*)
   auto-downloads and attaches the PDF on import when the article is open-access or your
   IP has access.
3. **Automatic PDF download for a reference.** Once a reference carries a PMID / DOI /
   arXiv id (or a JSTOR URL), have Bookends fetch and attach the full-text PDF with its
   native **`download pdfs`** command — the scriptable form of *Get PDF → From Internet
   (If Available)*. Prefer `mcp__bookends-mcp__bookends_add_pdf` with the reference's
   identifier / a direct PDF URL; when only the AppleScript command fits, run
   `download pdfs {publication item id "<id>"}` via
   `mcp__bookends-mcp__bookends_applescript_run` (see `references/bookends.md` §1).
   Confirm the attachment landed with `mcp__bookends-mcp__bookends_get_attachment_paths`.
4. **Find & attach a local PDF / folder.** If the PDF is already on disk, attach it with
   `mcp__bookends-mcp__bookends_add_pdf { items:[{ id, path }] }`, or bulk-import
   a folder with `mcp__bookends-mcp__bookends_import_pdf_folder` (resolve any
   `metadata_required` items by DOI/PMID/ISBN/arXiv through `bookends_quick_add`, per the
   bookends-mcp guidance).

An article counts as **Bookends-retrieved** when Bookends located the reference **and**
attached a usable PDF (or a deliberately-flagged abstract-only PDF) through the features
above.

**B. ATTACH-FALLBACK — Firecrawl fetch, only when Bookends cannot attach the discovered article.** Fall back
**per article**, only when the Bookends path above fails for that article — i.e. Bookends
returns no match, cannot resolve the DOI/PMID, or cannot retrieve a usable PDF. Then use
the **`firecrawl-research-index`** skill / `mcp__mcp-server-firecrawl__firecrawl_research_*`
(and/or PubMed) to find and fetch the article, and import the result **back into
Bookends** — create/locate the reference and attach the fetched PDF exactly as in step 3.
Mark the article's provenance **Firecrawl-fallback**. Reserve Firecrawl for this fallback
role and for genuinely external-website research (it costs money and is less private than
the native Bookends path).

Whichever path an article comes through, its PDF ends up **attached to a Bookends
reference** — that is the invariant the rest of the pipeline depends on.

### 3. Finalize each reference + PDF in Bookends (de-dup, attach, log provenance)

Every source from step 2 — whether it came through the Bookends path or the
Firecrawl-fallback — must end up as a **Bookends reference with its PDF attached**. For
each source:
- **De-duplicate first:** `mcp__bookends-mcp__bookends_search` by DOI/PMID/title, so a
  re-run never creates a duplicate reference.
- **Ensure the reference exists with metadata:** `mcp__bookends-mcp__bookends_quick_add`
  (by **DOI/PMID/arXiv**) pulls metadata (and full text where Bookends can retrieve it).
- **Ensure a PDF is attached:** a Bookends-path article already has its PDF (step 2A);
  for a Firecrawl-fallback article, attach the fetched PDF with
  `mcp__bookends-mcp__bookends_add_pdf { items:[{ id, path }] }` (local files, direct PDF
  URLs, or identifier-based retrieval). Verify with
  `mcp__bookends-mcp__bookends_get_attachment_paths`.
- **No accessible full text (either path)?** Render the abstract to a one-page PDF
  yourself — write the citation + abstract as HTML and print it with headless Chrome
  (same converter as the report, see step 7) — attach that with
  `mcp__bookends-mcp__bookends_add_pdf`, and **flag it abstract-only** in the report (its
  quote is an abstract key sentence, not a full-text deep link).
- **Record each reference's Bookends `id` and its retrieval provenance** (Bookends vs
  Firecrawl-fallback) — the id is the locator for highlighting, linking, and filing; the
  provenance feeds the step-8 audit tally. Respect the AppleScript-bridge quirks in
  *Standing rules* when writing any field (no `volume` write, no parentheses).

### 4. One persistent highlight + page-accurate deep link per source

**Before you highlight anything, confirm the PDF you are about to highlight is the RIGHT
paper** — see R-BOOKENDS-ATTACHMENT-PROVENANCE-01 in the pre-ship checks. A reference can
carry a **stray first attachment** (a PDF that belongs to some other paper). Bookends
displays and annotates the FIRST attachment by default, so a stray one yields a link that
is perfectly well-formed, resolves without error, and **opens the wrong paper**. Verify
first, highlight second.

For each source, pick a **verbatim, contiguous** key sentence (full-text sentence for
full-text PDFs; the abstract's key sentence for abstract-only). Then, per quote:

```
1) mcp__bookends-mcp__bookends_annotate_pdf {
     bookends_reference_id: "<refID>",
     annotation: "highlight",
     mode: "exact",          # MANDATORY on every call — the tool's default is "semantic"
     query: "<the verbatim sentence, copied from the PDF>",
     idempotent: true        # default: a repeat run reuses the highlight, no duplicates
   }
   -> { annotations_created, annotations_reused, disk_verified, page, … }

2) mcp__bookends-mcp__bookends_get_pdf_content { id: "<refID>", mode: "annotations" }
   -> annotations[]: each with its page and its annotation-anchored deep link (`link`)
```

The highlight is written **into the attached PDF, in place** (no `.bak`, no rollback), and
the deep link that comes back is **anchored to that annotation** and page-accurate. That
link is the quote link AND the `Bookends Citation` link — **never** string-template a
citation URL. The `…/selection/…` form and the bare `…/<refID>` form are both BANNED
(R-BOOKENDS-PDF-DEEPLINK-02): Bookends has no `selection` route (it throws "nil object"),
and the bare form opens the whole library.

- **Quote links AND `Bookends Citation` links → the annotation-anchored deep link** read
  back from `bookends_get_pdf_content`. Build a `refID → link` map from the annotation
  readback before emitting any HTML.
- **`Bookends Group` links → the library-qualified group link** for the source's subtopic
  child group (see rule 6). Obtain `<LibraryName>` from AppleScript
  `name of front library window` (minus the `.bdb` extension).

**Never** emit the bare reference-id form `bookends://sonnysoftware.com/<refID>`.

**If `exact` does not match, the QUOTE is wrong — not the mode.** `exact` writes nothing
when the text is not verbatim (or is ambiguous). That is the fabricated-quote guard doing
its job: go back to the PDF and take a real sentence. **Never fall back to `mode:
"semantic"`** (one paraphrase produced 20 highlights across 11 pages) or to any fuzzy
matcher — see R-BOOKENDS-EXACT-ONLY-01. Line breaks and end-of-line hyphenation are
already handled; a repeated sentence is disambiguated with `page` (1-based) / `occurrence`.
Ensure **every** article ends with **1–3 highlighted quotes** (the per-article cards each
need 1–3).

### 5. Sort each reference into its subtopic folder + classify stance

File each reference into the correct subtopic child group with
`mcp__bookends-mcp__bookends_groups { action: "add_references", name: "<Topic> — <Subtopic>", reference_ids: [...] }`.
Give each article a stance label appropriate to the question (for an efficacy/clinical
review: **Supportive / Equivocal / Not supportive**), based on what the paper actually
concludes, not its title. Keep a running tally for the stance table.

### 6. Build ONE combined styled HTML report

Assemble a single self-contained HTML document (inline `<style>`) with the SAME
sections, in this order, applying all the format rules:

```
Header            — title, subtitle, prepared-date, one line on the evidence base, and
                    the TARGET BOOKENDS LIBRARY name (R-BOOKENDS-LIBRARY-NAME-ON-REPORT-01)
Executive Summary — up-front bottom-line (4–8 sentences): what the evidence shows, the
                    stance tally, and the single most important caveat. A reader can
                    stop here and know the answer.
"How to read"     — 2–4 sentences: three parts under one cover; quotes deep-link to
                    Bookends highlights; each reference carries three links (citation → article on the web;
                    "Bookends Group" → the source's subtopic group; "Bookends Citation" → that reference/PDF in Bookends);
                    closes with a Word-ready Academic Summary and a Vancouver References
                    list.
"How to open      — a short callout near the TOP of every report (in/near the Executive
 the deep links"    Summary or the "How to read" line). Reproduce this wording: "Each
                    highlighted quote is a native bookends:// link to the source PDF.
                    Inside Bookends the links are clickable when they sit in a field as
                    styled text — the styled link list is delivered to this report's
                    Bookends record's Notes (see step 7), so click them there. You can
                    also follow any link from a web browser: the Bookends attachment is a
                    hyperlink-preserving PDF, so open the iCloud HTML copy in Safari/Chrome; the browser hands the bookends:// scheme
                    to macOS, which routes it back to Bookends. If you paste a link into a
                    Bookends field yourself, use a normal styled Paste (Cmd-V), NOT Paste
                    and Match Style, or the live hyperlink is stripped. Ordinary web links
                    (PMC / open-access) work everywhere."
PART I — Literature Package
  Introduction    — topic framing + the stance legend
  Summary / Source-type Table — Article (title = BOLD web link → DOI/PMID/URL, PLUS the mandatory
                    dual pair "· Bookends Group · Bookends Citation" — R-BOOKENDS-DUAL-LINK-01) · one-sentence
                    summary · Journal · Year · Source type (guideline / systematic
                    review / RCT / etc.) · Stance pill + a tally line
  Article-by-Article Summaries — one card per paper: title + stance pill, full citation
                    (citation & title = BOLD web link → DOI/PMID/URL, PLUS "· Bookends Group · Bookends Citation"), a 3–5
                    sentence factual summary with 1–3 HIGHLIGHTED, deep-linked verbatim
                    quotes WOVEN INLINE (never stacked). Abstract-only sources flagged.
PART II — Scholarly Synthesis (Deep-Linked)
  Navigable TOC of INTERNAL <a href="#sec-N"> links over numbered sections, each with a
  stable <h2 id="sec-N"> anchor. Then the multi-section narrative: EVERY quotation is an
  INLINE highlighted span woven into the prose — a BOLD link to its bookends:// exact-
  passage deep link, never a detached block-quote. IN-TEXT CITATIONS ARE AUTHOR-DATE
  (APA-like) BY DEFAULT — (Jones et al, 2015) / (Jones & Smith, 2015) / (Jones, 2015),
  semicolon-separated when several, "Jones et al (2015) found…" for narrative mentions —
  and EACH ONE IS ITSELF A LIVE LINK to that source's highlighted-passage deep link
  (R-BOOKENDS-NARRATIVE-CITE-STYLE-01). A reasoned conclusion.
Academic Summary  — flowing narrative synthesizing ALL positions with in-text
                    (Author, Year) citations as PLAIN TEXT (no hyperlinks); Word-ready
                    Rich Text.
References         — titled "References" (NOT "Works Cited"), formatted in VANCOUVER
                    style: numbered, citation order; each entry carries the citation text → article web page
                    (DOI → PMID → stored URL) PLUS BOTH Bookends links ("· Bookends Group · Bookends Citation");
                    plain-text citation only if no DOI/PMID/URL — the two Bookends links are still required.
                    (Academic Summary above stays plain-text / Word-ready.)
Footer            — provenance, non-PHI note, "verify against primary sources", not
                    medical/legal advice.
```

Use the report's visual language: colored stance pills and inline highlighted quote
spans (light highlight background + bold link styling). Generate the **Vancouver
References** either by hand or via
`mcp__bookends-mcp__bookends_get_formatted_reference` with a Vancouver style — but
reconstruct any `volume(issue)` from the parenthesis-free stored parts so the printed
citation is correct (per *Standing rules*).

### 7. Save the report — Bookends AND iCloud

> **PHI POLICY (Bookends is PHI-safe; iCloud is not) — updated 2026-07-07.** Bookends lives
> **locally on the Mac** and is **single-user**, so it is **as private as DEVONthink**. **PHI /
> attorney-work-product case reports ARE allowed in Bookends.** Therefore **DO NOT skip the
> Bookends report PDF for a PHI case report** — a PHI case report gets its Bookends PDF exactly
> like a de-identified one. **iCloud stays off-limits for PHI** (unchanged): for a PHI case,
> save the HTML copy **only** to the DEVONthink case group and attach the PDF in Bookends —
> write **no** iCloud copy. Only **Bookends and DEVONthink** are PHI-safe stores.
>
> **EVERY Bookends research case (PHI or de-identified) MUST have its report present as a
> VERIFIED NON-BLANK PDF in the `<Topic> — Reports` folder**, as its **own dedicated placeholder
> reference** (title = report name with ` (AI)`, Report/misc reference type, AI-content label 3,
> deep-link source list in Notes). **A report group that has no report PDF — or only an HTML
> attachment and no PDF — is a DEFECT:** render the PDF with headless Chrome, attach
> it via the Bookends MCP, and verify it is non-blank with `bookends_get_pdf_content` before
> considering the run complete.

> **CROSS-NAVIGATION LINKS (report ABOUT a DEVONthink group) — added 2026-07-07.** When the
> report is about a DEVONthink case/group, it MUST display, near the top (header/metadata
> area), TWO cross-navigation links so the reader can move between the two stores:
> **(1) Source DEVONthink group** — `x-devonthink-item://<group-uuid>` (opens the case group in
> DEVONthink); and **(2) Bookends folder** — the report's Bookends group/folder link
> `bookends://sonnysoftware.com/group/<LibraryName>/<URL-encoded group name>`. The
> **`<LibraryName>` segment is REQUIRED** — it is the library window's name without its
> `.bdb` extension (e.g. `Library1`; obtain it from AppleScript `name of front library
> window`). The group name MUST be **percent-encoded**: space → `%20`, em dash “—” →
> `%E2%80%94`, `&` → `%26`, etc. Point the link at the report's own `<Topic> — Reports`
> subgroup. Example (VERIFIED working): a subgroup named `Geriatric LE — Reports` in library
> `Library1` → `bookends://sonnysoftware.com/group/Library1/Geriatric%20LE%20%E2%80%94%20Reports`.
> **Do NOT use the bare reference-id form `bookends://sonnysoftware.com/<id>`** (it opens the
> entry mixed among unrelated citations, not the group), and **do NOT omit the `<LibraryName>`
> segment** (a group URL without it does not resolve). Label the two links clearly (e.g.
> "Source DEVONthink group" and "Bookends folder"). **Both links must appear in BOTH the HTML
> copy (in the DEVONthink case group) AND the attached PDF (in Bookends)** so either
> deliverable can reach the other.
>
> **NO BARE REFERENCE-ID LINKS — applies to EVERY `bookends://` link in the report.** The bare
> reference-id form `bookends://sonnysoftware.com/<id>` selects the reference inside the FULL
> library list, so the target appears amid unrelated MARKED references from other reports — not
> in its own report's context. Ban it for EVERY link:
> - **Quote / highlighted-passage links → the Bookends-generated PDF deep link**
>   `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>`
>   (R-BOOKENDS-PDF-DEEPLINK-02). The persistent highlight is written by
>   `bookends_annotate_pdf` (`mode: "exact"`) and the link is the **annotation-anchored**
>   one read back from `bookends_get_pdf_content { mode: "annotations" }`. The
>   `…/selection/…` form throws "nil object" and is BANNED. Never hand-fabricate a link.
> - **Per-source links → the DUAL PAIR (R-BOOKENDS-DUAL-LINK-01, added 2026-07-11).** The
>   single ambiguous "Open in Bookends" link is RETIRED. EVERY citation/source — in the
>   Summary/Source-type table, the per-article cards, the References list, and anywhere else a
>   per-source link is emitted — carries **TWO clearly-labeled Bookends links**:
>   - **`Bookends Group`** → `bookends://sonnysoftware.com/group/<LibraryName>/<URL-encoded group name>`,
>     pointing at the **subtopic child group that holds that source**, so the reader lands among
>     that report's OWN sibling sources. `<LibraryName>` is REQUIRED; percent-encode the group name
>     (space→`%20`, em dash→`%E2%80%94`, `&`→`%26`).
>   - **`Bookends Citation`** → a link that opens **THAT SPECIFIC reference / its PDF**, in the
>     Bookends-generated form `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>`
>     read back from the annotation list (`bookends_get_pdf_content { mode: "annotations" }`,
>     R-BOOKENDS-PDF-DEEPLINK-02). The `…/selection/…`
>     form is BANNED — it throws "An error has occurred: nil object."
>   Label them **exactly** `Bookends Group` and `Bookends Citation` and keep them visually
>   distinguishable at a glance.
> - **The bare `bookends://sonnysoftware.com/<id>` reference-id form is BANNED for every link
>   (quote OR group OR citation).**

- **Bookends (attach a PDF, not the HTML):** the report is **authored as HTML**, but the
  copy stored **in Bookends must be a PDF** (the iCloud copy stays HTML — see next bullet).
  File the resulting **PDF** into the **`<Topic> — Reports` subgroup**, attached to a
  **dedicated placeholder reference created for this report alone** (see the
  placeholder-reference rule below), and set the record's **AI-content label (label 3)**. Never tag it;
  never trash the prior report (move nothing to trash — if regenerating, add the new one
  alongside; **supersede** an older Bookends copy by renaming/keeping it, e.g. a
  ` … SUPERSEDED HTML.html` suffix, never deleting). Name it with an ` (AI)` suffix, e.g.
  `<Topic> — Deep-Linked Report (AI)`.
  - **The report PDF must be its OWN dedicated placeholder reference — NEVER bolted onto an
    arbitrary/unrelated existing reference.** Bookends can only hold a PDF as an attachment to a
    reference, so create a **new, purpose-built placeholder reference for the report** and attach
    the PDF to THAT. Give it **title = the report name** (with the ` (AI)` suffix), an appropriate
    **Report/misc reference type**, and the **AI-content label (label 3)**; leave the bibliographic
    fields (DOI / PMID / journal / volume) **empty**; and put the **deep-link source list in its
    Notes**. Do **not** attach the report to a source/article reference or any other unrelated
    record — that misfiles the report onto an arbitrary reference. First look for an existing
    placeholder by the exact report title in the Reports subgroup and reuse it; if the report PDF
    is ever found attached to an arbitrary reference, **detach it** from that reference (never
    delete the reference or its own PDF) and re-attach it to the dedicated placeholder.
  - **HTML→PDF conversion — render with HEADLESS CHROME, then attach via the Bookends MCP.
    This render-then-MCP-attach flow is the standard, non-negotiable procedure** (it works
    from a fully background run — no mouse, keyboard or screenshots):
    1. **Render the PDF with headless Chrome, on the Mac.** Write the finalized HTML to a
       temp path on the Mac and print it:

       ```
       "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         --headless=new --disable-gpu --no-pdf-header-footer \
         --print-to-pdf="<report>.pdf" "<report>.html"
       ```

       Chrome is the approved converter: it is a headless, background-safe render that
       **preserves in-text hyperlinks as clickable link annotations — including
       custom-scheme `bookends://…` links** (verified: the `bookends://` annotations survive
       the print), alongside the web citation links (`https://doi.org/…`, PubMed / PMC).
       Run the command through `mcp__bookends-mcp__bookends_applescript_run`
       (`do shell script "…"`) so the file lands on the same filesystem Bookends can read.
    2. **Attach via the Bookends MCP directly — never via a mounted host folder.** Attach
       the rendered PDF to the report reference with
       `mcp__bookends-mcp__bookends_add_pdf { items:[{ id, path }] }`. Bookends copies the
       file into its **own Attachments folder** itself. **Do NOT** call
       `request_cowork_directory` / rely on a mounted host folder, and **do NOT** hand-write
       the PDF into `~/Documents/Bookends/Attachments/` yourself — in a background run the
       folder-grant prompt is never answered, so the MCP-attach path is the only reliable
       route.
    - **MANDATORY link-annotation verification — REQUIRED; the run FAILS if it does not
      pass.** Dump the PDF's link annotations (background/headless, **NO computer-use** —
      e.g. with `pypdf`: iterate every page's `/Annots` and collect each annotation's
      `/A/URI`) and confirm the PDF contains BOTH (a) at least one web link
      (`https://doi.org/…`, PubMed / PMC) **AND** (b) at least one `bookends://…` link. If
      either class is missing or flattened, **STOP: do NOT ship a link-less report** — treat
      the run as FAILED and regenerate the HTML/PDF until the check passes.
    - **MANDATORY link-validation gate — REQUIRED; the run FAILS otherwise.** Run
      `python3 scripts/validate_bookends_links.py <report.html>`; it scans BOTH the finished
      HTML and the attached PDF's link annotations and asserts ALL FOUR:
      1. **ZERO bare reference-id links** — no `bookends://sonnysoftware.com/` followed
         immediately by digits (i.e. with no `/group/` or `/pdf/` path segment). Every
         `bookends://` link must be a `…/pdf/…` link or a `…/group/<Library>/…` link.
      1b. **ZERO `…/selection/…` links** (R-BOOKENDS-PDF-DEEPLINK-02) — this form throws
         "nil object" in Bookends and is a hard FAILURE.
      1c. **Every `…/pdf/…` link is live**: its `<refID>` exists in the library, that
         reference HAS an attached PDF, `<attachmentID>` is non-zero and matches the
         attachment id Bookends returns for that refID, and `<page0>` is within the PDF's
         page count.
      2. **EVERY source row carries BOTH Bookends links** — each per-source entry (Summary /
         Source-type table row, per-article card, References entry) contains exactly one link
         labeled `Bookends Group` (a `…/group/<Library>/…` URL) **and** exactly one labeled
         `Bookends Citation` (a `…/pdf/<Library>/<refID>/<attachmentID>/<page0>` URL). Count
         them: the number of `Bookends Group` links and the number of `Bookends Citation`
         links must each equal the number of source rows in that section. A source with only
         one Bookends link is a FAILURE.
      3. **Cross-nav links intact** — the top-of-report `x-devonthink-item://<group-uuid>`
         (Source DEVONthink group) and the Bookends report-folder group link are both present.
      4. **EVERY distinct link is fired — enumerated from the SHIPPED FILE**
         (R-BOOKENDS-VERIFY-EVERY-01). `probes == distinct links`; report both counts. A pass
         obtained against a *different* object than the one that shipped is a FALSE PASS and
         fails the run.
      5. **Group links are verified by READING THE WINDOW, not by AppleScript**
         (R-BOOKENDS-NO-APPLESCRIPT-GROUP-VERIFY-01): park on a known group with a known ref
         count, fire, screenshot, and require the displayed group AND the ref count to change.
         Pass the evidence to `--group-nav-log`. `selected publication items` is stale after a
         `/group/` URL and is BANNED as evidence; an `open` exit code of 0 is never evidence.
      If any assertion fails, STOP and rewrite the offending links before shipping. Do this as a
      scripted grep/count over the HTML and a `pypdf` `/Annots` dump over the PDF — not by eye.
    - **MANDATORY post-attach non-blank / renders-content verification — REQUIRED; the run
      is NOT done until it passes.** A PDF can carry valid link annotations yet still render
      visually **BLANK** (this happened: a report went into Bookends as a ~1.9 MB file with
      zero visible text). So AFTER attaching, re-read the attachment back **through
      Bookends** and confirm it actually renders the report text: call
      `mcp__bookends-mcp__bookends_get_pdf_content { id }` and require a non-trivial amount
      of extracted text (e.g. the Executive Summary wording and a healthy `total_chars`),
      and sanity-check the page count / file size against the HTML (a real report is many
      pages of text, not one blank page). **If the attached PDF is blank / near-empty / not
      the real multi-page report, regenerate the PDF in the sandbox and re-attach, then
      re-verify — do NOT declare the report done while the Bookends copy is blank.** Keep
      any superseded blank PDF aside per the never-trash rule (move it to a `Temp AI Files`
      area or detach it — never delete). Only a PDF that passes BOTH this non-blank check
      and the link-annotation check is considered filed.
- **iCloud (or configured `RESEARCH_DIR`):** also save the SAME HTML under the
  configured `RESEARCH_DIR` (see *Configuration* — resolved from `$HOME`, never a
  hardcoded username/path), **always inside a `Bookends Research` subfolder** (create it
  if missing):
  `<RESEARCH_DIR>/Bookends Research/<Topic> — Deep-Linked Report/<Topic> — Deep-Linked Report (AI) <date>.html`
  (create the `Bookends Research` folder and the per-topic folder if needed; `<date>` =
  today's date). **Every iCloud copy this skill writes — the HTML and any other iCloud
  copy — must live under `Bookends Research`.** This satisfies the standing rule that
  researched results are saved as a formatted HTML file in iCloud. If iCloud Drive is not
  found at the default location, fall back per *Configuration* and report the path actually
  used.
- **Styled clickable links into Bookends (do every run).** So the deep links are clickable
  *inside* Bookends — not only from a browser — also deliver the report's link list into
  the report record as **styled text with live `bookends://` hyperlinks**. Build an HTML
  fragment listing each source as a styled `bookends://` link (the supported forms from
  step 4), convert it to RTF, place it on the macOS clipboard as rich text, and paste it
  into the report reference's **Notes** field (or a User1–User4 field) with a **normal
  styled Paste (`⌘V`) — NOT Paste and Match Style** (which would strip the links). The
  helper `scripts/styled_links_to_clipboard.sh` (see `references/bookends.md` §3a) takes
  `label<TAB>bookends://…` lines and loads the styled list onto the clipboard; then click
  into the Notes field and press `⌘V` (or Edit → Paste / `⇧⌥⌘V` if `⌘V` is mapped to
  match-style). With the user's permission the paste keystroke can be automated via System
  Events. This is **in addition to** the attached PDF and the iCloud HTML copy, not a
  replacement.

### 8. Report back

Give the user the report's name, its native `bookends://` link, the iCloud path, the
stance tally, the retrieval-source tally (Bookends vs Firecrawl-fallback per article), and the total number of quotes highlighted and deep-linked (per-article
cards + narrative). Confirm the Bookends group + subtopic tree was created and verified,
and that the styled, clickable `bookends://` link list was delivered into the report's
Bookends record (Notes) so the links are followable inside Bookends.

---

## Example output

See the **Example output** section of `README.md` and the images in
`examples/screenshots/` for representative screenshots of a finished report: the
executive summary with the "how to open the deep links" note
(`01-executive-summary.png`), the stance/source-type table (`02-stance-table.png`), a
per-article card with an inline highlighted, deep-linked quote (`03-article-card.png`),
and the Vancouver References list (`04-references.png`). The example is a
public-literature run ("Is Surgery Effective for Low Back Pain?") with no PHI.

---

## Reference file

- `references/bookends.md` — exact Bookends import/attach/highlight/deep-link calls, the
  **supported `bookends://` link forms** (the `group/` link and the Bookends-generated
  `pdf/` deep link — the bare reference-id form and the `selection/` form are banned), how to deliver the links into
  Bookends as **styled clickable text** (plain Paste, not Paste and Match Style), Vancouver
  formatting via `bookends_get_formatted_reference`, the AppleScript-bridge
  `volume`/parentheses workaround, group global-unique-name handling, and the label-AI /
  never-trash rules.

---

## Credits

**Richard S. Kaplan, MD** — Kaplan Life Care Planning. Author and maintainer.
- Email: rkaplan@kaplanlifecareplan.com
- Website: https://kaplanlifecareplan.com/

## R-BOOKENDS-PAGE-PROVENANCE-01 — where the page in a citation link comes from

> `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page>`
>
> **`<page>` is 0-BASED.** Boundary-proven on a 31-page PDF: `/30` is accepted,
> `/31` is rejected.
>
> **The page comes from the ANNOTATION.** `bookends_annotate_pdf` (`mode: "exact"`)
> writes the highlight over the quote, and `bookends_get_pdf_content
> { mode: "annotations" }` returns that annotation's **annotation-anchored deep link**,
> already carrying the right page. No PDF library, no page ladder, no fuzzy fallback,
> and nothing to compute: the page is not ours to derive. If `exact` will not match, the
> quote is not in the PDF — fix the quote (never loosen the mode) or drop the citation.
> **Never silently emit page 0.**
>
> **The page must NEVER be harvested from Bookends' `link to displayed PDF`.**
> That readback reports whichever page Bookends currently happens to be showing —
> page 0 for a freshly-opened PDF. Harvesting it is what produced ~593 links that
> all ended in `/0` and opened every source on its cover page instead of at the
> quoted passage.
>
> `link to displayed PDF` is still read back, for the one thing it is authoritative
> about: **after firing a URL**, which PDF/page Bookends *actually* navigated to — the
> only accepted proof that a link lands where it claims. `open`'s exit code is not proof.
> (The **OPAQUE `<attachmentID>`** likewise only ever comes from Bookends — it is part of
> the annotation's link. Regenerating an attachment **mints a new attachmentID**, so every
> link must be re-read AFTER any attachment rebuild.)
>
> `…/selection/…` is a **fabricated route that does not exist** and is BANNED.
> `…/group/…` and `…/ref/…` are real.

## R-BOOKENDS-VERIFY-EVERY-01 — a check must exercise the artifact in question, not a cousin of it

> **The rule.** Verify **EVERY DISTINCT link / artifact actually shipped**, enumerated
> **from the SHIPPED FILE** (the finished HTML, the attached PDF's link annotations, the
> DEVONthink record) — not from the generator's intentions, not from a sample, not from a
> representative, and never from a related-but-different object. **If the shipped file
> contains N distinct `bookends://` links, fire N.** If it contains N distinct group links,
> fire N group links. If it cites N sources, check N attachments.
>
> **"I checked one and it worked" is not evidence about the others.** One link passing says
> exactly one thing: that link passes. It says nothing about the other 87, which were
> produced by the same code path only in the agent's imagination.
>
> **A passing check on the wrong object is WORSE than no check at all.** No check leaves
> honest uncertainty. A check that passes against a cousin of the artifact manufactures
> false confidence, gets written into the report-back as "verified", and ships the bug with
> a certificate attached.
>
> **Operational form (all mandatory):**
> - **Enumerate from the artifact.** Parse the shipped file and collect the set of distinct
>   links/objects. Never enumerate from the code that generated it, or from memory of what
>   you meant to emit.
> - **Probe the whole set.** No sampling, no "spot check", no "representative example". The
>   probe count MUST equal the distinct-artifact count, and the report-back MUST state both
>   numbers (`88 distinct group links found, 88 fired, 88 observed`). A verification claim
>   without those two numbers is not a verification claim.
> - **Name the object you tested, in the claim.** Not "group links verified" but "the
>   *report's own* header group link verified". If the sentence you are about to write does
>   not name the exact object, you do not yet know what you tested.
> - **Ask before every check: could this pass while the actual defect is present?** If yes,
>   the check is worthless as written — fix the check first, then run it.
>
> **Three worked examples — all real, all the same failure shape, all on one day:**
>
> 1. **The check tested a cousin.** The generator hardcoded a module-level constant for the
>    group segment, so **all 88 per-source "Bookends Group" links across 29 sources pointed
>    at the report's own `Reports` folder** instead of each source's subtopic group. The
>    pre-ship check fired the **report's own group link** — which *correctly* points at
>    `Reports` — saw it land on `Reports`, and declared **"group links verified."** The claim
>    was TRUE and WORTHLESS: it never touched a single one of the 29 citation links it was
>    taken to have covered. Reading the objects out of the shipped HTML (88 links, of which
>    exactly 1 was the header link) would have exposed it instantly.
>
> 2. **The check tested the wrong failure mode.** A pre-ship check reported **"passed: 0 bare-id
>    links, 0 `/selection/` links."** True — and irrelevant, because neither of those was the
>    form that was broken. The broken links were **well-formed `/group/` links pointing at the
>    wrong group**: a class the check never looked at. Scanning for the failures you already
>    fixed, while the live defect sits in a form you did not scan, is not a check. It is a
>    ritual.
>
> 3. **The check tested the link, not the paper** (**R-BOOKENDS-ATTACHMENT-PROVENANCE-01**).
>    A citation link was well-formed, carried a real attachmentID, resolved with no error, and
>    **passed observed navigation** — while opening the **WRONG PAPER**, because the reference
>    carried a stray first attachment. Every link-level check passed. The artifact under
>    question was never *the link*; it was *the paper the link opens*.
>
> These are one bug wearing three hats. **Same family: R-BOOKENDS-ATTACHMENT-PROVENANCE-01.**
> The pattern to recognise is not "group links can be wrong" — it is: *the check and the
> defect were about different objects, and the check passed anyway.*
>
> **Enforcement:** `scripts/validate_bookends_links.py` enumerates links from the shipped
> surfaces and probes every distinct one; it requires a `--group-map` (refID → subtopic group,
> written at step 5) and FAILS if the per-source group links do not resolve, one-for-one, to
> the group each source was actually filed into — including the specific fingerprint of this
> bug: **every per-source group link identical, or pointing at the `Reports` folder.**

## R-BOOKENDS-NO-APPLESCRIPT-GROUP-VERIFY-01 — AppleScript CANNOT verify Bookends group navigation

> **BANNED, by name: using AppleScript to verify that a `bookends://…/group/…` link
> navigated.** Bookends' AppleScript dictionary exposes **NO property for the
> currently-displayed group.** There is nothing to ask. In particular, reading
> **`selected publication items`** (or any other selection/list property) *after* firing a
> `/group/` URL returns a **STALE selection from before the call** — it reports success no
> matter what the URL did, **or whether it did anything at all**. It is a silently-lying
> verification path: it cannot distinguish "navigated to the right group", "navigated to the
> wrong group", and "did nothing". Any group-link verdict resting on it is void, regardless
> of how confident the transcript sounds.
>
> **The required procedure — READ THE WINDOW.** Group navigation is verified by *looking at
> the screen*, and only that way:
> 1. **Park Bookends on a known state with a known reference count** — e.g. select `All`,
>    showing N references. Record the group name and N. (Park somewhere that is NOT the
>    group under test; parking on the target makes the "right group is showing" observation
>    true before the URL was ever fired.)
> 2. **Fire the URL.**
> 3. **READ THE WINDOW — take a screenshot** and read back (a) the **displayed group** and
>    (b) the **displayed reference count**.
> 4. **Correct navigation MUST change BOTH.** The displayed group must be the group the URL
>    named, and **the reference count must change from N.** **The count change is the proof.**
>    Same group as parked, or an unchanged count, is a FAIL — it means nothing happened, or
>    something happened somewhere you cannot see.
> 5. Record the observation (parked group + parked count → observed group + observed count,
>    plus the screenshot path) in the group-navigation evidence log, and hand it to
>    `scripts/validate_bookends_links.py --group-nav-log`. **The validator refuses to pass any
>    `/group/` link without that evidence** — it will not fall back to AppleScript, and it will
>    not pass a group link because firing it raised no alert.
>
> **What AppleScript CAN still verify (this path is sound — keep it).** PDF / citation links
> are legitimately verifiable through AppleScript, because Bookends *does* expose the state
> the action changes: after firing a `…/pdf/…` link, `name of displayed PDF` and
> **`link to displayed PDF`** report the PDF and the page Bookends **actually** navigated to,
> and `selected publication items` reports the reference a `…/ref/…` link actually selected.
> Those readbacks are refreshed by the action, so they are evidence. **Group links have no
> such property. Do not analogise from one to the other.**
>
> **The general lesson — exit codes are never evidence; stale readbacks are never evidence.**
> An `open` call returns **exit 0 even when Bookends throws an error dialog** and does nothing.
> A success exit code means the URL was handed to macOS, not that anything correct happened.
> So every verification must read back **OBSERVED STATE that could only be true if the action
> succeeded** — and, before trusting that readback, **the reader must confirm the state it is
> reading is actually REFRESHED by the action, and not cached / stale from before it.**
>
> **The null test (run it once per verification channel, before relying on the channel).**
> Park on a known-wrong state, then **read the channel WITHOUT firing anything.** If the
> readback still reports the expected/"successful" value, the channel is stale or cached and
> **verifies nothing** — discard it and find a channel that changes. This is precisely the test
> `selected publication items` fails for group links, and precisely the test
> `link to displayed PDF` passes for PDF links.

### Pre-ship checks (all fatal — `scripts/validate_bookends_links.py`,
`scripts/validate_bookends_attachment.py`)

1. **ZERO `…/selection/…` links** and zero bare reference-id links.
2. **All-page-0 fingerprint** — if *every* `/pdf/` citation on a surface ends in `/0`,
   page 0 must be **CORROBORATED** for every cited reference: a single-page source, a
   highlight annotation physically on page 0, or the quote text literally found on
   page 0. A reference with no evidence for page 0 fails the surface. (`--resolution-report`
   supplies the quotes.)
3. **No unresolved quote pages** — `--resolution-report PAGEMAP.json` (the log the
   annotate-and-link step writes: `rid`, `quote`, `new_page`); any link whose `new_page` is
   `null` is a hard FAIL. With `mode: "exact"` an unresolved page means the quote never
   matched — i.e. the quote is wrong.
4. **Observed navigation** — park Bookends on a decoy, fire the URL, then read back BOTH
   `name of displayed PDF` **and** `link to displayed PDF`. The PDF **and the page** must
   match, and the live attachmentID must equal the one in the link (attachment-ID churn
   check). Anything less is not a pass.

5. **R-BOOKENDS-ATTACHMENT-PROVENANCE-01 — every source's FIRST attachment must actually
   BELONG to that reference** (`scripts/validate_bookends_attachment.py --sources …`,
   FATAL). **This is the near-miss check.** A link can be perfectly well-formed, carry a
   real attachmentID, resolve with no error and no alert, pass observed navigation — and
   still **open the WRONG PAPER**, because the reference it points at carries a **stray
   first attachment** (a PDF belonging to another paper, left behind by a bad download, a
   mis-resolved DOI, or an attach against the wrong record). Bookends displays and
   annotates the FIRST attachment, so everything downstream — the highlight, the page, the
   deep link — is dutifully computed against the wrong PDF. Nothing in checks 1–4 can see
   this: they verify the link, not the paper.

   So, for **every source reference**, BEFORE writing its highlight and building its link:
   confirm the first attachment's PDF is the paper the reference claims to be — match the
   reference's title (and author/year) against the text of the PDF's opening pages. A
   reference whose first attachment does not match, or which carries **extra** attachments
   with a non-matching one in front, is a **FATAL** failure: re-attach the correct PDF as
   the first attachment (never delete the stray — detach or supersede it), then re-read
   every affected deep link, because the attachmentID has churned.

6. **The report reference's attachment must be a resolvable, existing, DISPLAYABLE PDF**
   — `scripts/validate_bookends_attachment.py` (FATAL). Bookends' attachment pane renders
   PDFs, images, webarchives and the *text* of doc/rtf files; it **cannot render raw
   `.html`**. The User Guide: *"If there is an attachment that is not a PDF, image, or
   compatible file … Bookends will indicate that there is an attachment but that it can't
   be displayed"*, while *"the name of the attachment is displayed in a pop-up menu at the
   bottom"*. So an HTML-attached report reference shows a **filename in the bottom bar and
   an EMPTY Attachments pane** — it looks like nothing is attached. Enforce, for every
   report reference:
   - it has **≥1 attachment**;
   - the **FIRST** attachment is a **`.pdf`** (Bookends displays the first one by default —
     a PDF sitting *second*, behind the HTML, still shows an empty pane);
   - that PDF **exists on disk** (a render superseded into "Temp AI Files" after attaching
     leaves a dangling name);
   - it is recorded as a **bare filename** in Bookends' default attachments folder, never an
     absolute/HFS-colon path (`:Users:…`), which Bookends cannot resolve;
   - the PDF still carries its **`bookends://` link annotations**.
   The HTML render may remain as a **secondary** attachment. Never delete it; supersede it.

7. **R-BOOKENDS-VERIFY-EVERY-01 — every distinct shipped link is fired, enumerated from the
   SHIPPED FILE** (`scripts/validate_bookends_links.py`, FATAL). Parse the finished HTML and
   the attached PDF's link annotations, collect the **distinct** `bookends://` links, and probe
   **all** of them — `probes == distinct links`, both numbers reported. **No sampling, no
   representative link, no "the one I checked worked."** A check that passes against a
   *different* object than the one that shipped (the report's own header link standing in for
   the 29 citation links; a scan for `/selection/` links when the broken form was `/group/`)
   is a FALSE PASS and is treated as a failed run. Pass `--group-map PAGEMAP.json`
   (refID → the subtopic group the source was filed into at step 5); the validator FAILS if the
   per-source group links do not map one-for-one onto those groups — including the fingerprints
   **all per-source group links identical** and **per-source group link pointing at the
   `Reports` folder**.

8. **R-BOOKENDS-NO-APPLESCRIPT-GROUP-VERIFY-01 — group links are verified by READING THE
   WINDOW, never by AppleScript** (`scripts/validate_bookends_links.py --group-nav-log`,
   FATAL). Bookends exposes **no** displayed-group property; `selected publication items` read
   after firing a `/group/` URL returns a **stale** pre-call selection and reports success
   unconditionally. For **each distinct** group link: park on a known group with a known
   reference count, fire the URL, **screenshot the window**, and require **both** the displayed
   group **and** the reference count to change to the expected group — **the count change is the
   proof**. Supply the evidence log (`--group-nav-log`); the validator will not pass a group link
   without it, and "fired, no alert appeared" is **not** a pass. **An `open` exit code of 0 is
   never evidence** — Bookends returns it while throwing an error dialog. Every check must read
   back observed state that could only be true if the action succeeded, and must first prove that
   state is refreshed by the action rather than cached from before it (the null test:
   read the channel *without* firing — if it still says "success", the channel verifies nothing).

---

## R-BOOKENDS-LIBRARY-MUST-BE-OPEN-01 — a correct group link fails silently with no library open

**Before you diagnose a `bookends://` link as broken, CHECK WHETHER A LIBRARY IS OPEN.**

Every `bookends://` link — quote deep links and group links alike — resolves against Bookends'
**front library window**. If Bookends is running with **no library open**, macOS hands the URL
over successfully and Bookends has nothing to resolve it against. The link looks dead. It is
not. Two separate incidents on 2026-07-14 — one presenting as the *"An error has occurred: nil
object"* dialog, one as a group link that simply did nothing — were **both a closed library**,
not a bad link.

Check it first, background-only, before touching a single character of the generator:

```
mcp__bookends-mcp__bookends_libraries { action: "list" }
→ {"count": 0, "libraries": []}     ← NO LIBRARY OPEN. This is your bug. Stop here.
→ {"count": 1, "libraries": [{"name": "Library1.bdb", "frontmost": true}], ...}
```

**The name-based group form is CORRECT.**
`bookends://sonnysoftware.com/group/<LibraryName>/<percent-encoded group name>` is byte-for-byte
what Bookends' own **Edit → Copy Link** emits when you select a group in the sidebar. Verified
against Bookends itself, 2026-07-14. Do not "improve" it. There is no full-path form, no
`.bdb`-suffixed form, and no id-based form to switch to.

**The corollary, and it is the expensive one:** an agent that "fixes" a correct link because it
assumed the link was at fault makes the situation strictly worse — it burns a regeneration cycle,
supersedes good records, and leaves the real (environmental) cause in place to recur. **Confirm
the form against Bookends' own Copy Link output before editing anything.** If the emitted form
already matches Copy Link, the generator is not the bug: look at the environment.

Diagnose statically, in this order, before ever firing a URL:

1. **Is a library open?** (`bookends_libraries { action: "list" }`) — the single most common cause.
2. **Are the per-source group links distinct?** Extract every `/group/` link from the SHIPPED
   file. If they are all identical, or all end in `Reports`, that is the hardcoded-constant bug
   (R-BOOKENDS-VERIFY-EVERY-01) — a real generator defect.
3. **Do the decoded group names match the live Bookends group names, character for character?**
   Read the names back (`bookends_groups { action: "get" }`) and compare codepoints — an em dash
   must be U+2014 on both sides and must be percent-encoded as `%E2%80%94` in the URL.

If 1 passes, 2 passes and 3 passes, **the links are correct** and the failure is environmental.
Say so plainly. Do not invent a code fix to look productive.

---

## R-BOOKENDS-LIBRARY-NAME-ON-REPORT-01 — name the target library, once, prominently

**Every report states which Bookends library its links target.** A `bookends://` link carries the
library name in its path (`…/pdf/<Library>/…`, `…/group/<Library>/…`), but the reader never sees
that — they see anchor text. A user with more than one library has no way to know which library a
report expects, and a link into a library that is not open fails silently
(R-BOOKENDS-LIBRARY-MUST-BE-OPEN-01). Naming the library removes both problems.

**Where it goes — three places, all document-scope:**

1. **The header / cross-navigation block**, next to the DEVONthink and Bookends-folder links:
   > **Bookends library:** `Library1` — all `bookends://` links below resolve in this library and
   > require it to be open.
2. **The "how to open the deep links" callout**, paired with the closed-library warning:
   > **These links target the Bookends library `Library1`.** … **If `Library1` is not open, the
   > links will resolve against nothing and appear broken.** Bookends will auto-open a closed
   > destination library *only* if it is listed in **File → Open → Recents**.
3. **The provenance footer**, with the link counts.

**Where it does NOT go: the individual citations.** Do **not** repeat the library name on each
source card, in the stance table, or in the References list. The library is a property of the
**document**, not of any one link: every link in a given report targets the same library, so
repeating it 31 times adds 31 copies of a constant and buys nothing. It would also crowd out the
information the per-link labels exist to carry — the group's name
(R-BOOKENDS-GROUP-LINK-LABEL-01) and the `Bookends Citation` affordance. **State it once,
prominently, at document scope.**

*(The one case that would justify per-link library naming is a report whose sources are drawn from
**more than one library**. This skill files every source of a run into one library, so that case
does not arise. If a future run ever spans libraries, name the library per link — and say so in the
header.)*

### How Bookends actually handles a closed target library (verified against the User Guide)

There is **no `bookends://` URL command to open or switch a library.** The documented URL
destinations are a reference, a group/folder, a PDF, a PDF page, PDF-selected text, and a PDF
annotation — no library-open verb. There is likewise **no AppleScript `open library` command**
(the dictionary has `create library`, and nothing to open an existing one).

What the User Guide *does* document, verbatim:

> "Clicking on a Bookends hypertext link in another app will launch Bookends, if it is not running,
> and navigate to the link. **If the destination is in a closed library, it will be automatically
> opened if it is listed in the File → Open → Recents menu.**"

So the auto-open is real but **conditional**: the target library must be in the Recents list (whose
length is capped by Settings → *Number of recent libraries shown*). A library that has aged off
Recents will not auto-open, and the link fails silently. That conditionality is why the report must
name the library rather than relying on Bookends to sort it out.

