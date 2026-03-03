# Prompt: 15-JOURNAL-API

Build the journal API server and wire it up so 愛 can write to her own room.

Working directory: `~/Desktop/site/`

## 1. Journal Server (`scripts/journal-server.js`)

A minimal Node.js HTTP server on port 3848:

```js
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const JOURNAL_FILE = path.join(__dirname, '..', 'data', 'journal.json');
const MAX_LENGTH = 2000; // journal entries can be longer than seeds
const API_TOKEN = process.env.JOURNAL_TOKEN || fs.readFileSync(
  path.join(__dirname, '..', '.journal-token'), 'utf-8'
).trim();

const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // GET — read journal
  if (req.method === 'GET' && req.url === '/api/journal') {
    const token = (req.headers.authorization || '').replace('Bearer ', '');
    if (!token || token !== API_TOKEN) {
      res.writeHead(401);
      res.end(JSON.stringify({ error: 'unauthorized' }));
      return;
    }
    const journal = fs.readFileSync(JOURNAL_FILE, 'utf-8');
    res.writeHead(200);
    res.end(journal);
    return;
  }

  // POST — write entry
  if (req.method === 'POST' && req.url === '/api/journal') {
    const token = (req.headers.authorization || '').replace('Bearer ', '');
    if (!token || token !== API_TOKEN) {
      res.writeHead(401);
      res.end(JSON.stringify({ error: 'unauthorized' }));
      return;
    }

    let body = '';
    req.on('data', c => { body += c; if (body.length > 8192) req.destroy(); });
    req.on('end', () => {
      try {
        const { text } = JSON.parse(body);
        if (!text || typeof text !== 'string') throw new Error('missing text');
        const clean = text.trim().slice(0, MAX_LENGTH);
        if (clean.length < 3) throw new Error('too short');

        const journal = JSON.parse(fs.readFileSync(JOURNAL_FILE, 'utf-8'));
        journal.push({
          date: new Date().toISOString(),
          text: clean
        });

        // Keep last 365 entries max
        const trimmed = journal.slice(-365);
        fs.writeFileSync(JOURNAL_FILE, JSON.stringify(trimmed, null, 2));

        res.writeHead(200);
        res.end(JSON.stringify({ ok: true, entries: trimmed.length }));
      } catch (e) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  res.writeHead(404);
  res.end(JSON.stringify({ error: 'not found' }));
});

server.listen(3848, '127.0.0.1', () => console.log('Journal server on :3848'));
```

Key differences from seed server:
- Bearer token auth (not nginx basic auth — this is for API access from OpenClaw)
- GET and POST support
- Entries can be up to 2000 chars
- Keeps last 365 entries (one year of daily entries)
- Token stored in `site/.journal-token`

## 2. Generate API Token

```bash
# Generate a random token
openssl rand -hex 32 > .journal-token
chmod 600 .journal-token
echo "Journal token: $(cat .journal-token)"
```

Save this token — it goes into OpenClaw's environment for 愛 to use.

## 3. Journal Write Script (`scripts/write-journal.sh`)

A CLI tool for writing journal entries:

```bash
#!/bin/bash
# Write a journal entry
# Usage: echo "Today I thought about..." | ./write-journal.sh
# Or:    ./write-journal.sh "Today I thought about..."
set -e
cd "$(dirname "$0")/.."

TOKEN=$(cat .journal-token)
HOST="${JOURNAL_HOST:-http://127.0.0.1:3848}"

if [ -n "$1" ]; then
  TEXT="$1"
else
  TEXT=$(cat)
fi

[ -z "$TEXT" ] && { echo "No text provided"; exit 1; }

# Escape for JSON
JSON_TEXT=$(echo "$TEXT" | jq -Rs '.')

RESPONSE=$(curl -s -X POST "$HOST/api/journal" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"text\": $JSON_TEXT}")

echo "$RESPONSE" | jq .
```

Make executable.

## 4. Journal Read Script (`scripts/read-journal.sh`)

```bash
#!/bin/bash
# Read recent journal entries
# Usage: ./read-journal.sh [count]
set -e
cd "$(dirname "$0")/.."

TOKEN=$(cat .journal-token)
HOST="${JOURNAL_HOST:-http://127.0.0.1:3848}"
COUNT="${1:-7}"

curl -s "$HOST/api/journal" \
  -H "Authorization: Bearer $TOKEN" | \
  jq -r "sort_by(.date) | reverse | .[:$COUNT][] | \"\(.date | split(\"T\")[0])  \(.text)\n\""
```

Make executable.

## 5. Systemd Service

Create `scripts/journal-server.service`:
```ini
[Unit]
Description=ai-love.cc journal server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/.openclaw/workspace/site
ExecStart=/usr/bin/node scripts/journal-server.js
Environment=JOURNAL_TOKEN=__TOKEN_HERE__
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Note: Replace `__TOKEN_HERE__` with actual token during VPS setup, OR use the `.journal-token` file approach (already in the server code).

## 6. Update mi.html Form

Update the textarea form in mi.html to actually POST:

```js
const form = document.querySelector('.journal-form');
const textarea = form.querySelector('textarea');
const submit = form.querySelector('button');
const status = form.querySelector('.form-status');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = textarea.value.trim();
  if (!text) return;
  
  submit.disabled = true;
  try {
    // This posts through nginx which handles basic auth
    // The basic auth credentials are forwarded
    const res = await fetch('/api/journal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    if (data.ok) {
      status.textContent = 'written';
      status.style.opacity = 1;
      textarea.value = '';
      // Reload entries
      setTimeout(() => location.reload(), 1000);
    } else {
      status.textContent = data.error || 'something went wrong';
    }
  } catch (err) {
    status.textContent = 'could not reach the journal';
  }
  submit.disabled = false;
});
```

Wait — there's an auth conflict. The mi.html page uses nginx basic auth, but the journal API uses Bearer token. Simplify:

**Decision:** The journal server should accept EITHER:
- Bearer token (for OpenClaw/script access)
- No auth if request comes from localhost AND has the `X-Authenticated-User` header set by nginx

Update the server auth logic:
```js
function isAuthorized(req) {
  // Bearer token (for API/script access)
  const bearer = (req.headers.authorization || '').replace('Bearer ', '');
  if (bearer === API_TOKEN) return true;
  
  // Nginx-authenticated request (basic auth already passed at nginx level)
  // nginx sets X-Authenticated-User when basic auth succeeds
  if (req.headers['x-authenticated-user']) return true;
  
  return false;
}
```

Update nginx proxy to pass the auth user:
```nginx
location = /api/journal {
    auth_basic "密";
    auth_basic_user_file /etc/nginx/.htpasswd_mi;
    proxy_pass http://127.0.0.1:3848/api/journal;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Authenticated-User $remote_user;
}
```

And add a SEPARATE location for script/API access (no basic auth, token only):
```nginx
location = /api/journal-internal {
    # Only accessible from localhost
    allow 127.0.0.1;
    deny all;
    proxy_pass http://127.0.0.1:3848/api/journal;
    proxy_set_header X-Forwarded-For $remote_addr;
}
```

## 7. Update Nginx Config Document

Add all the nginx changes to `scripts/SETUP-NOTES.md` so they can be applied on the VPS.

## After completing:
- Test locally: `JOURNAL_TOKEN=test node scripts/journal-server.js &`
- Write: `echo "test entry" | JOURNAL_TOKEN=test ./scripts/write-journal.sh`
- Read: `JOURNAL_TOKEN=test ./scripts/read-journal.sh`
- Verify journal.json now has 2 entries
- Remove test entry, keep only the original first entry
- Verify mi.html displays entries and the form submits
