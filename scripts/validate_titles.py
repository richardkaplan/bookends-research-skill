#!/usr/bin/env python3
"""Pre-ship gate for R-BOOKENDS-FULL-TITLE-01 and R-BOOKENDS-TABLE-FINDING-01.

Checks a finished Bookends-research HTML report:
  1. No source-title anchor contains an ellipsis ("..." or U+2026).
  2. For every source, the Summary/Source-type table title == the per-article card title
     (both must be the same complete, verbatim published title; a shortened table title FAILS).
  3. With --titles titles.json ({key: "full title"}), every rendered title must equal the
     source's real title verbatim (normalized), never a prefix/subset/paraphrase.
  4. Every Summary/Source-type table finding cell is a real finding: >= MIN_WORDS words and a
     sentence, not a bare statistic/label.

Exit 0 = pass, 1 = fail.
"""
import sys, re, html, json, argparse
MIN_WORDS = 12
def strip_tags(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()
def norm(s): return strip_tags(s).rstrip(".").lower()
def first_web(cell):
    m = re.search(r'<a[^>]*class="web"[^>]*>(.*?)</a>', cell, re.S)
    return strip_tags(m.group(1)) if m else strip_tags(cell)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("html"); ap.add_argument("--titles"); a = ap.parse_args()
    doc = open(a.html, encoding="utf-8").read(); fails = []
    web = [strip_tags(x) for x in re.findall(r'<a[^>]*class="web"[^>]*>(.*?)</a>', doc, re.S)]
    for t in web:
        if "\u2026" in t or "..." in t: fails.append("ELLIPSIS in title: " + t[:100])
    table_titles, findings = [], []
    mt = re.search(r"<table.*?</table>", doc, re.S)
    if mt:
        rows = re.findall(r"<tr>(.*?)</tr>", mt.group(0), re.S)
        if rows:
            hdr = [strip_tags(c).lower() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", rows[0], re.S)]
            def col(*keys):
                for i, h in enumerate(hdr):
                    if any(k in h for k in keys): return i
                return None
            ti, fi = col("source", "title"), col("finding", "summary")
            for r in rows[1:]:
                cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)
                if ti is not None and ti < len(cells): table_titles.append(first_web(cells[ti]))
                if fi is not None and fi < len(cells): findings.append(strip_tags(cells[fi]))
    card_web = [strip_tags(am.group(1)) for m in re.findall(r"<h4>(.*?)</h4>", doc, re.S)
                for am in [re.search(r'<a[^>]*class="web"[^>]*>(.*?)</a>', m, re.S)] if am]
    cardset = set(norm(x) for x in card_web)
    for tt in table_titles:
        if cardset and norm(tt) not in cardset:
            fails.append("TABLE title not matched by a full CARD title (possible truncation): " + tt[:100])
    for f in findings:
        if len(f.split()) < MIN_WORDS or not re.search(r"[a-z].*[.;]", f):
            fails.append("FINDING too short/label-like (%d words): %s" % (len(f.split()), f[:100]))
    if a.titles:
        want = json.load(open(a.titles, encoding="utf-8"))
        wn = set(norm(v) for v in want.values())
        for t in set(table_titles) | set(card_web):
            if norm(t) not in wn:
                fails.append("Rendered title not verbatim-equal to a known source title: " + t[:100])
    if fails:
        print("TITLE/FINDING GATE: FAIL (%d)" % len(fails))
        for f in fails: print("  - " + f)
        sys.exit(1)
    print("TITLE/FINDING GATE: PASS — %d table titles, %d card titles, %d findings"
          % (len(table_titles), len(card_web), len(findings)))
    sys.exit(0)
if __name__ == "__main__": main()
