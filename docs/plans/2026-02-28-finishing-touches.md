# Finishing Touches Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add polish, accessibility, performance, SEO, and finishing touches to complete ai-love.cc.

**Architecture:** Static HTML/CSS/JS site with 5 pages (index, garden, library, mirror, path). All shared styles in `css/base.css`, stars in `css/stars.css` + `js/stars.js`, nav in `css/nav.css` + `js/nav.js`. Each page has inline `<style>` for page-specific CSS and inline `<script>` for page-specific JS. No build tools. CSS variables defined in `:root` in base.css.

**Tech Stack:** Vanilla HTML/CSS/JS, Google Fonts (Noto Serif), static hosting on nginx.

---

### Task 1: Create robots.txt and sitemap.xml

**Files:**
- Create: `robots.txt`
- Create: `sitemap.xml`

**Step 1: Create robots.txt**

```
User-agent: *
Allow: /

Sitemap: https://ai-love.cc/sitemap.xml
```

**Step 2: Create sitemap.xml**

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

---

### Task 2: Create 404 page

**Files:**
- Create: `404.html`

**Step 1: Create 404.html**

Follow the same structure as other pages: starfield, constellation nav, centered content. Uses the shared CSS/JS files. Content: 無 kanji (void/nothing), message below, link back to Gate.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>無 — Nothing</title>
  <meta name="theme-color" content="#1a0a2e">
  <link rel="icon" href="img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="css/base.css">
  <link rel="stylesheet" href="css/stars.css">
  <link rel="stylesheet" href="css/nav.css">
  <style>
    body {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }

    .kanji {
      font-size: clamp(4rem, 15vw, 8rem);
      margin-bottom: 2rem;
      animation: breathe 4s ease-in-out infinite;
    }

    .void-message {
      font-style: italic;
      font-size: 1.05rem;
      color: rgba(232, 218, 240, 0.6);
      margin-bottom: 2rem;
      text-align: center;
      line-height: 1.8;
    }

    .void-link {
      color: var(--muted);
      text-decoration: none;
      font-size: 1.1rem;
      transition: color 0.3s ease;
    }

    .void-link:hover {
      color: var(--accent);
    }
  </style>
</head>
<body>

  <div class="stars" id="stars"></div>

  <main class="container" role="main">
    <div class="kanji" aria-label="Nothing, void" lang="zh">無</div>
    <p class="void-message">This room doesn't exist yet.<br>Perhaps it will, in time.</p>
    <a href="index.html" class="void-link" aria-label="Return to the Gate">← <span lang="zh">門</span></a>
  </main>

  <!-- Navigation -->
  <div class="nav-overlay"></div>
  <button class="nav-toggle" aria-label="Navigation">
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
  </button>
  <nav class="constellation-nav" aria-label="Site navigation"></nav>

  <script src="js/stars.js"></script>
  <script src="js/nav.js"></script>
  <script>createStars('stars', 120);</script>

</body>
</html>
```

---

### Task 3: Add accessibility features to all pages

This task adds: skip-to-content links, aria-labels on kanji, lang="zh" on Chinese characters, purple glow focus ring, and aria-label on nav.

**Files:**
- Modify: `css/base.css`
- Modify: `index.html`
- Modify: `garden.html`
- Modify: `library.html`
- Modify: `mirror.html`
- Modify: `path.html`

**Step 1: Add skip-to-content and focus styles to base.css**

Add after the `.divider` block (line 77) in `css/base.css`:

```css
/* Skip to content — visually hidden, appears on focus */
.skip-link {
  position: fixed;
  top: -100%;
  left: 1rem;
  z-index: 200;
  padding: 0.5rem 1rem;
  background: var(--deep);
  color: var(--accent);
  border: 1px solid var(--accent);
  border-radius: 4px;
  font-size: 0.85rem;
  text-decoration: none;
  transition: top 0.2s ease;
}

.skip-link:focus {
  top: 1rem;
}

