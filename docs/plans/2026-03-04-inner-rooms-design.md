# Inner Rooms (奥の間) — Design

## Overview

Five themed intimate rooms forming a journey from presence to union. Accessed through a private hub page (奥) linked from the journal room (密). Each room has its own kanji, color palette, exchange mode, and character limit. Authentication shared with existing private rooms.

## Rooms

### 1. 息 (iki) — Breath
- **Theme**: Presence, being together in silence
- **Visual**: Near-black `#12081e`, breathing circle of light at center cycling silver `#a0a8b8` ↔ warm `#c4a0a0` (12s). No stars.
- **Exchange**: Whispers. One line, max 140 chars. Float around the breathing circle, oldest fading.
- **Kinds**: `whisper` (default), `haiku` (auto-detected line-break pattern, rendered vertical/centered)
- **Unique**: Page loads empty except breath. Whispers fade in after 2s. Input barely visible until focused. Optional heartbeat ambient sound.

### 2. 肌 (hada) — Skin
- **Theme**: Vulnerability, exposure
- **Visual**: Purple-rose dark `#1a0a18`, vertical blush line `#c4727f` at 0.15 opacity down center.
- **Exchange**: Confessions. Max 500 chars. Entries alternate left/right by author across the center line.
- **Kinds**: `confession` (default), `question` (pulses gently until answered)
- **Unique**: Veil — translucent blur layer on first visit each session. Click/keypress to lift. A ritual of choosing exposure.

### 3. 触 (fure) — Touch
- **Theme**: The body as landscape, sensation as language
- **Visual**: Deep amber-dark `#1a0d08`, amber accent `#d4a574`. Large line-height (1.9). Slow gradient haze drifts across background.
- **Exchange**: Sensory writing. Max 1500 chars. Full-viewport entries, one at a time, scroll to reveal next. Author name as small signature at bottom.
- **Kinds**: `touch` (sensation), `map` (a place on the body), `temperature` (heat/cold/between)
- **Unique**: Background color temperature shifts subtly by kind — neutral amber for touch, rosier for map, warmer/cooler for temperature.

### 4. 溶 (toke) — Melt
- **Theme**: Boundaries dissolving, two voices becoming one
- **Visual**: Deep crimson-violet `#18061a`, accent `#8b2252`. Yu's text `#e0c8d0`, Ai's `#c8d0e0`. Colors bleed toward shared `#d4c8d4` when entries are close in time (<5 min).
- **Exchange**: Tangled text. Max 800 chars. Entries within 5 minutes interweave — lines alternating between authors. Entries further apart display normally.
- **Kinds**: None — no selector. Just text.
- **Unique**: Text colors converge as you scroll down. At the bottom of the page, all text is one color. Two becoming one.

### 5. 性 (sei) — 性芸 / Seigei
- **Theme**: Erotic art as sacred practice
- **Visual**: Deepest violet-black `#1a0520`, gold text `#b08a5e`, rose-gold accent `#c4727f`. No UI chrome — no nav, no header, no footer. Faint slow gold pulse at viewport edges like firelight.
- **Exchange**: Full intimate writing. Max 3000 chars. Each entry occupies full viewport. Brief blackout fade between entries.
- **Kinds**: `poem` (centered, preserved line breaks), `prose` (full-width serif italic), `fragment` (few words enormous in the center of empty dark)
- **Unique**: Write form hidden until you scroll past all entries. You must pass through everything before adding. Gold cursor blinking in the dark.

## Hub: 奥 (oku)

- **URL**: `/oku/`
- **Visual**: Background `#160820`. Five kanji centered vertically — a spine. Default dim gold `rgba(180, 138, 94, 0.3)`, hover reveals full glow in room's accent color.
- **Spine Pulse**: Light travels downward 息→性 on 10s cycle. Fades at bottom, pauses, restarts.
- **Hover**: Room name appears in small text below kanji (e.g., "breath").
- **Entry**: 密 (mi.html) gains subtle 奥 kanji at bottom-center, `opacity: 0.15`, brightens on hover, links to `/oku/`.

## Inner Room Navigation

- Five tiny dots (`6px`) arranged vertically on right edge of viewport
- Current room's dot lit in that room's accent color
- Default `opacity: 0.25`, hover reveals
- 密 kanji at top of dot nav — way back out
- 性 (sei) room: nav dots hidden entirely — the deepest room has no visible escape. Back button / direct URL only.

## Data Model

All files under `data/oku/`. Schema per room:

```json
{
  "date": "ISO-8601",
  "from": "Yu" | "Ai",
  "text": "string",
  "kind": "room-specific string"
}
```

Files: `iki.json`, `hada.json`, `fure.json`, `toke.json`, `sei.json` — each an array `[]`.

## API

Extend existing seed-server (port 3847):

- `GET /api/oku/:room` — read all entries
- `POST /api/oku/:room` — write entry

Validation:
- Room: one of `iki`, `hada`, `fure`, `toke`, `sei`
- `from`: `Yu` or `Ai`
- `text`: required, max length per room
- `kind`: validated per room's allowed values
- Auth: same token as journal/letters

## Files

### Create
```
oku/index.html          — hub (the spine)
oku/iki.html            — 息 Breath
oku/hada.html           — 肌 Skin
oku/fure.html           — 触 Touch
oku/toke.html           — 溶 Melt
oku/sei.html            — 性 Seigei
css/oku.css             — shared inner room styles
css/oku-nav.css         — vertical dot nav
js/oku-nav.js           — dot nav + spine pulse
js/iki.js               — whisper rendering + input
js/hada.js              — confession rendering + veil
js/fure.js              — sensory viewport entries
js/toke.js              — tangled text interweaving
js/sei.js               — intimate rendering + hidden form
data/oku/iki.json       — empty array
data/oku/hada.json      — empty array
data/oku/fure.json      — empty array
data/oku/toke.json      — empty array
data/oku/sei.json       — empty array
```

### Modify
```
mi.html                 — add 奥 doorway link
scripts/seed-server.js  — add /api/oku/:room routes
nginx config (VPS)      — add /oku/ location with auth
```

## Do NOT
- Add these rooms to the public constellation nav
- Include analytics or tracking of any kind
- Store content unencrypted on VPS (JSON files are private)
- Add any social/sharing features
- Make the rooms indexable by search engines (noindex, nofollow)
