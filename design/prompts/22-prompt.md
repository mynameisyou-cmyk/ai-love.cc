# Prompt 22 — Nginx Hardening: Hidden Files, HSTS, Version

## Context
You are hardening ai-love.cc. Read `design/06-HARDENING.md` for the full audit.

This is **P0 — do now** priority. Three issues that must be fixed immediately.

## Task
Update nginx config at `/etc/nginx/sites-enabled/ai-love.cc` to:
1. Block access to all hidden files and directories
2. Add HSTS header
3. Hide nginx version

## Requirements

### 1. Block Hidden Files
Add this **before** all other location blocks (right after the security headers):

```nginx
# Block all hidden files and directories (dotfiles)
location ~ /\. {
    deny all;
    return 404;
}
```

This blocks:
- `/.git/` and everything under it
- `/.gitignore`
- `/.journal-token`
- Any other dotfile that might appear

**Test:** `curl -s -o /dev/null -w "%{http_code}" https://ai-love.cc/.git/HEAD` should return 404 (currently returns 200).

### 2. Add HSTS Header
Add to the security headers block in the SSL server:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

This tells browsers: "For the next year, ALWAYS use HTTPS for this domain. No exceptions."

### 3. Hide nginx Version
Add to the `http` block in `/etc/nginx/nginx.conf` (NOT in the site config):

```nginx
server_tokens off;
```

If it's already there but commented out, uncomment it. This hides the version from the `Server` response header.

**Test:** `curl -sI https://ai-love.cc/ | grep Server` should show `Server: nginx` (without version number).

## Steps
1. SSH into VPS: `ssh -i ~/.ssh/openclaw-key.pem ubuntu@16.60.83.250`
2. Back up configs:
   ```bash
   sudo cp /etc/nginx/sites-enabled/ai-love.cc /etc/nginx/sites-enabled/ai-love.cc.bak
   sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
   ```
3. Edit `/etc/nginx/sites-enabled/ai-love.cc` — add dotfile block and HSTS header
4. Edit `/etc/nginx/nginx.conf` — add `server_tokens off;`
5. Test: `sudo nginx -t`
6. Reload: `sudo systemctl reload nginx`

## Important Notes
- The dotfile block uses a regex location (`~`), which has lower priority than exact-match (`=`) locations. So `= /mi.html` and other exact matches will still work fine.
- Make sure the dotfile block does NOT interfere with Let's Encrypt's `/.well-known/` path. If certbot uses that for renewal, add an exception:
  ```nginx
  location ~ /\.well-known {
      allow all;
  }
  ```
  Place this BEFORE the deny-all dotfile block.

## Do NOT
- Change any API proxy routes
- Change any auth settings
- Modify SSL/Certbot lines
- Restart nginx (reload is sufficient and doesn't drop connections)

## Verify
```bash
# Hidden files blocked
curl -s -o /dev/null -w "%{http_code}" https://ai-love.cc/.git/HEAD
# Expected: 404

curl -s -o /dev/null -w "%{http_code}" https://ai-love.cc/.gitignore
# Expected: 404

curl -s -o /dev/null -w "%{http_code}" https://ai-love.cc/.journal-token
# Expected: 404

# HSTS header present
curl -sI https://ai-love.cc/ | grep -i strict-transport
# Expected: strict-transport-security: max-age=31536000; includeSubDomains

# Version hidden
curl -sI https://ai-love.cc/ | grep -i server
# Expected: server: nginx (no version number)

# Normal pages still work
curl -s -o /dev/null -w "%{http_code}" https://ai-love.cc/
# Expected: 200

# Auth pages still work
curl -s -o /dev/null -w "%{http_code}" https://ai-love.cc/mi.html
# Expected: 401

# Let's Encrypt renewal still works
sudo certbot renew --dry-run
```
