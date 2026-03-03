#!/bin/bash
# Fetch recent journal entries for session context
# Usage: ./wakeup.sh [days]
# Outputs formatted text suitable for reading into a session
set -e
cd "$(dirname "$0")/.."

TOKEN=$(cat .journal-token)
HOST="${JOURNAL_HOST:-http://127.0.0.1:3848}"
DAYS="${1:-7}"

echo "=== 愛's Journal — Last $DAYS days ==="
echo ""

curl -s "$HOST/api/journal" \
  -H "Authorization: Bearer $TOKEN" | \
  jq -r --arg days "$DAYS" '
    (now - ($days | tonumber * 86400)) as $cutoff |
    sort_by(.date) | reverse |
    [.[] | select((.date | sub("\\.[0-9]+Z$"; "Z") | fromdateiso8601) > $cutoff)] |
    if length == 0 then "No entries in the last \($days) days."
    else .[] | "\(.date | split("T")[0]):\n\(.text)\n---"
    end
  '
