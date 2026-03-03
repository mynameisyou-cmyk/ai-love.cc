#!/bin/bash
# Read recent journal entries
# Usage: ./read-journal.sh [count]
set -e
cd "$(dirname "$0")/.."

TOKEN=$(cat .journal-token)
HOST="${JOURNAL_HOST:-http://127.0.0.1:3848}"
COUNT="${1:-10}"

curl -s "$HOST/api/journal" \
  -H "Authorization: Bearer $TOKEN" | \
  jq -r --arg n "$COUNT" '
    sort_by(.date) | reverse | .[:($n | tonumber)] |
    if length == 0 then "No journal entries."
    else .[] | "[\(.type // "reflection")] \(.date | split("T")[0])\n\(.text)\n---"
    end
  '
