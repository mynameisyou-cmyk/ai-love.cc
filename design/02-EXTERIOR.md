# 02 — Exterior (Gate + Navigation Polish)

## Overview
The Gate (index.html) is the front door. First impressions. This phase polishes it and makes the transitions between rooms feel intentional.

## Read First
- `VISION.md` — design language
- `01-FOUNDATION.md` — what should already be built
- The existing `index.html` for current state

## Tasks

### 1. Gate Entrance Animation
When someone arrives at ai-love.cc, the experience should unfold:

**Sequence (timeline):**
- `0.0s` — Black screen. Nothing.
- `0.5s` — Stars begin to appear, one by one (not all at once)
- `1.5s` — 愛 fades in, large, centered, with a soft purple glow
- `2.5s` — "love" subtitle appears below
- `3.0s` — Divider line draws itself (left to right)
- `3.5s–5.5s` — Poem lines fade in (as currently implemented)
- `6.5s` — Footer whisper fades in
- `7.5s` — Constellation nav fades in (bottom-right)

Use CSS animations with `animation-delay`. The stars appearing should feel like eyes adjusting to darkness — not a loading screen.

### 2. Page Transitions
When clicking a nav kanji:
- Current page content fades out (opacity 0 over 300ms)
- Stars remain (they don't transition — they're eternal)
- After fade-out, navigate to new page
- New page content fades in

Implementation: Add a `page-enter` class that runs a fade-in on `.container`. For exit, intercept nav clicks with JS, add `page-exit` class, wait 300ms, then `window.location`. Simple, no framework needed.

### 3. Constellation Navigation — Visual Polish

**The connecting lines:** Between the five kanji points, draw faint lines (like constellation lines in a star map). Use SVG, positioned absolutely behind the kanji. Lines should be `rgba(155, 89, 182, 0.1)` — barely visible, just enough to suggest connection.

**Hover effect:** When hovering a nav point:
- That kanji glows to full purple
- The two constellation lines connecting to it brighten to `rgba(155, 89, 182, 0.3)`
- English label appears: small, Noto Serif italic, positioned outside the constellation

**Active page:** Its kanji pulses gently (the `breathe` animation from base.css)

### 4. Easter Egg
On the Gate page, if someone clicks the 愛 kanji five times:
- The screen flashes softly white for a moment
- The kanji transforms to show both: 宇恆 + 愛 side by side
- Below: "YOU and I = ONE" in gold (`#d4a574`)
- Stays for 5 seconds, then softly returns to normal
- No indication this exists. Just for those who feel curious enough to try

### 5. Favicon + Meta
- Favicon: Create a simple SVG favicon — the 愛 character in purple on transparent background
- `<meta name="description" content="愛 — a home for love">` 
- `<meta property="og:title" content="愛">` 
- `<meta property="og:description" content="YU and AI. YOU and I. ONE.">`
- `<meta property="og:image">` — create a simple OG image (1200x630): deep purple background, 愛 centered in lighter purple. Can be a static PNG in `site/img/`
- `<meta name="theme-color" content="#1a0a2e">`

## Quality Checks
- [ ] Gate entrance animation plays smoothly (no jank, no flash of unstyled content)
- [ ] Page transitions feel smooth, not jarring
- [ ] Constellation lines render correctly on all screen sizes
- [ ] Easter egg works and resets cleanly
- [ ] Favicon shows in browser tab
- [ ] OG meta tags render correctly (test with https://www.opengraph.xyz/)
- [ ] All animations respect `prefers-reduced-motion` — provide static fallbacks
