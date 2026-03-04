# Health Check

Run from local machine:
```
ssh -i ~/.ssh/openclaw-key.pem ubuntu@16.60.83.250 "bash /home/ubuntu/.openclaw/workspace/site/scripts/health-check.sh"
```

If `status` is not "healthy", Ai will alert Yu via the current chat channel.

Checks: nginx, openclaw, journal, letters, SSL cert, disk, memory, fail2ban, backups.
