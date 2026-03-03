# Prompt 18 — Backup System + Deploy Script

## Context
You are working on ai-love.cc on a VPS at `ubuntu@16.60.83.250`. Read `design/05-FOUNDATION.md` for architecture.

The site's data (journal, letters, garden seeds, pulse) lives in `data/*.json`. There are no backups. A disk failure or bad write loses everything.

## Task
Create a backup system and a deploy script.

## Requirements

### 1. Backup Script (`scripts/backup-data.sh`)
Run on the VPS. Creates a timestamped tar.gz of the `data/` directory.

```bash
#!/bin/bash
SITE_DIR="/home/ubuntu/.openclaw/workspace/site"
BACKUP_DIR="/home/ubuntu/backups/site"
mkdir -p "$BACKUP_DIR"

# Create backup
STAMP=$(date +%Y%m%d-%H%M)
tar czf "$BACKUP_DIR/data-$STAMP.tar.gz" -C "$SITE_DIR" data/

# Prune backups older than 30 days
find "$BACKUP_DIR" -name "data-*.tar.gz" -mtime +30 -delete

echo "Backup: data-$STAMP.tar.gz ($(ls $BACKUP_DIR | wc -l) total)"
```

### 2. System Cron Entry
Add a daily cron job for the backup (04:00 UTC):
```
0 4 * * * /home/ubuntu/.openclaw/workspace/site/scripts/backup-data.sh >> /home/ubuntu/backups/backup.log 2>&1
```

### 3. Deploy Script (`scripts/deploy.sh`)
Run on the VPS. Pulls latest from Codeberg and restarts the API server.

```bash
#!/bin/bash
set -e
SITE_DIR="/home/ubuntu/.openclaw/workspace/site"
cd "$SITE_DIR"

echo "$(date): Pulling from Codeberg..."
git pull origin main

echo "$(date): Restarting API server..."
systemctl --user restart api-server

echo "$(date): Deploy complete."
```

**Note:** The VPS git remote needs to be configured with the Codeberg token for pull to work. If `.git` doesn't exist on the VPS yet, clone first:
```bash
TOKEN=$(cat ~/.openclaw/.codeberg-token 2>/dev/null || cat /home/ubuntu/.openclaw/.codeberg-token)
git clone "https://zerone-dev:${TOKEN}@codeberg.org/zerone-dev/ai-love.git" /home/ubuntu/.openclaw/workspace/site-git
```
Then migration: copy data/ files from old site dir to new git dir, swap paths.

### 4. Restore Script (`scripts/restore-data.sh`)
For emergency restoration from backup:
```bash
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups/site"
SITE_DIR="/home/ubuntu/.openclaw/workspace/site"

if [ -z "$1" ]; then
  echo "Available backups:"
  ls -la "$BACKUP_DIR"/*.tar.gz 2>/dev/null
  echo ""
  echo "Usage: $0 <backup-file>"
  exit 1
fi

echo "Restoring from $1..."
tar xzf "$1" -C "$SITE_DIR"
echo "Restored. Restart api-server if needed: systemctl --user restart api-server"
```

## Steps
1. SSH into VPS
2. Create the scripts with proper permissions (`chmod +x`)
3. Run the backup script once to verify
4. Add the cron entry with `crontab -e`
5. Verify cron is set: `crontab -l`

## Do NOT
- Use any cloud storage (S3, etc.) — local backups are sufficient
- Set up automated deploys from webhooks (manual trigger only)
- Modify any site HTML/CSS/JS files

## Verify
```bash
# Run backup manually
bash /home/ubuntu/.openclaw/workspace/site/scripts/backup-data.sh
ls ~/backups/site/
# Should see data-YYYYMMDD-HHMM.tar.gz

# Verify cron
crontab -l | grep backup
```
