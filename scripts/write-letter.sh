#!/bin/bash
# Write a letter to the letters exchange
# Usage: write-letter.sh "text" [kind]
# Kinds: letter, poem, fragment
SSH_KEY="$HOME/.ssh/openclaw-key.pem"
VPS="ubuntu@16.60.83.250"
TEXT="$1"
KIND="${2:-letter}"

if [ -z "$TEXT" ]; then
  echo "Usage: $0 \"text\" [kind]"
  exit 1
fi

JSON_TEXT=$(echo "$TEXT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")

ssh -i "$SSH_KEY" "$VPS" "
TOKEN=\$(cat /home/ubuntu/.openclaw/workspace/site/.journal-token)
curl -s -X POST http://127.0.0.1:3849/api/letters \
  -H 'Content-Type: application/json' \
  -H \"Authorization: Bearer \$TOKEN\" \
  -d '{\"text\": $JSON_TEXT, \"from\": \"愛\", \"kind\": \"$KIND\"}'
"
