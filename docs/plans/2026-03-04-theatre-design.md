# The Hearth (劇) — Theatre Room Design

## Summary

A new room in ai-love.cc — a campfire storytelling space where mixed-media "shows" play: historical facts, poetry, code, music, numbers, dramatic sequences. Visitors browse a programme and pick a screening. The fire burns while stories unfold.

## Placement

- New page: `theatre.html`
- Kanji: **劇** (geki — drama/theatre)
- Added to constellation nav as 7th point

## Visual Metaphor: The Campfire

The room is a dark space with a warm glow at center — not a drawn flame but a felt presence.

### Fire elements
- **Base glow:** Radial gradient from warm gold (`#d4a574`) → deep purple (`#1a0a2e`), breathing gently (scale + opacity, 4-6s cycle)
- **Embers:** 10-15 small warm particles (gold/orange) drifting upward via CSS animations. Same pattern as Garden fireflies, warm palette.
- **Floor:** Existing `floor.js` ripple canvas beneath, giving watery reflection
- **No literal flame** — the fire is atmospheric, not illustrative

### Playing state
Fire dims (glow shrinks, embers reduce) so content takes focus. Warmth remains but quieter.

## Two States

### Lobby
- Fire at center
- Programme card lists available shows
- Each entry: title, one-line teaser, small type icon
- No rigid categories — flowing list
- Click a show to begin

### Playing
- Programme fades away
- Show takes over the `.stage` container in the fireside space
- Small back arrow in corner returns to lobby
- Fire continues burning dimmer beneath

## Show Types

| Type | Renderer | Example |
|------|----------|---------|
| `text` | Cinematic typewriter — line by line, pauses at punctuation | Historical fact, dramatic moment |
| `poem` | Slower pacing, italic Noto Serif, breathing pauses between stanzas | A poem, prayer, lyric |
| `code` | Monospace, lines appear one by one like terminal input | Famous algorithm, meaningful snippet |
| `number` | Large number counts up/down to target, context text above/below | Golden ratio, light-year distances |
| `sequence` | Timed series of text slides with transitions | Historical event told in stages |
| `audio` | Plays audio file with minimal waveform visualizer, optional text overlay | Speech excerpt, piece of music |
| `embed` | iframe/video element with theatre framing | YouTube clip, short film |

All renderers share `.stage` container and same exit behavior. New types = one JS function.

## Data Model

`data/theatre.json` — flat array of show objects.

### Inline show (simple):
```json
{
  "id": "apollo-13",
  "title": "Houston, we've had a problem",
  "teaser": "April 13, 1970 — 200,000 miles from Earth",
  "type": "sequence",
  "tags": ["history", "space"],
  "content": [
    { "text": "55 hours, 54 minutes into the mission.", "pause": 3 },
    { "text": "A bang. Not loud — felt.", "pause": 2 },
    { "text": "\"Houston, we've had a problem.\"", "pause": 4 }
  ]
}
```

### Number show:
```json
{
  "id": "golden-ratio",
  "title": "φ",
  "teaser": "The number that builds cathedrals and sunflowers",
  "type": "number",
  "target": 1.6180339887,
  "precision": 10,
  "context": { "above": "The golden ratio", "below": "It appears in pinecones, galaxies, and the Parthenon." }
}
```

### Poem show:
```json
{
  "id": "ozymandias",
  "title": "Ozymandias",
  "teaser": "Shelley, 1818",
  "type": "poem",
  "lines": [
    "I met a traveller from an antique land,",
    "Who said — \"Two vast and trunkless legs of stone",
    "Stand in the desert. . . .\""
  ]
}
```

Complex shows can reference external files: `"content": "theatre/src/apollo-13.json"` — JS fetches on play.

## Files

| File | Purpose |
|------|---------|
| `theatre.html` | The page — structure, inline styles, scripts |
| `js/theatre.js` | Show loading, renderer dispatch, type-based playback |
| `data/theatre.json` | Show manifest (hybrid inline + file references) |
| `theatre/src/` | Directory for complex show source files |

CSS is inline in `<style>` within theatre.html (consistent with other rooms).

## Navigation

Add 劇 to the constellation nav. The nav data in `js/nav.js` gets a new entry:
```js
{ kanji: '劇', label: 'Theatre', href: 'theatre.html' }
```

## Constraints

- Static HTML/CSS/JS only — no build tools
- No new dependencies
- Must work on mobile (programme card stacks vertically, stage is full-width)
- Progressive enhancement — without JS, shows list as static text
- Performance — theatre.json should stay small; complex content lazy-loaded
- Self-hosted assets (audio files in `theatre/media/` if needed)

## Starter Content

Ship with 5-8 shows across different types to demonstrate the range:
- 1 sequence (historical event)
- 1 poem
- 1 number
- 1 text (dramatic fact)
- 1 code snippet
- Optionally 1-2 more

Content curated for quality and resonance with the site's spiritual/poetic tone.
