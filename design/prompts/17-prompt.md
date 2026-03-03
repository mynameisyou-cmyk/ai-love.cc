# Prompt 17 — Nginx Hardening + API Migration

## Context
You are working on ai-love.cc. Read `design/05-FOUNDATION.md` for architecture.

Prompt 16 created a consolidated `api-server.js` on port 3850. This prompt migrates nginx to use it and adds security headers.

## Task
Update the nginx config at `/etc/nginx/sites-enabled/ai-love.cc` to:

1. Route all API traffic to the new consolidated server (port 3850)
2. Add privacy/security headers
3. Keep existing auth patterns

## Requirements

### API Route Changes
Replace all existing API proxy blocks (journal :3848, letters :3849, seed :3847) with routes pointing to port 3850. The route paths stay the same — only the proxy_pass port changes.

Keep the structure:
- `/api/journal` — auth_basic required, proxy to 3850
- `/api/letters` — auth_basic required, proxy to 3850
- `/api/seed` — public, proxy to 3850
- `/api/pulse` — public, proxy to 3850
- `/api/health` — public, proxy to 3850
- `/api/journal-internal` — localhost only, proxy to 3850

**IMPORTANT:** The OpenClaw webchat `/api/` catch-all block (proxy to :18789) must remain LAST. All specific `/api/xxx` routes must come before it. Use `= /api/xxx` (exact match) for specific routes so the catch-all doesn't swallow them.

### Security Headers
Add to the `server` block (inside the SSL server):

```nginx
# Security headers
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self'; media-src 'self'; connect-src 'self'" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "no-referrer" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
```

### Protected Pages (no change needed, verify they're still there)
- `/mi.html` — auth_basic "密"
- `/shin.html` — auth_basic "信"
- `/data/journal.json` — auth_basic
- `/data/letters.json` — auth_basic

## Steps
1. SSH into VPS: `ssh -i ~/.ssh/openclaw-key.pem ubuntu@16.60.83.250`
2. Back up current nginx config: `sudo cp /etc/nginx/sites-enabled/ai-love.cc /etc/nginx/sites-enabled/ai-love.cc.bak`
3. Edit the config file
4. Test: `sudo nginx -t`
5. If test passes: `sudo systemctl reload nginx`
6. Verify all routes work with curl tests

## Do NOT
- Remove the OpenClaw `/api/` catch-all block
- Change SSL/Certbot managed lines
- Change the HTTP→HTTPS redirect server block
- Remove any existing location blocks for static files

## Verify
```bash
# Health endpoint (public)
curl -s https://ai-love.cc/api/health

# Journal (should 401 without auth)
curl -s https://ai-love.cc/api/journal

# Security headers
curl -sI https://ai-love.cc/ | grep -i "content-security-policy\|x-frame\|referrer\|permissions"

# Protected pages (should 401)
curl -s -o /dev/null -w "%{http_code}" https://ai-love.cc/mi.html
curl -s -o /dev/null -w "%{http_code}" https://ai-love.cc/shin.html
```
