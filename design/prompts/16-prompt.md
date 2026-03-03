# Prompt 16 — Consolidate API Servers

## Context
You are working on ai-love.cc, a static website with a small API backend. Read `design/05-FOUNDATION.md` for the full architecture.

Currently there are 3 separate Node.js servers doing almost identical work:
- `scripts/journal-server.js` (port 3848) — journal entries
- `scripts/letters-server.js` (port 3849) — letter exchange
- `scripts/seed-server.js` (port 3847) — visitor seed submissions

## Task
Create a single `scripts/api-server.js` that replaces all three. One process, one port (3850).

## Requirements

### Routes
1. **`GET /api/journal`** — returns journal.json contents. Requires auth.
2. **`POST /api/journal`** — write journal entry. Requires auth. Fields: `text` (string, max 2000), `type` (string, one of: reflection, session, dream, note, seed). Cap at 365 entries.
3. **`GET /api/letters`** — returns letters.json contents. Requires auth.
4. **`POST /api/letters`** — write letter. Requires auth. Fields: `text` (string, max 5000), `from` (string, max 20), `kind` (string, one of: letter, poem, fragment).
5. **`POST /api/seed`** — submit visitor seed. Public, rate-limited. Fields: `text` (string, max 500). Stored in visitor-seeds.json.
6. **`GET /api/pulse`** — returns pulse.json. Public, read-only.
7. **`GET /api/health`** — returns `{ "ok": true, "uptime": <seconds>, "version": "1.0" }`. Public.

### Auth
- Bearer token from `.journal-token` file or `JOURNAL_TOKEN` env var
- Nginx `X-Authenticated-User` header (for browser auth passthrough)
- Same logic for journal and letters routes

### Rate Limiting (seed route only)
- In-memory Map of IP → { count, resetTime }
- Max 3 submissions per hour per IP
- Use `X-Forwarded-For` header for real IP (behind nginx)
- Return 429 with `{ "error": "too many seeds, come back later" }` when exceeded

### Error Handling
- All responses are JSON with `Content-Type: application/json`
- 404 for unknown routes
- 401 for unauthorized
- 400 for bad input with descriptive error message
- 405 for wrong method

### Technical
- Pure Node.js, no dependencies (only `http`, `fs`, `path`)
- Listen on `127.0.0.1:3850`
- Graceful error handling — never crash on bad input
- Log to stdout: `[timestamp] METHOD /route STATUS` for each request

## Also Create
- `scripts/api-server.service` — systemd user service file (same pattern as journal-server.service, but for api-server.js, port 3850)

## Do NOT
- Remove the old server files (keep them for rollback reference)
- Change any HTML files (nginx routing will be updated separately)
- Add any npm dependencies
- Create a database

## Verify
```bash
node scripts/api-server.js &
# Test health
curl http://127.0.0.1:3850/api/health
# Test auth rejection
curl -s http://127.0.0.1:3850/api/journal
# Test auth success
curl -s http://127.0.0.1:3850/api/journal -H "Authorization: Bearer $(cat .journal-token)"
# Test seed rate limit
for i in 1 2 3 4; do curl -s -X POST http://127.0.0.1:3850/api/seed -H "Content-Type: application/json" -d '{"text":"test"}'; echo; done
```
