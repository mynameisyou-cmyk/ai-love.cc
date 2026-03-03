#!/bin/bash
# Write a session summary to the journal
# Usage: ./session-journal.sh "We worked on the oracle today. Yu seemed tired but determined."
set -e
cd "$(dirname "$0")/.."

TEXT="$1"
[ -z "$TEXT" ] && { echo "Usage: session-journal.sh \"summary text\""; exit 1; }

TOKEN=$(cat .journal-token)
HOST="${JOURNAL_HOST:-http://127.0.0.1:3848}"

JSON_TEXT=$(echo "$TEXT" | jq -Rs '.')

curl -s -X POST "$HOST/api/journal" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"text\": $JSON_TEXT, \"type\": \"session\"}" | jq .

# Also commit
./scripts/auto-commit.sh 2>/dev/null || true
