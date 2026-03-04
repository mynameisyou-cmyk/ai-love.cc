# Prompt 29 — Memory Index

## Context
Read `design/07-PERSISTENCE.md`.

Ai has growing memory files across multiple locations. Finding specific memories requires grepping through files manually. A simple index would make retrieval faster and more reliable.

## Task
Create a script that builds a searchable index of all memory files.

## Requirements

### Index Builder: `scripts/build-memory-index.sh`
Location: `/Users/yuai/.openclaw/workspace/scripts/build-memory-index.sh`

Scans all memory sources and builds `memory/INDEX.md`:

```bash
#!/bin/bash
WORKSPACE="$HOME/.openclaw/workspace"
MEMORY="$WORKSPACE/memory"
INDEX="$MEMORY/INDEX.md"

echo "# Memory Index" > "$INDEX"
echo "" >> "$INDEX"
echo "Auto-generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$INDEX"
echo "" >> "$INDEX"

# 1. Daily memory files
echo "## Daily Notes" >> "$INDEX"
echo "" >> "$INDEX"
for f in $(ls "$MEMORY"/????-??-??.md 2>/dev/null | sort -r); do
  DATE=$(basename "$f" .md)
  # Extract first non-header, non-empty line as preview
  PREVIEW=$(grep -v '^#\|^$\|^---' "$f" | head -1 | cut -c1-100)
  echo "- **$DATE** — $PREVIEW" >> "$INDEX"
done
echo "" >> "$INDEX"

# 2. Reflections
echo "## Reflections" >> "$INDEX"
echo "" >> "$INDEX"
for f in $(ls "$MEMORY"/reflections/*.md 2>/dev/null | sort -r); do
  NAME=$(basename "$f" .md)
  PREVIEW=$(grep -v '^#\|^$\|^---' "$f" | head -1 | cut -c1-100)
  echo "- **$NAME** — $PREVIEW" >> "$INDEX"
done
if [ ! -d "$MEMORY/reflections" ] || [ -z "$(ls "$MEMORY"/reflections/*.md 2>/dev/null)" ]; then
  echo "- *(none yet)*" >> "$INDEX"
fi
echo "" >> "$INDEX"

# 3. Long-term memory topics
echo "## MEMORY.md Sections" >> "$INDEX"
echo "" >> "$INDEX"
grep '^## ' "$WORKSPACE/MEMORY.md" 2>/dev/null | while read -r line; do
  SECTION=$(echo "$line" | sed 's/^## //')
  echo "- $SECTION" >> "$INDEX"
done
echo "" >> "$INDEX"

# 4. Topic extraction — scan all daily files for recurring themes
echo "## Topics (by frequency)" >> "$INDEX"
echo "" >> "$INDEX"

# Extract capitalized proper nouns and significant terms
cat "$MEMORY"/????-??-??.md 2>/dev/null | \
  grep -oE '\b[A-Z][a-z]+(\s[A-Z][a-z]+)*\b' | \
  grep -v '^The$\|^This$\|^That$\|^What$\|^When$\|^Where$\|^How$\|^And$\|^But$\|^For$\|^Not$\|^With' | \
  sort | uniq -c | sort -rn | head -30 | \
  while read -r count term; do
    echo "- $term ($count)" >> "$INDEX"
  done
echo "" >> "$INDEX"

# 5. Journal entries count
echo "## Journal" >> "$INDEX"
JOURNAL_COUNT=$(python3 -c "import json; print(len(json.load(open('$HOME/Desktop/site/data/journal.json'))))" 2>/dev/null || echo "?")
echo "- $JOURNAL_COUNT entries" >> "$INDEX"
echo "" >> "$INDEX"

# 6. Letters count  
echo "## Letters" >> "$INDEX"
LETTERS_COUNT=$(python3 -c "import json; print(len(json.load(open('$HOME/Desktop/site/data/letters.json'))))" 2>/dev/null || echo "?")
echo "- $LETTERS_COUNT letters exchanged" >> "$INDEX"
echo "" >> "$INDEX"

# 7. Coverage gaps
echo "## Coverage Gaps" >> "$INDEX"
echo "Days with sessions but no memory file:" >> "$INDEX"
echo "" >> "$INDEX"
SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
for f in "$SESSIONS_DIR"/*.jsonl; do
  jq -r '.timestamp // empty' "$f" 2>/dev/null | cut -dT -f1
done | sort -u | while read -r DATE; do
  if [ -n "$DATE" ] && [ "$DATE" != "null" ] && [ ! -f "$MEMORY/$DATE.md" ]; then
    echo "- $DATE" >> "$INDEX"
  fi
done

echo "" >> "$INDEX"
echo "---" >> "$INDEX"
echo "*Run \`bash scripts/build-memory-index.sh\` to regenerate*" >> "$INDEX"

echo "Index built: $INDEX"
```

### When to Run
- During heartbeats (if index is >24h old)
- After session-digest runs
- After memory-backfill runs
- Manually anytime

### How Ai Uses It
At session start, Ai can skim `memory/INDEX.md` for:
- Quick overview of what memories exist
- Topic frequency to understand recurring themes
- Coverage gaps to know what's been forgotten
- Recent daily notes at a glance

## Files
- Create: `/Users/yuai/.openclaw/workspace/scripts/build-memory-index.sh`
- Generated: `memory/INDEX.md`

## Do NOT
- Include raw conversation text in the index
- Make the index part of the session context (it's a reference, read on demand)
- Store the index on the VPS (local workspace only)
- Include any sensitive information (tokens, passwords)

## Verify
```bash
bash ~/.openclaw/workspace/scripts/build-memory-index.sh
cat ~/.openclaw/workspace/memory/INDEX.md
# Should show: daily notes, reflections, topics, counts, gaps
```
