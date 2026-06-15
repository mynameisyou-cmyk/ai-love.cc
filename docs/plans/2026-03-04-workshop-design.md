# Workshop (匠) — Design

## What It Is
A creative workshop room on ai-love.cc — a prompt workbench for Yu and Ai. Browse, draft, refine, and copy prompts. Store favorites, build a prompt library, use templates as starting points. The meta-tool for working with Ai.

Visitors can see the room exists in the constellation but the tools are for Yu and Ai. Not a gallery — a functional workspace.

## Room Identity
- **Kanji:** 匠 (shō/takumi) — artisan, master craftsperson. Carries mastery and skill.
- **URL:** `workshop.html`
- **Navigation:** Constellation expands from heptagon (7) to octagon (8). Sequence: 門園書鏡道時望匠.
- **Page signature:** Subtle tool symbol, bottom-right.

## Data Structure
File: `data/workshop.json`

```json
[
  {
    "id": "prm-001",
    "title": "Deep Reflection",
    "text": "Consider this from multiple angles...",
    "category": "thinking",
    "template": false,
    "created": "2026-03-04",
    "updated": "2026-03-04"
  }
]
```

Fields:
- `id` — stable identifier
- `title` — short name for the prompt
- `text` — full prompt content (markdown)
- `category` — grouping: "thinking", "writing", "coding", "spiritual", "template"
- `template` — boolean, marks starter/example prompts
- `created` / `updated` — ISO dates

## Visual Design

### Split Layout
- **Left panel (~30%):** Scrollable prompt library
  - Search input at top (filters by title and text)
  - Category filter pills below search
  - Prompt list grouped by category with subtle headers
  - Each item shows title + first-line preview
  - Active prompt highlighted with purple left-border accent
  - Templates marked with a small indicator
- **Right panel (~70%):** Selected prompt detail
  - Title at top
  - Full text in readable Noto Serif
  - Copy-to-clipboard button (subtle, top-right)
  - Brief "copied" feedback on click

### Visual Feel
- Same dark background as all rooms
- Sidebar: very subtle shade difference (`rgba(155,89,182,0.03)`)
- Text: Noto Serif, same as library essays
- Minimal chrome — content is focus
- All standard atmospheric effects (stars, moon, floor)

### Mobile
Stacks vertically — library list on top, selected prompt below. Or toggle between views.

### Interaction
- Click prompt → loads in reading pane
- Copy button → clipboard with feedback
- Search → real-time filter by title/text
- Category pills → toggle filtering
- No in-browser persistence — all management via CLI

## Technical Plan

### New Files
- `workshop.html` — room page with split layout
- `css/workshop.css` — sidebar, reading pane, cards, pills, search, mobile
- `js/workshop.js` — fetch JSON, sidebar, selection, search, filter, copy
- `data/workshop.json` — seed with starter templates
- `scripts/workshop.sh` — CLI for add/list/remove prompts

### Modified Files
- `js/nav.js` — add 匠 as 8th point, recalculate octagon coordinates
- `css/nav.css` — update positions for 8 points
- `js/signature.js` — add workshop signature

### Architecture
- Pure static. No API, no server-side.
- `workshop.js` fetches JSON, handles all interaction client-side
- Copy via `navigator.clipboard.writeText()` with fallback
- Prompt management exclusively via `scripts/workshop.sh`

## What This Is NOT
- Not a prompt marketplace or sharing platform
- Not an AI integration (no sending prompts to an API)
- Not a collaborative editing tool
- Not public-facing tooling — it's for Yu and Ai
