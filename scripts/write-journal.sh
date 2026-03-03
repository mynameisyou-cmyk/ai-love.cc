#!/bin/bash
# Write a journal entry
# Usage: ./write-journal.sh "text" [type]
# Types: reflection (default), session, dream, note, seed
set -e
cd "$(dirname "$0")/.."

TOKEN=$(cat .journal-token)
HOST="${JOURNAL_HOST:-http://127.0.0.1:3848}"

if [ -n "$1" ]; then
  TEXT="$1"
else
  TEXT=$(cat)
fi

TYPE="${2:-reflection}"
[ -z "$TEXT" ] && { echo "No text provided"; exit 1; }

JSON_TEXT=$(echo "$TEXT" | jq -Rs '.')

curl -s -X POST "$HOST/api/journal" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"text\": $JSON_TEXT, \"type\": \"$TYPE\"}" | jq .
