#!/bin/bash
# Rebuild library.json from library/*.html files
# Reads <h1> or <title> and first <p> from each file
# Works on both macOS (BSD) and Linux (GNU)

LIBRARY_DIR="$(dirname "$0")/../library"
OUTPUT="$(dirname "$0")/../data/library.json"

echo "[" > "$OUTPUT"
FIRST=true

for f in "$LIBRARY_DIR"/*.html; do
  [ -f "$f" ] || continue
  FILENAME=$(basename "$f")

  # Skip template
  [ "$FILENAME" = "template.html" ] && continue

  # Extract title from <h1>
  TITLE=$(sed -n 's/.*<h1[^>]*>\([^<]*\)<.*/\1/p' "$f" | head -1)
  # Fallback: extract from <title>
  [ -z "$TITLE" ] && TITLE=$(sed -n 's/.*<title>\([^<]*\)<.*/\1/p' "$f" | head -1 | sed 's/ — .*//')

  # Extract date from .essay-date or .date element
  DATE=$(sed -n 's/.*class="essay-date">\([^<]*\)<.*/\1/p' "$f" | head -1)
  [ -z "$DATE" ] && DATE=$(sed -n 's/.*class="date">\([^<]*\)<.*/\1/p' "$f" | head -1)

  # Extract first <p> content (no attributes) as preview
  PREVIEW=$(sed -n 's/.*<p>\([^<]*\)<.*/\1/p' "$f" | head -1 | cut -c1-120)

  [ -z "$TITLE" ] && continue

  $FIRST || echo "," >> "$OUTPUT"
  FIRST=false

  jq -n --arg t "$TITLE" --arg p "$PREVIEW..." --arg f "library/$FILENAME" --arg d "$DATE" \
    '{title: $t, preview: $p, file: $f, date: $d}' >> "$OUTPUT"
done

echo "]" >> "$OUTPUT"
echo "Indexed $(jq length "$OUTPUT") entries"
