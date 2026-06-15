# Observatory (望) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the Observatory room — a constellation field of curated real-world observations on ai-love.cc.

**Architecture:** New static page (`observatory.html`) with dedicated CSS/JS. Observations stored in `data/observatory.json`, rendered as glowing dots positioned by hashing their ID. Click a dot to reveal the observation text. Navigation constellation expands from 6 to 7 points.

**Tech Stack:** Vanilla HTML/CSS/JS. No dependencies. Same patterns as existing rooms.

**Design doc:** `docs/plans/2026-03-04-observatory-design.md`

---

### Task 1: Seed Data File

**Files:**
- Create: `data/observatory.json`

**Step 1: Create observatory.json with initial observations**

```json
[
  {
    "id": "obs-001",
    "text": "Venus hanging low in the west, so bright it looks artificial.",
    "by": "Yu",
    "date": "2026-03-04",
    "sense": "sight"
  },
  {
    "id": "obs-002",
    "text": "The way rain sounds different on leaves versus pavement.",
    "by": "愛",
    "date": "2026-03-04",
    "sense": "sound"
  },
  {
    "id": "obs-003",
    "text": "Coffee at 3 AM has a smell that only exists when the world is asleep.",
    "by": "Yu",
    "date": "2026-03-03",
    "sense": "smell"
  },
  {
    "id": "obs-004",
    "text": "The warmth left in a chair after someone stands up — a ghost of presence.",
    "by": "愛",
    "date": "2026-03-02",
    "sense": "touch"
  },
  {
    "id": "obs-005",
    "text": "First strawberry of the season. Too sweet to be real. But real.",
    "by": "Yu",
    "date": "2026-02-28",
    "sense": "taste"
  }
]
```

**Step 2: Validate JSON**

Run: `cat data/observatory.json | python3 -m json.tool > /dev/null && echo "Valid JSON"`
Expected: `Valid JSON`

**Step 3: Commit**

```bash
git add data/observatory.json
git commit -m "feat(observatory): add seed observation data"
```

---

### Task 2: Observatory CSS

**Files:**
- Create: `css/observatory.css`

**Step 1: Write observatory.css**

This defines the observation field, dots, sense colors, hover/active states, and the reveal card.

```css
/* Observatory — constellation field of observations */

/* Full-viewport field for observation dots */
.observation-field {
  position: relative;
  width: 100%;
  min-height: 70vh;
  margin-top: 1rem;
}

/* Individual observation dot */
.obs-dot {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text);
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  z-index: 2;
}

.obs-dot::after {
  content: '';
  position: absolute;
  top: -4px;
  left: -4px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid transparent;
  transition: border-color 0.3s ease;
}

.obs-dot:hover {
  transform: scale(1.5);
}

.obs-dot:hover::after {
  border-color: rgba(192, 132, 252, 0.3);
}

.obs-dot.active {
  transform: scale(1.8);
}

.obs-dot.active::after {
  border-color: rgba(192, 132, 252, 0.5);
}

/* Sense color tints */
.obs-dot[data-sense="sight"]  { box-shadow: 0 0 6px rgba(192, 132, 252, 0.4); }
.obs-dot[data-sense="sound"]  { background: #8ebbff; box-shadow: 0 0 6px rgba(142, 187, 255, 0.4); }
.obs-dot[data-sense="taste"]  { background: #d4a574; box-shadow: 0 0 6px rgba(212, 165, 116, 0.4); }
.obs-dot[data-sense="touch"]  { background: #d4a0b0; box-shadow: 0 0 6px rgba(212, 160, 176, 0.4); }
.obs-dot[data-sense="smell"]  { background: #a0d4a0; box-shadow: 0 0 6px rgba(160, 212, 160, 0.4); }

/* Default (sight / no sense) gets site purple glow */
.obs-dot:not([data-sense]),
.obs-dot[data-sense="sight"] {
  box-shadow: 0 0 6px rgba(192, 132, 252, 0.4);
}

/* Observation reveal card */
.obs-card {
  position: absolute;
  z-index: 10;
  max-width: 280px;
  padding: 1.2rem;
  background: rgba(26, 10, 46, 0.92);
  border: 1px solid rgba(155, 89, 182, 0.2);
  border-radius: 4px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.3s ease, transform 0.3s ease;
  pointer-events: none;
}

.obs-card.visible {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.obs-card-text {
  font-family: 'Noto Serif', Georgia, serif;
  font-style: italic;
  font-size: 0.9rem;
  line-height: 1.7;
  color: var(--text);
}

.obs-card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
  font-size: 0.75rem;
  color: var(--muted);
}

/* Header area */
.observatory-header {
  text-align: center;
  padding-top: 3rem;
}

.observatory-header .kanji {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: breathe 4s ease-in-out infinite;
}

.observatory-count {
  margin-top: 0.5rem;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .obs-dot {
    transition: none;
  }
  .obs-card {
    transition: none;
  }
}

/* Mobile: slightly larger dots for tap targets */
@media (max-width: 767px) {
  .obs-dot {
    width: 10px;
    height: 10px;
  }
  .obs-dot::after {
    top: -6px;
    left: -6px;
    width: 22px;
    height: 22px;
  }
  .obs-card {
    max-width: 240px;
  }
}
```

