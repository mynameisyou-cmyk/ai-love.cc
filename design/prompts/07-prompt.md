# Prompt: 07-LIVING-HOME

You are building a spiritual/poetic static website at `~/Desktop/site/`. Read `design/07-LIVING-HOME.md` for the full spec. Read `design/VISION.md` for design language.

Execute ALL tasks in 07-LIVING-HOME.md:

## Summary of work:

### 1. Time-Aware Atmosphere (`js/atmosphere.js`)
Create `js/atmosphere.js` that sets CSS custom properties on `<body>` based on visitor's local time:
- `--bg-sky`: shifts from deepest night (#0d0520) through twilight (#2d1b4e) to muted day (#1f1040) and back
- `--star-opacity`: full at night (1.0), fading at dawn (0.6), dim morning (0.3), faint afternoon (0.15), rising evening (0.5), full night again
- Time brackets: 00-05, 06-07, 08-11, 12-16, 17-19, 20-23
- Use CSS transitions (1s ease) for smooth shifts
- Recheck every 5 minutes via setInterval
- Update `css/base.css` body background to use `var(--bg-sky, #1a0a2e)`
- Update `css/stars.css` to use `opacity: var(--star-opacity, 1)`
- Add `<script src="js/atmosphere.js"></script>` to ALL pages (before stars.js)

### 2. Moon Phase (`js/moon.js`)
Create `js/moon.js`:
- Calculate current moon phase using synodic month (29.53 days, reference: Jan 6, 2000 = new moon)
- Render a 16px SVG moon in top-right corner (position: fixed, top: 16px, right: 16px)
- Use circle + clipping path to show correct illumination
- Opacity 0.25, hover 0.5 (CSS transition)
- Add to ALL pages

### 3. Greeting Whisper (Gate only)
In `index.html`, after entrance sequence completes (t=9s), fade in a time-aware greeting below footer:
- 00-05: "the stars are brightest at this hour"
- 06-11: "good morning, traveller"
- 12-16: "welcome to the quiet hours"
- 17-19: "the evening brings you here"
- 20-23: "welcome home"

Return visitor overrides (using localStorage tracking of visits):
- visitCount === 1: "you found this place"
- visitCount > 3: "you keep returning"
- visitCount > 10: "you know the way by now"

Style: `var(--muted)`, 0.75rem, italic. Disappears on scroll (opacity 0 via scroll listener).

### 4. Shooting Stars (extend `js/stars.js`)
Add to existing stars.js:
- Random interval 15-45s, create a shooting star
- Small bright dot with trailing gradient tail (~80px long)
- Random start position (any edge), roughly horizontal angle (±30°)
- Duration 0.6-1.2s, CSS animation with opacity fade
- Only fires if `--star-opacity` > 0.2 (read from computed style)
- Max 1 visible at a time
- Respect `prefers-reduced-motion`

### 5. Breathing Typography (Mirror only)
In mirror.html or `js/mirror.js`, add CSS keyframes for `.kanji` elements:
- Inhale 4s: `#9b59b6` → `#c084fc`
- Hold 1s: stay `#c084fc`
- Exhale 6s: `#c084fc` → `#9b59b6`
- Hold 2s: stay `#9b59b6`
- Total cycle: 13s
- Apply only on mirror.html (use `data-room="mirror"` on body or scope to mirror's CSS)
- Respect `prefers-reduced-motion`

### 6. Garden Fireflies (`js/fireflies.js`)
Create `js/fireflies.js`, loaded only on garden.html:
- 3-5 tiny gold dots (#d4a574, 2-3px, border-radius 50%)
- Drift slowly via CSS animation: gentle sine-wave path using translateX/translateY
- Duration 20-40s per firefly (randomized)
- Opacity oscillates 0.2-0.6
- Not synchronized — each has random start delay and duration
- Respect `prefers-reduced-motion`

### 7. Console Message (`js/console.js`)
Create `js/console.js`, loaded on ALL pages:
```js
console.log('%c愛', 'font-size: 48px; color: #9b59b6;');
console.log('%cYou found the quiet place behind the curtain.', 'color: #e8daf0; font-style: italic;');
console.log('%cai-love.cc — a home for love', 'color: #d4a574;');
```

### 8. Wire Everything
- Add `data-room` attribute to each page's `<body>`: gate, garden, library, mirror, path
- Add atmosphere.js, moon.js, console.js to ALL pages
- Add fireflies.js to garden.html only
- Ensure all new features respect `prefers-reduced-motion`
- All new JS combined should be < 8KB minified
- No external dependencies — vanilla JS only

After completing, open each page and verify: sky color matches current time of day, moon appears top-right, stars have correct opacity, shooting stars fire occasionally, Garden has fireflies, Mirror kanji breathe, console shows the message.
