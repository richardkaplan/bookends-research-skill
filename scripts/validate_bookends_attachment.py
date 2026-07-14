#!/usr/bin/env python3
"""Pre-ship checks (FATAL) on Bookends attachments.

TWO CHECKS, TWO POPULATIONS
---------------------------

A) REPORT references  (default mode)
   A Bookends report reference must have a RESOLVABLE, EXISTING PDF as its FIRST
   attachment.

   Bookends' attachment display pane renders PDFs, images, webarchives, and the text of
   doc/docx/rtf/text files.  It CANNOT render a raw .html file.  The Bookends User Guide:

       "If there is an attachment that is not a PDF, image, or compatible file
        (e.g. a word processing document), Bookends will indicate that there is an
        attachment but that it can't be displayed."

       "The name of the attachment is displayed in a pop-up menu at the bottom, and if
        there is more than one attachment you can select which one to show."

   So a report reference whose attachment is the report HTML shows the FILENAME in the
   bottom bar and an EMPTY attachments pane.  It looks like nothing is attached.

   Two further ways a report attachment goes dark, both also checked here:
     * the attachments field holds an ABSOLUTE/colon path (":Users:...") instead of a bare
       filename resolved against Bookends' default attachments folder; and
     * the file was MOVED after attaching (e.g. superseded into "Temp AI Files"), so the
       recorded name no longer resolves.

   INVARIANTS (any violation = FATAL, do not ship)
     1. The reference HAS at least one attachment.
     2. The FIRST attachment is a .pdf  (Bookends displays the first one by default).
     3. That PDF EXISTS on disk.
     4. It is recorded as a BARE FILENAME inside Bookends' default attachments folder,
        not an absolute/colon path.
     5. The PDF still carries its bookends:// link annotations (the deep links survived
        the HTML->PDF render).

B) SOURCE references  (--sources)   R-BOOKENDS-ATTACHMENT-PROVENANCE-01
   Every source's FIRST attachment must actually BELONG to that reference.

   A citation link can be perfectly well-formed, carry a real (opaque) attachmentID,
   resolve with no error and no alert, pass observed navigation — and STILL OPEN THE WRONG
   PAPER, because the reference carries a STRAY FIRST ATTACHMENT: a PDF belonging to some
   other article, left behind by a bad download, a mis-resolved DOI, or an attach against
   the wrong record.  Bookends displays AND ANNOTATES the first attachment, so the
   highlight, the page and the deep link are all faithfully computed against the wrong PDF.
   Link-level validation cannot see this: it validates the link, not the paper.

   INVARIANTS (any violation = FATAL)
     1. The reference HAS at least one attachment, and the FIRST is a .pdf that exists.
     2. The first attachment's OPENING PAGES contain the reference's TITLE (matched on
        content words, so subtitle/case differences don't trip it).  Corroborating signals
        (first author's surname, the year) are reported but the title match is the gate.
   On failure: re-attach the correct PDF FIRST (never delete the stray -- detach or
   supersede it), then RE-READ every deep link for that reference: the attachmentID churns
   whenever an attachment is rebuilt.

NO PyMuPDF.  PDFs are read with pypdf only.

Usage:
    validate_bookends_attachment.py 95928 13738 ...        # report refs, explicit ids
    validate_bookends_attachment.py --group "<Topic> — Reports"
    validate_bookends_attachment.py --all-reports          # every "… Reports" group
    validate_bookends_attachment.py --sources --group "<Topic> — Diagnosis"
    validate_bookends_attachment.py --sources 8721 8722    # source refs, explicit ids

Exit code 0 = all pass.  Non-zero = at least one FATAL violation.
"""
import argparse
import os
import re
import subprocess
import sys

try:
    from pypdf import PdfReader
except ImportError:                                    # checked at point of use
    PdfReader = None

ATT = os.path.expanduser("~/Documents/Bookends/Attachments")

STOP = {"the", "a", "an", "of", "and", "or", "in", "on", "for", "to", "with",
        "after", "before", "from", "by", "at", "as", "is", "are", "its", "into",
        "study", "trial", "randomized", "randomised", "systematic", "review"}


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
              '& (attachments of h) & "|::|" & (authors of h) & "|::|" '
              '& (publication date of h) & "|:::|"\n'
              '  end repeat\n  return out\n end tell\nend tell')
    rows = []
    for chunk in osa(script).split("|:::|"):
        if not chunk.strip():
            continue
        p = chunk.split("|::|")
        if len(p) >= 3:
            rows.append({"id": p[0].strip(), "title": p[1].strip(),
                         "attachments": [n for n in p[2].split("\n") if n.strip()],
                         "authors": p[3].strip() if len(p) > 3 else "",
                         "date": p[4].strip() if len(p) > 4 else ""})
    return rows


def resolve(first):
    """(path, complaint-or-None) for an attachment name as Bookends records it."""
    if first.startswith(":"):
        return "/" + first.lstrip(":").replace(":", "/"), (
            "first attachment is an HFS-colon path, not a bare filename resolved "
            "against the Bookends attachments folder: %r" % first)
    if first.startswith("/"):
        return first, ("first attachment is an absolute path, not a bare filename "
                       "resolved against the Bookends attachments folder: %r" % first)
    return os.path.join(ATT, first), None


def bookends_link_count(path):
    n = 0
    for page in PdfReader(path).pages:
        for a in (page.get("/Annots") or []):
            try:
                act = a.get_object().get("/A")
                uri = act.get_object().get("/URI") if act is not None else None
            except Exception:
                continue
            if uri and str(uri).startswith("bookends://"):
                n += 1
    return n


