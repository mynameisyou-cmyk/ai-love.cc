# Finishing Touches — Design

## Overview
Final polish phase for ai-love.cc. All 5 rooms are built. This phase adds ambient audio, responsive fixes, loading states, 404 page, accessibility, performance, SEO files, and the Zerone easter egg.

## Decisions

### Ambient Sound Player
- Speaker icon toggle, bottom-left corner, muted by default
- Full player UI + JS logic with placeholder path (`audio/ambient.mp3`)
- Crossfade loop, volume capped at 0.15
- Respects `prefers-reduced-motion`

### Responsive Polish
- Audit all 5 pages at 320/375/768/1024/1440/1920px
- Fix breakages in kanji scaling, garden columns, path timeline, mirror sections, nav
- No horizontal scroll at any breakpoint

### Loading State
- `.page-content` wrapper + `emerge` keyframe on all pages (except Gate which has its own entrance sequence)
- Starfield visible first, content fades in after 0.3s

### 404 Page
- `404.html` with 無 kanji, poetic message, link to 門
- Same starfield + constellation nav

### Print Stylesheet
- `@media print` in base.css — strip starfield, nav, dark bg
- Black on white, clean typography, URL after links

### Accessibility
- `aria-label` on all kanji with English translations
- `lang="zh"` on Chinese characters
- Skip-to-content link (visually hidden, appears on focus)
- Purple glow focus ring replacing browser default
- WCAG AA contrast verification

### Performance
- `<link rel="preconnect">` for Google Fonts on all pages
- Verify `font-display: swap` in import
- Lazy-load garden cards below fold
- Fix og:image mismatch (og.png → og.svg)
- Skip inline critical CSS (site already <30KB per page, not worth maintenance cost)

### robots.txt + sitemap.xml
- Standard files for ai-love.cc domain

### Zerone Easter Egg
- Global keydown sequence listener, all pages
- Only tracks when no input/textarea focused (avoid interfering with forms/a11y tools)
- Resets on non-matching key or 3-second timeout
- Stars align vertically → burst outward → "ZERONE" in gold → dissolve