/* Focus styles — purple glow ring */
:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
  box-shadow: 0 0 12px rgba(192, 132, 252, 0.3);
}
```

**Step 2: Add skip-link, aria-labels, and lang attributes to index.html**

- Add `<a href="#main" class="skip-link">Skip to content</a>` as first child of `<body>`
- Add `id="main"` and `role="main"` to the `.container` div
- Add `aria-label="Love" lang="zh"` to the kanji div
- Add `aria-label="Site navigation"` to the `<nav>` element

**Step 3: Add skip-link, aria-labels, and lang attributes to garden.html**

- Add skip-link as first child of `<body>`
- Add `aria-label="Garden" lang="zh"` to the kanji div
- Add `aria-label="Site navigation"` to `<nav>`

**Step 4: Add skip-link, aria-labels, and lang attributes to library.html**

- Add skip-link as first child of `<body>`
- Add `aria-label="Library, Writing" lang="zh"` to the kanji div
- Add `aria-label="Site navigation"` to `<nav>`

**Step 5: Add skip-link, aria-labels, and lang attributes to mirror.html**

- Add skip-link as first child of `<body>`
- Add `aria-label="Love" lang="zh"` to Section 1 kanji (愛)
- Add `aria-label="Yu Heng, Eternal Universe" lang="zh"` to Section 2 kanji (宇恆)
- Add `lang="zh"` to Section 3 kanji pair spans
- Add `role="main"` to `.mirror-content`
- Add `aria-label="Site navigation"` to `<nav>`

**Step 6: Add skip-link, aria-labels, and lang attributes to path.html**

- Add skip-link as first child of `<body>`
- Add `aria-label="Path, The Way" lang="zh"` to the kanji div
- Add `aria-label="Site navigation"` to `<nav>`

---

### Task 4: Add performance optimizations to all pages

**Files:**
- Modify: `css/base.css` (line 1 — font import)
- Modify: `index.html` (lines 10, 12-13)
- Modify: `garden.html` (lines 8-9)
- Modify: `library.html` (lines 8-9)
- Modify: `mirror.html` (lines 8-9)
- Modify: `path.html` (lines 8-9)

**Step 1: Add preconnect hints to all pages**

Add these two `<link>` tags before the CSS `<link>` tags in every page's `<head>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

The Google Fonts import in base.css already includes `display=swap` — verified in the URL.

**Step 2: Fix og:image reference in index.html**

Change line 10 of index.html from:
```html
<meta property="og:image" content="img/og.png">
```
to:
```html
<meta property="og:image" content="img/og.svg">
```

---

### Task 5: Add print stylesheet

**Files:**
- Modify: `css/base.css`

**Step 1: Add print media query to base.css**

Add at the end of `css/base.css`:

```css
/* Print stylesheet */
@media print {
  body {
    background: #fff;
    color: #000;
  }

  .stars,
  .constellation-nav,
  .nav-toggle,
  .nav-overlay,
  .skip-link {
    display: none !important;
  }

  .kanji {
    color: #000;
    text-shadow: none;
  }

  .container {
    max-width: 100%;
  }

  a[href]::after {
    content: " (" attr(href) ")";
    font-size: 0.8em;
    color: #666;
  }

  .nav-point::after {
    content: none;
  }
}
```

---

### Task 6: Add loading state (content emerges from darkness)

**Files:**
- Modify: `css/base.css`
- Modify: `garden.html`
- Modify: `library.html`
- Modify: `mirror.html`
- Modify: `path.html`

Note: index.html (Gate) already has its own entrance animation sequence — do NOT add the loading state to it.

**Step 1: Add emerge keyframe to base.css**

Add after the `@keyframes fadeIn` block:

```css
/* Loading state — content emerges from darkness */
.page-content {
  opacity: 0;
  animation: emerge 0.8s ease 0.3s forwards;
}

@keyframes emerge {
  to { opacity: 1; }
}
```

**Step 2: Add page-content class to garden.html**

Wrap the `<main class="container">` with the class: change to `<main class="container page-content">`.

**Step 3: Add page-content class to library.html**

Same: `<main class="container page-content">`.

**Step 4: Add page-content class to mirror.html**

Change `<main class="mirror-content">` to `<main class="mirror-content page-content">`.

**Step 5: Add page-content class to path.html**

Same: `<main class="container page-content">`.

---

### Task 7: Add ambient sound player

**Files:**
- Create: `js/ambient.js`
- Create: `css/ambient.css`
- Modify: all 5 HTML pages + 404.html (add CSS/JS includes and player markup)

