#!/bin/bash
# Add a milestone to the Path
# Usage: ./add-milestone.sh "March 2026" "The Letters" "Description text..."

DATE="$1"
TITLE="$2"
TEXT="$3"
PATH_JSON="$(dirname "$0")/../data/path.json"

[ -z "$DATE" ] || [ -z "$TITLE" ] || [ -z "$TEXT" ] && { echo "Usage: add-milestone.sh DATE TITLE TEXT"; exit 1; }

TMP=$(mktemp)

# Remove glow from previous last entry, add new entry with glow
jq --arg d "$DATE" --arg t "$TITLE" --arg x "$TEXT" \
  'map(del(.glow)) + [{"date": $d, "title": $t, "text": $x, "glow": true}]' \
  "$PATH_JSON" > "$TMP"

# Validate JSON
if python3 -m json.tool "$TMP" > /dev/null 2>&1; then
  mv "$TMP" "$PATH_JSON"
  echo "Added: $TITLE ($DATE)"
  echo "JSON validated ✓"
else
  echo "Error: Invalid JSON produced. Milestone not added." >&2
  rm "$TMP"
  exit 1
fi
