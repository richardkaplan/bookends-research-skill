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

## Files

```
bookends-research-skill/
├── SKILL.md                     # the parameterized pipeline (topic = only variable)
├── README.md                    # this file
├── .claude-plugin/
│   └── plugin.json              # standalone plugin manifest
└── references/
    └── bookends.md              # Bookends calls, bookends:// scheme, Vancouver, bridge quirks
```

## Credits

**Richard S. Kaplan, MD** — Kaplan Life Care Planning
- Email: rkaplan@kaplanlifecareplan.com
- Website: https://kaplanlifecareplan.com/