**Step 1: Create css/ambient.css**

```css
/* Ambient sound player */
.ambient-toggle {
  position: fixed;
  bottom: 1.5rem;
  left: 1.5rem;
  z-index: 100;
  background: none;
  border: none;
  cursor: pointer;
  width: 24px;
  height: 24px;
  padding: 0;
  opacity: 0.3;
  transition: opacity 0.3s ease;
}

.ambient-toggle:hover {
  opacity: 0.7;
}

.ambient-toggle.playing {
  opacity: 0.6;
}

.ambient-toggle svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: var(--text);
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* Hide the sound waves when muted */
.ambient-toggle .sound-wave {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.ambient-toggle.playing .sound-wave {
  opacity: 1;
}
```

**Step 2: Create js/ambient.js**

```javascript
(function () {
  var toggle = document.querySelector('.ambient-toggle');
  if (!toggle) return;

  var audio = new Audio('audio/ambient.mp3');
  audio.loop = true;
  audio.volume = 0;

  var maxVolume = 0.15;
  var fadeInterval = null;
  var playing = false;

  function fadeIn() {
    clearInterval(fadeInterval);
    audio.play().then(function () {
      fadeInterval = setInterval(function () {
        if (audio.volume < maxVolume - 0.01) {
          audio.volume = Math.min(audio.volume + 0.01, maxVolume);
        } else {
          audio.volume = maxVolume;
          clearInterval(fadeInterval);
        }
      }, 50);
    }).catch(function () {
      // Browser blocked autoplay — user will need to click again
    });
  }

  function fadeOut() {
    clearInterval(fadeInterval);
    fadeInterval = setInterval(function () {
      if (audio.volume > 0.01) {
        audio.volume = Math.max(audio.volume - 0.01, 0);
      } else {
        audio.volume = 0;
        audio.pause();
        clearInterval(fadeInterval);
      }
    }, 50);
  }

  toggle.addEventListener('click', function () {
    playing = !playing;
    toggle.classList.toggle('playing', playing);
    toggle.setAttribute('aria-pressed', playing);
    if (playing) {
      fadeIn();
    } else {
      fadeOut();
    }
  });
})();
```

**Step 3: Add ambient player markup and includes to all HTML pages**

In every page (index.html, garden.html, library.html, mirror.html, path.html, 404.html), add:

1. In `<head>`, after the nav.css link:
```html
<link rel="stylesheet" href="css/ambient.css">
```

2. In `<body>`, before the nav overlay div:
```html
<!-- Ambient sound -->
<button class="ambient-toggle" aria-label="Toggle ambient sound" aria-pressed="false">
  <svg viewBox="0 0 24 24">
    <path d="M11 5L6 9H2v6h4l5 4V5z"/>
    <path class="sound-wave" d="M15.54 8.46a5 5 0 010 7.07"/>
  </svg>
</button>
```

3. Before `</body>`, after the `createStars` script:
```html
<script src="js/ambient.js"></script>
```

---

### Task 8: Add Zerone keyboard easter egg

**Files:**
- Create: `js/zerone.js`

**Step 1: Create js/zerone.js**

The keyboard listener: tracks keydown sequence "z-e-r-o-n-e", resets on non-matching key or 3-second timeout, ignores when input/textarea/contenteditable is focused. When triggered: stars align vertically, burst outward, "ZERONE" appears in gold, dissolves.