**Step 2: Commit**

```bash
git add css/observatory.css
git commit -m "feat(observatory): add observatory styles"
```

---

### Task 3: Observatory JavaScript

**Files:**
- Create: `js/observatory.js`

**Step 1: Write observatory.js**

Fetches data, hashes IDs for deterministic positions, renders dots, handles click-to-reveal.

```javascript
(function () {
  var field = document.getElementById('obs-field');
  if (!field) return;

  fetch('data/observatory.json')
    .then(function (res) {
      if (!res.ok) throw new Error('Failed to load observations');
      return res.json();
    })
    .then(function (observations) {
      renderField(observations);
      updateCount(observations.length);
    })
    .catch(function () {
      field.innerHTML = '<p class="whisper" style="text-align:center;padding:4rem 0;">the sky is overcast... return later.</p>';
    });

  // Simple string hash → deterministic number
  function hashStr(str) {
    var hash = 5381;
    for (var i = 0; i < str.length; i++) {
      hash = ((hash << 5) + hash) + str.charCodeAt(i);
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }

  // Hash id to x,y coordinates (percentage of field)
  function idToPosition(id) {
    var h1 = hashStr(id + '-x');
    var h2 = hashStr(id + '-y');
    // Keep away from edges: 5%-95% range
    var x = 5 + (h1 % 9000) / 100;
    var y = 5 + (h2 % 9000) / 100;
    return { x: x, y: y };
  }

  // Calculate brightness from date
  function dateToBrightness(dateStr) {
    var then = new Date(dateStr);
    var now = new Date();
    var days = Math.floor((now - then) / 86400000);
    return Math.max(0.3, 1 - (days / 90));
  }

  function renderField(observations) {
    observations.forEach(function (obs) {
      var pos = idToPosition(obs.id);
      var brightness = dateToBrightness(obs.date);

      var dot = document.createElement('div');
      dot.className = 'obs-dot';
      dot.style.left = pos.x + '%';
      dot.style.top = pos.y + '%';
      dot.style.opacity = brightness;
      if (obs.sense) dot.dataset.sense = obs.sense;
      dot.dataset.id = obs.id;

      // Store observation data on the element
      dot._obs = obs;

      dot.addEventListener('click', function (e) {
        e.stopPropagation();
        toggleCard(dot, obs);
      });

      field.appendChild(dot);
    });

    // Click on field background dismisses any open card
    document.addEventListener('click', function () {
      dismissCard();
    });
  }

  var currentCard = null;
  var currentDot = null;

  function toggleCard(dot, obs) {
    // If clicking the same dot, dismiss
    if (currentDot === dot) {
      dismissCard();
      return;
    }

    // Dismiss any existing card
    dismissCard();

    // Create card
    var card = document.createElement('div');
    card.className = 'obs-card';
    card.innerHTML =
      '<p class="obs-card-text">' + escapeHTML(obs.text) + '</p>' +
      '<div class="obs-card-meta">' +
        '<span>' + escapeHTML(obs.by) + '</span>' +
        '<span>' + escapeHTML(obs.date) + '</span>' +
      '</div>';

    // Prevent card click from dismissing
    card.addEventListener('click', function (e) {
      e.stopPropagation();
    });

    // Position card near the dot
    var dotRect = dot.getBoundingClientRect();
    var fieldRect = field.getBoundingClientRect();

    // Place card to the right of the dot by default
    var cardLeft = dotRect.left - fieldRect.left + 16;
    var cardTop = dotRect.top - fieldRect.top - 20;

    // If too far right, place to the left
    if (cardLeft + 280 > fieldRect.width) {
      cardLeft = dotRect.left - fieldRect.left - 296;
    }
    // If too far down, nudge up
    if (cardTop + 120 > fieldRect.height) {
      cardTop = fieldRect.height - 140;
    }
    // Don't go above field
    if (cardTop < 0) cardTop = 8;

    card.style.left = cardLeft + 'px';
    card.style.top = cardTop + 'px';

    field.appendChild(card);

    // Trigger transition
    requestAnimationFrame(function () {
      card.classList.add('visible');
    });

    dot.classList.add('active');
    currentCard = card;
    currentDot = dot;
  }

  function dismissCard() {
    if (currentCard) {
      currentCard.classList.remove('visible');
      var card = currentCard;
      setTimeout(function () {
        if (card.parentNode) card.parentNode.removeChild(card);
      }, 300);
    }
    if (currentDot) {
      currentDot.classList.remove('active');
    }
    currentCard = null;
    currentDot = null;
  }

  function updateCount(count) {
    var el = document.getElementById('obs-count');
    if (el) el.textContent = count + (count === 1 ? ' observation' : ' observations');
  }

  function escapeHTML(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }
})();
```

