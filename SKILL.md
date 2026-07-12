---
name: bookends-research-skill
description: "Produce a Bookends-native, deep-linked, highlighted research report on any topic — the pipeline behind the Priapism report, parameterized so only the topic changes each run. Creates a Bookends group with subtopic child groups plus a Reports folder, retrieves sources (guidelines, systematic reviews, key studies) Bookends-first — via Bookends' search, identifier retrieval and PDF download, with candidate papers first enumerated by a ROUTINE Firecrawl Research / PubMed search per subtopic (verified PMIDs/DOIs), falling back to a Firecrawl fetch only when Bookends cannot attach — attaches full-text PDFs, writes one persistent highlight and page-accurate bookends:// deep link per source, and assembles ONE combined HTML report (highlighted deep-linked quotes, stance table, narrative synthesis, Vancouver references). Use whenever the user asks for a Bookends research report, deep-linked or highlighted literature review, evidence synthesis or annotated bibliography in Bookends, or says 'run the Bookends research skill' or 'bookends:// deep-linked quotes'. Depends on the bookends-mcp and pdf-highlight-and-deep-link MCP."
---

# Bookends Research Skill

This skill reproduces **exactly** the workflow and report format of the Priapism
deep-linked Bookends project — the report the user called "excellent" — **parameterized
so that only the RESEARCH TOPIC changes from run to run.** Everything else stays
identical, with **one deliberate format change**: the citation list at the end is
titled **"References"** (not "Works Cited") and is formatted in **Vancouver** style.

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
references**; deep links are **`bookends://…` page/selection links**. Drive Bookends
through its MCP (`mcp__bookends-mcp__*`) and the highlight/deep-link MCP
(`mcp__pdf-highlight-and-deep-link__*`) — **never** through screen automation.

**Dependency — PyMuPDF, not the MCP's link generator.**

```
pip install pymupdf                    # `import fitz` — quote location, highlight, page index
pip install pyobjc-framework-Quartz    # so the validator can SEE a Bookends modal alert
```

Quote location, the persistent highlight, and the page index come from **PyMuPDF**
(`scripts/highlight_and_link.py`), run against the real PDF. The **citation URL is
read back from Bookends itself** (AppleScript `link to displayed PDF`) — never from
an MCP. The **pdf-highlight-and-deep-link MCP** is optional and **its `deepLink` is
never used**: it fabricates the non-existent `…/selection/…` route whenever its call
into Bookends fails, silently, which is how ten reports shipped with every citation
link throwing "nil object". Install **bookends-mcp** alongside.

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
     marked-library list (user-confirmed defect, Skala report 2026-07-10);
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
   circumstance, from any source — including the `deepLink` field returned by the
   pdf-highlight-and-deep-link MCP, which fabricates that shape.** Bookends does not
   implement a `selection` route with a nil (`0`) attachment/annotation id: it dereferences
   a nil object and throws the modal **"An error has occurred: nil object."** dialog.
   (Empirically reproduced and fixed 2026-07-11, Skala Pediatric-LLD report: all 131
   citation links in that report used the selection form and every one of them errored.)

   **Citation links must be GENERATED BY BOOKENDS, never string-templated.** Obtain each
   one from Bookends' own AppleScript property, which returns the authoritative URL:

   ```applescript
   tell application "Bookends"
     tell front library window
       set selected publication items to {publication item id "264081"}
       delay 0.9                            -- let the PDF pane load
       set theLink to link to displayed PDF -- e.g. bookends://sonnysoftware.com/pdf/Library1/264081/1783717403/0
     end tell
   end tell
   ```

   Batch this over every refID in the report and build a `refID → deepLink` map BEFORE
   emitting any HTML. A reference whose `link to displayed PDF` comes back empty has no
   usable PDF attachment: attach one (or drop the citation link) — do not fabricate a URL.
   The `bookends://sonnysoftware.com/<refID>` bare form remains banned
   (R-BOOKENDS-DUAL-LINK-01). Run `scripts/validate_bookends_links.py` before shipping;
   it fails the build on any selection-form, bare-id, zero-attachmentID or out-of-range-page
   link, and on any card missing either of its two links.

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
normally types ONE line, e.g. `Run the Bookends Research Skill on Ischemic Priapism`
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

The report MUST reproduce the Priapism report's structure and follow these six rules.

