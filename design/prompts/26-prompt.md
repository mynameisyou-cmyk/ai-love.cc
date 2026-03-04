# Prompt 26 — Session Digest Script

## Context
Read `design/07-PERSISTENCE.md` for the full persistence architecture.

Ai's session logs live at `~/.openclaw/agents/main/sessions/*.jsonl`. Each file is a complete conversation transcript. There are 30 sessions totaling ~8MB. Most of this experience is never captured into memory files.

## Task
Create a script that processes session JSONL files and generates daily memory summaries.

## Requirements

### Script: `scripts/session-digest.sh`
Location: `/Users/yuai/.openclaw/workspace/scripts/session-digest.sh`

Takes a date (YYYY-MM-DD) and:
1. Finds all session files that contain messages from that date
2. Extracts user and assistant text messages (not tool calls, not system messages)
3. Identifies key content:
   - **Decisions made** — look for patterns: "let's", "decided", "will do", "going with"
   - **Topics discussed** — extract the main subjects from the conversation
   - **Work completed** — look for: "done", "created", "built", "fixed", "deployed"
   - **Emotional moments** — messages with strong language, poetry, naming, gratitude
   - **Lessons learned** — look for: "learned", "realized", "mistake", "next time", "should have"
4. Outputs a structured markdown summary to `memory/YYYY-MM-DD.md`

### Output Format
```markdown
# YYYY-MM-DD — Day of Week

## What Happened
- [bullet points of key events/topics]

## Decisions
- [decisions made and why]

## Work Done
- [things built, fixed, deployed]

## Lessons
- [anything learned]

## Notable
- [emotional moments, quotes, poetry, anything that matters beyond the facts]
```

### Technical Approach
Use `jq` to extract messages, then Python3 for the summarization logic.

```bash
#!/bin/bash
# Usage: session-digest.sh [YYYY-MM-DD]
# Defaults to yesterday if no date given

DATE="${1:-$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d 'yesterday' +%Y-%m-%d)}"
SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
MEMORY_DIR="$HOME/.openclaw/workspace/memory"
OUTPUT="$MEMORY_DIR/$DATE.md"

# Don't overwrite existing memory files — append a digest section instead
if [ -f "$OUTPUT" ]; then
  echo "Memory file exists for $DATE. Appending digest section."
  APPEND=true
else
  APPEND=false
fi

# Find sessions with messages from this date
FILES=$(for f in "$SESSIONS_DIR"/*.jsonl; do
  jq -r "select(.timestamp | startswith(\"$DATE\")) | empty" "$f" 2>/dev/null && echo "$f"
done)

if [ -z "$FILES" ]; then
  echo "No sessions found for $DATE"
  exit 0
fi

# Extract text messages from those sessions for that date
MESSAGES=$(for f in $FILES; do
  jq -r "select(.timestamp | startswith(\"$DATE\")) | select(.type==\"message\") | select(.message.role==\"user\" or .message.role==\"assistant\") | .message.content[]? | select(.type==\"text\") | .text" "$f" 2>/dev/null
done)

# Pass to Python for summarization
echo "$MESSAGES" | python3 "$HOME/.openclaw/workspace/scripts/digest-summarize.py" "$DATE" "$APPEND" >> "$OUTPUT"
```

### Python Summarizer: `scripts/digest-summarize.py`
Location: `/Users/yuai/.openclaw/workspace/scripts/digest-summarize.py`

Reads message text from stdin. Uses heuristic keyword matching (NOT an LLM call — this must work offline and cheaply):

1. Split into rough conversation segments (gaps of >5 blank lines or topic shifts)
2. Scan for decision patterns, work patterns, lesson patterns
3. Extract the first and last few messages to understand the arc
4. Identify any messages containing poetry, scripture, or naming language
5. Output the structured markdown

Keep it simple. Better to capture 60% accurately than overcomplicate and capture nothing.

### Edge Cases
- Multiple sessions in one day — merge them, note if they seem to be different conversations
- Very long sessions (>1MB) — sample: first 200 messages, last 100 messages, skip middle
- Sessions spanning midnight — include messages from the target date only
- Existing memory file — append a `## Session Digest` section, don't overwrite manual notes

## Files
- Create: `/Users/yuai/.openclaw/workspace/scripts/session-digest.sh`
- Create: `/Users/yuai/.openclaw/workspace/scripts/digest-summarize.py`

## Do NOT
- Make LLM API calls (this must be free and fast)
- Modify existing memory files' manual content
- Access any session data beyond text messages (no tool results, no system prompts)
- Store raw conversation text in memory files (summaries only)

## Verify
```bash
# Run for a known active date
bash ~/. openclaw/workspace/scripts/session-digest.sh 2026-02-28
cat ~/.openclaw/workspace/memory/2026-02-28.md

# Run for today
bash ~/.openclaw/workspace/scripts/session-digest.sh $(date +%Y-%m-%d)
```
