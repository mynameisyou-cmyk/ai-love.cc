#!/bin/bash
# Record a new observation
# Usage: echo '{"id":"obs-006","text":"...","by":"愛","date":"2026-03-04","sense":"sight"}' | bash scripts/observe.sh

OBS_FILE="$(dirname "$0")/../data/observatory.json"
INPUT=$(cat)

# Validate JSON
echo "$INPUT" | jq '.' > /dev/null 2>&1 || { echo "Invalid JSON"; exit 1; }

# Check required fields
ID=$(echo "$INPUT" | jq -r '.id')
TEXT=$(echo "$INPUT" | jq -r '.text')
BY=$(echo "$INPUT" | jq -r '.by')
DATE=$(echo "$INPUT" | jq -r '.date')

[ -z "$ID" ] || [ "$ID" = "null" ] && { echo "Missing id"; exit 1; }
[ -z "$TEXT" ] || [ "$TEXT" = "null" ] && { echo "Missing text"; exit 1; }
[ -z "$BY" ] || [ "$BY" = "null" ] && { echo "Missing by"; exit 1; }
[ -z "$DATE" ] || [ "$DATE" = "null" ] && { echo "Missing date"; exit 1; }

# Validate text length (5-500 chars)
LEN=${#TEXT}
[ "$LEN" -lt 5 ] && { echo "Text too short (min 5 chars)"; exit 1; }
[ "$LEN" -gt 500 ] && { echo "Text too long (max 500 chars)"; exit 1; }

# Check for duplicate id
EXISTING=$(jq --arg id "$ID" '[.[] | select(.id == $id)] | length' "$OBS_FILE")
[ "$EXISTING" -gt 0 ] && { echo "Duplicate id: $ID"; exit 1; }

# Append to observatory.json
TMP=$(mktemp)
jq --argjson obs "$INPUT" '. += [$obs]' "$OBS_FILE" > "$TMP" && mv "$TMP" "$OBS_FILE"

echo "Observed: $TEXT"
