# Design: Consolidate API Servers

**Date:** 2026-03-03
**Prompt:** design/prompts/16-prompt.md

## Problem
Three separate Node.js servers (seed:3847, journal:3848, letters:3849) doing nearly identical work — duplicated auth, file I/O, error handling.

## Solution
Single `scripts/api-server.js` on port 3850 replacing all three.

## Routes

| Route | Method | Auth | Data file | Notes |
|-------|--------|------|-----------|-------|
| `GET /api/health` | GET | Public | — | `{ ok, uptime, version }` |
| `GET /api/pulse` | GET | Public | pulse.json | Read-only |
| `POST /api/seed` | POST | Public + rate limit | visitor-seeds.json | 500 char max, 3/hr/IP |
| `GET /api/journal` | GET | Bearer | journal.json | — |
| `POST /api/journal` | POST | Bearer | journal.json | 2000 char max, 365 entry cap |
| `GET /api/letters` | GET | Bearer | letters.json | — |
| `POST /api/letters` | POST | Bearer | letters.json | 5000 char max |

## Auth
- Bearer token from `.journal-token` file or `JOURNAL_TOKEN` env var
- Nginx `X-Authenticated-User` header passthrough
- Applied to journal and letters routes only

## Rate Limiting (seed only)
- In-memory Map: IP → { count, resetTime }
- 3 submissions per hour per IP
- `X-Forwarded-For` for real IP behind nginx
- 429 response when exceeded

## Technical
- Pure Node.js (http, fs, path only)
- Listen on 127.0.0.1:3850
- JSON responses with Content-Type: application/json
- Logging: `[timestamp] METHOD /route STATUS`
- CORS for seed route (ai-love.cc)

## Deliverables
1. `scripts/api-server.js`
2. `scripts/api-server.service`

## Not changing
- Old server files kept for rollback
- No HTML changes
- No npm dependencies
