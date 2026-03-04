# Prompt 23 — Gateway Lockdown + Firewall

## Context
You are hardening ai-love.cc VPS (ubuntu@16.60.83.250). Read `design/06-HARDENING.md`.

**Problem:** The OpenClaw gateway listens on `0.0.0.0:18789` — accessible to anyone on the internet. It's also proxied through nginx at `/api/`. Direct access on port 18789 bypasses all nginx security headers, auth rules, and rate limits.

## Task
Lock down port 18789 so it's only accessible through nginx, and tighten the firewall.

## Requirements

### Option A: Bind OpenClaw to localhost (preferred)
If OpenClaw config allows binding to `127.0.0.1` instead of `0.0.0.0`:

1. Check OpenClaw config: `cat /home/ubuntu/.openclaw/config.yaml` (or wherever the config lives)
2. Find the gateway listen/bind address setting
3. Change it to `127.0.0.1:18789`
4. Restart OpenClaw: `openclaw gateway restart` or `systemctl --user restart openclaw-gateway`

### Option B: Firewall (if OpenClaw can't bind to localhost)
Use `ufw` to block external access to port 18789:

```bash
# Enable ufw if not already
sudo ufw status

# Allow SSH (critical — do this FIRST or you'll lock yourself out)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Block 18789 from outside (allow localhost only)
# Don't add a rule for 18789 — ufw default deny handles it
# But make sure it's not in any allow rule

sudo ufw enable
sudo ufw status
```

**WARNING:** Always ensure SSH (port 22) is allowed BEFORE enabling ufw. Locking yourself out of a VPS is permanent without console access.

### Also: Explicit SSH hardening
Add to `/etc/ssh/sshd_config.d/99-hardening.conf`:

```
PermitRootLogin no
MaxAuthTries 3
LoginGraceTime 30
AllowUsers ubuntu
```

Then: `sudo systemctl reload sshd`

## Steps
1. SSH into VPS
2. Check current firewall state: `sudo ufw status`
3. Check if AWS Security Group already restricts 18789 (it might — check via AWS console or CLI)
4. Try Option A first (check OpenClaw config)
5. If Option A isn't possible, use Option B
6. Apply SSH hardening
7. Verify you can still SSH in (test from a second terminal BEFORE closing the first)

## Critical Safety Rules
- **NEVER close your SSH session until you've verified you can open a new one**
- **ALWAYS allow port 22 before enabling any firewall**
- **Test SSH access from a second terminal before proceeding**
- If something goes wrong: AWS console → EC2 → Instance → Connect (serial console) is the emergency exit

## Do NOT
- Change nginx config (that's a separate prompt)
- Modify OpenClaw's chat/session settings
- Block port 80 or 443
- Change SSH keys

## Verify
```bash
# From local machine — port 18789 should be unreachable
curl -s --connect-timeout 5 http://16.60.83.250:18789/ ; echo "exit: $?"
# Expected: connection timeout or refused

# nginx proxy still works
curl -s -o /dev/null -w "%{http_code}" https://ai-love.cc/api/chat
# Expected: 200

# SSH still works
ssh -i ~/.ssh/openclaw-key.pem ubuntu@16.60.83.250 "echo 'SSH OK'"

# Webchat still works
# Open https://ai-love.cc in browser, verify chat loads
```
