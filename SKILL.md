---
name: bookends-research-skill
description: "Produce a Bookends-native, deep-linked, highlighted research report on ANY topic — the exact pipeline behind the 'excellent' Priapism deep-linked report, parameterized so only the RESEARCH TOPIC changes each run. Creates a new Bookends group named for the topic with topic-appropriate subtopic child groups (always including a Reports folder), finds authoritative sources (guidelines, systematic reviews, key primary studies) via Firecrawl Research / PubMed, attaches full-text PDFs (or flagged abstract-only PDFs) to Bookends references, writes one persistent highlight + page-accurate bookends:// deep link per source, sorts each reference into its subtopic, and assembles ONE combined styled HTML report (executive summary; per-article cards with inline highlighted deep-linked verbatim quotes; stance/source-type table; internally navigable narrative synthesis; Word-ready Academic Summary; and a References section in VANCOUVER format). Saves the report into Bookends (Reports subgroup — the finished HTML is converted headlessly to a hyperlink-preserving PDF and that PDF is attached, label = AI content) AND to iCloud as HTML. Use this skill whenever the user asks for a Bookends research report, a deep-linked / highlighted literature review, an evidence synthesis or annotated bibliography built in Bookends, or says things like 'run the Bookends research skill on <topic>', 'deep-link report in Bookends', 'bookends:// deep-linked quotes', or 'do a <topic> report like the priapism one'. Depends on the bookends-mcp and the pdf-highlight-and-deep-link MCP."
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

The finished report is written to
`<RESEARCH_DIR>/<Topic> — Deep-Linked Report/<Topic> — Deep-Linked Report (AI) <date>.html`.

---

## Home is Bookends (always)

This skill is Bookends-native. The PDFs live as **attachments on Bookends
references**; deep links are **`bookends://…` page/selection links**. Drive Bookends
through its MCP (`mcp__bookends-mcp__*`) and the highlight/deep-link MCP
(`mcp__pdf-highlight-and-deep-link__*`) — **never** through screen automation.

**Dependency.** This skill requires the **pdf-highlight-and-deep-link MCP**
(`github.com/richardkaplan/pdf-highlight-and-deep-link-mcp`), which does the
quote-location, highlight-writing, and `bookends://` deep-link generation. Install
and configure it first, alongside the **bookends-mcp**.

---

## Reading the deep links (Bookends link scheme + how to follow them)

Every highlighted quote is a `bookends://` link to its source PDF. **The `bookends://`
URL scheme works perfectly INSIDE Bookends** — clicking such a link that sits in a
Bookends field (Notes or User1–User4, which hold styled text) opens the PDF at the right
place. Two requirements make this reliable:

1. **Use Bookends' supported link forms (never a fabricated one).** Bookends resolves:
   - a **reference link** `bookends://sonnysoftware.com/<refID>` (selects the reference), and
   - a **page-accurate PDF link** `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>`
     (opens the attached PDF at `page0`, a 0-based page index).

   Both are exactly what Bookends itself emits (Edit → Copy Link for a reference; the PDF
   viewer's Copy Link, or the AppleScript `link to displayed PDF` property). **Do NOT emit
   the old `…/selection/<Library>/<id>/0/0/0/0/0/0` form.** That fabricated "selection" URL
   carries a zero (nil) attachment/annotation id; Bookends tries to resolve object id `0`,
   finds nothing, and throws **"An error has occurred: nil object."** The hand-off from the
   browser succeeds — the error is Bookends failing to resolve the fabricated target. See
   step 4 for how to build the correct link.

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
- **SEARCH SOURCE** defaults to **Firecrawl Research / PubMed** (open-access
  full-text). Honor an explicitly named alternative if the user gives one.
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
   never a web proxy.** Link every source inside the report with a direct `bookends://…`
   link — a page-accurate `…/pdf/<Library>/<refID>/<attachmentID>/<page0>` link or, as a
   fallback, a reference link `bookends://sonnysoftware.com/<refID>` (see step 4). **Never
   the fabricated `…/selection/…/0/…` form** — it makes Bookends throw "nil object." The
   report opens on the Mac, so these native links resolve. Web-only sources → the article
   URL (e.g. PMC).
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
   is **dual-linked**: the citation text hyperlinks to the article on the web (DOI → PMID →
   stored URL) and a trailing **"· Open in Bookends"** `bookends://` link opens it in
   Bookends. The **Academic Summary above stays plain text** (Word-ready); only the
   References list is linked.
5. **The narrative synthesis is internally navigable.** Open Part II with a short table
   of contents whose items are **internal in-document links** (`<a href="#sec-N">`) to
   numbered sections, each carrying a **stable anchor id** (`<h2 id="sec-N">N. …</h2>`).
   These `#sec-N` links live only in the narrative — distinct from the external quote
   deep links (rule 1) and the native source links (rule 2). Do **not** put internal
   section links in the Academic Summary or References; the Academic Summary stays Word-ready plain text, while the References list carries only the rule-6 links (web citation + Open in Bookends), not `#sec-N` anchors.

6. **Every reference carries TWO distinct links — a web citation link and an
   Open-in-Bookends link.** In BOTH the Part I per-article cards and the References
   (Vancouver) list, render each source with:
   - **The citation text (and the article title where shown) hyperlinked to the article
     on the WEB** — a click opens the paper online in the browser. Build the URL from the
     Bookends record in priority order: **DOI → `https://doi.org/<doi>`**, else **PMID →
     `https://pubmed.ncbi.nlm.nih.gov/<pmid>/`**, else the reference's **stored URL /
     publisher link** (`url` field). Pull `doi` / `pmid` / `url` from the record
     (`bookends_get_properties`).
   - **A separate "· Open in Bookends" affordance** (the "Open in Bookends" / "BE" tag)
     carrying the corrected `bookends://` deep link (rule 2 — page-accurate `pdf` form or
     reference-level fallback; never the nil-object `selection/…/0/…` form), delivered as
     styled clickable text (see "Reading the deep links").

   So **clicking the citation → the article's web page; clicking "Open in Bookends" → the
   Bookends app** at that reference/passage. **If a reference has NO DOI, PMID, or URL,**
   leave the citation as **plain text (no dead link)**, keep only the Open-in-Bookends
   link, and note the reference has no online source. Style both links per rule 3, and
   keep them visually distinct (citation vs the "Open in Bookends" tag).

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

### 2. Find authoritative sources

Gather a stance-balanced set of authoritative sources on the topic — **clinical
practice guidelines, systematic reviews / meta-analyses, and key primary studies** —
via **Firecrawl Research** (`firecrawl-research-index` skill /
`mcp__mcp-server-firecrawl__firecrawl_research_*`) and/or **PubMed**. Prefer
**open-access full-text PDFs** spanning supportive, equivocal, and critical findings.
**Target ≥25 references** when that many quality sources exist; favor reviews,
meta-analyses, and guidelines first. Gather fewer only when the literature genuinely
does not support 25 — and say so explicitly. Honor an explicit user count if given.

### 3. Attach PDFs to Bookends references

For each source, create/locate the reference and attach its PDF:
- **De-duplicate first:** `mcp__bookends-mcp__bookends_search` by DOI/PMID/title.
- **Add by identifier:** `mcp__bookends-mcp__bookends_quick_add` (by **DOI/PMID/arXiv**)
  pulls metadata (and full text where Bookends can retrieve it).
- **Attach a downloaded full-text PDF:**
  `mcp__pdf-highlight-and-deep-link__bookends_attach_pdf { id, pdfPath }`, or
  `mcp__bookends-mcp__bookends_add_pdf` for local files / direct PDF URLs / identifier-
  based retrieval.
- **No accessible full text?** Attach a rendered **abstract PDF** with
  `mcp__pdf-highlight-and-deep-link__bookends_attach_abstract_pdf` and **flag it
  abstract-only** in the report (its quote is an abstract key sentence, not a full-text
  deep link).
- Record each reference's Bookends **id** — it is the locator for highlighting,
  linking, and filing. Respect the AppleScript-bridge quirks in *Standing rules* when
  writing any field (no `volume` write, no parentheses).

### 4. One persistent highlight + page-accurate deep link per source

For each source, pick a **verbatim, contiguous** key sentence (full-text sentence for
full-text PDFs; the abstract's key sentence for abstract-only). Then:

```
mcp__pdf-highlight-and-deep-link__pdf_link_for_quote
  params: { "locator": "<bookends id or bookends:// URL>", "quote": "<verbatim fragment>" }
```

It writes a persistent highlight into the attached PDF (keeping a one-time `.bak`) and
returns, among its fields, the **page index** of the match, a **`referenceLink`**
(`bookends://sonnysoftware.com/<refID>`), and a legacy `deepLink` in the
`…/selection/<Library>/<id>/0/<page>/0/0/0/0` form. **Do NOT use that `selection` deepLink
as the quote's `href`** — its zero (nil) attachment/annotation id makes Bookends throw
**"nil object"** when the link is followed. Instead build one of Bookends' **supported**
link forms:

- **Preferred — page-accurate PDF link.** Get the reference's real attachment id from
  Bookends and build
  `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>`
  (`<page0>` = the match's 0-based page index). The attachment id is the 4th path segment
  of Bookends' own `link to displayed PDF` for that reference, obtained via
  `bookends_applescript_run`:

  ```
  tell application "Bookends"
    set selected publication items of front library window to ¬
      (publication items of front library window whose id is <refID>)
    delay 0.3
    return link to displayed PDF of front library window
    -- e.g. bookends://sonnysoftware.com/pdf/Library1/<refID>/<attachmentID>/0
  end tell
  ```

  Take the `<attachmentID>` from that result and substitute your `<page0>` for the
  trailing page segment. This opens the exact PDF at the right page (the persistent
  highlight marks the passage on that page) and never errors.
- **Fallback — reference link.** If the attachment id can't be obtained (e.g. an
  abstract-only ref, or one whose PDF isn't displayable), use the `referenceLink`
  `bookends://sonnysoftware.com/<refID>`. It opens cleanly and selects the reference; the
  in-PDF highlight still marks the passage. This is the form the original "excellent"
  Priapism report used.

Whichever form you use, it must be one Bookends actually resolves — never the fabricated
`selection/.../0/...` URL.

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
                    Bookends highlights; each reference is dual-linked (citation → article on the web; "Open in Bookends" → the item in Bookends);
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
  Summary / Source-type Table — Article (title = BOLD web link → DOI/PMID/URL, plus a "· Open in Bookends" bookends:// link) · one-sentence
                    summary · Journal · Year · Source type (guideline / systematic
                    review / RCT / etc.) · Stance pill + a tally line
  Article-by-Article Summaries — one card per paper: title + stance pill, full citation
                    (citation & title = BOLD web link → DOI/PMID/URL, PLUS a "· Open in Bookends" bookends:// link), a 3–5
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
                    style: numbered, citation order; each entry dual-linked — citation text → article web page (DOI → PMID → stored URL), plus a "· Open in Bookends" bookends:// link; plain-text citation only if no DOI/PMID/URL. (Academic Summary above stays plain-text / Word-ready.)
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

- **Bookends (attach a PDF, not the HTML):** the report is **authored as HTML**, but the
  copy stored **in Bookends must be a PDF** (the iCloud copy stays HTML — see next bullet).
  After the HTML is finalized, convert it to PDF **headlessly, preserving every hyperlink as
  a clickable link annotation** — both the web citation links (`https://doi.org/…`,
  PubMed / PMC) **AND** the custom-scheme `bookends://…` "Open in Bookends" deep links.
  **No computer-use** (no mouse, keyboard, or screenshots) — this runs as a background /
  headless conversion only. File the resulting **PDF** into the **`<Topic> — Reports`
  subgroup**, attached to a report reference, and set the record's **AI-content label
  (label 3)**. Never tag it; never trash the prior report (move nothing to trash — if
  regenerating, add the new one alongside; **supersede** an older Bookends copy by
  renaming/keeping it, e.g. a ` … SUPERSEDED HTML.html` suffix, never deleting). Name it
  with an ` (AI)` suffix, e.g. `<Topic> — Deep-Linked Report (AI)`.
  - **Headless HTML→PDF conversion — APPROVED / PRIMARY converter: headless Chrome print-to-pdf.**
    Convert the finalized HTML to PDF with **headless Google Chrome / Chromium** — the
    approved, confirmed converter (verified 2026-07-04 to preserve clickable link
    annotations for BOTH the web citation links AND the custom-scheme `bookends://` deep
    links). Run it in the background / headless — **NO computer-use** (no mouse, keyboard,
    or screenshots) — using exactly this command:
    `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="<report>.pdf" "file://<ABSOLUTE-PATH>/<report>.html"`
    (Any Chromium build with `--headless=new --print-to-pdf` is equivalent. Do NOT use a
    browser "Print…" dialog or any GUI/computer-use path — background/headless only.
    WeasyPrint / wkhtmltopdf are NOT the documented method and should not be used for this
    report PDF.)
    **MANDATORY link-annotation verification — this check is REQUIRED and the run FAILS if
    it does not pass.** Before attaching, dump the generated PDF's link annotations
    (background/headless, **NO computer-use** — e.g. with `pypdf`: iterate every page's
    `/Annots` and collect each annotation's `/A/URI`) and confirm the PDF contains BOTH
    (a) at least one web link (`https://doi.org/…`, PubMed / PMC) **AND** (b) at least one
    `bookends://…` link. If either class of link is missing or has been flattened, **STOP:
    do NOT attach the PDF and do NOT ship a link-less report** — treat the run as FAILED,
    report which links were lost, and re-render (re-run headless Chrome / regenerate the
    HTML) until the check passes. Only a PDF that passes this verification may be filed
    into Bookends.
    Attach the verified PDF with `bookends_add_pdf` (bookends-mcp) or
    `mcp__pdf-highlight-and-deep-link__bookends_attach_pdf`.
- **iCloud (or configured `RESEARCH_DIR`):** also save the SAME HTML under the
  configured `RESEARCH_DIR` (see *Configuration* — resolved from `$HOME`, never a
  hardcoded username/path):
  `<RESEARCH_DIR>/<Topic> — Deep-Linked Report/<Topic> — Deep-Linked Report (AI) <date>.html`
  (create the folder if needed; `<date>` = today's date). This satisfies the standing
  rule that researched results are saved as a formatted HTML file in iCloud. If iCloud
  Drive is not found at the default location, fall back per *Configuration* and report
  the path actually used.
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
stance tally, and the total number of quotes highlighted and deep-linked (per-article
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
  **supported `bookends://` link forms** (reference link and page-accurate `pdf` link) and
  why the old `selection/…/0/…` form throws "nil object", how to deliver the links into
  Bookends as **styled clickable text** (plain Paste, not Paste and Match Style), Vancouver
  formatting via `bookends_get_formatted_reference`, the AppleScript-bridge
  `volume`/parentheses workaround, group global-unique-name handling, and the label-AI /
  never-trash rules.

---

## Credits

**Richard S. Kaplan, MD** — Kaplan Life Care Planning. Author and maintainer.
- Email: rkaplan@kaplanlifecareplan.com
- Website: https://kaplanlifecareplan.com/