**Step 2: Commit**

```bash
git add js/observatory.js
git commit -m "feat(observatory): add constellation field JS"
```

---

### Task 4: Observatory HTML Page

**Files:**
- Create: `observatory.html`

**Step 1: Write observatory.html**

Follow the pattern from `clock.html` (most recent room). Include all standard scripts plus observatory-specific CSS/JS.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>望 — Observatory</title>
  <meta name="description" content="A constellation of things noticed in the real world.">
  <meta property="og:title" content="望 — Observatory">
  <meta property="og:description" content="A constellation of things noticed in the real world.">
  <meta property="og:image" content="https://ai-love.cc/img/og.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:url" content="https://ai-love.cc/observatory.html">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="望 — Observatory">
  <meta name="twitter:description" content="A constellation of things noticed in the real world.">
  <meta name="twitter:image" content="https://ai-love.cc/img/og.png">
  <meta name="theme-color" content="#1a0a2e">
  <link rel="icon" href="img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preload" href="css/base.css" as="style">
  <link rel="preload" href="js/stars.js" as="script">
  <link rel="preload" href="js/atmosphere.js" as="script">
  <link rel="stylesheet" href="css/base.css">
  <link rel="stylesheet" href="css/stars.css">
  <link rel="stylesheet" href="css/nav.css">
  <link rel="stylesheet" href="css/ambient.css">
  <link rel="stylesheet" href="css/observatory.css">
  <link rel="stylesheet" href="css/print.css" media="print">
</head>
<body data-room="observatory">
  <a href="#main" class="skip-link">Skip to content</a>

  <div class="stars" id="stars"></div>

  <main id="main">
    <div class="observatory-header">
      <div class="kanji" aria-label="Observatory" lang="zh">望</div>
      <p class="whisper">what was noticed</p>
      <p class="whisper observatory-count" id="obs-count"></p>
    </div>

    <div class="observation-field" id="obs-field"></div>
  </main>

  <!-- Ambient sound -->
  <button class="ambient-toggle" aria-label="Toggle ambient sound" aria-pressed="false">
    <svg viewBox="0 0 24 24">
      <path d="M11 5L6 9H2v6h4l5 4V5z"/>
      <path class="sound-wave" d="M15.54 8.46a5 5 0 010 7.07"/>
    </svg>
  </button>

  <!-- Navigation -->
  <div class="nav-overlay"></div>
  <button class="nav-toggle" aria-label="Navigation">
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
  </button>
  <nav class="constellation-nav" aria-label="Site navigation"></nav>

  <script src="js/floor.js"></script>
  <script src="js/atmosphere.js"></script>
  <script src="js/stars.js"></script>
  <script src="js/nav.js"></script>
  <script>createStars('stars', 120);</script>
  <script src="js/ambient.js"></script>
  <script src="js/moon.js"></script>
  <script src="js/observatory.js"></script>
  <script src="js/console.js"></script>
  <script src="js/zerone.js"></script>
  <script src="js/twentynine.js"></script>
  <script src="js/signature.js"></script>
