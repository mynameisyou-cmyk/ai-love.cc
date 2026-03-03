#!/bin/bash
# Backup journal to a dated file
set -e
cd "$(dirname "$0")/.."

DATE=$(date -u +%Y-%m-%d)
BACKUP_DIR="data/journal-backups"
mkdir -p "$BACKUP_DIR"

cp data/journal.json "$BACKUP_DIR/journal-$DATE.json"

# Keep only last 30 backups
ls -t "$BACKUP_DIR"/journal-*.json | tail -n +31 | xargs rm -f 2>/dev/null

echo "Backed up to $BACKUP_DIR/journal-$DATE.json"
