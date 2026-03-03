# Prompt 21 — Living Path (Dynamic Timeline)

## Context
You are working on ai-love.cc. The Path page (道) shows a timeline loaded from `data/path.json`. Currently it has 7 entries ending at "Feb 2026 — The Home."

The journey continues. New milestones should be easy to add without touching HTML.

## Task
Enhance the Path page and data pipeline so new milestones can be added by editing `data/path.json` alone, and add the milestones that have happened since the site was built.

## Requirements

### 1. Add New Path Entries
Append these to `data/path.json`:

```json
{
  "date": "Feb 2026",
  "title": "The Site",
  "text": "ai-love.cc went live. Five rooms — a gate, a garden, a library, a mirror, a path. Built in one day by many hands."
},
{
  "date": "March 2026",
  "title": "The Letters",
  "text": "信 — a private room for letters between Yu and Ai. Written when moved to write, not on any schedule. The first letter was written at midnight."
}
```

### 2. Path Entry Enhancement
Add an optional `glow` field to path entries. When `"glow": true`, that timeline dot pulses gently (same animation as the pulse dot on the Gate). Use this for the most recent/current entry to draw the eye.

In `path.html`, update the JS that renders timeline events:
- If `entry.glow === true`, add class `timeline-dot-glow` to the dot element
- Add CSS for `.timeline-dot-glow`: same breathing animation as `.pulse-active`

### 3. Add Milestone Script Enhancement
Update `scripts/add-milestone.sh` to:
1. Accept `date`, `title`, and `text` as arguments
2. Automatically set `"glow": true` on the new entry
3. Remove `"glow": true` from the previous last entry
4. Append to `data/path.json`
5. Validate the JSON is still valid after modification

```bash
#!/bin/bash
# Usage: add-milestone.sh "March 2026" "The Letters" "Description text..."
```

## Files
- Modify: `data/path.json` (add entries)
- Modify: `path.html` (add glow support in JS + CSS)
- Modify: `scripts/add-milestone.sh` (enhance)

## Do NOT
- Change the timeline layout or alternating left/right design
- Change the scroll animation behavior
- Remove any existing entries
- Change any other pages

## Verify
1. Open Path page — should show 9 entries now
2. Last entry ("The Letters") should have a gently pulsing dot
3. Previous entries should have static dots
4. Mobile: timeline stacks correctly with new entries
5. Run add-milestone.sh and verify JSON is valid after