def opening_text(path, pages=3):
    reader = PdfReader(path)
    out = []
    for page in reader.pages[:pages]:
        try:
            out.append(page.extract_text() or "")
        except Exception:
            pass
    return re.sub(r"[^a-z0-9 ]+", " ", " ".join(out).lower())


def words(s):
    return [w for w in re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower()).split()
            if len(w) > 3 and w not in STOP]


# --------------------------------------------------------------------------
def check_report(ref):
    fails = []
    names = ref["attachments"]
    if not names:
        return ["no attachment recorded at all"]

    first = names[0]
    path, complaint = resolve(first)
    if complaint:
        fails.append(complaint)

    ext = os.path.splitext(first)[1].lower()
    if ext != ".pdf":
        fails.append("first attachment is %s, not .pdf -- Bookends will show the "
                     "filename but an EMPTY attachments pane (raw HTML is not a "
                     "displayable attachment type)" % (ext or "(no extension)"))

    if not os.path.exists(path):
        fails.append("first attachment does not exist on disk: %s "
                     "(was it moved/superseded after attaching?)" % path)
        return fails

    if ext == ".pdf" and PdfReader is not None:
        if bookends_link_count(path) == 0:
            fails.append("attached PDF carries ZERO bookends:// link annotations -- "
                         "the deep links were flattened by the HTML->PDF render")
    return fails


def check_source(ref, threshold=0.5):
    """R-BOOKENDS-ATTACHMENT-PROVENANCE-01: is the FIRST attachment this paper?"""
    fails = []
    names = ref["attachments"]
    if not names:
        return ["no attachment recorded at all -- nothing to highlight or link"]

    first = names[0]
    path, complaint = resolve(first)
    if complaint:
        fails.append(complaint)

    if os.path.splitext(first)[1].lower() != ".pdf":
        fails.append("first attachment is not a .pdf (%r) -- Bookends annotates the "
                     "FIRST attachment, so the highlight and the deep link would be "
                     "computed against it" % first)
        return fails
    if not os.path.exists(path):
        fails.append("first attachment does not exist on disk: %s" % path)
        return fails
    if PdfReader is None:
        return ["pypdf unavailable -- attachment provenance cannot be verified "
                "(pip install pypdf)"]

    title_words = words(ref["title"])
    if not title_words:
        return ["reference has no usable title -- provenance cannot be verified"]

    try:
        text = opening_text(path)
    except Exception as exc:
        return ["cannot read the first attachment (%s): %s" % (path, exc)]
    if len(text.strip()) < 40:
        return ["first attachment has no extractable text (scanned/blank?) -- "
                "provenance cannot be verified: %s" % first]

    hit = sum(1 for w in set(title_words) if w in text)
    frac = hit / float(len(set(title_words)))
    if frac < threshold:
        extra = ""
        surname = (ref["authors"].split(",")[0] or "").strip().lower()
        if surname and surname in text:
            extra = " (the first author's surname DOES appear -- check for a wrong "
            extra += "edition/companion paper)"
        fails.append(
            "STRAY FIRST ATTACHMENT: only %d/%d title words from this reference appear "
            "in the first 3 pages of %s (%.0f%%, need %.0f%%). Bookends annotates the "
            "FIRST attachment, so every highlight, page and deep link built from this "
            "reference would silently point at ANOTHER PAPER. Re-attach the correct PDF "
            "first (detach/supersede the stray -- never delete it), then RE-READ every "
            "deep link: the attachmentID churns on re-attach.%s"
            % (hit, len(set(title_words)), first, 100 * frac, 100 * threshold, extra))
    elif len(names) > 1:
        # First one matched — not a failure. But an EXTRA attachment is how a stray ends
        # up in front in the first place, so say so out loud.
        print("       note: %d attachments; the first one matches (%.0f%% of title "
              "words). Keep it FIRST." % (len(names), 100 * frac))
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--group")
    ap.add_argument("--all-reports", action="store_true")
    ap.add_argument("--sources", action="store_true",
                    help="check SOURCE references: the first attachment must be the "
                         "paper the reference claims to be "
                         "(R-BOOKENDS-ATTACHMENT-PROVENANCE-01)")
    ap.add_argument("--threshold", type=float, default=0.5,
                    help="fraction of the reference's title words that must appear in "
                         "the PDF's opening pages (default 0.5)")
    a = ap.parse_args()

    refs = refs_for(a.ids, a.group, a.all_reports)
    bad = 0
    for r in refs:
        fails = (check_source(r, a.threshold) if a.sources else check_report(r))
        if fails:
            bad += 1
            print("FATAL  %-8s %s" % (r["id"], r["title"][:70]))
            for f in fails:
                print("         - %s" % f)
        else:
            print("ok     %-8s %s" % (r["id"], r["title"][:70]))

    print("\n%d checked, %d FATAL" % (len(refs), bad))
    if bad and a.sources:
        print("R-BOOKENDS-ATTACHMENT-PROVENANCE-01: a source's FIRST attachment must be "
              "the paper the reference claims to be. A stray first attachment yields a "
              "link that is well-formed, resolves cleanly, and OPENS THE WRONG PAPER. "
              "Fix the attachment order, re-read the deep links, DO NOT SHIP.")
    elif bad:
        print("A report reference must have a resolvable, existing PDF as its FIRST "
              "attachment. Render the finalized HTML to PDF with headless Chrome "
              "(--print-to-pdf), verify the link annotations, and attach the PDF "
              "FIRST (the HTML may stay as a secondary attachment). DO NOT SHIP.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