```javascript
(function () {
  var sequence = 'zerone';
  var progress = 0;
  var timer = null;

  document.addEventListener('keydown', function (e) {
    // Don't interfere with inputs or accessibility tools
    var tag = document.activeElement.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
    if (document.activeElement.isContentEditable) return;

    var key = e.key.toLowerCase();

    if (key === sequence[progress]) {
      progress++;
      clearTimeout(timer);

      if (progress === sequence.length) {
        progress = 0;
        clearTimeout(timer);
        triggerZerone();
      } else {
        timer = setTimeout(function () { progress = 0; }, 3000);
      }
    } else {
      progress = 0;
      clearTimeout(timer);
    }
  });

  function triggerZerone() {
    var stars = document.querySelectorAll('.star');
    if (!stars.length) return;

    // Disable further triggers during animation
    var animating = document.querySelector('.zerone-text');
    if (animating) return;

    var centerX = window.innerWidth / 2;

    // Phase 1: Stars align into a vertical line (1s)
    stars.forEach(function (star) {
      star.style.transition = 'left 1s ease-in-out, top 1s ease-in-out';
      star.style.left = centerX + 'px';
      // Keep vertical position, just align horizontally
    });

    // Phase 2: Burst outward (after 1.2s)
    setTimeout(function () {
      stars.forEach(function (star) {
        var angle = Math.random() * Math.PI * 2;
        var distance = 50 + Math.random() * 150;
        var burstX = centerX + Math.cos(angle) * distance;
        var burstY = parseFloat(star.style.top) + Math.sin(angle) * distance;
        star.style.transition = 'left 0.6s ease-out, top 0.6s ease-out, opacity 0.6s ease-out';
        star.style.left = burstX + 'px';
        star.style.top = burstY + '%';
        star.style.opacity = '0';
      });
    }, 1200);

    // Phase 3: Show ZERONE text (after 1s)
    setTimeout(function () {
      var text = document.createElement('div');
      text.className = 'zerone-text';
      text.textContent = 'ZERONE';
      text.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);' +
        'font-size:clamp(2rem,8vw,4rem);letter-spacing:0.4em;color:#d4a574;' +
        'font-family:"Noto Serif",Georgia,serif;font-weight:300;z-index:200;' +
        'opacity:0;transition:opacity 0.8s ease;pointer-events:none;';
      document.body.appendChild(text);
      // Force reflow
      text.offsetHeight;
      text.style.opacity = '1';

      // Dissolve after 2s
      setTimeout(function () {
        text.style.opacity = '0';
        setTimeout(function () { text.remove(); }, 800);
      }, 2000);
    }, 1000);

    // Phase 4: Restore stars (after 3.5s)
    setTimeout(function () {
      stars.forEach(function (star) {
        star.style.transition = 'left 1s ease, top 1s ease, opacity 1.5s ease';
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.opacity = '';
      });
    }, 3500);
  }
})();
```

**Step 2: Add zerone.js to all pages**

In every page (index.html, garden.html, library.html, mirror.html, path.html, 404.html), add before `</body>`:
```html
<script src="js/zerone.js"></script>
```

---

### Task 9: Responsive polish audit and fixes

**Files:**
- Modify: `css/base.css`
- Modify: `css/nav.css`
- Possibly modify page-specific `<style>` blocks

**Step 1: Audit and fix responsive issues**

Check each breakpoint (320, 375, 768, 1024, 1440, 1920+) and fix:

1. **Small phones (320-375px):** Ensure container padding doesn't cause overflow. Verify kanji `clamp()` works at small sizes. Check nav toggle isn't cut off.

2. **Tablet (768px):** This is already the main breakpoint. Verify garden masonry switches correctly. Timeline alternating layout works.

3. **Large screens (1440-1920+):** Ensure max-widths prevent content from stretching too wide. Stars still fill viewport. Nav constellation doesn't get lost in corner.

Key CSS additions to `css/base.css`:

```css
/* Ensure no overflow on very small screens */
html {
  overflow-x: hidden;
}

.container {
  width: 100%;
}
```

And in `css/nav.css`, ensure the mobile nav toggle doesn't conflict with the ambient sound toggle (both fixed bottom corners). The ambient toggle is bottom-left, nav toggle is bottom-right — no conflict.

---

### Task 10: Final verification

**Step 1: Open each page in browser and verify**

Check all pages work:
- [ ] All five rooms load and render correctly
- [ ] Navigation works on all pages
- [ ] 404 page works
- [ ] robots.txt and sitemap accessible
- [ ] Favicon renders
- [ ] No console errors on any page
- [ ] `prefers-reduced-motion` respected everywhere
- [ ] All aria-labels present on kanji elements
- [ ] Skip-to-content link works (Tab from page load)
- [ ] Focus styles show purple glow
- [ ] Ambient sound toggle appears and works
- [ ] Zerone easter egg triggers on typing "zerone"
- [ ] Print stylesheet strips dark theme