1. **Per-article summaries carry 1–3 highlighted, hyperlinked quotes woven INLINE.**
   Each article's summary card embeds 1–3 exact verbatim quotes from *that* article.
   Each quote is (a) highlighted in the attached PDF via the pdf-highlight MCP (the
   call is idempotent — an identical highlight is reused) and (b) rendered as an active
   hyperlink to its exact-passage `bookends://` deep link. **Weave each quoted phrase
   directly into the running sentence** so reading the paragraph carries you through
   the quote (e.g. *…the panel concluded ischemic priapism is "a compartment syndrome"
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
   formatted in Vancouver style** — numbered, in citation order. *(This
   References/Vancouver section is the ONE deliberate change from the original Priapism
   template, which ended with a "Works Cited" list.)* Per **rule 6**, each References entry
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
   - **(b) A link labeled exactly `Bookends Group`** → the **library-qualified GROUP link**
     `bookends://sonnysoftware.com/group/<LibraryName>/<URL-encoded group name>` for the
     **subtopic child group that actually holds that source**. Lands the reader among that
     report's sibling sources. `<LibraryName>` is REQUIRED (e.g. `Library1`); percent-encode
     the group name (space→`%20`, em dash “—”→`%E2%80%94`, `&`→`%26`).
   - **(c) A link labeled exactly `Bookends Citation`** → a link that opens **THAT SPECIFIC
     reference / its PDF**, never the whole library. It MUST be the Bookends-generated PDF
     deep link `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>`,
     read back from Bookends via the AppleScript `link to displayed PDF` property
     (R-BOOKENDS-PDF-DEEPLINK-02). **Never string-template a citation URL, and never emit the
     `…/selection/…` form** — including the `deepLink` field returned by
     `pdf_link_for_quote`, which fabricates that shape and makes Bookends throw
     "An error has occurred: nil object." The same Bookends-generated `/pdf/` URL is used for
     the quote links inside the card.

   **Render them as a visibly distinguishable trio**, e.g.:

   ```html
   <strong><a href="https://doi.org/10.xxxx/yyy">Source title</a></strong>
   <span class="be-links"> · <a class="be-group" href="bookends://sonnysoftware.com/group/Library1/Topic%20%E2%80%94%20Subtopic">Bookends Group</a>
   · <a class="be-cite" href="bookends://sonnysoftware.com/pdf/Library1/8721/1783717403/2">Bookends Citation</a></span>
   ```

   So: **citation → the article's web page; "Bookends Group" → the subtopic group;
   "Bookends Citation" → that reference/PDF itself.** The two Bookends links must be
   distinguishable **at a glance** — never collapsed into one ambiguous "Open in Bookends".
   Style all links per rule 3. **The bare reference-id form
   `bookends://sonnysoftware.com/<id>` remains BANNED for every link** (see the standing
   rule and the pre-ship check).

---

## End-to-end workflow

Do these in order. Idempotent and resumable throughout.

### 1. Create the Bookends group + topic-appropriate subtopic child groups

Create a **NEW Bookends group named for the topic**, e.g. `<Topic> — Deep-Linked
Report`. Inside it, create **subtopic child groups that are natural for THIS topic** —
derive them from the topic's own structure, do not copy the priapism labels verbatim.
**Always include a `Reports` child group** (the finished report is filed there).

**Derive the subtopics from the topic.** Look at how the literature on the topic is
actually organized and mirror it. For reference, the priapism run used:
`Causes & Etiology` · `Diagnosis` · `Treatment (Ischemic)` ·
`Treatment (Non-ischemic / High-flow)` · `Stuttering / Recurrent` ·
`Prognosis & Outcomes` · `Reports`. For a **different** topic, produce the analogous
natural breakdown (typically some mix of *Etiology/Pathophysiology*,
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
   `mcp__pdf-highlight-and-deep-link__bookends_attach_pdf { id, pdfPath }`, or bulk-import
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
  `mcp__pdf-highlight-and-deep-link__bookends_attach_pdf { id, pdfPath }`, or
  `mcp__bookends-mcp__bookends_add_pdf` for local files / direct PDF URLs / identifier-
  based retrieval. Verify with `mcp__bookends-mcp__bookends_get_attachment_paths`.
- **No accessible full text (either path)?** Attach a rendered **abstract PDF** with
  `mcp__pdf-highlight-and-deep-link__bookends_attach_abstract_pdf` and **flag it
  abstract-only** in the report (its quote is an abstract key sentence, not a full-text
  deep link).
- **Record each reference's Bookends `id` and its retrieval provenance** (Bookends vs
  Firecrawl-fallback) — the id is the locator for highlighting, linking, and filing; the
  provenance feeds the step-8 audit tally. Respect the AppleScript-bridge quirks in
  *Standing rules* when writing any field (no `volume` write, no parentheses).

### 4. One persistent highlight + page-accurate deep link per source

For each source, pick a **verbatim, contiguous** key sentence (full-text sentence for
full-text PDFs; the abstract's key sentence for abstract-only). Then:

```
python3 scripts/highlight_and_link.py --ref <refID> --quote "<verbatim fragment>"
  -> { "ref", "library", "page", "url", "kind": "pdf"|"ref", "pdf",
       "quote_found", "highlighted" }
```

PyMuPDF locates the quote in the attached PDF (tolerating line breaks, hyphenation and
ligatures), writes the persistent `/Highlight`, and resolves the 0-based page. The
returned `url` is Bookends' OWN link — read back with `link to displayed PDF` — with only
the page index substituted:
`bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>`. The
`<attachmentID>` is **opaque** and is never derived, templated or guessed. If the quote
cannot be located the script exits non-zero and emits **no link** rather than guessing a
page. A reference with no displayable PDF returns `kind: "ref"` and the reference route
`bookends://sonnysoftware.com/ref/<Library>/<refID>`.

**Do not call `mcp__pdf-highlight-and-deep-link__pdf_link_for_quote` for the URL.** Its
`deepLink` (`…/selection/…`) and `referenceLink` (bare `…/<refID>`) are both BANNED
(R-BOOKENDS-PDF-DEEPLINK-02): the first is fabricated by the MCP — Bookends has no such
route and throws "nil object" — and the second opens the whole library.

- **Quote links AND `Bookends Citation` links → the Bookends-generated PDF deep link.**
  Build a `refID → link` map by reading `link to displayed PDF` from Bookends for every
  refID (see R-BOOKENDS-PDF-DEEPLINK-02), then substitute the MCP's page index into the
  final path segment:
  `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>`.
  Never string-template the `<attachmentID>` — it only ever comes from Bookends.
- **`Bookends Group` links → the library-qualified group link** for the source's subtopic
  child group (see rule 6). Obtain `<LibraryName>` from AppleScript
  `name of front library window` (minus the `.bdb` extension).

**Never** emit the bare reference-id form `bookends://sonnysoftware.com/<refID>`.

Tips that save reruns: if a quote returns `found:false`, the PDF has irregular spacing
— shorten to a cleaner, distinctive sub-fragment (or call `pdf_get_layout` to read the
real token stream) and retry; don't abandon the article, pick another verbatim
sentence that makes the same point. The call is idempotent. Ensure **every** article
ends with **1–3 highlighted quotes** (the per-article cards each need 1–3).

### 5. Sort each reference into its subtopic folder + classify stance

File each reference into the correct subtopic child group with
`mcp__bookends-mcp__bookends_groups { action: "add_references", name: "<Topic> — <Subtopic>", reference_ids: [...] }`.
Give each article a stance label appropriate to the question (for an efficacy/clinical
review: **Supportive / Equivocal / Not supportive**), based on what the paper actually
concludes, not its title. Keep a running tally for the stance table.

### 6. Build ONE combined styled HTML report

Assemble a single self-contained HTML document (inline `<style>`) with the SAME
sections as the Priapism report, in this order, applying all five format rules:

```
Header            — title, subtitle, prepared-date, one line on the evidence base
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
  passage deep link, never a detached block-quote. A reasoned conclusion.
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
> attachment and no PDF — is a DEFECT:** generate the PDF in the sandbox with WeasyPrint, attach
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
> **NO BARE REFERENCE-ID LINKS — applies to EVERY `bookends://` link in the report (added
> 2026-07-10, Skala Pediatric-LLD report).** That report shipped with per-source "Open in
> Bookends" links AND highlighted-quote links in the bare reference-id form
> `bookends://sonnysoftware.com/<id>`. That form selects the reference inside the FULL library
> list, so the target appears amid unrelated MARKED references from other reports — not in its
> own report's context. Ban it for EVERY link:
> - **Quote / highlighted-passage links → the Bookends-generated PDF deep link**
>   `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>`
>   (R-BOOKENDS-PDF-DEEPLINK-02). Use `pdf_link_for_quote` ONLY to write the persistent
>   highlight and to learn the page index; its `deepLink` (`…/selection/…`) is fabricated,
>   throws "nil object", and is BANNED. Never hand-fabricate a link.
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
>     read back from `link to displayed PDF` (R-BOOKENDS-PDF-DEEPLINK-02). The `…/selection/…`
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
  - **HTML→PDF conversion — ALWAYS generate the PDF in the sandbox with WeasyPrint, then
    attach it via the Bookends MCP. This sandbox-generate-then-MCP-attach flow is the
    standard, non-negotiable procedure** (it works from a fully background / Dispatch run):
    1. **Generate the PDF in the sandbox.** Write the finalized HTML into the sandbox and
       convert it to PDF with **WeasyPrint** (`weasyprint <report>.html <report>.pdf`, or
       the `weasyprint` Python API) — a fully background/headless conversion that preserves
       the in-text hyperlinks/anchors as clickable link annotations, both the web citation
       links (`https://doi.org/…`, PubMed / PMC) **AND** the custom-scheme `bookends://…`
       "Open in Bookends" deep links. **NO computer-use** (no mouse, keyboard, or
       screenshots). If WeasyPrint isn't present in the sandbox, `pip install weasyprint
       --break-system-packages` first.
    2. **Attach via the Bookends MCP directly — never via a mounted host folder.** Attach
       the sandbox PDF to the report reference with
       `mcp__bookends-mcp__bookends_add_pdf { items:[{ id, path }] }` (or
       `mcp__pdf-highlight-and-deep-link__bookends_attach_pdf { id, pdf_path }`). Bookends
       copies the file into its **own Attachments folder** itself. **Do NOT** call
       `request_cowork_directory` / rely on a mounted host folder, and **do NOT** hand-write
       the PDF into `~/Documents/Bookends/Attachments/` yourself — in a background /
       Dispatch run the folder-grant prompt is never answered, so the MCP-attach path is the
       only reliable route. (Headless Chrome / wkhtmltopdf are NOT the documented converter
       for this report PDF — use WeasyPrint.)
    - **MANDATORY link-annotation verification — REQUIRED; the run FAILS if it does not
      pass.** Dump the PDF's link annotations (background/headless, **NO computer-use** —
      e.g. with `pypdf`: iterate every page's `/Annots` and collect each annotation's
      `/A/URI`) and confirm the PDF contains BOTH (a) at least one web link
      (`https://doi.org/…`, PubMed / PMC) **AND** (b) at least one `bookends://…` link. If
      either class is missing or flattened, **STOP: do NOT ship a link-less report** — treat
      the run as FAILED and regenerate the HTML/PDF until the check passes.
    - **MANDATORY link-validation gate — REQUIRED; the run FAILS otherwise (added 2026-07-10;
      extended 2026-07-11 for R-BOOKENDS-DUAL-LINK-01 and R-BOOKENDS-PDF-DEEPLINK-02).** Run
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
> **`<page>` is 0-BASED.** The PyMuPDF page index is used **RAW — never `+1`**.
> Boundary-proven on a 31-page PDF: `/30` is accepted, `/31` is rejected.
> Known-good: `bookends://sonnysoftware.com/pdf/Library1/186606/1782012096/5`
> (Bertoch 2025, the 6th page of 31).
>
> **The page MUST be resolved from the QUOTE with PyMuPDF**, by this ladder:
> `highlight annotation` > `exact text` > `prefix (>=30 chars)` > `fuzzy (>=0.72)` >
> `single-page PDF` > `sole highlight`. If none of them hit, the quote is
> **UNRESOLVED** — highlight the passage in Bookends or drop the citation.
> **Never silently emit page 0.**
>
> **The page must NEVER be harvested from Bookends' `link to displayed PDF`.**
> That readback reports whichever page Bookends currently happens to be showing —
> page 0 for a freshly-opened PDF. Harvesting it is what produced ~593 links that
> all ended in `/0` and opened every source on its cover page instead of at the
> quoted passage (2026-07-11 repair).
>
> `link to displayed PDF` is still read back, for the only two things it is
> authoritative about:
> * the **OPAQUE `<attachmentID>`** — read back, never derived or templated.
>   Regenerating an attachment **mints a new attachmentID**, so every ID must be
>   re-read AFTER any attachment rebuild, and links repointed.
> * **after firing a URL**, which page Bookends *actually* navigated to — the only
>   accepted proof that a link lands where it claims. `open`'s exit code is not proof.
>
> `…/selection/…` is a **fabricated route that does not exist** and is BANNED.
> `…/group/…` and `…/ref/…` are real.

### Pre-ship checks (all fatal — `scripts/validate_bookends_links.py`,
`scripts/validate_bookends_attachment.py`)

1. **ZERO `…/selection/…` links** and zero bare reference-id links.
2. **All-page-0 fingerprint** — if *every* `/pdf/` citation on a surface ends in `/0`,
   page 0 must be **CORROBORATED** for every cited reference: a single-page source, a
   highlight annotation physically on page 0, or the quote text literally found on
   page 0. A reference with no evidence for page 0 fails the surface. (`--resolution-report`
   supplies the quotes.)
3. **No unresolved quote pages** — `--resolution-report PAGEMAP.json`; any link whose
   `new_page` is `null` is a hard FAIL.
4. **Observed navigation** — park Bookends on a decoy, fire the URL, then read back BOTH
   `name of displayed PDF` **and** `link to displayed PDF`. The PDF **and the page** must
   match, and the live attachmentID must equal the one in the link (attachment-ID churn
   check). Anything less is not a pass.

5. **The report reference's attachment must be a resolvable, existing, DISPLAYABLE PDF**
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
