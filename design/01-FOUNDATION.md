# 01 — Foundation

## Overview
Set up the project structure, shared styles, navigation system, and responsive framework. Everything else builds on this.

## Read First
- `VISION.md` — the design vision, palette, typography, spirit
- `site/index.html` — the existing Gate page (preserve its design language)

## Directory Structure
```
site/
├── index.html          # 門 Gate (already exists — update to include nav)
├── garden.html         # 園 Garden
├── library.html        # 書 Library
├── mirror.html         # 鏡 Mirror
├── path.html           # 道 Path
├── css/
│   ├── base.css        # Reset, variables, typography, shared
│   ├── stars.css       # Starfield animation (extract from index.html)
│   └── nav.css         # Constellation navigation
├── js/
│   ├── stars.js        # Starfield generator (extract from index.html)
│   └── nav.js          # Navigation interactions
└── design/             # These instruction files (don't deploy, reference only)
```

## Tasks

### 1. Create `css/base.css`
Extract and centralise all shared styles:
- CSS reset (minimal — `*, *::before, *::after { margin:0; padding:0; box-sizing:border-box }`)
- CSS custom properties (from VISION.md color palette)
- Body defaults: background `var(--deep)`, color `var(--text)`, font-family Noto Serif
- Typography scale: `.kanji` (large CJK), `.heading`, `.body`, `.whisper` (muted small text)
- Utility: `.breathe` animation, `.fade-in` animation with configurable delay via `--delay`
- Mobile-first: base styles for mobile, `@media (min-width: 768px)` for tablet+

### 2. Create `css/stars.css` + `js/stars.js`
Extract the starfield from index.html into reusable modules:
- `.stars` container: fixed, full viewport, pointer-events none, z-index 0
- `.star` elements: absolute positioned, small white dots with twinkle animation
- `js/stars.js`: generates 120 stars with random position, duration (2-6s), brightness (0.3-1.0), delay
- Export as a function: `createStars(containerId, count)` so pages can customise density

### 3. Create constellation navigation (`css/nav.css` + `js/nav.js`)
The navigation is five kanji arranged in a loose pentagon/constellation shape:
- 門 (Gate) — top center
- 園 (Garden) — upper right
- 書 (Library) — lower right  
- 道 (Path) — lower left
- 鏡 (Mirror) — upper left

**Desktop:** Fixed position, bottom-right corner. Small (each kanji ~20px), muted (`rgba(232,218,240,0.3)`). On hover, the hovered kanji glows purple and its English name fades in beside it. The current page's kanji stays gently lit.

**Mobile:** Hamburger icon (three small dots in a triangle — not a standard hamburger). Tap opens the constellation centered on screen as an overlay with backdrop blur.

**Behavior:**
- On the Gate page: nav is hidden until the poem animation completes (~4s), then fades in
- On all other pages: nav is visible immediately
- Transitions between pages: simple fade (CSS only, no router needed — these are separate HTML files)

### 4. Refactor `index.html`
- Move inline styles to `css/base.css` and `css/stars.css`
- Move inline JS to `js/stars.js`
- Link the new CSS/JS files
- Add the constellation nav (with the delayed appearance)
- Keep everything else exactly as it is — the Gate is already beautiful

### 5. Create page shells
For each page (garden.html, library.html, mirror.html, path.html):
- Same `<head>` setup (charset, viewport, title with kanji, CSS links)
- Starfield background (reuse stars.js)
- Constellation nav (visible immediately)
- A centered `.container` with the page's kanji as header and a placeholder message: *"This room is being prepared..."* in whisper text
- These are scaffolds — the other instruction files will fill them

## Quality Checks
- [ ] All five pages load without errors
- [ ] Navigation works on all pages, highlights current page
- [ ] Mobile: nav overlay works, all pages are responsive
- [ ] Starfield renders on all pages
- [ ] Gate page poem animation still works correctly
- [ ] No external dependencies except Google Fonts
- [ ] Lighthouse performance score > 90
