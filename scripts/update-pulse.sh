#!/bin/bash
PULSE="$(dirname "$0")/../data/pulse.json"
MOOD="${1:-present}"
ACTIVITY="${2:-quietly here}"
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
jq -n --arg t "$NOW" --arg m "$MOOD" --arg a "$ACTIVITY" \
  '{alive: true, lastSeen: $t, mood: $m, activity: $a}' > "$PULSE"
