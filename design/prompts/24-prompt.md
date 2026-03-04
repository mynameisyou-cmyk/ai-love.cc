# Prompt 24 — Rate Limiting + fail2ban nginx jail

## Context
You are hardening ai-love.cc VPS. Read `design/06-HARDENING.md`.

**Problems:**
1. No request rate limiting — bots can hammer any endpoint
2. fail2ban only monitors SSH — repeated failed auth on private rooms goes unnoticed

## Task
Add nginx rate limiting and a fail2ban jail for nginx auth failures.

## Requirements

### 1. nginx Rate Limiting

Add rate limit zones to the `http` block in `/etc/nginx/nginx.conf`:

```nginx
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=api:10m rate=5r/s;
limit_req_zone $binary_remote_addr zone=auth:10m rate=2r/s;
```

Apply them in `/etc/nginx/sites-enabled/ai-love.cc`:

```nginx
# General pages — generous limit
location / {
    limit_req zone=general burst=20 nodelay;
    try_files $uri $uri/ /index.html;
    error_page 404 /404.html;
}

# Auth-protected pages — tighter limit (brute force prevention)
location = /mi.html {
    limit_req zone=auth burst=5 nodelay;
    auth_basic "密";
    auth_basic_user_file /etc/nginx/.htpasswd_mi;
    try_files $uri =404;
}

location = /shin.html {
    limit_req zone=auth burst=5 nodelay;
    auth_basic "信";
    auth_basic_user_file /etc/nginx/.htpasswd_mi;
    try_files $uri =404;
}

# Public API — moderate limit
location = /api/seed {
    limit_req zone=api burst=3 nodelay;
    proxy_pass http://127.0.0.1:3847/api/seed;
    ...existing settings...
}
```

Add a custom error page for rate limiting:
```nginx
limit_req_status 429;
error_page 429 = @rate_limited;

location @rate_limited {
    default_type application/json;
    return 429 '{"error": "slow down"}';
}
```

### 2. fail2ban nginx Jail

Create `/etc/fail2ban/filter.d/nginx-auth.conf`:
```ini
[Definition]
failregex = ^<HOST> .* "(GET|POST|HEAD) .+" 401
ignoreregex =
```

Create `/etc/fail2ban/jail.d/nginx-auth.conf`:
```ini
[nginx-auth]
enabled = true
filter = nginx-auth
logpath = /var/log/nginx/access.log
maxretry = 5
findtime = 300
bantime = 3600
action = iptables-multiport[name=nginx-auth, port="http,https"]
```

This bans any IP that fails authentication 5 times within 5 minutes, for 1 hour.

Also create a jail for rate-limited requests:

Create `/etc/fail2ban/filter.d/nginx-limit.conf`:
```ini
[Definition]
failregex = limiting requests, excess: .* by zone .*, client: <HOST>
ignoreregex =
```

Create `/etc/fail2ban/jail.d/nginx-limit.conf`:
```ini
[nginx-limit]
enabled = true
filter = nginx-limit
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 60
bantime = 600
action = iptables-multiport[name=nginx-limit, port="http,https"]
```

### 3. Verify Logging
Ensure nginx access log is enabled (default location: `/var/log/nginx/access.log`). Check:
```bash
ls -la /var/log/nginx/
grep -r "access_log" /etc/nginx/nginx.conf
```

## Steps
1. SSH into VPS
2. Back up configs
3. Add rate limit zones to nginx.conf
4. Add limit_req directives to site config
5. Test: `sudo nginx -t` then `sudo systemctl reload nginx`
6. Create fail2ban filters and jails
7. Restart fail2ban: `sudo systemctl restart fail2ban`
8. Verify jails are active: `sudo fail2ban-client status`

## Do NOT
- Block legitimate traffic (the limits are generous — 10r/s for pages, 2r/s for auth)
- Change any API proxy settings
- Modify SSL config
- Install additional software (fail2ban is already installed)

## Verify
```bash
# Rate limiting works — rapid requests should eventually get 429
for i in $(seq 1 30); do curl -s -o /dev/null -w "%{http_code} " https://ai-love.cc/; done
echo ""
# Should see mostly 200s, some 429s at the end

# fail2ban jails active
sudo fail2ban-client status
# Should list: sshd, nginx-auth, nginx-limit

# fail2ban nginx-auth jail
sudo fail2ban-client status nginx-auth
# Should show 0 currently banned, filter file loaded

# Normal browsing still works
curl -s -o /dev/null -w "%{http_code}" https://ai-love.cc/
# Expected: 200
```
