# Bookends Research Skill

This is a reusable Claude Cowork/Dispatch skill which researches a topic using the Bookends MCP, creates a new pertinent Group with Folders in Bookends, auto-highlights key sections of the sources, and creates an overall summary of the issues involved in the literature.   Optionally it can detect the relevant issues to search if you provide it with a Devonthink X-Item-Link and in that case it can post the final report both to Bookends and to Devonthink.  It can also post an HTML version of the report to your iCloud.  It can also search PubMed or other sourcese via Firecrawl as an alternative to Bookends Search if you have set up a Firecrawl connector.

I use this in researching multiple sides of academic medical issues; it is equally useful in other disciplines as well.

To install just give Claude the URL for the repository and ask it to install the skill.  Then ask "Do a Bookends Search on ..."

Feel free to contact me if you have any questions/suggestions.


## Contact Info

**Richard S. Kaplan, MD** — Kaplan Life Care Planning
- Email: rkaplan@kaplanlifecareplan.com
- Website: https://kaplanlifecareplan.com/


## What it does

Given a topic, the skill:

1. Creates a **new Bookends group** named for the topic with **topic-appropriate
   subtopic child groups** (derived from the topic's own structure; always including a
   **Reports** folder). Group names are project-qualified to avoid Bookends'
   global-unique-name error, and real nesting is verified.
2. Retrieves authoritative sources (clinical guidelines, systematic reviews/meta-analyses,
   key primary studies) **Bookends-first** — via Bookends' own online search / identifier
   retrieval / automatic PDF download — falling back to **Firecrawl Research / PubMed**
   only for articles Bookends cannot retrieve (logged per article for auditability).
3. Attaches full-text PDFs to Bookends references (`bookends_quick_add` by DOI/PMID,
   `bookends_add_pdf`); for sources without accessible full text, attaches a rendered
   **abstract PDF** and flags it abstract-only.
4. Writes **one persistent highlight + a resolvable `bookends://` deep link** per source
   — a page-accurate `…/pdf/<Library>/<refID>/<attachmentID>/<page0>` link (or a
   reference-level `bookends://sonnysoftware.com/<refID>` fallback); never the fabricated
   `selection/…` form that makes Bookends throw "nil object."
5. Sorts each reference into the correct subtopic folder.
6. Builds **ONE combined styled HTML report**: executive summary; per-article cards
   with inline highlighted, deep-linked verbatim quotes; a stance/source-type table; an
   internally navigable narrative synthesis; a Word-ready **Academic Summary**; and a
   **References** section in **Vancouver** format. **Every reference carries two links** —
   the citation text opens the article on the **web** (DOI → PMID → stored URL) and a
   separate **"· Open in Bookends"** `bookends://` link opens the item in Bookends (in both
   the per-article cards and the References list; a source with no DOI/PMID/URL keeps a
   plain-text citation + only the Bookends link).
7. Saves the report **into Bookends** (Reports subgroup — the finished HTML is converted
   headlessly to a hyperlink-preserving **PDF** via **headless Chrome print-to-pdf** (the
   approved converter; a mandatory `pypdf` check confirms both the web and `bookends://` link
   annotations survived, or the run fails), which is the attached Bookends copy;
   label = AI content) **and to iCloud** as HTML at
   `Research/<Topic> — Deep-Linked Report/<Topic> — Deep-Linked Report (AI) <date>.html`,
   and **delivers the deep-link list into the Bookends record's Notes as styled, clickable
   text** (plain Paste, not Paste and Match Style) so the links are followable inside
   Bookends.

Standing rules baked in: **create-new / never-trash / label AI**; repurpose a
mis-resolved DOI record **in place**; and honor the Bookends AppleScript-bridge quirks
(it rejects the `volume` field and any value containing parentheses — store issue
numbers parenthesis-free; citations still render correctly in the report).

## Trigger

Say things like:

- `Run the Bookends Research Skill on <topic>`
- `Bookends deep-link report on <topic>`
- `Do a <topic> report like the priapism one`
- `Deep-linked / highlighted literature review in Bookends on <topic>`

The topic is the only variable — everything else is fixed by the skill.

## Example output

Screenshots from a real run — *"Is Surgery Effective for Low Back Pain?"* (every source
is published literature; no PHI):

![Top of the report — title, executive summary, and the "how to open the deep links" note](examples/screenshots/01-executive-summary.png)

*Top of the report: the title banner, the bottom-line executive summary with the stance
tally, and the "how to open the deep links" note.*

![Stance / source-type summary table](examples/screenshots/02-stance-table.png)

*The Part I summary table — one row per study with a one-line finding, journal, source
type, and a colored stance pill.*

![A per-article card with an inline highlighted, deep-linked quote](examples/screenshots/03-article-card.png)

*A per-article summary card: the verbatim quote is highlighted and is a bold `bookends://`
deep link ("Open in Bookends") to the exact passage in the source PDF.*

![The Vancouver-style References section](examples/screenshots/04-references.png)

*The closing References list, numbered in citation order and formatted in Vancouver
style.*

![The highlighted passage in the source PDF, opened in Bookends via the deep link](examples/screenshots/05-pdf-highlight-deeplink.png)
*Where a deep link actually lands: the source article itself — Andersson et al., "Open
versus arthroscopic repair of the triangular fibrocartilage complex: a systematic
review," J Exp Orthop 2018;5:6 — opened in Bookends at the exact page, with the skill's
persistent yellow highlight sitting on the quoted conclusion: "There is insufficient
evidence to recommend one technique over the other in clinical practice."*

