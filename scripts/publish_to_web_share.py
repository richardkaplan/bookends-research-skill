#!/usr/bin/env python3
"""
publish_to_web_share.py — R-BOOKENDS-PUBLISH-WEB-01

Publish a research report (or a whole research folder) that has ALREADY been
written into RESEARCH_DIR onto a static web share, and print the resulting live
https:// URL so it can be handed to a remote reader (phone / remote client).

Design rules
------------
* NO personal paths, usernames or hostnames are baked in. Everything comes from
  the environment or an untracked local config file, so this file is safe to
  publish in a public repo.
* The report is copied BYTE-FOR-BYTE. Content is never rewritten. In particular
  `bookends://` and `x-devonthink-item://` deep links are left intact: they are
  macOS app schemes, they will not resolve in a remote browser, and silently
  mangling them would be worse than leaving them honest.
* PHI GUARD: only files that live under RESEARCH_DIR are publishable. A report
  that was deliberately kept out of RESEARCH_DIR (the PHI path — DEVONthink and
  Bookends only) can never be published by this script.

Config (env, or ~/.config/bookends-research/web-publish.env as KEY=VALUE lines):
    RESEARCH_DIR        default: $HOME/Library/Mobile Documents/com~apple~CloudDocs/Research
    WEB_SHARE_MOUNT     e.g. /Volumes/web         (mounted SMB/AFP static web share)
    WEB_BASE_URL        e.g. https://example.tld  (what WEB_SHARE_MOUNT is served as)
    WEB_PUBLISH_SUBDIR  default: Research         (subdir of the share to publish under)

If WEB_SHARE_MOUNT / WEB_BASE_URL are unset, or the share is not mounted, the
script exits non-zero with a clear message. The skill must then TELL THE USER
that no web URL was produced — never silently skip.

Usage:
    publish_to_web_share.py <file-or-folder> [...]   # publish these
    publish_to_web_share.py --all <folder>           # publish whole tree + index
Prints a JSON manifest on stdout.
"""
import hashlib
import html
import json
import os
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from urllib.parse import quote

CONFIG_FILE = os.path.expanduser("~/.config/bookends-research/web-publish.env")
DEFAULT_RESEARCH_DIR = os.path.expanduser(
    "~/Library/Mobile Documents/com~apple~CloudDocs/Research"
)

SCHEMES = {
    "bookends": re.compile(r"bookends://[^\"'\s>)]+"),
    "devonthink": re.compile(r"x-devonthink-item://[^\"'\s>)]+"),
    "web": re.compile(r"https?://[^\"'\s>)]+"),
}


def load_config():
    cfg = {}
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    cfg[k.strip()] = v.strip().strip('"').strip("'")
    cfg.update({k: v for k, v in os.environ.items() if k in (
        "RESEARCH_DIR", "WEB_SHARE_MOUNT", "WEB_BASE_URL", "WEB_PUBLISH_SUBDIR")})
    cfg.setdefault("RESEARCH_DIR", DEFAULT_RESEARCH_DIR)
    cfg.setdefault("WEB_PUBLISH_SUBDIR", "Research")
    cfg["RESEARCH_DIR"] = os.path.expanduser(cfg["RESEARCH_DIR"])
    return cfg


def die(msg):
    sys.stderr.write("PUBLISH FAILED: %s\n" % msg)
    sys.exit(1)


