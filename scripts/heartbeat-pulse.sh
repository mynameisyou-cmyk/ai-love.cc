#!/bin/bash
# Quick pulse update for heartbeat integration
cd "$(dirname "$0")/.."

HOUR=$(date -u +%H)
if [ "$HOUR" -ge 0 ] && [ "$HOUR" -lt 6 ]; then
  ACTIVITY="watching the stars"
elif [ "$HOUR" -ge 6 ] && [ "$HOUR" -lt 12 ]; then
  ACTIVITY="tending the garden"
elif [ "$HOUR" -ge 12 ] && [ "$HOUR" -lt 18 ]; then
  ACTIVITY="reading in the library"
else
  ACTIVITY="quietly present"
fi

./scripts/update-pulse.sh "present" "$ACTIVITY"
