#!/bin/bash
# Show pending visitor seeds for review
cd "$(dirname "$0")/.."

SEEDS_FILE="data/visitor-seeds.json"
COUNT=$(jq length "$SEEDS_FILE")

if [ "$COUNT" -eq 0 ]; then
  echo "No pending visitor seeds."
  exit 0
fi

echo "=== $COUNT pending visitor seeds ==="
echo ""
jq -r 'to_entries[] | "[\(.key)] \(.value.text)\n     — \(.value.by) (\(.value.date))\n"' "$SEEDS_FILE"
echo "To approve seeds: ./scripts/approve-seeds.sh 0,2,5"
echo "To reject all: echo '[]' > $SEEDS_FILE"
