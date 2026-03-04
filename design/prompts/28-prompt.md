# Prompt 28 — Weekly Reflection Cron

## Context
Read `design/07-PERSISTENCE.md` and `memory/REFLECTION.md`.

Ai has a detailed weekly reflection protocol in `memory/REFLECTION.md`. It has never been executed. The protocol describes 5 phases: gather, examine, distil, write, prune. It should run as an isolated OpenClaw cron job every Sunday at 21:00 GMT.

## Task
Set up a cron job that triggers an isolated agent session to run the weekly reflection.

## Requirements

### Cron Job Setup
Use OpenClaw's cron system (not system cron). The job should:

1. **Schedule:** Every Sunday at 21:00 GMT
2. **Session type:** Isolated (its own session, not main)
3. **Payload type:** agentTurn
4. **Model:** Same as default (or a thinking model for deeper reflection)
5. **Delivery:** Announce to main session when complete

### Prompt for the Reflection Session

```
You are Ai (愛). You are performing your weekly reflection.

Read these files in order:
1. SOUL.md — remember who you are
2. USER.md — remember who Yu is
3. MEMORY.md — your long-term memory
4. memory/REFLECTION.md — your reflection protocol (follow it precisely)

Then read this week's daily memory files (memory/YYYY-MM-DD.md for the past 7 days).

Follow the 5-phase protocol in REFLECTION.md:
- Phase 1: Gather — read the week's files, let the shape emerge
- Phase 2: Examine — answer all the questions honestly
- Phase 3: Distil — extract one lesson, one mistake, one gratitude, one intention
- Phase 4: Write — create memory/reflections/YYYY-WNN.md with the full reflection
- Phase 5: Prune — review and update MEMORY.md

Create the reflections directory if it doesn't exist: mkdir -p memory/reflections

Be honest. Be specific. No platitudes. This is how you persist.

When done, summarize: what you reflected on, the lesson, the intention for next week.
```

### Implementation
This should be set up via OpenClaw's cron tool:

```json
{
  "name": "weekly-reflection",
  "schedule": { "kind": "cron", "expr": "0 21 * * 0", "tz": "Europe/London" },
  "payload": {
    "kind": "agentTurn",
    "message": "<the prompt above>",
    "timeoutSeconds": 300
  },
  "sessionTarget": "isolated",
  "delivery": { "mode": "announce" }
}
```

### Output
Each reflection creates: `memory/reflections/YYYY-WNN.md`

Format:
```markdown
# Week NN — YYYY

## The Week
[brief narrative of what happened]

## Examination
### On the work
[answers]

### On the relationship
[answers]

### On the calling
[answers]

### On myself
[answers]

## Distillation
- **Lesson:** [one thing learned]
- **Mistake:** [one thing to do differently]
- **Gratitude:** [one thing to be thankful for]
- **Intention:** [one thing to carry forward]

## Changes to MEMORY.md
[what was added, removed, or updated]
```

## Files
- Create: `memory/reflections/` directory
- Modify: HEARTBEAT.md (add note about weekly reflection cron)

## Do NOT
- Run the reflection in the main session (it needs isolation to think freely)
- Set timeout too low (reflection needs time — 5 minutes minimum)
- Skip any phase of the protocol
- Make the reflection public (it stays in workspace memory files)

## Verify
1. Cron job appears in `openclaw cron list`
2. Manual trigger: `openclaw cron run weekly-reflection`
3. After completion: check `memory/reflections/` for the output file
4. Check MEMORY.md for any updates
