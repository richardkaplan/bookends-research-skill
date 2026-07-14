#!/usr/bin/env python3
"""Pre-ship validator for the bookends:// links in a deep-linked report.

WHAT IT REFUSES TO DO
---------------------
It does not pass a link because the URL *looks* right, and it does not pass a
link because `open` returned 0. `open` returns 0 even when Bookends then throws
"An error has occurred: nil object" — that false signal is exactly what lets a
earlier "the links are fixed" reports ship broken.

NO PDF LIBRARY BEYOND pypdf
---------------------------
This validator reads PDFs with `pypdf` only (link annotations, page counts,
page-0 corroboration). There is NO PyMuPDF / `fitz` dependency anywhere in this
skill — the highlight, the page and the deep link all come from the Bookends MCP
(`bookends_annotate_pdf` with mode="exact", then `bookends_get_pdf_content`
mode="annotations"). Do not reintroduce a PDF library to do that work.

PAGE CONVENTION — PROVEN, DO NOT RE-LITIGATE
-------------------------------------------
    bookends://sonnysoftware.com/pdf/<Library>/<refID>/<attachmentID>/<page>

`<page>` is **0-BASED**. Boundary-proven on a 31-page PDF: `/30` is accepted,
`/31` is rejected.

The page MUST come from the ANNOTATION Bookends wrote over the quote — the
annotation-anchored deep link `bookends_get_pdf_content` returns. It must NEVER
be harvested from Bookends' `link to displayed PDF` readback: that link reports
whichever page Bookends currently happens to be showing — which is page 0 for a
freshly-opened PDF. Harvesting it produced ~593 links that all ended in `/0` and
opened every source on its cover page instead of the quoted passage. That is the
bug this validator exists to catch.

`link to displayed PDF` is still read back — but only for what it is
authoritative about: after firing a URL, which PDF/page Bookends actually
navigated to.

WHAT IT ACTUALLY CHECKS
-----------------------
Every link, on every surface the report was written to, verified by OBSERVED
NAVIGATION:

  1. Banned forms are fatal.
       bookends://sonnysoftware.com/selection/<Lib>/<ref>/0/0/0/0/0/0
       bookends://sonnysoftware.com/<ref>                      (bare id)
     Bookends has no /selection/ route. Any tool that
     SYNTHESISES that URL whenever Bookends' own link call fails, so its
     `deepLink` field can never be trusted.

  2. /pdf/<Lib>/<ref>/<attachmentID>/<page0> — the only legal citation form.
     * the URL must be byte-identical to what Bookends itself returns for that
       reference (`link to displayed PDF`). The attachmentID is OPAQUE: it must
       be READ BACK, never derived, templated or guessed.
     * OBSERVED NAVIGATION: park Bookends on a decoy reference, fire the URL,
       then ask Bookends which PDF it is NOW displaying. PASS requires the
       expected PDF to be on screen.
     * the page index must be inside the PDF (pypdf page count).

  3. /ref/<Lib>/<ref> — the fallback for a reference with NO displayable PDF
     (no /pdf/ link can exist for it). OBSERVED NAVIGATION: fire it, then read
     back which reference Bookends now has SELECTED.

  4. /group/<Lib>/<name> — CANNOT be verified from here.
     R-BOOKENDS-NO-APPLESCRIPT-GROUP-VERIFY-01: Bookends' AppleScript
     dictionary exposes NO property for the currently-displayed group, and
     `selected publication items` read after firing a /group/ URL returns a
     STALE selection from before the call — it reports success no matter what
     the URL did, or whether it did anything at all. Firing a group link and
     seeing no alert is NOT a pass; it is the absence of a check.
     Group links are therefore verified by READING THE WINDOW: park Bookends on
     a known group with a known reference count, fire the URL, SCREENSHOT the
     window, and require BOTH the displayed group AND the reference count to
     change to the expected group. The count change is the proof. Hand that
     observation in with --group-nav-log; without it every /group/ link FAILS.

  4b. R-BOOKENDS-VERIFY-EVERY-01 — every DISTINCT link in the SHIPPED FILE is
     fired. No sampling, no representative link, no cousin. `probes` must equal
     `distinct links`, and both numbers are printed. A check that passes against
     a different object than the one that shipped (the report's own header group
     link standing in for 29 citation links; a scan for /selection/ links when
     the broken form was /group/) is a FALSE PASS — worse than no check, because
     it manufactures confidence. --group-map maps each source refID to the
     subtopic group it was filed into; the per-source group links must land on
     THOSE groups, one for one.

  5. A nil-object modal appearing at ANY point during the run is fatal. The
     alert is detected via CoreGraphics window enumeration (no Accessibility
     permission needed), diffed against a baseline captured before the run.

  6. If observation cannot be performed at all — Bookends not running, no front
     library window, AppleScript error — the link FAILS. It never passes by
     default.

SURFACES
--------
  --html PATH   an HTML report (iCloud copy, Bookends HTML attachment, …)
  --pdf  PATH   a PDF render (links read from the real PDF link ANNOTATIONS with
                pypdf — `strings`/grep miss annotations inside compressed
                object streams and will happily call a fully-broken report clean)
  --dt   UUID   a DEVONthink HTML record (source read via AppleScript)

Usage
  python3 validate_bookends_links.py --html report.html
  python3 validate_bookends_links.py --dt UUID --pdf render.pdf --html icloud.html
  python3 validate_bookends_links.py --manifest surfaces.json
  ... --json out.json     write the full result
  ... --library Library1  (default)

Exit 0 = every link on every surface observed to resolve. Non-zero = do not ship.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from urllib.parse import unquote

SELECTION = re.compile(r"bookends://sonnysoftware\.com/selection/([^/]+)/(\d+)[^\"'<>\s)]*")
BARE = re.compile(r"bookends://sonnysoftware\.com/(\d+)")
PDFL = re.compile(r"bookends://sonnysoftware\.com/pdf/([^/]+)/(\d+)/(\d+)/(\d+)")
REFL = re.compile(r"bookends://sonnysoftware\.com/ref/([^/]+)/(\d+)")
GROUP = re.compile(r"bookends://sonnysoftware\.com/group/([^/]+)/([^\"'<>\s)]+)")
ANY = re.compile(r"bookends://sonnysoftware\.com/[^\"'<>\s)]+")


# --------------------------------------------------------------------------
# AppleScript. NOTE: `tab` inside a `tell application id "DNtp"` block resolves
# to DEVONthink's *tab* class, not the tab character — it silently emits the
# literal word "tab" and every parse downstream comes back empty. Use an
# explicit delimiter.
DELIM = "|::|"


# Read back Bookends' link for whatever PDF is on screen. Authoritative for the
# OPAQUE attachmentID and for the page Bookends ACTUALLY navigated to after a
# URL is fired. NEVER a source of truth for what page a citation SHOULD target.
SHOWN_LINK = '''tell application "Bookends"
  tell front library window
    set l to "<none>"
    try
      set l to link to displayed PDF
    end try
    return l
  end tell
end tell'''


def osa(script, timeout=180):
    """Run AppleScript. Written to a UTF-8 file: `osascript -e` mangles
    non-ASCII (em-dashes in record names) and matches nothing."""
    with tempfile.NamedTemporaryFile("w", suffix=".applescript",
                                     encoding="utf-8", delete=False) as fh:
        fh.write(script)
        path = fh.name
    try:
        r = subprocess.run(["osascript", path], capture_output=True,
                           text=True, timeout=timeout)
    finally:
        os.unlink(path)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


FIRE = 'do shell script "open " & quoted form of "%s"'

SHOWN = '''tell application "Bookends"
  tell front library window
    set n to "<none>"
    try
      set n to name of displayed PDF
    end try
    return n
  end tell
end tell'''

SELECTED = '''tell application "Bookends"
  tell front library window
    set s to selected publication items
    if (count of s) is 0 then return "<none>"
    return (id of item 1 of s) as text
  end tell
end tell'''

TRUTH = '''do shell script "open " & quoted form of "bookends://sonnysoftware.com/ref/%s/%s"
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
    return l & "%s" & p
  end tell
end tell''' % ("%s", "%s", DELIM)


def alert_windows():
    """Bookends windows that look like a modal alert rather than the library."""
    try:
        import Quartz
    except ImportError:
        return None  # cannot observe -> caller treats as a hard failure
    wins = Quartz.CGWindowListCopyWindowInfo(0, Quartz.kCGNullWindowID) or []
    out = []
    for w in wins:
        if "Bookends" not in (w.get("kCGWindowOwnerName") or ""):
            continue
        b = w.get("kCGWindowBounds") or {}
        out.append((int(w.get("kCGWindowNumber", 0)),
                    w.get("kCGWindowName") or "",
                    int(b.get("Width", 0)), int(b.get("Height", 0))))
    return sorted(out)


# --------------------------------------------------------------------------
ELLIPSIS = "\u2026"


def links_in_html(text):
    """Every bookends:// URL in the document, minus the elided PLACEHOLDERS a report
    prints in its own methods/legend prose (e.g. `bookends://…/pdf/…`). A placeholder
    is not a link; a real link never contains an ellipsis."""
    return [u for u in ANY.findall(text) if ELLIPSIS not in u]


def placeholders_in_html(text):
    return [u for u in ANY.findall(text) if ELLIPSIS in u]


def _pdf_annot_uris(page):
    """Every /A/URI on a pypdf page object."""
    out = []
    try:
        annots = page.get("/Annots") or []
    except Exception:
        return out
    for a in annots:
        try:
            obj = a.get_object()
            act = obj.get("/A")
            if act is None:
                continue
            uri = act.get_object().get("/URI")
            if uri:
                out.append(str(uri))
        except Exception:
            continue
    return out


def links_in_pdf(path):
    """PDF link ANNOTATIONS — the only trustworthy read. grep/strings cannot see
    annotations stored in compressed object streams. Read with pypdf (no PyMuPDF)."""
    from pypdf import PdfReader
    out = []
    for page in PdfReader(path).pages:
        for u in _pdf_annot_uris(page):
            if u.startswith("bookends://"):
                out.append(u)
    return out


DT_SRC = '''tell application id "DNtp"
  set r to get record with uuid "%s"
  return source of r
end tell'''


def links_in_dt(uuid):
    return ANY.findall(osa(DT_SRC % uuid, timeout=300))


def page_count(path):
    try:
        from pypdf import PdfReader
        return len(PdfReader(path).pages)
    except Exception:
        return None


# --------------------------------------------------------------------------
class Verifier:
    """Observed-navigation verification, memoised per distinct URL."""

    def __init__(self, library="Library1", decoys=(), settle=1.4):
        self.library = library
        # TWO decoys: parking on a reference that the link under test also
        # points at would make "Bookends is showing the right PDF" true before
        # the URL was ever fired — a false PASS. park() always picks a decoy
        # that is NOT the reference being probed.
        self.decoys = [d for d in decoys if d]
        self.settle = settle
        self.truth = {}     # refID -> (bookends link, pdf path)
        self.results = {}   # url -> (ok, detail)
        # url -> observed-window evidence for /group/ links. Empty = no group link
        # can pass (R-BOOKENDS-NO-APPLESCRIPT-GROUP-VERIFY-01).
        self.group_evidence = {}
        self.baseline = alert_windows()
        if self.baseline is None:
            raise RuntimeError(
                "cannot observe Bookends' windows (PyObjC/Quartz missing) — "
                "refusing to validate, because a nil-object modal would go unseen")

    # -- ground truth, straight from Bookends -------------------------------
    def load_truth_cache(self, path):
        """Bookends' link for a reference is stable, so it may be cached across runs.
        The OBSERVATION is never cached — it is re-performed every run."""
        if path and os.path.exists(path):
            for rid, v in json.load(open(path)).items():
                if isinstance(v, list) and v and v[0]:
                    self.truth[rid] = (v[0], v[1] if len(v) > 1 else "", "")

    def bookends_truth(self, rid):
        if rid not in self.truth:
            try:
                raw = osa(TRUTH % (self.library, rid), timeout=90).strip("\n")
            except Exception as exc:
                self.truth[rid] = ("", "", str(exc))
                return self.truth[rid]
            parts = raw.split(DELIM)
            self.truth[rid] = (parts[0].strip() if parts else "",
                               parts[1].strip() if len(parts) > 1 else "", "")
        return self.truth[rid]

    def park(self, avoid=None):
        for d in self.decoys:
            if d == avoid:
                continue
            osa(FIRE % ("bookends://sonnysoftware.com/ref/%s/%s"
                        % (self.library, d)), timeout=60)
            time.sleep(self.settle)
            return d
        return None

    def new_alert(self):
        now = alert_windows()
        if now is None:
            return "window observation unavailable"
        fresh = [w for w in now if w not in self.baseline]
        return fresh or None

    # -- the observation ----------------------------------------------------
    def observe(self, url):
        if url in self.results:
            return self.results[url]
        try:
            r = self._observe(url)
        except Exception as exc:
            r = (False, "observation failed: %s" % exc)
        self.results[url] = r
        return r

    def _observe(self, url):
        m = PDFL.match(url)
        if m:
            lib, rid, att, page = m.groups()
            link, path, err = self.bookends_truth(rid)
            if err:
                return False, "Bookends could not be asked about ref %s: %s" % (rid, err)
            if not link:
                return False, ("ref %s has NO displayable PDF in Bookends — a /pdf/ "
                               "citation link into it cannot resolve" % rid)
            # The library, the refID and the OPAQUE attachmentID must be exactly
            # what Bookends emits — they cannot be derived. The PAGE is ours to set
            # (the Bookends annotation carries it); Bookends' own link merely
            # reports whichever page it happens to be displaying, so page equality
            # is NOT required — only that the page exists in the PDF.
            tm = PDFL.match(link)
            if not tm:
                return False, "Bookends returned an unreadable link for ref %s: %r" % (rid, link)
            t_lib, _t_rid, t_att, _t_page = tm.groups()
            if (lib, att) != (t_lib, t_att):
                return False, ("link does not match Bookends for ref %s: got library=%s "
                               "attachmentID=%s, Bookends says library=%s attachmentID=%s "
                               "— the attachmentID is opaque and must be read back from "
                               "Bookends, never derived" % (rid, lib, att, t_lib, t_att))
            n = page_count(path)
            if n is None:
                return False, "cannot read the target PDF (%s) to bound the page" % path
            if int(page) >= n:
                return False, "page %s out of range (PDF has %d pages)" % (page, n)

            expected = os.path.basename(path)
            parked = self.park(avoid=rid)
            if parked is None:
                return False, ("no decoy reference available to park on — cannot "
                               "prove the URL navigated rather than the PDF already "
                               "being on screen")
            osa(FIRE % url, timeout=60)
            time.sleep(self.settle)
            shown = osa(SHOWN, timeout=60).strip()
            alert = self.new_alert()
            if alert:
                return False, "Bookends raised an alert window: %s" % (alert,)
            if shown != expected:
                return False, ("fired the URL but Bookends is displaying %r, not %r "
                               "— it did not navigate" % (shown, expected))
            # The PDF being right is only half of it. A link whose page segment is
            # wrong still opens the right PDF — on the wrong page. Read back what
            # Bookends actually navigated to and require the page to match.
            live = osa(SHOWN_LINK, timeout=60).strip()
            lm = PDFL.match(live)
            if not lm:
                return False, ("Bookends will not report a link for the PDF it is "
                               "displaying (%r) — the page cannot be observed" % live)
            obs_page = int(lm.group(4))
            if lm.group(3) != att:
                return False, ("ATTACHMENT-ID CHURN: link carries %s, Bookends now says "
                               "%s. The attachment was rebuilt after the link was "
                               "written; re-read every attachmentID" % (att, lm.group(3)))
            if obs_page != int(page):
                return False, ("PAGE: link asked for %s, Bookends navigated to %s — the "
                               "citation opens the right PDF at the wrong place"
                               % (page, obs_page))
            return True, ("observed: navigated from decoy %s to %s page %d"
                          % (parked, expected, obs_page))

        m = REFL.match(url)
        if m:
            lib, rid = m.groups()
            if self.park(avoid=rid) is None:
                return False, "no decoy reference available to park on"
            osa(FIRE % url, timeout=60)
            time.sleep(self.settle)
            sel = osa(SELECTED, timeout=60).strip()
            alert = self.new_alert()
            if alert:
                return False, "Bookends raised an alert window: %s" % (alert,)
            if sel != rid:
                return False, ("fired the URL but Bookends has ref %r selected, not %r"
                               % (sel, rid))
            return True, "observed: Bookends selected ref %s" % rid

        gm = GROUP.match(url)
        if gm:
            # R-BOOKENDS-NO-APPLESCRIPT-GROUP-VERIFY-01.
            # There is NOTHING to ask AppleScript here: Bookends exposes no
            # displayed-group property, and `selected publication items` read after
            # a /group/ URL is the STALE pre-call selection — it says "success"
            # unconditionally. Firing the link and seeing no alert is not evidence
            # either: `open` exits 0 even when Bookends throws a dialog and does
            # nothing. The ONLY accepted proof is the window itself.
            want = unquote(gm.group(2))
            ev = self.group_evidence.get(url)
            if not ev:
                return False, (
                    "GROUP LINK UNVERIFIED (R-BOOKENDS-NO-APPLESCRIPT-GROUP-VERIFY-01): "
                    "AppleScript cannot observe which group Bookends is displaying, so this "
                    "link CANNOT be passed from here. Park Bookends on a known group with a "
                    "known reference count, fire the URL, SCREENSHOT the window, and require "
                    "the displayed group AND the ref count to change to %r (the count change "
                    "is the proof). Record it in --group-nav-log. Never pass a group link "
                    "because firing it raised no alert." % want)
            got = (ev.get("observed_group") or "").strip()
            parked = (ev.get("parked_group") or "").strip()
            pc, oc = ev.get("parked_ref_count"), ev.get("observed_ref_count")
            shot = ev.get("screenshot") or ""
            if got != want:
                return False, ("window shows group %r after firing, expected %r" % (got, want))
            if not parked or parked == want:
                return False, ("evidence parked Bookends on %r — the group under test (or "
                               "nothing). Park elsewhere, or 'the right group is showing' was "
                               "already true before the URL was fired" % parked)
            if not isinstance(pc, int) or not isinstance(oc, int):
                return False, ("evidence carries no before/after reference count — the count "
                               "change IS the proof of navigation")
            if pc == oc:
                return False, ("reference count did not change (%d -> %d): the window did not "
                               "navigate, or it navigated somewhere invisible to this check" % (pc, oc))
            if not shot or not os.path.exists(shot):
                return False, ("no screenshot on file (%r) — group navigation is verified by "
                               "READING THE WINDOW, and the read must be kept" % shot)
            return True, ("observed in the window: %s (%d refs) -> %s (%d refs) [%s]"
                          % (parked, pc, got, oc, os.path.basename(shot)))

        return False, "unrecognised bookends:// route — refusing to pass it"


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# STRUCTURAL PRE-SHIP CHECKS — run before any AppleScript, cheap, and fatal.


def _page0_corroboration(rid, path, quotes):
    """Is page 0 POSITIVELY supported for this reference, or merely asserted?

    Three independent kinds of evidence, any one of which is enough:
      * the source PDF has exactly ONE page — page 0 is the only page there is;
      * a HIGHLIGHT annotation physically sits on page 0 — someone marked the
        passage there;
      * the quote text is literally FOUND on page 0.
    No evidence => page 0 was asserted, not resolved. That is the bug.
    """
    if not path or not os.path.exists(path):
        return None, "source PDF unreadable — page 0 cannot be corroborated"
    try:
        from pypdf import PdfReader
    except ImportError:
        return None, "pypdf unavailable — page 0 cannot be corroborated"
    reader = PdfReader(path)
    n = len(reader.pages)
    if n == 1:
        return "single-page source", ""
    p0 = reader.pages[0]
    for a in (p0.get("/Annots") or []):
        try:
            if a.get_object().get("/Subtype") == "/Highlight":
                return "highlight annotation on page 0", ""
        except Exception:
            continue
    if quotes:
        try:
            t = re.sub(r"\s+", " ", p0.extract_text() or "").strip().lower()
        except Exception:
            t = ""
        for q in quotes:
            q = re.sub(r"\s+", " ", (q or "")).strip().lower()[:70]
            if len(q) >= 30 and q in t:
                return "quote text found on page 0", ""
    return None, ("%d-page source with no highlight on page 0 and no quote text "
                  "matching page 0" % n)


def check_all_page_zero(links, pdf_path_for_ref, quotes_for_ref=None):
    """FAIL the all-page-0 fingerprint.

    Every /pdf/ citation on a surface ending in `/0` is the signature of a page
    segment harvested from Bookends' `link to displayed PDF` readback (which
    reports the page Bookends happens to be showing — page 0 for a freshly
    opened PDF) instead of taken from the annotation Bookends wrote over the quote.

    It is not enough for the pages to LOOK plausible: page 0 must be
    CORROBORATED for every cited reference (see _page0_corroboration). Any
    reference whose page 0 rests on nothing is a FAIL, and the whole surface is
    a FAIL, because that is what a report built from displayed-page readback
    looks like.
    """
    pdfs = [m for m in (PDFL.match(l) for l in links) if m]
    if not pdfs:
        return None
    if any(int(m.group(4)) > 0 for m in pdfs):
        return None                       # at least one real page — not the fingerprint
    quotes_for_ref = quotes_for_ref or (lambda r: [])
    unsupported = []
    for rid in sorted({m.group(2) for m in pdfs}):
        why, detail = _page0_corroboration(rid, pdf_path_for_ref(rid), quotes_for_ref(rid))
        if not why:
            unsupported.append("%s (%s)" % (rid, detail))
    if not unsupported:
        return None
    return ("ALL %d /pdf/ citation(s) on this surface point at page 0 — the fingerprint of "
            "pages harvested from Bookends' displayed page instead of resolved from the "
            "annotation Bookends wrote over the quote. %d cited reference(s) have NO evidence "
            "for page 0: %s. "
            "Re-highlight each quote with bookends_annotate_pdf (mode=exact) and take the page "
            "from the annotation-anchored deep link; the page is 0-BASED."
            % (len(pdfs), len(unsupported), "; ".join(unsupported[:6])))


def quotes_by_ref(path):
    """refID -> [quote, …] from the annotate-and-link step's log, so page 0 can be
    corroborated against the actual quoted text."""
    if not path or not os.path.exists(path):
        return lambda rid: []
    data = json.load(open(path, encoding="utf-8"))
    idx = {}
    for v in data.values():
        for l in v.get("links", []):
            if l.get("quote"):
                idx.setdefault(l["rid"], []).append(l["quote"])
    return lambda rid: idx.get(rid, [])


def check_resolution(path):
    """FAIL on any quote whose page was never resolved.

    `path` is the resolution report the page-resolver writes: a JSON map of
    surface -> {"links": [{"rid":…, "quote":…, "new_page": int|null,
    "method": str}, …]}. A null page means the passage was never located; the
    link would silently keep whatever page it already had (usually 0). Nothing
    ships with an unresolved quote page.
    """
    if not path:
        return None
    data = json.load(open(path, encoding="utf-8"))
    bad = []
    for surface, v in data.items():
        for l in v.get("links", []):
            # A cross-report citation uses the stable /ref/ route on purpose (a
            # /pdf/ link into a report would rot the moment its attachment is
            # rebuilt and the attachmentID churns). It has no page BY DESIGN and
            # is not an unresolved quote.
            if l.get("route") == "ref":
                continue
            if l.get("new_page") is None:
                bad.append((surface, l.get("rid"), (l.get("quote") or "")[:60]))
    if not bad:
        return None
    refs = sorted({b[1] for b in bad})
    return ("%d citation(s) across %d surface(s) have an UNRESOLVED quote page "
            "(refs: %s). bookends_annotate_pdf (mode=exact) never matched the passage in the "
            "source PDF, which means the QUOTE IS WRONG — "
            "highlight the passage in Bookends, or drop the citation. Do not ship a "
            "link whose page is a guess." % (len(bad), len({b[0] for b in bad}),
                                             ", ".join(refs[:8])))


def load_group_map(path):
    """refID -> the subtopic group name the source was filed into (step 5).

    Without it, the per-source group links cannot be checked against anything, and
    the exact bug R-BOOKENDS-VERIFY-EVERY-01 exists to catch — a hardcoded group
    segment sending EVERY source's group link to the same (wrong) group — is
    invisible to a validator that only asks "does this URL resolve".
    """
    if not path or not os.path.exists(path):
        return None
    return {str(k): v for k, v in json.load(open(path, encoding="utf-8")).items()}


def check_group_targets(links, group_map):
    """FATAL structural checks on the group links actually present in the SHIPPED file.

    R-BOOKENDS-VERIFY-EVERY-01. Enumerated from the artifact, never from intent.

      * the hardcoded-constant fingerprint: EVERY per-source group link identical,
        while the report cites sources filed into more than one subtopic group;
      * any per-source group link pointing at the report's own `… — Reports` folder
        (the Reports link belongs to the header cross-nav, not to a source);
      * a group link naming a group no source was ever filed into.

    This is the check the false "group links verified" pass did not perform: it fired
    the report's OWN header link (which legitimately targets Reports), and never looked
    at the 88 per-source links sitting in the same file.
    """
    errs = []
    gms = [m for m in (GROUP.match(l) for l in links) if m]
    if not gms:
        return errs
    names = [unquote(m.group(2)) for m in gms]
    distinct = sorted(set(names))
    reports_links = [n for n in names if n.strip().lower().endswith("reports")]
    # The header cross-nav contributes exactly ONE Reports link. More than one means
    # per-source group links were pointed at the Reports folder.
    if len(reports_links) > 1:
        errs.append(
            "%d group link(s) point at the report's own '%s' folder. Only the ONE header "
            "cross-nav link may target Reports; a per-source 'Bookends Group' link must "
            "target the SOURCE's subtopic group (R-BOOKENDS-VERIFY-EVERY-01: the hardcoded "
            "group-segment fingerprint)." % (len(reports_links), reports_links[0]))
    if group_map is None:
        errs.append(
            "no --group-map supplied: the per-source group links cannot be checked against "
            "the group each source was actually filed into, so an all-links-point-at-one-group "
            "bug would pass unseen (R-BOOKENDS-VERIFY-EVERY-01). Write the refID -> subtopic "
            "group map at step 5 and pass it in.")
        return errs
    filed = sorted(set(group_map.values()))
    unknown = [n for n in distinct
               if n not in filed and not n.strip().lower().endswith("reports")]
    if unknown:
        errs.append("group link(s) name group(s) no source was filed into: %s (filed groups: %s)"
                    % (", ".join(unknown[:5]), ", ".join(filed[:8])))
    per_source = [n for n in distinct if not n.strip().lower().endswith("reports")]
    if len(filed) > 1 and len(per_source) <= 1:
        errs.append(
            "sources are filed across %d subtopic groups (%s) but the shipped file carries "
            "only %d distinct per-source group link(s) — the fingerprint of a hardcoded group "
            "segment (R-BOOKENDS-VERIFY-EVERY-01)."
            % (len(filed), ", ".join(filed[:6]), len(per_source)))
    missing = [g for g in filed if g not in distinct]
    if missing:
        errs.append("no group link in the shipped file targets these groups that sources were "
                    "filed into: %s" % ", ".join(missing[:6]))
    return errs


def gather(args):
    surfaces = []
    for p in args.html:
        surfaces.append(("html", p, links_in_html(open(p, encoding="utf-8",
                                                       errors="replace").read())))
    for p in args.pdf:
        surfaces.append(("pdf", p, links_in_pdf(p)))
    for u in args.dt:
        surfaces.append(("devonthink", u, links_in_dt(u)))
    if args.manifest:
        man = json.load(open(args.manifest))
        for kind, target in man:
            if kind == "html":
                surfaces.append(("html", target,
                                 links_in_html(open(target, encoding="utf-8",
                                                    errors="replace").read())))
            elif kind == "pdf":
                surfaces.append(("pdf", target, links_in_pdf(target)))
            elif kind in ("dt", "devonthink"):
                surfaces.append(("devonthink", target, links_in_dt(target)))
    return surfaces


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", action="append", default=[])
    ap.add_argument("--pdf", action="append", default=[])
    ap.add_argument("--dt", action="append", default=[])
    ap.add_argument("--manifest")
    ap.add_argument("--library", default="Library1")
    ap.add_argument("--decoy", action="append", default=[],
                    help="refID to park Bookends on between probes. Give at least "
                         "TWO (any references WITH a PDF) so a probe never parks on "
                         "the reference it is about to test.")
    ap.add_argument("--resolution-report",
                    help="pagemap JSON from the annotate-and-link step; any link with "
                         "new_page=null (unresolved quote page) is a hard FAIL")
    ap.add_argument("--json")
    ap.add_argument("--group-map",
                    help="refID -> subtopic group name (written at step 5). REQUIRED whenever "
                         "the report carries per-source 'Bookends Group' links: without it a "
                         "hardcoded group segment pointing every source at one group cannot be "
                         "seen (R-BOOKENDS-VERIFY-EVERY-01)")
    ap.add_argument("--group-nav-log",
                    help="observed-window evidence for /group/ links: "
                         "{url: {parked_group, parked_ref_count, observed_group, "
                         "observed_ref_count, screenshot}}. REQUIRED — AppleScript cannot "
                         "observe Bookends' displayed group, so without this every group link "
                         "FAILS (R-BOOKENDS-NO-APPLESCRIPT-GROUP-VERIFY-01)")
    ap.add_argument("--truth-cache",
                    help="refID -> [bookends link, pdf path] JSON; saves re-asking Bookends for links it already gave us")
    args = ap.parse_args()

    surfaces = gather(args)
    if not surfaces:
        print(__doc__)
        return 2

    v = Verifier(library=args.library, decoys=args.decoy or ["264081", "100116"])
    v.load_truth_cache(args.truth_cache)
    if args.group_nav_log and os.path.exists(args.group_nav_log):
        v.group_evidence = json.load(open(args.group_nav_log, encoding="utf-8"))
    group_map = load_group_map(args.group_map)

    out = {"surfaces": [], "verified_urls": {}, "fatal": []}
    quote_lookup = quotes_by_ref(args.resolution_report)
    res_err = check_resolution(args.resolution_report)
    if res_err:
        out["fatal"].append(res_err)
        print("FATAL  %s" % res_err, file=sys.stderr, flush=True)
    total_links = 0
    total_bad = 0

    for kind, target, links in surfaces:
        errs = []
        banned_sel = [l for l in links if SELECTION.match(l)]
        banned_bare = [l for l in links
                       if BARE.match(l) and not (PDFL.match(l) or REFL.match(l)
                                                 or GROUP.match(l) or SELECTION.match(l))]
        if banned_sel:
            errs.append("%d BANNED /selection/ link(s) — Bookends has no such route; "
                        "these throw 'nil object'" % len(banned_sel))
        if banned_bare:
            errs.append("%d BANNED bare reference-id link(s)" % len(banned_bare))
        fp = check_all_page_zero(links, lambda r: v.bookends_truth(r)[1], quote_lookup)
        if fp:
            errs.append(fp)
        errs.extend(check_group_targets(links, group_map))

        # R-BOOKENDS-VERIFY-EVERY-01 — enumerate from the SHIPPED file and probe
        # EVERY distinct link in it. No sampling, no representative, no cousin.
        distinct = sorted(set(links))
        checked = 0
        for url in distinct:
            if SELECTION.match(url) or (BARE.match(url) and not
                                        (PDFL.match(url) or REFL.match(url)
                                         or GROUP.match(url))):
                continue  # already fatal above
            ok, detail = v.observe(url)
            checked += 1
            if not ok:
                errs.append("%s -> %s" % (url, detail))

        # The probe count MUST equal the distinct-link count: every distinct link that
        # shipped was fired. A shortfall means something was skipped, and a verdict over
        # a subset is not a verdict (R-BOOKENDS-VERIFY-EVERY-01).
        expected_probes = len([u for u in distinct
                               if not (SELECTION.match(u) or
                                       (BARE.match(u) and not (PDFL.match(u) or REFL.match(u)
                                                               or GROUP.match(u))))])
        if checked != expected_probes:
            errs.append("probed %d of %d distinct links — a verdict over a subset is not a "
                        "verdict (R-BOOKENDS-VERIFY-EVERY-01)" % (checked, expected_probes))
        total_links += len(links)
        total_bad += len(errs)
        rec = {"surface": kind, "target": target, "links": len(links),
               "distinct_links": len(distinct), "probes": checked,
               "links_observed": checked, "banned_selection": len(banned_sel),
               "banned_bare": len(banned_bare), "errors": errs,
               "verdict": "PASS" if not errs else "FAIL"}
        out["surfaces"].append(rec)
        print("%-4s %-11s links=%-4d distinct=%-4d probed=%-4d  %s"
              % (rec["verdict"], kind, rec["links"], len(distinct), checked,
                 os.path.basename(str(target))), flush=True)
        for e in errs[:5]:
            print("       ! %s" % e, flush=True)
        if len(errs) > 5:
            print("       ! ... and %d more" % (len(errs) - 5), flush=True)

    out["verified_urls"] = {u: {"ok": ok, "detail": d}
                            for u, (ok, d) in v.results.items()}
    failed = [s for s in out["surfaces"] if s["verdict"] == "FAIL"]
    out["summary"] = {
        "surfaces": len(out["surfaces"]),
        "surfaces_passed": len(out["surfaces"]) - len(failed),
        "surfaces_failed": len(failed),
        "links_total": total_links,
        "distinct_urls_observed": len(v.results),
        "distinct_urls_failing": sum(1 for ok, _ in v.results.values() if not ok),
    }
    if args.json:
        json.dump(out, open(args.json, "w"), indent=1, ensure_ascii=False)

    print("")
    print(json.dumps(out["summary"], indent=1))
    if failed or out["fatal"]:
        print("\nFAIL — do not ship. %d surface(s) carry links that could not be "
              "observed to resolve." % len(failed), file=sys.stderr)
        return 1
    print("\nPASS — every DISTINCT link on every surface was fired and observed to resolve "
          "in Bookends (group links via the window, not AppleScript).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
