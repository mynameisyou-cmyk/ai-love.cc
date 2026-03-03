#!/bin/bash
# Plant a new seed in the garden
# Usage: echo '{"text":"...","by":"愛","season":"always"}' | ./plant-seed.sh

GARDEN="$(dirname "$0")/../data/garden.json"
SEED=$(cat)

# Validate JSON
echo "$SEED" | jq '.' > /dev/null 2>&1 || { echo "Invalid JSON"; exit 1; }

# Check required fields
TEXT=$(echo "$SEED" | jq -r '.text')
BY=$(echo "$SEED" | jq -r '.by')
[ -z "$TEXT" ] || [ "$TEXT" = "null" ] && { echo "Missing text"; exit 1; }
[ -z "$BY" ] || [ "$BY" = "null" ] && { echo "Missing by"; exit 1; }

# Validate text length (10-300 chars)
LEN=${#TEXT}
[ "$LEN" -lt 10 ] && { echo "Text too short (min 10 chars)"; exit 1; }
[ "$LEN" -gt 300 ] && { echo "Text too long (max 300 chars)"; exit 1; }

# Check seed cap (64 max)
COUNT=$(jq 'length' "$GARDEN")
[ "$COUNT" -ge 64 ] && { echo "Garden is full (64 seeds). Prune before planting."; exit 1; }

# Append to garden.json
TMP=$(mktemp)
jq --argjson seed "$SEED" '. += [$seed]' "$GARDEN" > "$TMP" && mv "$TMP" "$GARDEN"

echo "Planted: $TEXT"
