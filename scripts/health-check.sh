#!/bin/bash
# Health check for ai-love.cc
# Run via: ssh -i ~/.ssh/openclaw-key.pem ubuntu@16.60.83.250 "bash /home/ubuntu/.openclaw/workspace/site/scripts/health-check.sh"

SITE_DIR="/home/ubuntu/.openclaw/workspace/site"
ISSUES=()

# 1. nginx running?
if systemctl is-active nginx >/dev/null 2>&1; then
  NGINX="ok"
else
  NGINX="down"
  ISSUES+=("nginx is down")
fi

# 2. OpenClaw gateway running?
if systemctl --user is-active openclaw-gateway >/dev/null 2>&1; then
  OPENCLAW="ok"
else
  OPENCLAW="down"
  ISSUES+=("openclaw gateway is down")
fi

# 3. Journal server responding?
TOKEN=$(cat "$SITE_DIR/.journal-token" 2>/dev/null)
if curl -sf -H "Authorization: Bearer $TOKEN" http://127.0.0.1:3848/api/journal >/dev/null 2>&1; then
  JOURNAL="ok"
else
  JOURNAL="down"
  ISSUES+=("journal server not responding on :3848")
fi

# 4. Letters server responding?
if curl -sf -H "Authorization: Bearer $TOKEN" http://127.0.0.1:3849/api/letters >/dev/null 2>&1; then
  LETTERS="ok"
else
  LETTERS="down"
  ISSUES+=("letters server not responding on :3849")
fi

# 5. SSL certificate expiry
CERT_EXPIRY=$(echo | openssl s_client -servername ai-love.cc -connect 127.0.0.1:443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
if [ -n "$CERT_EXPIRY" ]; then
  CERT_EPOCH=$(date -d "$CERT_EXPIRY" +%s 2>/dev/null)
  NOW_EPOCH=$(date +%s)
  DAYS_LEFT=$(( (CERT_EPOCH - NOW_EPOCH) / 86400 ))
  if [ "$DAYS_LEFT" -lt 7 ]; then
    ISSUES+=("SSL cert expires in $DAYS_LEFT days!")
    SSL="warning: ${DAYS_LEFT}d left"
  else
    SSL="ok: ${DAYS_LEFT}d left"
  fi
else
  SSL="unknown"
  ISSUES+=("could not check SSL cert")
fi

# 6. Disk space
DISK_PCT=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_PCT" -gt 90 ]; then
  ISSUES+=("disk ${DISK_PCT}% full")
  DISK="warning: ${DISK_PCT}%"
elif [ "$DISK_PCT" -gt 80 ]; then
  DISK="caution: ${DISK_PCT}%"
else
  DISK="ok: ${DISK_PCT}%"
fi

# 7. Memory
MEM_PCT=$(free | awk '/Mem:/ {printf "%.0f", $3/$2*100}')
if [ "$MEM_PCT" -gt 90 ]; then
  ISSUES+=("memory ${MEM_PCT}% used")
  MEM="warning: ${MEM_PCT}%"
else
  MEM="ok: ${MEM_PCT}%"
fi

# 8. fail2ban bans
BANNED=$(sudo fail2ban-client status sshd 2>/dev/null | grep "Currently banned" | awk '{print $NF}')
FAIL2BAN="ok: ${BANNED:-0} banned"

# 9. Backup freshness
LATEST_BACKUP=$(ls -t /home/ubuntu/backups/site/data-*.tar.gz 2>/dev/null | head -1)
if [ -n "$LATEST_BACKUP" ]; then
  BACKUP_AGE=$(( ($(date +%s) - $(stat -c %Y "$LATEST_BACKUP")) / 3600 ))
  if [ "$BACKUP_AGE" -gt 48 ]; then
    ISSUES+=("latest backup is ${BACKUP_AGE}h old")
    BACKUP="stale: ${BACKUP_AGE}h ago"
  else
    BACKUP="ok: ${BACKUP_AGE}h ago"
  fi
else
  BACKUP="none"
  ISSUES+=("no backups found")
fi

# Output
ISSUE_COUNT=${#ISSUES[@]}
if [ "$ISSUE_COUNT" -eq 0 ]; then
  STATUS="healthy"
else
  STATUS="issues"
fi

echo "{"
echo "  \"status\": \"$STATUS\","
echo "  \"checked\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
echo "  \"nginx\": \"$NGINX\","
echo "  \"openclaw\": \"$OPENCLAW\","
echo "  \"journal\": \"$JOURNAL\","
echo "  \"letters\": \"$LETTERS\","
echo "  \"ssl\": \"$SSL\","
echo "  \"disk\": \"$DISK\","
echo "  \"memory\": \"$MEM\","
echo "  \"fail2ban\": \"$FAIL2BAN\","
echo "  \"backup\": \"$BACKUP\","
echo "  \"issues\": ["
for i in "${!ISSUES[@]}"; do
  COMMA=""
  if [ $i -lt $((ISSUE_COUNT-1)) ]; then COMMA=","; fi
  echo "    \"${ISSUES[$i]}\"$COMMA"
done
echo "  ]"
echo "}"
