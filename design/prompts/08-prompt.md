# Prompt: 08-SMART-HOME

You are building a spiritual/poetic static website at `~/Desktop/site/`. Read `design/08-SMART-HOME.md` for the full spec.

This batch creates automation scripts and a small API server. Execute ALL tasks:

## Summary of work:

### 1. Garden Seed Planting Script (`scripts/plant-seed.sh`)
Create `site/scripts/plant-seed.sh`:
- Reads JSON from stdin: `{"text": "...", "by": "愛", "season": "always"}`
- Validates with `jq`: must have `text` (10-300 chars) and `by` fields
- Appends to `data/garden.json` array
- Caps garden at 64 seeds — exits with message if already at cap
- Make executable (`chmod +x`)

### 2. Garden Pruning Script (`scripts/prune-garden.sh`)
Create `site/scripts/prune-garden.sh`:
- Only acts if garden.json has > 48 seeds
- Outputs the current seed list with indices for review
- Accepts a comma-separated list of indices to remove as argument: `./prune-garden.sh 3,7,12`
- Removes those indices and rewrites garden.json
- Make executable

### 3. Path Milestone Script (`scripts/add-milestone.sh`)
Create `site/scripts/add-milestone.sh`:
- Usage: `./add-milestone.sh "Feb 2026" "The Oracle" "A macro prediction system..."`
- Validates 3 arguments (date, title, text)
- Appends to `data/path.json`
- Make executable

### 4. Library Indexer (`scripts/index-library.sh`)
Create `site/scripts/index-library.sh`:
- Scans `library/*.html` files
- Extracts title (from `<h1>` or `<title>`), date (from `.date` element), preview (first `<p>`, truncated to 120 chars)
- Writes `data/library.json` as a JSON array
- Make executable

### 5. Pulse System
Create `data/pulse.json`:
```json
{"alive": true, "lastSeen": "2026-02-28T15:00:00Z", "mood": "present", "activity": "tending the garden"}
```

Create `js/pulse.js`:
- Fetches `data/pulse.json`
- If lastSeen < 1 hour ago: create a 4px purple dot (position: fixed, bottom: 20px, left: 60px) with breathe animation
- If lastSeen < 24 hours ago: same dot but static, opacity 0.4
- If lastSeen > 24 hours ago: no dot
- Silent fail on fetch error

Add CSS for `.pulse-dot`, `.pulse-active`, `.pulse-recent` to `css/base.css`:
- 4px width/height, border-radius 50%, `var(--primary)` background
- `.pulse-active`: breathe animation
- `.pulse-recent`: opacity 0.4, no animation

Create `scripts/update-pulse.sh`:
```bash
#!/bin/bash
PULSE="$(dirname "$0")/../data/pulse.json"
MOOD="${1:-present}"
ACTIVITY="${2:-quietly here}"
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
jq -n --arg t "$NOW" --arg m "$MOOD" --arg a "$ACTIVITY" \
  '{alive: true, lastSeen: $t, mood: $m, activity: $a}' > "$PULSE"
```
Make executable.

Add `js/pulse.js` to `index.html` (Gate page only — the pulse lives at the entrance).

### 6. Visitor Seed Server (`scripts/seed-server.js`)
Create `site/scripts/seed-server.js` — a minimal Node.js HTTP server:
- Listens on 127.0.0.1:3847
- POST `/api/seed` only
- CORS: only `https://ai-love.cc`
- Rate limit: 1 submission per IP per 5 minutes (in-memory Map)
- Validates: JSON body with `text` field, string, 3-280 characters after trim
- Appends to `data/visitor-seeds.json` with `by: "a visitor"` and ISO date
- Returns `{"ok": true, "message": "Your seed has been planted in the soil. It will sprout after tending."}`
- Error responses: 400 for bad input, 429 for rate limit, 404 for wrong path

Create `data/visitor-seeds.json`: `[]`

### 7. Garden Visitor Form (garden.html)
At the bottom of garden.html, below the seed count, add:
- A muted "plant a seed" text link
- On click: slides down a form (CSS transition, max-height trick)
- Textarea: placeholder "leave a thought...", maxlength 280
- Character counter: "0 / 280" in muted text, updates on input
- Submit button: just "🌱" (styled as muted, small)
- On submit: POST to `/api/seed`, show success message ("your seed is in the soil..."), hide form
- On error: show error message in muted red
- No name field. Fully anonymous

Style the form to match the site: transparent bg, border matching seed cards, muted inputs, no harsh focus rings (use purple glow).

### 8. Git Auto-Commit (`scripts/auto-commit.sh`)
Create `site/scripts/auto-commit.sh`:
- `cd` to site root
- `git add data/ library/`
- Check for staged changes, exit if none
- Commit with message: "🌱 daily tending (YYYY-MM-DD) — N files"
- If a remote named `origin` exists, `git push`
- Make executable

### 9. Systemd Service for Seed Server
Create `scripts/seed-server.service` (systemd unit file template):
```ini
[Unit]
Description=ai-love.cc seed submission server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/.openclaw/workspace/site
ExecStart=/usr/bin/node scripts/seed-server.js
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### After completing:
- Test plant-seed.sh: `echo '{"text":"Test seed","by":"test"}' | ./scripts/plant-seed.sh`
- Test add-milestone.sh: verify it appends to path.json (then remove test entry)
- Test seed-server.js: `node scripts/seed-server.js &` then `curl -X POST -H 'Content-Type: application/json' -d '{"text":"hello"}' http://localhost:3847/api/seed`
- Test update-pulse.sh and verify pulse.json updates
- Verify the Garden form appears and submits correctly
- All scripts should be idempotent and safe to run multiple times
