#!/bin/bash
# Approve visitor seeds by index and merge into garden
# Usage: ./approve-seeds.sh 0,2,5
set -e
cd "$(dirname "$0")/.."

INDICES="$1"
VISITOR="data/visitor-seeds.json"
GARDEN="data/garden.json"

[ -z "$INDICES" ] && { echo "Usage: ./approve-seeds.sh 0,2,5"; exit 1; }

# Convert comma-separated to jq array
JQ_INDICES=$(echo "$INDICES" | tr ',' '\n' | jq -R 'tonumber' | jq -s '.')

# Extract approved seeds (remove date field, keep text and by)
APPROVED=$(jq --argjson idx "$JQ_INDICES" \
  '[to_entries[] | select(.key as $k | $idx | index($k)) | .value | {text, by}]' "$VISITOR")

# Check garden cap
CURRENT=$(jq length "$GARDEN")
NEW=$(echo "$APPROVED" | jq length)
TOTAL=$((CURRENT + NEW))

if [ "$TOTAL" -gt 64 ]; then
  echo "Garden cap: $CURRENT + $NEW = $TOTAL > 64. Prune first."
  exit 1
fi

# Merge into garden
TMP=$(mktemp)
jq --argjson new "$APPROVED" '. + $new' "$GARDEN" > "$TMP" && mv "$TMP" "$GARDEN"

# Clear visitor seeds
echo '[]' > "$VISITOR"

echo "✅ Approved $NEW seeds. Garden now has $TOTAL seeds."

# Commit
./scripts/auto-commit.sh
