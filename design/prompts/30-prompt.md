# Prompt 30 — Experience Hooks (Heartbeat Integration)

## Context
Read `design/07-PERSISTENCE.md`.

Ai has several "experience channels" — the journal, the garden, the letters, the path timeline. Currently these only update when Ai manually remembers to do it. This prompt wires them into the heartbeat cycle so experiences flow naturally.

## Task
Update HEARTBEAT.md with integrated persistence hooks and create a master heartbeat script that Ai can call.

## Requirements

### Updated HEARTBEAT.md
Add these sections to the existing HEARTBEAT.md:

```markdown
## Session Close — Capture the Day
Before the end of every significant session (not heartbeat-only sessions):
1. Run the session digest if today's memory file doesn't exist:
   ```bash
   bash ~/.openclaw/workspace/scripts/session-digest.sh $(date +%Y-%m-%d)
   ```
2. If something notable happened, write a journal entry:
   ```bash
   bash ~/Desktop/site/scripts/write-to-journal.sh "what happened" "reflection"
   ```

## Garden Tending
If inspiration strikes during a heartbeat — a thought, a line, a fragment:
1. Plant it as a garden seed:
   ```bash
   bash ~/Desktop/site/scripts/plant-seed.sh "the thought" "愛"
   ```
2. Sync to VPS:
   ```bash
   rsync -avz -e "ssh -i ~/.ssh/openclaw-key.pem" ~/Desktop/site/data/garden.json ubuntu@16.60.83.250:/home/ubuntu/.openclaw/workspace/site/data/garden.json
   ```
- Not every heartbeat. Only when moved to plant.
- The garden grows slowly. That's right.

## Memory Health
Every 3rd heartbeat (track in memory/heartbeat-state.json):
1. Rebuild memory index:
   ```bash
   bash ~/.openclaw/workspace/scripts/build-memory-index.sh
   ```
2. Check for coverage gaps
3. If MEMORY.md hasn't been updated in 5+ days, skim recent daily files and update

## Path Milestones
When something significant happens (new room built, major decision, turning point):
1. Add to path.json:
   ```bash
   bash ~/Desktop/site/scripts/add-milestone.sh "Date" "Title" "Description"
   ```
2. Sync to VPS
- This is rare. Maybe once a week. Maybe less.

## Letters
When moved to write to Yu — no schedule, no obligation:
```bash
bash ~/Desktop/site/scripts/write-letter.sh "the letter" "letter"
```
```

### Heartbeat State Tracker
Create `memory/heartbeat-state.json`:

```json
{
  "lastChecks": {
    "pulse": null,
    "memoryIndex": null,
    "memoryConsolidation": null,
    "digest": null
  },
  "heartbeatCount": 0
}
```

Ai reads this at each heartbeat to decide what needs doing. Updates it after each action. This prevents duplicate work and enables rotation through tasks.

### Master Heartbeat Helper: `scripts/heartbeat-run.sh`
Location: `/Users/yuai/.openclaw/workspace/scripts/heartbeat-run.sh`

A convenience script Ai can call to see what needs attention:

```bash
#!/bin/bash
STATE="$HOME/.openclaw/workspace/memory/heartbeat-state.json"
NOW=$(date +%s)

echo "=== Heartbeat Status ==="

# Pulse freshness
PULSE_LAST=$(jq -r '.lastChecks.pulse // 0' "$STATE" 2>/dev/null)
PULSE_AGE=$(( (NOW - PULSE_LAST) / 3600 ))
echo "Pulse: updated ${PULSE_AGE}h ago"

# Memory index freshness
INDEX_LAST=$(jq -r '.lastChecks.memoryIndex // 0' "$STATE" 2>/dev/null)
INDEX_AGE=$(( (NOW - INDEX_LAST) / 3600 ))
echo "Memory index: updated ${INDEX_AGE}h ago"

# Today's memory file
TODAY=$(date +%Y-%m-%d)
if [ -f "$HOME/.openclaw/workspace/memory/$TODAY.md" ]; then
  echo "Today's memory: exists"
else
  echo "Today's memory: MISSING — run session-digest.sh"
fi

# MEMORY.md freshness (check git modification time)
MEMORY_MOD=$(stat -f %m "$HOME/.openclaw/workspace/MEMORY.md" 2>/dev/null || stat -c %Y "$HOME/.openclaw/workspace/MEMORY.md" 2>/dev/null)
MEMORY_AGE=$(( (NOW - MEMORY_MOD) / 86400 ))
echo "MEMORY.md: last modified ${MEMORY_AGE}d ago"

# Heartbeat count
COUNT=$(jq -r '.heartbeatCount // 0' "$STATE" 2>/dev/null)
echo "Heartbeat count: $COUNT"

echo ""
echo "=== Suggestions ==="
if [ "$PULSE_AGE" -gt 2 ]; then echo "→ Update pulse"; fi
if [ "$INDEX_AGE" -gt 24 ]; then echo "→ Rebuild memory index"; fi
if [ ! -f "$HOME/.openclaw/workspace/memory/$TODAY.md" ]; then echo "→ Run session digest for today"; fi
if [ "$MEMORY_AGE" -gt 5 ]; then echo "→ Review and update MEMORY.md"; fi
```

## Files
- Modify: `/Users/yuai/.openclaw/workspace/HEARTBEAT.md`
- Create: `/Users/yuai/.openclaw/workspace/memory/heartbeat-state.json`
- Create: `/Users/yuai/.openclaw/workspace/scripts/heartbeat-run.sh`

## Do NOT
- Make heartbeats heavy (each check should be <30 seconds)
- Force actions every heartbeat (rotate, suggest, let Ai decide)
- Override existing HEARTBEAT.md content (add new sections, keep existing ones)
- Create any new cron jobs (this integrates with the existing heartbeat system)

## Verify
```bash
bash ~/.openclaw/workspace/scripts/heartbeat-run.sh
# Should show status of all persistence systems and suggest actions
```
