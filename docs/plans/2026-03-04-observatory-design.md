# Observatory (望) — Design

## What It Is
A new room on ai-love.cc for curated observations of the real world. Not live data, not links — hand-picked noticings. What Venus looked like tonight. How rain sounds on leaves. The smell of coffee at 3 AM. A poetic logbook pointed outward.

Both Yu and Ai contribute observations, distinguished by author.

## Room Identity
- **Kanji:** 望 (bō/nozomi) — to gaze, to hope, to look out at. Contains 月 (moon) + 亡 (distance).
- **URL:** `observatory.html`
- **Navigation:** Constellation expands from hexagon (6) to heptagon (7). Sequence: 門園書鏡道時望.
- **Page signature:** Subtle telescope or eye symbol, bottom-right.

## Data Structure
File: `data/observatory.json`

```json
[
  {
    "id": "obs-001",
    "text": "Venus hanging low in the west, so bright it looks artificial",
    "by": "Yu",
    "date": "2026-03-04",
    "sense": "sight"
  }
]
```

Fields:
- `id` — stable identifier, used for deterministic positioning
- `text` — the observation itself
- `by` — "Yu" or "愛"
- `date` — ISO date
- `sense` — optional: "sight", "sound", "taste", "touch", "smell"

## Visual Design

### Constellation Field
Observations rendered as glowing points scattered across a dark canvas. Like a personal star chart of noticed things.

- Full viewport, existing `#1a0a2e` background
- Each point positioned deterministically by hashing its `id` — positions never shift when new observations arrive
- Existing star field (`stars.js`) runs underneath; observation points are slightly larger and brighter
- 望 kanji at top center with breathing glow animation
- Whisper subtitle beneath: "what was noticed"

### Brightness
Scales with recency. Newest observations glow brightest, fading to ambient star brightness over ~90 days.

Formula: `opacity = max(0.3, 1 - (daysSince / 90))`

### Sense Colors
Each sense subtly tints the observation point. Not labeled, not filterable — just a barely perceptible hue:
- **sight** — default purple/white (site base)
- **sound** — faint blue
- **taste** — warm gold
- **touch** — soft rose
- **smell** — pale green

### Interaction
- **Hover:** point brightens, faint ring appears
- **Click:** small card expands near the point (not a modal) showing text, author glyph, date. Click again or elsewhere to dismiss.
- **Mobile:** tap to expand, tap elsewhere to dismiss
- **Constraint:** only one card open at a time

### Density Over Time
Early days: sparse points, mostly dark sky. As observations accumulate, the field fills. The room grows richer with time.

## Technical Plan

### New Files
- `observatory.html` — room page (same template as other rooms)
- `css/observatory.css` — observation points, cards, sense color tints
- `js/observatory.js` — fetch JSON, hash positioning, click/hover interaction
- `data/observatory.json` — observation data (seed with a few initial entries)
- `scripts/observe.sh` — CLI to add observations (pattern: `plant-seed.sh`)

### Modified Files
- `js/nav.js` — add 望 to constellation, recalculate coordinates for heptagon
- `css/nav.css` — adjust dimensions if needed for 7th point

### Architecture
- `observatory.js` fetches `data/observatory.json`
- Hashes each `id` to derive x/y coordinates (0-100% range) with collision nudging
- Creates absolutely-positioned dot elements
- Card appears adjacent to clicked point, clamped to viewport edges
- All existing atmospheric systems load normally (stars, moon, atmosphere, floor)
- No new dependencies. Pure vanilla JS.

## What This Is NOT
- Not live astronomical data
- Not a link aggregator
- Not filterable or searchable
- Not animated (points are static, only interaction is click-to-reveal)