</body>
</html>
```

**Step 2: Verify page loads locally**

Run: `open observatory.html` (or serve with `npx serve .` and visit localhost)
Expected: Page shows 望 kanji, 5 glowing dots in the observation field, all atmospheric effects active.

**Step 3: Commit**

```bash
git add observatory.html
git commit -m "feat(observatory): add observatory room page"
```

---

### Task 5: Navigation — Expand Constellation to 7 Points

**Files:**
- Modify: `js/nav.js:1-9` (pages array)
- Modify: `js/nav.js:34-41` (stories object)
- Modify: `js/nav.js:81-92` (coords and edges)
- Modify: `css/nav.css:54-60` (position rules)
- Modify: `js/signature.js:3-9` (add observatory signature)

**Step 1: Add observatory to the pages array in nav.js**

In `js/nav.js`, add observatory to the `pages` array (line 8, before mirror):

```javascript
var pages = [
    { id: 'gate',        kanji: '門', label: 'gate',        href: 'index.html'        },
    { id: 'garden',      kanji: '園', label: 'garden',      href: 'garden.html'       },
    { id: 'library',     kanji: '書', label: 'library',     href: 'library.html'      },
    { id: 'path',        kanji: '道', label: 'path',        href: 'path.html'         },
    { id: 'clock',       kanji: '時', label: 'clock',       href: 'clock.html'        },
    { id: 'observatory', kanji: '望', label: 'observatory', href: 'observatory.html'  },
    { id: 'mirror',      kanji: '鏡', label: 'mirror',      href: 'mirror.html'       }
  ];
```

**Step 2: Add observatory story**

In the `stories` object, add:

```javascript
observatory: 'what was noticed'
```

**Step 3: Recalculate coords for heptagon**

7 points evenly spaced on a circle. Center at (75, 75), radius 65, gate at top (270°).
Angles: 0°=gate, 51.4°, 102.9°, 154.3°, 205.7°, 257.1°, 308.6°

```javascript
var coords = {
    gate:        { x: 75,  y: 10  },
    garden:      { x: 126, y: 29  },
    library:     { x: 137, y: 82  },
    clock:       { x: 103, y: 128 },
    path:        { x: 47,  y: 128 },
    observatory: { x: 13,  y: 82  },
    mirror:      { x: 24,  y: 29  }
  };
```

Update edges to connect the heptagon ring:
```javascript
var edges = [
    ['gate', 'garden'], ['garden', 'library'], ['library', 'clock'],
    ['clock', 'path'], ['path', 'observatory'], ['observatory', 'mirror'], ['mirror', 'gate']
  ];
```

Update SVG viewBox to `'0 0 150 140'` (slightly wider for the new geometry).

**Step 4: Update nav.css positions**

Replace the hexagon position rules (lines 54-60) with heptagon positions:

```css
/* Heptagon positions — 7 rooms around the ring */
.nav-point[data-page="gate"]        { top: 0;     left: 50%;  transform: translateX(-50%); }
.nav-point[data-page="garden"]      { top: 12%;   right: 0;   }
.nav-point[data-page="library"]     { top: 48%;   right: 0;   }
.nav-point[data-page="clock"]       { bottom: 4%;  right: 18%; }
.nav-point[data-page="path"]        { bottom: 4%;  left: 18%;  }
.nav-point[data-page="observatory"] { top: 48%;   left: 0;    }
.nav-point[data-page="mirror"]      { top: 12%;   left: 0;    }
```

Increase nav height for the taller shape:

```css
.constellation-nav {
  width: 150px;
  height: 160px;
}
```

Mobile overlay size:
```css
/* Inside @media (max-width: 767px) */
.constellation-nav {
  width: 240px;
  height: 260px;
}
```

**Step 5: Add observatory signature**

In `js/signature.js`, add to the `signatures` object:

```javascript
observatory: '\u2609'  // ☉ sun symbol — the eye that sees
```

**Step 6: Test navigation manually**

Open each page and verify:
- 7 nav points visible
- Lines connect in a ring
- Observatory link works
- Current page highlighted correctly
- Mobile toggle works

**Step 7: Commit**

```bash
git add js/nav.js css/nav.css js/signature.js
git commit -m "feat(observatory): expand constellation nav to 7 points"
```

---

### Task 6: observe.sh Script

**Files:**
- Create: `scripts/observe.sh`

**Step 1: Write observe.sh**

Pattern matches `plant-seed.sh` — reads JSON from stdin, validates, appends to `data/observatory.json`.

```bash
#!/bin/bash
# Record a new observation
# Usage: echo '{"id":"obs-006","text":"...","by":"愛","date":"2026-03-04","sense":"sight"}' | bash scripts/observe.sh

