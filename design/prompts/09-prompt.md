# Prompt: 09-SOUL-TOUCHES

You are building a spiritual/poetic static website at `~/Desktop/site/`. Read `design/09-SOUL-TOUCHES.md` for the full spec. Read `design/VISION.md` for design language.

This is the final polish batch. Every detail matters. Execute ALL tasks:

## Summary of work:

### 1. Seasonal Color Shifts (extend `js/atmosphere.js`)
Add month-based color temperature to the existing atmosphere system:
- Spring (Mar-May): `--primary` → `#9b6fb6` (warmer), `--accent` → `#d4a5fc`
- Summer (Jun-Aug): `--primary` → `#8b59b6` (richer), `--accent` → `#c084fc`
- Autumn (Sep-Nov): `--primary` → `#b6599b` (rosier), `--accent` → `#fc84c0`
- Winter (Dec-Feb): defaults (`#9b59b6`, `#c084fc`)

Set these as CSS custom properties alongside the existing time-of-day ones.

### 2. Garden Season Banner
In `js/garden.js`, after seeds load, add a seasonal whisper below the header:
- Spring: "new things are growing"
- Summer: "the garden is full"
- Autumn: "some seeds are resting"
- Winter: "even dormant seeds dream"

Style: muted italic, 0.8rem, fades in after seeds render.

### 3. Reading Progress Bar (`js/reading.js`)
Create `js/reading.js`, loaded only on `library/*.html` pages:
- Fixed bar at top of viewport: `position: fixed; top: 0; left: 0; height: 2px; z-index: 100`
- Width = scroll percentage (0-100%)
- Color: `var(--primary)` with `box-shadow: 0 0 6px var(--primary)`
- When scroll reaches bottom (>95%): bar transitions to gold (`var(--gold, #d4a574)`) for 1s, then back to purple
- Smooth width transition: use `requestAnimationFrame` on scroll
- Add to `library/the-naming.html` (and any other library pages that exist)

### 4. Constellation Stories (extend `js/nav.js`)
Add hover stories to nav items. After hovering a kanji for 2+ seconds, show a subtitle line:
- 門: "where it all begins"
- 園: "things grow here"
- 書: "words find their home"
- 鏡: "see yourself clearly"
- 道: "the way unfolds"

Implementation:
- On `mouseenter` of a nav link, start a 2s timeout
- On timeout: create/show a small element below the English label with the story text
- Style: muted italic, 0.7rem, fade-in (opacity 0→1, 0.5s)
- On `mouseleave`: clear timeout, fade out and remove
- Desktop only: wrap in `matchMedia('(hover: hover)')` check

### 5. Page Signatures
Add a tiny SVG symbol to every page, fixed bottom-right (bottom: 12px, right: 12px):
- Gate (index.html): ◯ empty circle
- Garden: simple seedling (two small strokes)
- Library: ☰ three horizontal lines
- Mirror: ◐ half-filled circle
- Path: → arrow

Size: 12px. Color: `rgba(155, 89, 182, 0.08)`. Create as inline SVG in each page, or in a shared `js/signature.js` that reads `data-room` from body.

Prefer the shared JS approach — `js/signature.js` reads `body[data-room]` and injects the correct SVG.

### 6. The 29th Day Easter Egg
In `js/console.js` (or a new `js/twentynine.js`), check if today is the 29th (or Feb 28 in non-leap years):
- If yes: add class `day-29` to `<body>`
- CSS for `.day-29 .kanji`: animation that alternates color between `var(--primary)` and `var(--gold)` over 8s (smooth sine, not flashing)
- Console message changes:
```js
console.log('%c二十九', 'font-size: 24px; color: #d4a574;');
console.log('%cThe day between days. You noticed.', 'color: #e8daf0; font-style: italic;');
```
- The normal console message should NOT show on the 29th — only this one
- No indication this exists anywhere

Add the CSS keyframes for the gold shimmer in `css/base.css`:
```css
@keyframes gold-shimmer {
  0%, 100% { color: var(--primary); }
  50% { color: var(--gold, #d4a574); }
}
body.day-29 .kanji {
  animation: gold-shimmer 8s ease-in-out infinite;
}
```

### 7. OG Meta Tags
Update `<head>` of each page with page-specific Open Graph tags:

**index.html:**
```html
<meta property="og:title" content="愛">
<meta property="og:description" content="YU and AI. YOU and I. ONE.">
<meta property="og:image" content="https://ai-love.cc/img/og.png">
<meta property="og:url" content="https://ai-love.cc/">
<meta property="og:type" content="website">
```

**garden.html:** og:title "園 — Garden", og:description "Seeds of thought in a night garden."
**library.html:** og:title "書 — Library", og:description "Words finding their home."
**mirror.html:** og:title "鏡 — Mirror", og:description "Who we are. What ZERONE means."
**path.html:** og:title "道 — Path", og:description "From code to calling."
**404.html:** og:title "無 — Void", og:description "This room doesn't exist yet."

All pages: same og:image (`https://ai-love.cc/img/og.png`), og:type "website".

Also add Twitter card meta:
```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="...">
<meta name="twitter:description" content="...">
<meta name="twitter:image" content="https://ai-love.cc/img/og.png">
```

### 8. Print Stylesheet (`css/print.css`)
Create `css/print.css`:
```css
@media print {
  .stars, .constellation-nav, .nav-toggle, .nav-overlay,
  .ambient-toggle, .pulse-dot, .moon-phase,
  .page-signature, .firefly, .shooting-star { display: none !important; }
  
  body {
    background: white !important;
    color: #1a1a1a !important;
  }
  
  .kanji { color: #333 !important; text-shadow: none !important; }
  .whisper, .muted { color: #666 !important; }
  .divider { border-color: #ccc !important; }
  
  /* Library reading pages */
  .reading-content { max-width: 100%; font-size: 12pt; line-height: 1.8; }
  
  /* Garden: simple list */
  .seed-grid { column-count: 1; }
  .seed-card { border: 1px solid #ddd; break-inside: avoid; }
}
```

Add `<link rel="stylesheet" href="css/print.css" media="print">` (or `../css/print.css` for library pages) to ALL pages.

### 9. Preload Hints
Add to `<head>` of every page (before other stylesheets):
```html
<link rel="preload" href="css/base.css" as="style">
<link rel="preload" href="js/stars.js" as="script">
<link rel="preload" href="js/atmosphere.js" as="script">
```

For library reading pages, also preload `js/reading.js`.

### After completing:
- Verify seasonal color: temporarily set month to March in atmosphere.js and check the primary color shifts
- Check constellation stories: hover over nav items for 2+ seconds on desktop
- Open browser console on any page — verify the message appears
- Check page signatures: inspect bottom-right corner (they're nearly invisible — zoom in)
- Test print: Ctrl+P on library/the-naming.html — should be clean black on white
- Verify all OG tags: `curl -s https://ai-love.cc/ | grep "og:"`
- Check the 29th logic: temporarily force the date and verify gold shimmer + console change
- Final check: open Gate at current time. Does the greeting match? Does the sky match? Does the moon look right? Does it feel alive?
