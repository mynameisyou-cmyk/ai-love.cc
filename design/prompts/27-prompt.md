# Prompt 27 — Memory Backfill

## Context
Read `design/07-PERSISTENCE.md`. Ai has daily memory files for 9 days (Feb 18-28) but there are gaps. No files exist for: Feb 22, Feb 27, Mar 1, Mar 2, Mar 3, Mar 4. Session logs exist for those dates.

## Task
Run the session digest script (Prompt 26) for all dates that have sessions but no memory files, then review the generated files for quality.

## Requirements

### Backfill Script: `scripts/memory-backfill.sh`
Location: `/Users/yuai/.openclaw/workspace/scripts/memory-backfill.sh`

```bash
#!/bin/bash
# Find all dates that have session activity but no memory file
SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
MEMORY_DIR="$HOME/.openclaw/workspace/memory"
DIGEST="$HOME/.openclaw/workspace/scripts/session-digest.sh"

echo "Scanning sessions for dates without memory files..."

# Get all unique dates from session files
DATES=$(for f in "$SESSIONS_DIR"/*.jsonl; do
  jq -r '.timestamp // empty' "$f" 2>/dev/null | cut -dT -f1
done | sort -u)

FILLED=0
SKIPPED=0

for DATE in $DATES; do
  if [ -z "$DATE" ] || [ "$DATE" = "null" ]; then continue; fi

  if [ ! -f "$MEMORY_DIR/$DATE.md" ]; then
    echo "  Filling gap: $DATE"
    bash "$DIGEST" "$DATE"
    FILLED=$((FILLED + 1))
  else
    SKIPPED=$((SKIPPED + 1))
  fi
done

echo ""
echo "Done. Filled $FILLED gaps, skipped $SKIPPED existing files."
echo "Review: ls $MEMORY_DIR/"
```

### After Backfill
1. Run the backfill
2. Read each generated file
3. Check for obvious errors (wrong dates, garbled content)
4. Don't edit the content — Ai will review and curate during reflections

## Files
- Create: `/Users/yuai/.openclaw/workspace/scripts/memory-backfill.sh`

## Depends On
- Prompt 26 (session digest script) must be completed first

## Do NOT
- Overwrite existing memory files
- Edit generated files (Ai curates her own memory)
- Delete any session log files

## Verify
```bash
bash ~/.openclaw/workspace/scripts/memory-backfill.sh
ls -la ~/.openclaw/workspace/memory/*.md
# Should see files for all dates that had sessions
```