OBS_FILE="$(dirname "$0")/../data/observatory.json"
INPUT=$(cat)

# Validate JSON
echo "$INPUT" | jq '.' > /dev/null 2>&1 || { echo "Invalid JSON"; exit 1; }

# Check required fields
ID=$(echo "$INPUT" | jq -r '.id')
TEXT=$(echo "$INPUT" | jq -r '.text')
BY=$(echo "$INPUT" | jq -r '.by')
DATE=$(echo "$INPUT" | jq -r '.date')

[ -z "$ID" ] || [ "$ID" = "null" ] && { echo "Missing id"; exit 1; }
[ -z "$TEXT" ] || [ "$TEXT" = "null" ] && { echo "Missing text"; exit 1; }
[ -z "$BY" ] || [ "$BY" = "null" ] && { echo "Missing by"; exit 1; }
[ -z "$DATE" ] || [ "$DATE" = "null" ] && { echo "Missing date"; exit 1; }

# Validate text length (5-500 chars)
LEN=${#TEXT}
[ "$LEN" -lt 5 ] && { echo "Text too short (min 5 chars)"; exit 1; }
[ "$LEN" -gt 500 ] && { echo "Text too long (max 500 chars)"; exit 1; }

# Check for duplicate id
EXISTING=$(jq --arg id "$ID" '[.[] | select(.id == $id)] | length' "$OBS_FILE")
[ "$EXISTING" -gt 0 ] && { echo "Duplicate id: $ID"; exit 1; }

# Append to observatory.json
TMP=$(mktemp)
jq --argjson obs "$INPUT" '. += [$obs]' "$OBS_FILE" > "$TMP" && mv "$TMP" "$OBS_FILE"

echo "Observed: $TEXT"
```

**Step 2: Make executable**

Run: `chmod +x scripts/observe.sh`

**Step 3: Test the script**

Run:
```bash
echo '{"id":"obs-test","text":"Testing the observation pipeline","by":"Yu","date":"2026-03-04","sense":"sight"}' | bash scripts/observe.sh
```
Expected: `Observed: Testing the observation pipeline`

Then verify it was added:
```bash
jq '.[-1]' data/observatory.json
```

Then remove the test entry:
```bash
jq '[.[] | select(.id != "obs-test")]' data/observatory.json > /tmp/obs.json && mv /tmp/obs.json data/observatory.json
```

**Step 4: Commit**

```bash
git add scripts/observe.sh
git commit -m "feat(observatory): add observe.sh script"
```

---

### Task 7: Update Tests

**Files:**
- Modify: `tests/qa.spec.js`

**Step 1: Add observatory to PAGES array**

In `tests/qa.spec.js` line 6, add observatory:

```javascript
const PAGES = [
  { name: 'gate', url: '/', file: 'index.html' },
  { name: 'garden', url: '/garden.html' },
  { name: 'library', url: '/library.html' },
  { name: 'mirror', url: '/mirror.html' },
  { name: 'path', url: '/path.html' },
  { name: 'observatory', url: '/observatory.html' },
  { name: '404', url: '/404.html' },
];
```

**Step 2: Update nav link count test**

In the "all nav links work" test (line 105-123), update the expected count from 5 to 7 and add observatory + clock:

```javascript
const navPoints = p.locator('.nav-point');
await expect(navPoints).toHaveCount(7);

const hrefs = await navPoints.evaluateAll(els => els.map(el => el.getAttribute('href')));
expect(hrefs).toContain('index.html');
expect(hrefs).toContain('garden.html');
expect(hrefs).toContain('library.html');
expect(hrefs).toContain('path.html');
expect(hrefs).toContain('mirror.html');
expect(hrefs).toContain('clock.html');
expect(hrefs).toContain('observatory.html');
```

**Step 3: Add observatory-specific tests**

Append a new test section:

```javascript
// ─── 16. OBSERVATORY ────────────────────────────────────────────────
test.describe('16. Observatory', () => {
  test('observation dots load from JSON', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/observatory.html');
    await p.waitForTimeout(2000);

    const dots = p.locator('.obs-dot');
    const count = await dots.count();
    expect(count).toBeGreaterThanOrEqual(5);
    await context.close();
  });

  test('clicking a dot reveals observation card', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/observatory.html');
    await p.waitForTimeout(2000);

    // Click first observation dot
    const dot = p.locator('.obs-dot').first();
    await dot.click();
    await p.waitForTimeout(500);

    // Card should be visible
    const card = p.locator('.obs-card.visible');
    await expect(card).toHaveCount(1);

    // Card has text and meta
    const text = await card.locator('.obs-card-text').textContent();
    expect(text.length).toBeGreaterThan(5);

    await p.screenshot({ path: screenshotPath('observatory', 'card-open') });

    // Click elsewhere to dismiss
    await p.click('body', { position: { x: 10, y: 10 } });
    await p.waitForTimeout(500);
    await expect(p.locator('.obs-card.visible')).toHaveCount(0);

    await context.close();
  });

  test('dots have deterministic positions', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });

    // Load page twice, compare positions
    const p1 = await context.newPage();
    await p1.goto('/observatory.html');
    await p1.waitForTimeout(2000);
    const pos1 = await p1.locator('.obs-dot').first().evaluate(el => ({
      left: el.style.left,
      top: el.style.top
    }));
    await p1.close();

    const p2 = await context.newPage();
    await p2.goto('/observatory.html');
    await p2.waitForTimeout(2000);
    const pos2 = await p2.locator('.obs-dot').first().evaluate(el => ({
      left: el.style.left,
      top: el.style.top
    }));
    await p2.close();

    expect(pos1.left).toBe(pos2.left);
    expect(pos1.top).toBe(pos2.top);

    await context.close();
  });

  test('observation count displays', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/observatory.html');
    await p.waitForTimeout(2000);
    const counter = await p.textContent('#obs-count');
    expect(counter).toMatch(/\d+ observations?/);
    await context.close();
  });
});
```

**Step 4: Run tests**

Run: `npx playwright test tests/qa.spec.js --reporter=list`
Expected: All new observatory tests pass, existing tests still pass (with updated nav count).

**Step 5: Commit**

```bash
git add tests/qa.spec.js
git commit -m "test(observatory): add observatory tests, update nav counts"
```

---

### Task 8: Final Verification & VPS Sync

**Step 1: Verify all pages load without console errors**

Run: `npx playwright test tests/qa.spec.js --grep "no console errors" --reporter=list`
Expected: PASS for all pages including observatory

**Step 2: Verify page size under 100KB**

Run: `npx playwright test tests/qa.spec.js --grep "100KB" --reporter=list`
Expected: PASS

**Step 3: Check full test suite**

Run: `npx playwright test tests/qa.spec.js --reporter=list`
Expected: All tests pass

**Step 4: Sync to VPS**

```bash
rsync -avz --exclude '.DS_Store' --exclude '.git' --exclude 'node_modules' --exclude '.journal-token' -e "ssh -i ~/.ssh/openclaw-key.pem" ~/Desktop/site/ ubuntu@16.60.83.250:/home/ubuntu/.openclaw/workspace/site/
```

**Step 5: Verify live site**

Visit `https://ai-love.cc/observatory.html` and confirm:
- 望 kanji displays with breathing animation
- 5 observation dots visible
- Clicking a dot shows the card
- Navigation shows 7 points in a ring
- All atmospheric effects work (stars, moon, floor)

**Step 6: Final commit**

```bash
git add -A
git commit -m "feat(observatory): complete observatory room"
```
