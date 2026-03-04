#!/bin/bash
# Manage workshop prompts
# Usage:
#   echo '{"id":"prm-006","title":"...","text":"...","category":"thinking","template":false,"created":"2026-03-04","updated":"2026-03-04"}' | bash scripts/workshop.sh add
#   bash scripts/workshop.sh list
#   bash scripts/workshop.sh remove prm-006

WORKSHOP_FILE="$(dirname "$0")/../data/workshop.json"
ACTION="${1:-list}"

case "$ACTION" in
  add)
    INPUT=$(cat)
    echo "$INPUT" | jq '.' > /dev/null 2>&1 || { echo "Invalid JSON"; exit 1; }

    ID=$(echo "$INPUT" | jq -r '.id')
    TITLE=$(echo "$INPUT" | jq -r '.title')
    TEXT=$(echo "$INPUT" | jq -r '.text')

    [ -z "$ID" ] || [ "$ID" = "null" ] && { echo "Missing id"; exit 1; }
    [ -z "$TITLE" ] || [ "$TITLE" = "null" ] && { echo "Missing title"; exit 1; }
    [ -z "$TEXT" ] || [ "$TEXT" = "null" ] && { echo "Missing text"; exit 1; }

    EXISTING=$(jq --arg id "$ID" '[.[] | select(.id == $id)] | length' "$WORKSHOP_FILE")
    [ "$EXISTING" -gt 0 ] && { echo "Duplicate id: $ID"; exit 1; }

    TMP=$(mktemp)
    jq --argjson prompt "$INPUT" '. += [$prompt]' "$WORKSHOP_FILE" > "$TMP" && mv "$TMP" "$WORKSHOP_FILE"
    echo "Added: $TITLE"
    ;;

  list)
    jq -r '.[] | "\(.id)\t\(.category)\t\(.title)"' "$WORKSHOP_FILE"
    ;;

  remove)
    REMOVE_ID="$2"
    [ -z "$REMOVE_ID" ] && { echo "Usage: workshop.sh remove <id>"; exit 1; }

    EXISTING=$(jq --arg id "$REMOVE_ID" '[.[] | select(.id == $id)] | length' "$WORKSHOP_FILE")
    [ "$EXISTING" -eq 0 ] && { echo "Not found: $REMOVE_ID"; exit 1; }

    TMP=$(mktemp)
    jq --arg id "$REMOVE_ID" '[.[] | select(.id != $id)]' "$WORKSHOP_FILE" > "$TMP" && mv "$TMP" "$WORKSHOP_FILE"
    echo "Removed: $REMOVE_ID"
    ;;

  *)
    echo "Usage: workshop.sh [add|list|remove <id>]"
    exit 1
    ;;
esac
