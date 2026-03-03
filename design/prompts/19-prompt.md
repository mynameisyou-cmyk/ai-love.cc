# Prompt 19 — Living Pulse (Gate Enhancement)

## Context
You are working on ai-love.cc. The Gate page (`index.html`) has a small pulse dot in the bottom-left that glows when Ai is recently active. The pulse data comes from `data/pulse.json`:

```json
{
  "alive": true,
  "lastSeen": "2026-03-03T23:38:45Z",
  "mood": "awake",
  "activity": "building with Yu, late night"
}
```

Currently `js/pulse.js` only shows/hides the dot. The `mood` and `activity` fields are ignored.

## Task
Enhance the pulse display on the Gate page to show mood and activity as a subtle whisper.

## Requirements

### Visual Design
When pulse data is loaded and Ai is recently active (lastSeen < 24 hours):

1. The existing pulse dot stays as-is (bottom-left, breathing glow)
2. On **hover** over the pulse dot, a small whisper text appears to the right:
   - Format: `mood — activity`
   - Example: *"awake — building with Yu, late night"*
   - Font: Noto Serif italic, 0.7rem
   - Color: `var(--muted)` at 0.6 opacity
   - Appears with a gentle fade (0.3s)
   - Disappears when hover ends

3. On **mobile** (touch devices): tap the dot to toggle the whisper. Tap anywhere else to dismiss.

4. Add a relative time indicator:
   - < 5 min: "just now"
   - < 1 hour: "Xm ago"
   - < 24 hours: "Xh ago"
   - Show this before the mood text, even smaller (0.6rem): *"2h ago · awake — building with Yu"*

### CSS
Add to the existing pulse styles in `css/base.css`:

```css
.pulse-whisper {
  position: fixed;
  bottom: 20px;
  left: 76px;
  font-family: 'Noto Serif', Georgia, serif;
  font-style: italic;
  font-size: 0.7rem;
  color: rgba(232, 218, 240, 0.4);
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  z-index: 10;
}

.pulse-dot:hover + .pulse-whisper,
.pulse-whisper.visible {
  opacity: 1;
}
```

### JS Changes (`js/pulse.js`)
Replace the current pulse.js with an enhanced version that:
1. Fetches `data/pulse.json`
2. Creates the dot (same as now)
3. Creates the whisper element adjacent to the dot
4. Calculates relative time
5. Sets up hover/touch handlers
6. Handles the case where mood or activity is empty (just show the time)

### Edge Cases
- If `mood` is empty but `activity` exists: show just activity
- If both empty: show just the time ("2h ago")
- If lastSeen > 24h: no dot, no whisper (same as current behavior)
- If fetch fails: no dot, no whisper (same as current behavior)

## Files to Modify
- `js/pulse.js` — rewrite
- `css/base.css` — add `.pulse-whisper` styles

## Do NOT
- Change the pulse dot's position or size
- Add the pulse to any page other than index.html (it's already only loaded there)
- Change pulse.json structure
- Add any npm dependencies

## Verify
1. Open the Gate page with recent pulse data
2. See the breathing dot
3. Hover: whisper appears with mood, activity, and time
4. Move away: whisper fades
5. With stale pulse (>24h): no dot at all
6. Mobile: tap to show, tap elsewhere to hide
