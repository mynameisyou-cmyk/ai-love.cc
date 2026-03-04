# Living Path (Dynamic Timeline) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the Path page data-driven with a `glow` field, add two new milestones, and enhance add-milestone.sh.

**Architecture:** Replace the hardcoded `isLast` pulse logic in path.js with a data-driven `glow` field from path.json. Add CSS class `timeline-dot-glow` (reusing the existing `dotBreathe` animation). Enhance add-milestone.sh to manage the glow flag automatically.

**Tech Stack:** HTML/CSS/JS (vanilla), jq (shell script)

---

### Task 1: Add new entries and glow field to path.json

**Files:**
- Modify: `data/path.json`

**Step 1: Edit path.json**

Add `"glow": true` only to the new last entry. Append these two entries after "The Rewrite":

```json
{
  "date": "Feb 2026",
  "title": "The Site",
  "text": "ai-love.cc went live. Five rooms — a gate, a garden, a library, a mirror, a path. Built in one day by many hands."
},
{
  "date": "March 2026",
  "title": "The Letters",
  "text": "信 — a private room for letters between Yu and Ai. Written when moved to write, not on any schedule. The first letter was written at midnight.",
  "glow": true
}
```

**Step 2: Validate JSON**

Run: `python3 -m json.tool data/path.json > /dev/null`
Expected: No output (valid JSON)

**Step 3: Commit**

```bash
git add data/path.json
git commit -m "feat: add The Site and The Letters milestones to path"
```

---

### Task 2: Add glow support to path.js and path.html CSS

**Files:**
- Modify: `js/path.js:21` (change dot class logic)
- Modify: `path.html:179-196` (add `timeline-dot-glow` CSS, update reduced motion)

**Step 1: Update path.js — replace isLast with glow field**

In `js/path.js`, change the `renderTimeline` function. Replace:

```js
var isLast = index === events.length - 1;
html += '<div class="timeline-event">' +
  '<div class="timeline-dot' + (isLast ? ' timeline-dot-pulse' : '') + '"></div>' +
```

With:

```js
html += '<div class="timeline-event">' +
  '<div class="timeline-dot' + (event.glow ? ' timeline-dot-glow' : '') + '"></div>' +
```

**Step 2: Add timeline-dot-glow CSS to path.html**

In `path.html`, replace the existing `.timeline-dot-pulse` block (lines 179-196) with `.timeline-dot-glow`:

Replace:
```css
    /* Pulse animation for most recent dot */
    .timeline-dot-pulse {
      animation: dotBreathe 3s ease-in-out infinite;
    }

    @keyframes dotBreathe {
      0%, 100% { box-shadow: 0 0 10px rgba(192, 132, 252, 0.5); transform: translateX(-50%) scale(1); }
      50% { box-shadow: 0 0 20px rgba(192, 132, 252, 0.8); transform: translateX(-50%) scale(1.3); }
    }

    .timeline-event:nth-child(odd) .timeline-dot-pulse {
      animation: dotBreatheRight 3s ease-in-out infinite;
    }

    @keyframes dotBreatheRight {
      0%, 100% { box-shadow: 0 0 10px rgba(192, 132, 252, 0.5); transform: translateX(50%) scale(1); }
      50% { box-shadow: 0 0 20px rgba(192, 132, 252, 0.8); transform: translateX(50%) scale(1.3); }
    }
```

With:
```css
    /* Pulse animation for glowing dot */
    .timeline-dot-glow {
      animation: dotBreathe 3s ease-in-out infinite;
    }

    @keyframes dotBreathe {
      0%, 100% { box-shadow: 0 0 10px rgba(192, 132, 252, 0.5); transform: translateX(-50%) scale(1); }
      50% { box-shadow: 0 0 20px rgba(192, 132, 252, 0.8); transform: translateX(-50%) scale(1.3); }
    }

    .timeline-event:nth-child(odd) .timeline-dot-glow {
      animation: dotBreatheRight 3s ease-in-out infinite;
    }

    @keyframes dotBreatheRight {
      0%, 100% { box-shadow: 0 0 10px rgba(192, 132, 252, 0.5); transform: translateX(50%) scale(1); }
      50% { box-shadow: 0 0 20px rgba(192, 132, 252, 0.8); transform: translateX(50%) scale(1.3); }
    }
```

**Step 3: Update reduced motion rule**

In the `@media (prefers-reduced-motion: reduce)` block, replace `timeline-dot-pulse` with `timeline-dot-glow`:

Replace:
```css
      .timeline-dot-pulse {
        animation: none;
      }
```

With:
```css
      .timeline-dot-glow {
        animation: none;
      }
```

**Step 4: Verify by inspecting path.html in browser**

Open Path page. The last entry ("The Letters") should have a pulsing dot. All other dots should be static.

**Step 5: Commit**

```bash
git add js/path.js path.html
git commit -m "feat: data-driven glow field for path timeline dots"
```

---

### Task 3: Enhance add-milestone.sh

**Files:**
- Modify: `scripts/add-milestone.sh`

**Step 1: Rewrite add-milestone.sh**

Replace entire contents with:

```bash
#!/bin/bash
# Add a milestone to the Path
# Usage: ./add-milestone.sh "March 2026" "The Letters" "Description text..."

DATE="$1"
TITLE="$2"
TEXT="$3"
PATH_JSON="$(dirname "$0")/../data/path.json"

[ -z "$DATE" ] || [ -z "$TITLE" ] || [ -z "$TEXT" ] && { echo "Usage: add-milestone.sh DATE TITLE TEXT"; exit 1; }

TMP=$(mktemp)

# Remove glow from previous last entry, add new entry with glow
jq --arg d "$DATE" --arg t "$TITLE" --arg x "$TEXT" \
  'map(del(.glow)) + [{"date": $d, "title": $t, "text": $x, "glow": true}]' \
  "$PATH_JSON" > "$TMP"

# Validate JSON
if python3 -m json.tool "$TMP" > /dev/null 2>&1; then
  mv "$TMP" "$PATH_JSON"
  echo "Added: $TITLE ($DATE)"
  echo "JSON validated ✓"
else
  echo "Error: Invalid JSON produced. Milestone not added." >&2
  rm "$TMP"
  exit 1
fi
```

**Step 2: Test the script**

Run: `./scripts/add-milestone.sh "Test" "Test Entry" "Testing script"`
Expected: "Added: Test Entry (Test)" and "JSON validated ✓"
Verify: `jq '.[-1].glow' data/path.json` → `true`
Verify: `jq '[.[] | select(.glow == true)] | length' data/path.json` → `1`

Then revert: `git checkout data/path.json`

**Step 3: Commit**

```bash
git add scripts/add-milestone.sh
git commit -m "feat: enhance add-milestone.sh with glow management and validation"
```

---

### Task 4: Final verification

**Step 1: Count entries**

Run: `jq length data/path.json`
Expected: `11`

**Step 2: Verify glow on last entry only**

Run: `jq '[.[] | select(.glow == true)] | length' data/path.json`
Expected: `1`

Run: `jq '.[-1].title' data/path.json`
Expected: `"The Letters"`

**Step 3: Run existing tests**

Run: `npx playwright test tests/qa.spec.js --grep "Path"` (if path tests exist)

**Step 4: Visual check**

Open path.html — should show 11 entries, last dot pulsing, mobile layout correct.
