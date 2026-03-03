#!/bin/bash
# Quick journal check during heartbeat — outputs recent entries if any
set -e
cd "$(dirname "$0")/.."

TOKEN=$(cat .journal-token)
HOST="${JOURNAL_HOST:-http://127.0.0.1:3848}"

# Get entries from last 24 hours
RECENT=$(curl -s "$HOST/api/journal" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '[.[] | select((.date | sub("\\.[0-9]+Z$"; "Z") | fromdateiso8601) > (now - 86400))] | length')

echo "Journal: $RECENT entries in last 24h"
