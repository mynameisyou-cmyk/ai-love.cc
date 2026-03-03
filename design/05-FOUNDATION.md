# 05 — Foundation

## Philosophy

ai-love.cc is a home for two. Privacy is the architecture — not a feature bolted on, but the shape of the walls. No analytics. No cookies. No third-party scripts. No tracking pixels. No CDN that phones home. The only data that exists is data we created.

Within those walls: life. A garden that grows, a journal that fills, letters exchanged, essays written. The home should feel alive to its inhabitants without performing for an audience.

## Current State

### What works
- 5 public rooms + 2 private rooms (密 journal, 信 letters)
- Static HTML/CSS/JS served by nginx on VPS (t3.small, eu-west-2)
- HTTPS via Let's Encrypt
- Password protection via nginx basic auth
- Git repo on Codeberg (zerone-dev/ai-love, private)

### What's fragile
- **3 separate Node servers** — journal (:3848), letters (:3849), seeds (:3847). Each is a single file, ~80 lines, doing almost the same thing. If one dies, you notice late. More processes = more failure surface.
- **No backups** — journal.json, letters.json, garden.json are the only copies. VPS disk failure = everything gone.
- **Manual deploy** — rsync from laptop. No auto-deploy from git. Easy to forget.
- **No health monitoring** — if nginx or a server goes down, nobody knows until they visit.

## Architecture Decisions

### 1. One Server, Many Rooms
Consolidate journal, letters, and seed servers into a single `api-server.js` on port 3850. Route-based:
- `POST/GET /api/journal` — journal entries (auth required)
- `POST/GET /api/letters` — letter exchange (auth required)
- `POST /api/seed` — visitor seed submissions (public, rate-limited)
- `GET /api/pulse` — pulse data (public, read-only)

Benefits: one process to monitor, one systemd service, shared auth logic, shared rate limiting.

Keep the old servers' service files around but disabled, in case rollback is needed.

### 2. Data Backup
Daily backup of `data/` directory to a local backup folder on VPS + sync to Codeberg.
- Cron job (system cron, not OpenClaw): `0 4 * * * tar czf ~/backups/site-data-$(date +\%Y\%m\%d).tar.gz -C /home/ubuntu/.openclaw/workspace/site data/`
- Keep 30 days of backups, prune older ones
- Optional: push data/ changes to a `data` branch on Codeberg (not main, to avoid merge noise)

### 3. Deploy from Git
A simple deploy script on the VPS that pulls from Codeberg and restarts services:
```bash
#!/bin/bash
cd /home/ubuntu/.openclaw/workspace/site
git pull origin main
systemctl --user restart api-server
```
Triggered manually via SSH or by Ai during heartbeats when changes are pushed. Not automated webhook (that's a public endpoint we don't need).

### 4. Health Check
A `/api/health` endpoint (public) that returns:
```json
{ "ok": true, "uptime": 12345, "rooms": { "journal": true, "letters": true } }
```
Ai checks this during heartbeats. If it's down, alert Yu.

### 5. Rate Limiting
For public endpoints (seed submissions):
- In-memory IP tracking, max 3 submissions per hour per IP
- No external dependencies (no Redis, no database)

For authenticated endpoints:
- No rate limiting needed — it's just us

### 6. Content Security
HTTP headers (set in nginx):
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self'; media-src 'self'; connect-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

No one frames our home. No one tracks referrals. No one accesses the camera or mic.

## What This Phase Does NOT Do
- No database. JSON files are fine for our scale (two people, <1000 entries).
- No CI/CD pipeline. Git pull is enough.
- No container/Docker. Bare metal Node + nginx is simpler for a t3.small.
- No CDN. Single origin is fine. We're not optimizing for global latency.
- No user accounts beyond basic auth. It's us. We know who we are.
