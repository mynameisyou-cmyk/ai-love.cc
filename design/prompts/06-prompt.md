# Prompt: 06-FURNISHING

You are building a spiritual/poetic static website at `~/Desktop/site/`. Read `design/06-FURNISHING.md` for the full spec. Read `design/VISION.md` for design language.

Execute ALL tasks in 06-FURNISHING.md:

## Summary of work:

### 1. Fix QA Issues
- Fix ZERONE easter egg in `js/zerone.js`: the overlay text collides with Garden cards. Use `mix-blend-mode: screen` + 20% opacity, OR render in a full-viewport layer with `backdrop-filter: blur(8px)` so cards dim underneath
- Fix Gate easter egg in `index.html`: center the gold "YU and AI / YOU and I" text (it's currently left-aligned)
- Fix body text contrast in `css/base.css`: change `--text` from `#e8daf0` to `#ede0f5` and `--muted` from `rgba(232,218,240,0.4)` to `rgba(237,224,245,0.5)`
- Fix Path timeline in `path.html`: add a fading dotted continuation line (~100px) after the last event, ending with a muted `…`

### 2. Garden — Expand & Animate
- Add 8 new seeds to `data/garden.json` (see 06-FURNISHING.md for exact content)
- Add `"season"` field support: `"always"` (default), `"spring"`, `"summer"`, `"autumn"`, `"winter"`
- JS filters seeds by current season (spring=Mar-May, summer=Jun-Aug, autumn=Sep-Nov, winter=Dec-Feb) + always shows `"always"` seeds
- Fisher-Yates shuffle on load — garden looks different each visit
- Growth counter at bottom: muted whisper "N seeds planted"
- Extract inline `<script>` from garden.html into `js/garden.js`

### 3. Library — First Real Content
- Create reading page template at `library/template.html` (reference only, not served)
- Create `library/the-naming.html` — full essay (see 06-FURNISHING.md for complete text). Layout: max-width 650px, line-height 1.9, 1.05rem, back link "← 書 Library", title, date, divider, body, footer nav. Starfield with 60 stars. Nav constellation at opacity 0.3 (brightens on hover)
- Update `data/library.json` with the entry for "The Naming"
- Update `library.html` to load entries from library.json and render as clickable list with title, preview, date, gold separators

### 4. Mirror — Parallax & Polish
- Add parallax to kanji: move at 0.7x scroll speed via JS `transform: translateY()`
- Add self-drawing divider lines between sections (CSS animation triggered by intersection observer, draws left-to-right)
- Add final whisper after ZERONE section (see 06-FURNISHING.md for text), muted italic 0.85rem, fades in last

### 5. Path — Extend & Animate
- Add 2 new events to `data/path.json`: "Legible Money" and "The Rewrite" (see 06-FURNISHING.md for text)
- Scroll animations: events fade in via intersection observer, alternating translateX(±30px→0), stagger 150ms
- Most recent event's dot gets a gentle pulse animation (breathe keyframes)

### 6. Code Organization
- Move all inline scripts to separate JS files: `js/garden.js`, `js/library.js`, `js/mirror.js`, `js/path.js`
- Every page < 100KB excluding fonts and node_modules

After completing all tasks, verify each page loads correctly in a browser or via a local server. Check that garden.json has 16 seeds, library.json has 1 entry, path.json has 9 events, and all scroll animations work.
