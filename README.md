# Bookends Research Skill

A reusable Cowork/Dispatch skill that reproduces **exactly** the workflow and report
format of the "excellent" Priapism deep-linked Bookends project — **parameterized so
that only the research TOPIC changes each run.** One deliberate change from the
original: the closing citation list is titled **References** and formatted in
**Vancouver** style (the original ended with a "Works Cited" list).

## What it does

Given a topic, the skill:

1. Creates a **new Bookends group** named for the topic with **topic-appropriate
   subtopic child groups** (derived from the topic's own structure; always including a
   **Reports** folder). Group names are project-qualified to avoid Bookends'
   global-unique-name error, and real nesting is verified.
2. Finds authoritative sources (clinical guidelines, systematic reviews/meta-analyses,
   key primary studies) via **Firecrawl Research / PubMed**.
3. Attaches full-text PDFs to Bookends references (`bookends_quick_add` by DOI/PMID,
   `bookends_add_pdf`); for sources without accessible full text, attaches a rendered
   **abstract PDF** and flags it abstract-only.
4. Writes **one persistent highlight + page-accurate `bookends://` deep link** per
   source.
5. Sorts each reference into the correct subtopic folder.
6. Builds **ONE combined styled HTML report**: executive summary; per-article cards
   with inline highlighted, deep-linked verbatim quotes; a stance/source-type table; an
   internally navigable narrative synthesis; a Word-ready **Academic Summary**; and a
   **References** section in **Vancouver** format.
7. Saves the report **into Bookends** (Reports subgroup, HTML attached, label = AI
   content) **and to iCloud** at
   `Research/<Topic> — Deep-Linked Report/<Topic> — Deep-Linked Report (AI) <date>.html`.

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
- **Firecrawl Research** (or PubMed) for source discovery.

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

**Opening the `bookends://` deep links.** Every highlighted quote links to the exact
passage in the source PDF via a `bookends://` deep link. **To follow one, open the report
in a web browser** — either double-click the attached `.html` in Bookends (it opens in
your default browser) or open the iCloud copy in Safari/Chrome:

- **In a web browser (Safari/Chrome):** click normally — the browser passes the
  `bookends://` scheme to macOS, which routes it back to Bookends and opens the PDF at the
  highlighted passage. (The report is also saved to your iCloud `RESEARCH_DIR`, so you
  always have a browser-openable copy.)
- **Bookends' built-in preview pane cannot follow `bookends://` links on any click** —
  not on a left-click and not on a right-click. Its embedded WebKit viewer follows
  ordinary `http(s)` links itself but never hands a custom `bookends://` link to macOS, so
  the deep links there appear dead even though they are correct.
- **Ordinary web links** (PMC / open-access URLs) work on a normal click everywhere.

Each generated report includes a short version of this note near the top.

## Files

```
bookends-research-skill/
├── SKILL.md                     # the parameterized pipeline (topic = only variable)
├── README.md                    # this file
├── .claude-plugin/
│   └── plugin.json              # standalone plugin manifest
├── references/
│   └── bookends.md              # Bookends calls, bookends:// scheme, Vancouver, bridge quirks
└── examples/
    └── screenshots/             # example report screenshots (see "Example output")
```

## Credits

**Richard S. Kaplan, MD** — Kaplan Life Care Planning
- Email: rkaplan@kaplanlifecareplan.com
- Website: https://kaplanlifecareplan.com/
