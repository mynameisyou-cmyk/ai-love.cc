#!/bin/bash
# Prune seeds from the garden
# Usage: ./prune-garden.sh 3,7,12
# Only acts if garden has > 48 seeds

GARDEN="$(dirname "$0")/../data/garden.json"
COUNT=$(jq 'length' "$GARDEN")

if [ "$COUNT" -le 48 ]; then
  echo "Garden has $COUNT seeds (threshold: 48). No pruning needed."
  exit 0
fi

echo "Garden has $COUNT seeds."

if [ -z "$1" ]; then
  echo ""
  echo "Current seeds:"
  jq -r 'to_entries[] | "\(.key): \(.value.text | .[0:80])... — \(.value.by)"' "$GARDEN"
  echo ""
  echo "Usage: $0 INDEX1,INDEX2,INDEX3"
  echo "Example: $0 3,7,12"
  exit 0
fi

# Parse indices to remove
INDICES="$1"
TMP=$(mktemp)

# Build jq filter to remove indices (process in reverse to preserve positions)
jq --arg indices "$INDICES" '
  ($indices | split(",") | map(tonumber)) as $remove |
  [to_entries[] | select(.key | IN($remove[]) | not) | .value]
' "$GARDEN" > "$TMP" && mv "$TMP" "$GARDEN"

NEW_COUNT=$(jq 'length' "$GARDEN")
REMOVED=$((COUNT - NEW_COUNT))
echo "Pruned $REMOVED seeds. Garden now has $NEW_COUNT seeds."
