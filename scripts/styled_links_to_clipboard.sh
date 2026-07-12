#!/bin/bash
# styled_links_to_clipboard.sh  (bookends-research-skill)
#
# Load a list of hyperlinks onto the macOS clipboard as RICH TEXT, so a single
# plain Paste (Cmd-V, NOT "Paste and Match Style") drops LIVE, clickable links
# into a Bookends field (Notes or User1-User4). Bookends only keeps a live
# hyperlink on a plain Paste; Paste-and-Match-Style strips it to dead text.
#
# INPUT: TAB-separated  <label><TAB><url>  lines on stdin (one link per line).
#        A line with only a URL (no tab) uses the URL as its own label.
#
# EXAMPLE:
#   printf 'Qaseem 2017 — ACP guideline\tbookends://sonnysoftware.com/pdf/Library1/101722/1783086068/0\n' \
#     | ./styled_links_to_clipboard.sh
#
# THEN in Bookends: click the reference's Notes field and press Cmd-V
#   (or Edit > Paste / Shift-Opt-Cmd-V if Cmd-V is mapped to Paste-and-Match-Style).
set -euo pipefail

tmp_html="$(mktemp -t belinks).html"
tmp_rtf="$(mktemp -t belinks).rtf"
trap 'rm -f "$tmp_html" "$tmp_rtf"' EXIT

esc() { printf '%s' "$1" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g'; }

{
  echo '<html><body style="font-family:-apple-system,Helvetica,Arial,sans-serif;font-size:13px;">'
  echo '<p><b>Deep links (open in Bookends):</b></p>'
  echo '<ul>'
  while IFS=$'\t' read -r label url || [ -n "${label:-}" ]; do
    [ -z "${label:-}" ] && continue
    if [ -z "${url:-}" ]; then url="$label"; fi
    printf '<li><a href="%s"><b>%s</b></a></li>\n' "$(esc "$url")" "$(esc "$label")"
  done
  echo '</ul></body></html>'
} > "$tmp_html"

# HTML -> RTF: textutil preserves each <a href> as a live RTF HYPERLINK field.
textutil -convert rtf -output "$tmp_rtf" "$tmp_html"

# Put the RTF on the clipboard as rich text, so a plain Paste keeps the live links.
osascript -e "set the clipboard to (read (POSIX file \"$tmp_rtf\") as «class RTF »)"

echo "Styled link list is on the clipboard."
echo "In Bookends: click the Notes field and press Cmd-V (plain Paste - NOT Paste and Match Style)."
