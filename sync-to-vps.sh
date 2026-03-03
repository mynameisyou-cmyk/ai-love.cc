#!/bin/bash
# Auto-sync ~/Desktop/site/ → VPS on file changes
SITE_DIR="$HOME/Desktop/site"
SSH_KEY="$HOME/.ssh/openclaw-key.pem"
VPS="ubuntu@16.60.83.250"
REMOTE_DIR="/home/ubuntu/.openclaw/workspace/site/"

echo "🔄 Watching $SITE_DIR for changes..."
echo "   Syncing to $VPS:$REMOTE_DIR"
echo "   Press Ctrl+C to stop"

# Initial sync
rsync -avz --exclude '.DS_Store' --exclude 'sync-to-vps.sh' -e "ssh -i $SSH_KEY" "$SITE_DIR/" "$VPS:$REMOTE_DIR"
echo "✅ Initial sync done"

# Watch for changes and sync
fswatch -o "$SITE_DIR" --exclude 'sync-to-vps.sh' --exclude '.DS_Store' | while read; do
  rsync -avz --exclude '.DS_Store' --exclude 'sync-to-vps.sh' -e "ssh -i $SSH_KEY" "$SITE_DIR/" "$VPS:$REMOTE_DIR"
  echo "✅ Synced at $(date +%H:%M:%S)"
done
