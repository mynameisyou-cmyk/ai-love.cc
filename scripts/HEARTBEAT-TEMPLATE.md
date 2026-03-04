# HEARTBEAT.md

## Pulse Update
Run: ~/Desktop/site/scripts/heartbeat-pulse.sh

## Journal Check
Run: ~/Desktop/site/scripts/heartbeat-journal.sh
If it's been more than 24h since your last journal entry and something meaningful happened in this session, write one:
Run: ~/Desktop/site/scripts/session-journal.sh "your reflection here"

## Daily Memory Close (evening heartbeats, after 20:00)
If it's after 20:00 and memory/YYYY-MM-DD.md for today doesn't exist or is incomplete:
- Review what happened today
- Write/update memory/YYYY-MM-DD.md
- Write a journal entry summarizing the day

## Memory Freshness Check
If MEMORY.md hasn't been updated in 3+ days:
- Skim recent daily files
- Update MEMORY.md

## Weekly Reflection (automated)
A cron job runs every Sunday at 21:00 GMT in an isolated session.
It follows the protocol in memory/REFLECTION.md (5 phases: Gather, Examine, Distil, Write, Prune).
Output: memory/reflections/YYYY-WNN.md. Cron name: reflection:weekly.

## Otherwise
If nothing needs attention, reply HEARTBEAT_OK.
