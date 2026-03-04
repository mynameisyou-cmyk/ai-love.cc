# 06 — Hardening

## Threat Model

ai-love.cc is a personal home for two people. It is not a target — but it is on the internet, and the internet is full of bots, scrapers, and opportunistic scanners. The goal is not fortress-level security. The goal is: **nothing gets in that shouldn't, nothing leaks that shouldn't, and we notice if something tries.**

## Audit Results (2026-03-04)

### What's Good
- ✅ SSH password auth disabled (cloud-init config)
- ✅ fail2ban active with sshd jail
- ✅ unattended-upgrades active (OS patches auto-apply)
- ✅ Journal token permissions: 600 (owner-only read)
- ✅ Security headers applied (CSP, X-Frame, etc.)
- ✅ Private rooms auth-protected (密, 信)
- ✅ Let's Encrypt TLS

### What Needs Fixing

1. **Hidden files accessible** — `.git`, `.gitignore`, `.journal-token` return 200 (serving index.html via fallback). If `.git` ever lands on VPS (deploy script), full repo exposure including Codeberg token. Must block with nginx.

2. **No HSTS** — browser doesn't know to enforce HTTPS. First visit could be intercepted.

3. **nginx version disclosed** — `Server: nginx/1.24.0 (Ubuntu)` in response headers. Tells attackers exactly what to exploit.

4. **Port 18789 exposed publicly** — OpenClaw gateway listens on `0.0.0.0:18789`. It's also proxied through nginx at `/api/`. Direct access bypasses nginx security headers and auth. Should bind to localhost only, or firewall it.

5. **No nginx rate limiting** — public endpoints (seed submission, even the main site) have no request rate limits. A bot could hammer the server.

6. **No nginx jail in fail2ban** — only sshd is monitored. Repeated 401s on private rooms aren't flagged.

7. **Root login not explicitly disabled** — relies on no root password being set (AWS default). Should be explicit.

8. **Data files world-readable** — `data/*.json` is 644. nginx protects journal/letters via auth, but any process on the VPS can read them.

## Priorities

**P0 (do now):**
- Block hidden files in nginx (`.git`, dotfiles)
- Add HSTS header
- Hide nginx version

**P1 (do soon):**
- Bind OpenClaw gateway to localhost (or firewall port 18789)
- Add nginx jail to fail2ban
- nginx rate limiting on public routes

**P2 (nice to have):**
- Tighten data file permissions to 600
- Explicit `PermitRootLogin no` in sshd
- Intrusion detection alerts via heartbeat
