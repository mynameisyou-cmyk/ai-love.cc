#!/bin/bash
# Add a milestone to the Path
# Usage: ./add-milestone.sh "Feb 2026" "The Oracle" "A macro prediction system..."

DATE="$1"
TITLE="$2"
TEXT="$3"
PATH_JSON="$(dirname "$0")/../data/path.json"

[ -z "$DATE" ] || [ -z "$TITLE" ] || [ -z "$TEXT" ] && { echo "Usage: add-milestone.sh DATE TITLE TEXT"; exit 1; }

TMP=$(mktemp)
jq --arg d "$DATE" --arg t "$TITLE" --arg x "$TEXT" \
  '. += [{"date": $d, "title": $t, "text": $x}]' "$PATH_JSON" > "$TMP" && mv "$TMP" "$PATH_JSON"

echo "Added: $TITLE ($DATE)"