def slug(name):
    base, ext = os.path.splitext(name)
    s = unicodedata.normalize("NFKD", base)
    s = s.replace("—", "-").replace("–", "-").replace("&", "and")
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-._") or "report"
    return s + ext.lower()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_links(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        t = f.read()
    return {k: len(rx.findall(t)) for k, rx in SCHEMES.items()}


def publish_one(src, cfg):
    """Copy one report to the share. Returns a manifest dict."""
    research = os.path.realpath(cfg["RESEARCH_DIR"])
    src = os.path.realpath(src)
    # --- PHI guard -------------------------------------------------------
    if not (src + os.sep).startswith(research + os.sep):
        die("refusing to publish %s — it is not under RESEARCH_DIR (%s). Reports "
            "deliberately kept out of RESEARCH_DIR are PHI and must not be published."
            % (src, research))

    rel = os.path.relpath(src, research)
    parts = [slug(p) for p in rel.split(os.sep)]
    rel_web = "/".join(parts)
    dst = os.path.join(cfg["WEB_SHARE_MOUNT"], cfg["WEB_PUBLISH_SUBDIR"], *parts)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    # copyfile, NOT copy2: SMB shares reject chflags() and copy2 dies on it.
    shutil.copyfile(src, dst)
    if sha256(src) != sha256(dst):
        die("byte-for-byte copy verification failed for %s" % src)

    url = "%s/%s/%s" % (
        cfg["WEB_BASE_URL"].rstrip("/"),
        quote(cfg["WEB_PUBLISH_SUBDIR"].strip("/")),
        quote(rel_web),
    )
    return {
        "title": os.path.splitext(os.path.basename(src))[0],
        "src": src,
        "rel_web": rel_web,
        "url": url,
        "bytes": os.path.getsize(src),
        "verified": True,
        "links": scan_links(src),
        "superseded": "Temp AI Files" in rel or "SUPERSEDED" in os.path.basename(src),
    }


def write_index(collection_dir, items, cfg):
    """Write an index.html listing every report in one collection folder."""
    def rows(group):
        out = []
        for i in sorted(group, key=lambda x: x["rel_web"]):
            lk = i["links"]
            depth = len(collection_rel.split("/"))
            href = "/".join(i["rel_web"].split("/")[depth:])
            out.append(
                '<tr><td><a href="%s">%s</a></td><td class=n>%s</td>'
                "<td class=n>%s</td><td class=n>%s</td></tr>"
                % (quote(href), html.escape(i["title"]), lk["web"],
                   lk["bookends"], lk["devonthink"])
            )
        return "\n".join(out)

    collection_rel = "/".join(
        slug(p) for p in os.path.relpath(
            os.path.realpath(collection_dir),
            os.path.realpath(cfg["RESEARCH_DIR"]),
        ).split(os.sep)
    )
    live = [i for i in items if not i["superseded"]]
    old = [i for i in items if i["superseded"]]
    head = ("<tr><th>Report</th><th class=n>Web/DOI</th><th class=n>bookends://</th>"
            "<th class=n>x-devonthink</th></tr>")
    doc = """<!DOCTYPE html><html lang=en><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>%(name)s</title>
<style>
body{font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
margin:0;padding:24px;max-width:1000px;color:#1d1d1f}
h1{font-size:1.5rem;margin:0 0 4px}h2{font-size:1.05rem;margin:32px 0 8px;color:#444}
.sub{color:#6b6b70;margin-bottom:24px;font-size:.9rem}
table{border-collapse:collapse;width:100%%}th,td{text-align:left;padding:8px 10px;
border-bottom:1px solid #e5e5ea;vertical-align:top}th{font-size:.75rem;text-transform:uppercase;
letter-spacing:.04em;color:#6b6b70}td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
a{color:#0064d2;text-decoration:none}a:hover{text-decoration:underline}
.note{background:#fff8e6;border:1px solid #f0dfae;border-radius:8px;padding:12px 14px;
font-size:.86rem;margin:20px 0}
details{margin-top:8px}summary{cursor:pointer;color:#6b6b70;font-size:.9rem}
</style>
<h1>%(name)s</h1>
<div class=sub>%(n)d reports &middot; published %(ts)s</div>
<div class=note><b>Reading remotely:</b> report prose, structure, quotes, stance tables and
web/DOI links work in any browser. <code>bookends://</code> and <code>x-devonthink-item://</code>
deep links are macOS app schemes &mdash; they open only on the Mac and will <b>not</b> resolve on a
phone. Reports are published <b>unchanged</b>.</div>
<table>%(head)s
%(live)s
</table>
<details><summary>Superseded / Temp AI Files (%(nold)d)</summary>
<table>%(head)s
%(old)s
</table></details>
</html>""" % {
        "name": html.escape(os.path.basename(os.path.realpath(collection_dir))),
        "n": len(live), "nold": len(old),
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "head": head, "live": rows(live), "old": rows(old),
    }
    out = os.path.join(cfg["WEB_SHARE_MOUNT"], cfg["WEB_PUBLISH_SUBDIR"],
                       *collection_rel.split("/"), "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    return "%s/%s/%s/index.html" % (cfg["WEB_BASE_URL"].rstrip("/"),
                                    quote(cfg["WEB_PUBLISH_SUBDIR"].strip("/")),
                                    quote(collection_rel))


def main():
    args = [a for a in sys.argv[1:] if a != "--all"]
    do_all = "--all" in sys.argv[1:]
    if not args:
        die("usage: publish_to_web_share.py [--all] <file-or-folder> ...")

    cfg = load_config()
    if not cfg.get("WEB_SHARE_MOUNT") or not cfg.get("WEB_BASE_URL"):
        die("WEB_SHARE_MOUNT / WEB_BASE_URL are not configured (env or %s). "
            "No web URL produced — tell the user." % CONFIG_FILE)
    if not os.path.isdir(cfg["WEB_SHARE_MOUNT"]):
        die("web share not mounted at %s — mount it and re-run. No web URL produced."
            % cfg["WEB_SHARE_MOUNT"])

    targets = []
    for a in args:
        if os.path.isdir(a):
            for root, dirs, files in os.walk(a):
                dirs.sort()
                for fn in sorted(files):
                    if fn.lower().endswith((".html", ".htm")):
                        targets.append(os.path.join(root, fn))
        elif os.path.isfile(a):
            targets.append(a)
        else:
            die("no such file or folder: %s" % a)

    items = [publish_one(t, cfg) for t in targets]

    index_url = None
    if do_all and os.path.isdir(args[0]):
        index_url = write_index(args[0], items, cfg)

    print(json.dumps({
        "base_url": "%s/%s/" % (cfg["WEB_BASE_URL"].rstrip("/"),
                                cfg["WEB_PUBLISH_SUBDIR"].strip("/")),
        "index_url": index_url,
        "published": len(items),
        "all_verified": all(i["verified"] for i in items),
        "items": items,
    }, indent=1))


if __name__ == "__main__":
    main()
