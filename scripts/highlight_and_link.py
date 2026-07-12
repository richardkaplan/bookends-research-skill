#!/usr/bin/env python3
"""Highlight a quote in a Bookends-attached PDF and return its citation URL.

This REPLACES the pdf-highlight-and-deep-link MCP's link generation.

Why
---
The MCP's `pdf_link_for_quote` / `bookends_get_selection_link` return a
`deepLink` of the form

    bookends://sonnysoftware.com/selection/<Lib>/<refID>/0/0/0/0/0/0

Bookends has NO /selection/ route. The MCP SYNTHESISES that URL whenever its
call into Bookends fails, and it does so silently — so a report can be built,
validated by eye, shipped, and every single citation link in it throws
"An error has occurred: nil object" when the reader clicks. That happened
across ten reports and three storage surfaces before anyone clicked one.

So the link is no longer taken from the MCP at all:

  * the HIGHLIGHT and the PAGE INDEX are produced here, with PyMuPDF, against
    the actual PDF file;
  * the CITATION URL is READ BACK FROM BOOKENDS ITSELF (AppleScript
    `link to displayed PDF`), whose form is
        bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page0>
    The <attachmentID> is OPAQUE — it is Bookends' internal handle for that
    attachment. It CANNOT be derived, templated or guessed; it must be read
    back. Only the page index is ours to set, from PyMuPDF.

A reference with no displayable PDF gets no /pdf/ link at all — it falls back
to the reference route `bookends://sonnysoftware.com/ref/<Library>/<refID>`,
which resolves (it selects the reference) and raises no modal.

Usage
  python3 highlight_and_link.py --ref 264081 --quote "the exact sentence" \
      [--pdf /path/to.pdf] [--library Library1] [--no-highlight]

Emits JSON: {ref, library, page, url, kind, pdf, quote_found, highlighted}
Exit non-zero if the quote could not be located or Bookends would not answer.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unicodedata

import fitz  # PyMuPDF  (pip install pymupdf)

PDFL = re.compile(r"bookends://sonnysoftware\.com/pdf/([^/]+)/(\d+)/(\d+)/(\d+)")


def osa(script, timeout=120):
    """AppleScript via a UTF-8 file — `osascript -e` mangles non-ASCII."""
    with tempfile.NamedTemporaryFile("w", suffix=".applescript",
                                     encoding="utf-8", delete=False) as fh:
        fh.write(script)
        p = fh.name
    try:
        r = subprocess.run(["osascript", p], capture_output=True, text=True,
                           timeout=timeout)
    finally:
        os.unlink(p)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


TRUTH = '''do shell script "open " & quoted form of "bookends://sonnysoftware.com/ref/{lib}/{ref}"
delay 0.9
tell application "Bookends"
  tell front library window
    set l to ""
    set p to ""
    try
      set l to link to displayed PDF
    end try
    try
      set p to path to displayed PDF
    end try
    return l & "|::|" & p
  end tell
end tell'''


def bookends_truth(ref, lib):
    """(citation-link template, pdf path) exactly as BOOKENDS emits them."""
    raw = osa(TRUTH.format(lib=lib, ref=ref), timeout=90).strip("\n")
    parts = raw.split("|::|")
    return (parts[0].strip() if parts else "",
            parts[1].strip() if len(parts) > 1 else "")


# --------------------------------------------------------------------------
def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = (s.replace("’", "'").replace("‘", "'")
          .replace("“", '"').replace("”", '"')
          .replace("–", "-").replace("—", "-")
          .replace("­", ""))
    return re.sub(r"\s+", " ", s).strip()


def find_quote(doc, quote):
    """Locate the quote. PyMuPDF's search_for is exact; PDFs break lines, use
    ligatures and soft hyphens, so fall back to a normalised word-window scan."""
    q = norm(quote)
    for pno in range(doc.page_count):
        rects = doc[pno].search_for(quote)
        if rects:
            return pno, rects
    for pno in range(doc.page_count):
        page = doc[pno]
        if q.lower() in norm(page.get_text()).lower():
            words = [w for w in q.split() if len(w) > 3]
            probes = [" ".join(words[i:i + 6]) for i in range(0, len(words), 6)] or [q]
            rects = []
            for pr in probes:
                rects += page.search_for(pr)
            if rects:
                return pno, rects
            return pno, []
    return None, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--quote", required=True)
    ap.add_argument("--pdf")
    ap.add_argument("--library", default="Library1")
    ap.add_argument("--no-highlight", action="store_true")
    a = ap.parse_args()

    link, path = bookends_truth(a.ref, a.library)
    pdf = a.pdf or path

    if not link or not pdf or not os.path.exists(pdf):
        # No displayable PDF: a /pdf/ citation link into this reference cannot
        # exist. Do NOT fabricate one.
        out = {"ref": a.ref, "library": a.library, "page": None,
               "url": "bookends://sonnysoftware.com/ref/%s/%s" % (a.library, a.ref),
               "kind": "ref", "pdf": pdf or None, "quote_found": False,
               "highlighted": False,
               "note": "reference has no displayable PDF in Bookends; "
                       "citation falls back to the reference route"}
        print(json.dumps(out, indent=1))
        return 0

    m = PDFL.match(link)
    if not m:
        print("Bookends returned an unexpected link for ref %s: %r"
              % (a.ref, link), file=sys.stderr)
        return 2
    lib, ref, att, _page = m.groups()

    doc = fitz.open(pdf)
    pno, rects = find_quote(doc, a.quote)
    if pno is None:
        doc.close()
        print("quote not found in %s — refusing to emit a page-accurate link"
              % pdf, file=sys.stderr)
        return 3

    highlighted = False
    if rects and not a.no_highlight:
        page = doc[pno]
        annot = page.add_highlight_annot(rects)
        annot.set_info(title="Deep Link Report")
        annot.update()
        doc.saveIncr()          # persistent highlight, written into the PDF
        highlighted = True
    doc.close()

    # attachmentID is BOOKENDS' — read back, never derived. Page is ours.
    url = "bookends://sonnysoftware.com/pdf/%s/%s/%s/%d" % (lib, ref, att, pno)
    print(json.dumps({"ref": ref, "library": lib, "page": pno, "url": url,
                      "kind": "pdf", "pdf": pdf, "quote_found": True,
                      "highlighted": highlighted}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