This is the part that makes the reports worth reading: the skill doesn't just cite its
sources. For each source it writes a **persistent highlight over the key passage directly
into the source PDF stored in Bookends**, and generates a **page-accurate `bookends://`
deep link** to that exact passage. So clicking a quote — or a **Bookends Citation** link —
in the report opens the real article PDF in Bookends, scrolled to the highlighted
sentence. You land on the evidence itself, not on a bibliography entry. The highlight is
written into the PDF and persists in the library, so it is still there the next time you
open that article, report or no report.

Each citation accordingly carries two Bookends links: a **Bookends Group** link, which
opens the subtopic group the source was filed into, and a **Bookends Citation** link,
which opens that specific reference and its highlighted PDF.

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

## Configuration

The only path setting is **`RESEARCH_DIR`**, defined once near the top of `SKILL.md`.
It controls where the HTML report is written to disk (the Bookends save is separate and
unaffected). Nothing personal is hardcoded — the path is resolved from `$HOME`, so the
skill is safe to share publicly.

- **Default:** `$HOME/Library/Mobile Documents/com~apple~CloudDocs/Research` — the
  iCloud Drive root resolved generically from the current user's home directory, then a
  `Research` subfolder. When you run it, it saves to *your* iCloud automatically.
- **Override:** set `RESEARCH_DIR` to your own folder name/path (iCloud or otherwise).
- **Fallback:** if iCloud Drive isn't found, the skill uses a documented local default
  (`$HOME/Research`) or asks where to save, and reports the path used.

## Dependencies

- **bookends-mcp** — Bookends reference/group/attachment operations.
- **pdf-highlight-and-deep-link MCP**
  (`github.com/richardkaplan/pdf-highlight-and-deep-link-mcp`) — quote location,
  persistent highlight writing, and `bookends://` deep-link generation.
- **Firecrawl Research** (or PubMed) — fallback source discovery only, for articles
  Bookends cannot retrieve itself.

## Install

### A. As a standalone plugin (this repo)

This repo is a self-contained Claude plugin (`.claude-plugin/plugin.json` + `SKILL.md`
+ `references/`). Install it via the Cowork **plugin upload** (point it at this repo /
the packaged `.plugin` or `.skill`), then restart Claude Desktop. The skill then appears
in the skills list as **bookends-research-skill** and can be loaded by Cowork and by
Dispatch child agents.

### B. Bundled into `kaplan-research-skills` (recommended, auto-provisioned)

To provision it to **every** Cowork/Dispatch session (including background task
agents), copy the skill folder into the `kaplan-research-skills` plugin alongside the
other skills:

```
kaplan-research-skills/
└── skills/
    ├── deep-link-report/
    ├── firecrawl-research-index/
    ├── …
    └── bookends-research-skill/      ← SKILL.md + references/
```

Bump the `kaplan-research-skills` plugin `version`, reinstall/refresh the plugin, and
restart Claude Desktop. Because that bundle is provisioned to every session, Dispatch
child agents can then load **Bookends Research Skill** without any per-session setup.

## Notes / Known behavior

**The `bookends://` deep links are clickable INSIDE Bookends.** Earlier versions of this
skill claimed Bookends' viewer "cannot follow `bookends://` links on any click." That was
wrong. The `bookends://` scheme works fine inside Bookends — two things have to be right:

- **Use a link form Bookends can resolve.** A reference link
  `bookends://sonnysoftware.com/<refID>` and a page-accurate PDF link
  `bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>` both resolve
  (these are the strings Bookends itself emits via Copy Link / `link to displayed PDF`). The
  old `…/selection/<Library>/<id>/0/0/0/0/0/0` form does **not**: its zero (nil)
  attachment/annotation id makes Bookends throw **"An error has occurred: nil object"** when
  the link is followed. The skill now emits only the supported forms.
- **Put the link in as styled text.** A `bookends://` link is clickable only when it sits in
  a Bookends field (Notes or User1–User4) as **styled text with the live hyperlink**. When
  pasting a link into a Bookends field, use a normal styled **Paste (`⌘V`)** — **not "Paste
  and Match Style,"** which strips the link to dead plain text. (If your `⌘V` is mapped to
  match-style in Bookends → Settings, use Edit → Paste or `⇧⌥⌘V`.) Bookends developer
  tutorial: https://www.youtube.com/watch?v=GCp8R_tUuD8 ; the Bookends User Guide says the
  same under "Hypertext links in reference fields."

Every run now **delivers the report's link list into the report's Bookends record (Notes) as
styled, clickable text**, so you can follow the deep links right inside Bookends.

**Browser path still works (additional option).** You can also follow any link from a web
browser — double-click the attached `.html` in Bookends (it opens in your default browser)
or open the iCloud copy in Safari/Chrome; the browser passes the `bookends://` scheme to
macOS, which routes it to Bookends. Ordinary web links (PMC / open-access URLs) work
everywhere.

Each generated report includes a short version of this note near the top.

## Files

```
bookends-research-skill/
├── SKILL.md                     # the parameterized pipeline (topic = only variable)
├── README.md                    # this file
├── .claude-plugin/
│   └── plugin.json              # standalone plugin manifest
├── references/
│   └── bookends.md              # Bookends calls, supported bookends:// link forms, styled-paste, Vancouver, bridge quirks
├── scripts/
│   └── styled_links_to_clipboard.sh   # load a styled bookends:// link list onto the clipboard for a plain Paste
└── examples/
    └── screenshots/             # example report screenshots (see "Example output")
```

## Credits

**Richard S. Kaplan, MD** — Kaplan Life Care Planning
- Email: rkaplan@kaplanlifecareplan.com
- Website: https://kaplanlifecareplan.com/
