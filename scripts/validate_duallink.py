#!/usr/bin/env python3
"""Pre-ship gate for R-BOOKENDS-DUAL-LINK-01 + R-BOOKENDS-GROUP-LINK-LABEL-01.

Enforces the dual Bookends link standard: EVERY per-source citation must be
accompanied, inline, by a subtopic GROUP link whose anchor text is that group's
own name. Checks a finished Bookends-research HTML report:

  1. Every citation link (a `bookends://.../pdf/Library1/<id>/<att>/<pg>` link whose
     anchor text is a citation label — "Open in Bookends" or "Bookends Citation")
     has a `bookends://.../group/Library1/...` link within the preceding CONTEXT
     characters (i.e. in the same source entry). A citation with no adjacent group
     link is a FAILURE (the dropped-group-link regression).
  2. Every group link's anchor TEXT equals the URL-decoded group name in its own
     href (R-BOOKENDS-GROUP-LINK-LABEL-01) — a generic label like "Bookends Group"
     or "Group" is a FAILURE.
  3. No per-source citation's adjacent group link points at a "…Reports" group
     (sources file to their own subtopic, never to Reports).

Exit 0 = pass, 1 = fail.
"""
import sys, re, html, urllib.parse, argparse
CONTEXT = 300
def strip_tags(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()
CIT_LABEL = re.compile(r"open in bookends|bookends citation", re.I)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("html"); a = ap.parse_args()
    doc = open(a.html, encoding="utf-8").read(); fails = []
    # every anchor
    anchors = [(m.start(), m.group(1), strip_tags(m.group(2)))
               for m in re.finditer(r'<a[^>]*href="(bookends://[^"]+)"[^>]*>(.*?)</a>', doc, re.S)]
    cites = [(pos, href) for (pos, href, txt) in anchors
             if "/pdf/Library1/" in href and CIT_LABEL.search(txt)]
    groups = [(pos, href, txt) for (pos, href, txt) in anchors if "/group/Library1/" in href]
    grp_by_pos = [(pos, href) for (pos, href, txt) in groups]
    # 2 + 3: group link label + reports check
    for pos, href, txt in groups:
        seg = href.split("/group/Library1/", 1)[1]
        name = urllib.parse.unquote(seg)
        if txt != name:
            fails.append(f"GROUP link anchor text != group name: text={txt!r} name={name!r}")
    # 1: each citation must have a preceding group link within CONTEXT chars
    reports_hits = 0
    for pos, href in cites:
        window = doc[max(0, pos - CONTEXT):pos]
        gm = list(re.finditer(r'href="(bookends://sonnysoftware\.com/group/Library1/[^"]+)"', window))
        if not gm:
            snip = strip_tags(doc[max(0, pos-90):pos])[-70:]
            fails.append(f"CITATION link with NO adjacent group link: …{snip} -> {href}")
            continue
        gname = urllib.parse.unquote(gm[-1].group(1).split("/group/Library1/", 1)[1])
        if gname.lower().endswith("reports"):
            reports_hits += 1
            fails.append(f"CITATION's adjacent group link points at a Reports group: {gname}")
    if fails:
        print("DUAL-LINK GATE: FAIL (%d)" % len(fails))
        for f in fails[:60]: print("  - " + f)
        sys.exit(1)
    print("DUAL-LINK GATE: PASS — %d citation links, each paired with a group-name link; "
          "%d group links all correctly labeled" % (len(cites), len(groups)))
    sys.exit(0)
if __name__ == "__main__":
    main()
