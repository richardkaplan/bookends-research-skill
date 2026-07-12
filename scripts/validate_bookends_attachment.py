#!/usr/bin/env python3
"""Pre-ship check (FATAL): a Bookends report reference must have a RESOLVABLE,
EXISTING PDF as its FIRST attachment.

WHY THIS EXISTS
---------------
Bookends' attachment display pane renders PDFs, images, webarchives, and the text of
doc/docx/rtf/text files.  It CANNOT render a raw .html file.  The Bookends User Guide:

    "If there is an attachment that is not a PDF, image, or compatible file
     (e.g. a word processing document), Bookends will indicate that there is an
     attachment but that it can't be displayed."

    "The name of the attachment is displayed in a pop-up menu at the bottom, and if
     there is more than one attachment you can select which one to show."

So a report reference whose attachment is the report HTML shows the FILENAME in the
bottom bar and an EMPTY attachments pane.  It looks like nothing is attached.  That is
the 2026-07-11 defect: the deep-link pipeline (and the link-repair sweep) left the HTML
render attached to Bookends report references instead of the hyperlink-preserving PDF.

Two further ways a report attachment goes dark, both also checked here:
  * the attachments field holds an ABSOLUTE/colon path (":Users:...") instead of a bare
    filename resolved against Bookends' default attachments folder; and
  * the file was MOVED after attaching (e.g. superseded into "Temp AI Files"), so the
    recorded name no longer resolves.

INVARIANTS ENFORCED (any violation = FATAL, do not ship)
  1. The reference HAS at least one attachment.
  2. The FIRST attachment is a .pdf  (Bookends displays the first one by default).
  3. That PDF EXISTS on disk.
  4. It is recorded as a BARE FILENAME inside Bookends' default attachments folder,
     not an absolute/colon path.
  5. The PDF still carries its bookends:// link annotations (the deep links survived
     the HTML->PDF render).

Usage:
    validate_bookends_attachment.py 95928 13738 ...      # explicit reference ids
    validate_bookends_attachment.py --group "Priapism — Reports"
    validate_bookends_attachment.py --all-reports        # every "… Reports" group

Exit code 0 = all pass.  Non-zero = at least one FATAL violation.
"""
import argparse
import os
import subprocess
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

ATT = os.path.expanduser("~/Documents/Bookends/Attachments")


def osa(script, timeout=300):
    p = subprocess.run(["osascript", "-e", script], capture_output=True,
                       text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip())
    return p.stdout


def refs_for(ids, group, all_reports):
    if ids:
        sel = 'set hits to {}\n' + "".join(
            'set end of hits to (first publication item whose id is "%s")\n' % i
            for i in ids)
    elif group:
        sel = ('set hits to (every publication item of group item named "%s")\n'
               % group.replace('"', '\\"'))
    elif all_reports:
        sel = ('set hits to {}\n'
               'repeat with g in (every group item whose name contains "Reports")\n'
               '  repeat with h in (every publication item of g)\n'
               '    set end of hits to h\n'
               '  end repeat\n'
               'end repeat\n')
    else:
        raise SystemExit("give reference ids, --group, or --all-reports")

    script = ('tell application "Bookends"\n tell front library window\n'
              '  set out to ""\n  ' + sel +
              '  repeat with h in hits\n'
              '    set out to out & (id of h) & "|::|" & (title of h) & "|::|" '
              '& (attachments of h) & "|:::|"\n'
              '  end repeat\n  return out\n end tell\nend tell')
    rows = []
    for chunk in osa(script).split("|:::|"):
        if not chunk.strip():
            continue
        p = chunk.split("|::|")
        if len(p) >= 3:
            rows.append({"id": p[0].strip(), "title": p[1].strip(),
                         "attachments": [n for n in p[2].split("\n") if n.strip()]})
    return rows


def check(ref):
    fails = []
    names = ref["attachments"]
    if not names:
        return ["no attachment recorded at all"]

    first = names[0]

    # 4. bare filename, not an absolute / HFS-colon path
    if first.startswith(":") or first.startswith("/"):
        fails.append("first attachment is an absolute/colon path, not a bare filename "
                     "resolved against the Bookends attachments folder: %r" % first)
        path = "/" + first.lstrip(":").replace(":", "/") if first.startswith(":") else first
    else:
        path = os.path.join(ATT, first)

    # 2. must be a PDF -- Bookends cannot render .html in the attachment pane
    ext = os.path.splitext(first)[1].lower()
    if ext != ".pdf":
        fails.append("first attachment is %s, not .pdf -- Bookends will show the "
                     "filename but an EMPTY attachments pane (raw HTML is not a "
                     "displayable attachment type)" % (ext or "(no extension)"))

    # 3. must exist
    if not os.path.exists(path):
        fails.append("first attachment does not exist on disk: %s "
                     "(was it moved/superseded after attaching?)" % path)
        return fails

    # 5. deep links survived the render
    if ext == ".pdf" and fitz is not None:
        n = 0
        with fitz.open(path) as doc:
            for page in doc:
                for l in page.get_links():
                    if (l.get("uri") or "").startswith("bookends://"):
                        n += 1
        if n == 0:
            fails.append("attached PDF carries ZERO bookends:// link annotations -- "
                         "the deep links were flattened by the HTML->PDF render")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--group")
    ap.add_argument("--all-reports", action="store_true")
    a = ap.parse_args()

    refs = refs_for(a.ids, a.group, a.all_reports)
    bad = 0
    for r in refs:
        fails = check(r)
        if fails:
            bad += 1
            print("FATAL  %-8s %s" % (r["id"], r["title"][:70]))
            for f in fails:
                print("         - %s" % f)
        else:
            print("ok     %-8s %s" % (r["id"], r["title"][:70]))

    print("\n%d checked, %d FATAL" % (len(refs), bad))
    if bad:
        print("A report reference must have a resolvable, existing PDF as its FIRST "
              "attachment. Render the finalized HTML to PDF with headless Chrome "
              "(--print-to-pdf), verify the link annotations, and attach the PDF "
              "FIRST (the HTML may stay as a secondary attachment). DO NOT SHIP.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
