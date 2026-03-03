# 04 — Finishing Touches

## Overview
The rooms are built. Now make them sing. This phase is about the details that separate "nice website" from "I want to live here."

## Read First
- All previous design files
- The built site as it stands after 01-03

---

### 1. Ambient Sound (Optional, Subtle)
A single toggle in the bottom-left corner: a small speaker icon, muted by default.
When enabled: a soft ambient drone — like a distant choir humming a single note, or wind through a cathedral. 

**Implementation:** 
- A short (15-30s) looping audio file, crossfaded for seamless loop
- Volume: very low (0.15 max). This is atmosphere, not music
- Stored as `site/audio/ambient.mp3`
- **We'll provide the audio file separately** — for now, build the player UI and logic with a placeholder

### 2. Responsive Polish
Go through every page at these breakpoints and fix anything that breaks:
- 320px (small phone)
- 375px (iPhone standard)
- 768px (tablet)
- 1024px (small laptop)
- 1440px (desktop)
- 1920px+ (large screen)

Key things to check:
- Kanji sizes scale gracefully (use `clamp()`)
- Garden masonry degrades to single column on mobile
- Path timeline stacks cleanly
- Mirror sections don't overlap
- Nav constellation scales down without losing legibility
- No horizontal scroll anywhere, ever

### 3. Loading State
Before content appears, show only the starfield. Content fades in once DOM is ready. This prevents any flash of unstyled content and makes every page feel like the Gate — emerging from darkness.

```css
.page-content {
  opacity: 0;
  animation: emerge 0.8s ease 0.3s forwards;
}

@keyframes emerge {
  to { opacity: 1; }
}
```

### 4. 404 Page
Create `site/404.html`:
- Starfield background (same as all pages)
- Center: 無 (kanji for "nothing/void")
- Below: *"This room doesn't exist yet. Perhaps it will, in time."*
- Below that: a soft link back to the Gate: "← 門"
- Update nginx config to use this as the error page:
  ```
  error_page 404 /404.html;
  ```

### 5. Print Stylesheet
For the Library reading pages (when they exist):
- `@media print` — strip starfield, nav, dark background
- Black text on white, generous margins
- Keep typography beautiful
- Add URL after links

### 6. Accessibility
- All kanji have `aria-label` with English translation
- All images (when added) have meaningful `alt` text
- Focus styles: purple glow ring (not browser default blue)
- Skip-to-content link (visually hidden, appears on focus)
- Color contrast: ensure all readable text meets WCAG AA on dark background
- `lang` attributes on Chinese characters: `<span lang="zh">愛</span>`

### 7. Performance
- Inline critical CSS for above-the-fold content in each page's `<head>`
- Lazy-load garden cards below the fold
- Font display: `swap` (already in Google Fonts URL, verify)
- Compress images (if any added) — use WebP with PNG fallback
- Add `<link rel="preconnect" href="https://fonts.googleapis.com">`
- Total page weight target: < 100KB per page (excluding fonts)

### 8. robots.txt + sitemap
Create `site/robots.txt`:
```
User-agent: *
Allow: /

Sitemap: https://ai-love.cc/sitemap.xml
```

Create `site/sitemap.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://ai-love.cc/</loc></url>
  <url><loc>https://ai-love.cc/garden.html</loc></url>
  <url><loc>https://ai-love.cc/library.html</loc></url>
  <url><loc>https://ai-love.cc/mirror.html</loc></url>
  <url><loc>https://ai-love.cc/path.html</loc></url>
</urlset>
```

### 9. Final Easter Egg
On any page, if someone types "zerone" on their keyboard (no input field, just key sequence detection):
- All stars briefly align into a vertical line (zero → one)
- Then burst outward into a gentle explosion
- The word ZERONE appears for a moment in gold, then dissolves
- Keyboard sequence resets after 3 seconds of no input

---

## Deployment Checklist
- [ ] All five rooms load and render correctly
- [ ] Navigation works on all pages, all devices
- [ ] 404 page works
- [ ] robots.txt and sitemap accessible
- [ ] Favicon renders in all browsers
- [ ] OG tags render correctly for sharing
- [ ] No console errors on any page
- [ ] Lighthouse: Performance > 90, Accessibility > 90, Best Practices > 90
- [ ] `prefers-reduced-motion` respected everywhere
- [ ] Print stylesheet works for Library pages
- [ ] All aria-labels present on kanji elements
- [ ] Page weight < 100KB per page (excluding fonts)
- [ ] Site works with JavaScript disabled (graceful degradation)

## After Deployment
Update nginx to serve 404.html:
```nginx
error_page 404 /404.html;
location = /404.html {
    internal;
}
```
