#!/bin/bash
# Write a journal entry to the live VPS journal
# Usage: write-to-journal.sh "text" [type]
# Types: reflection, session, dream, note, seed
SSH_KEY="$HOME/.ssh/openclaw-key.pem"
VPS="ubuntu@16.60.83.250"
TEXT="$1"
TYPE="${2:-reflection}"

if [ -z "$TEXT" ]; then
  echo "Usage: $0 \"text\" [type]"
  exit 1
fi

# Escape for JSON
JSON_TEXT=$(echo "$TEXT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")

ssh -i "$SSH_KEY" "$VPS" "
TOKEN=\$(cat /home/ubuntu/.openclaw/workspace/site/.journal-token)
curl -s -X POST http://127.0.0.1:3848/api/journal \
  -H 'Content-Type: application/json' \
  -H \"Authorization: Bearer \$TOKEN\" \
  -d '{\"text\": $JSON_TEXT, \"type\": \"$TYPE\"}'
"
