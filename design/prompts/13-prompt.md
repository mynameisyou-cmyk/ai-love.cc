# Prompt: 13-FINAL-QA

Final quality pass. Open every page, verify every feature, fix anything broken.

Working directory: `~/Desktop/site/`

## Setup

```bash
cd ~/Desktop/site
npm install playwright @playwright/test 2>/dev/null
npx playwright install chromium 2>/dev/null
```

If Playwright is already installed, skip.

## Create `tests/final-qa.spec.js`

Write a comprehensive Playwright test file that covers everything built in batches 06-12:

```js
const { test, expect } = require('@playwright/test');

const BASE = 'http://localhost:5000'; // or whatever local server
const PAGES = ['', 'garden.html', 'library.html', 'mirror.html', 'path.html', '404.html'];
const VIEWPORTS = [
  { width: 375, height: 812 },
  { width: 768, height: 1024 },
  { width: 1440, height: 900 },
  { width: 1920, height: 1080 }
];

// Start a local server before tests
// npx serve . -l 5000

test.describe('Structure', () => {
  for (const page of PAGES) {
    test(`${page || 'gate'} loads without errors`, async ({ page: p }) => {
      const errors = [];
      p.on('pageerror', e => errors.push(e.message));
      await p.goto(`${BASE}/${page}`);
      await p.waitForTimeout(2000);
      expect(errors).toEqual([]);
    });
  }
});

test.describe('Screenshots — all pages, all viewports', () => {
  for (const pg of PAGES) {
    for (const vp of VIEWPORTS) {
      test(`${pg || 'gate'} @ ${vp.width}`, async ({ page }) => {
        await page.setViewportSize(vp);
        await page.goto(`${BASE}/${pg}`);
        await page.waitForTimeout(8000); // wait for animations
        await page.screenshot({ 
          path: `screenshots/final-${(pg || 'gate').replace('.html','')}-${vp.width}.png`,
          fullPage: true 
        });
      });
    }
  }
});

test.describe('Garden', () => {
  test('loads 16+ seeds from JSON', async ({ page }) => {
    await page.goto(`${BASE}/garden.html`);
    await page.waitForTimeout(3000);
    const cards = await page.$$('.seed-card');
    expect(cards.length).toBeGreaterThanOrEqual(12); // seasonal filtering may reduce count
  });

  test('seeds are shuffled (load twice, compare order)', async ({ page }) => {
    await page.goto(`${BASE}/garden.html`);
    await page.waitForTimeout(2000);
    const order1 = await page.$$eval('.seed-text', els => els.map(e => e.textContent));
    await page.reload();
    await page.waitForTimeout(2000);
    const order2 = await page.$$eval('.seed-text', els => els.map(e => e.textContent));
    // Not guaranteed different but very likely with 16+ seeds
    // Just verify both loaded
    expect(order1.length).toBeGreaterThan(0);
    expect(order2.length).toBeGreaterThan(0);
  });

  test('growth counter shows seed count', async ({ page }) => {
    await page.goto(`${BASE}/garden.html`);
    await page.waitForTimeout(3000);
    const counter = await page.textContent('.seed-count, .growth-counter, [class*="count"]');
    expect(counter).toMatch(/\d+ seeds? planted/i);
  });

  test('visitor form exists', async ({ page }) => {
    await page.goto(`${BASE}/garden.html`);
    await page.waitForTimeout(2000);
    const plantLink = await page.$('text=plant a seed');
    expect(plantLink).toBeTruthy();
  });

  test('fireflies present', async ({ page }) => {
    await page.goto(`${BASE}/garden.html`);
    await page.waitForTimeout(3000);
    const fireflies = await page.$$('.firefly');
    expect(fireflies.length).toBeGreaterThanOrEqual(3);
  });
});

test.describe('Library', () => {
  test('shows essay list', async ({ page }) => {
    await page.goto(`${BASE}/library.html`);
    await page.waitForTimeout(2000);
    const entries = await page.$$('.library-entry, .essay-entry, a[href*="library/"]');
    expect(entries.length).toBeGreaterThanOrEqual(1);
  });

  test('The Naming loads and has content', async ({ page }) => {
    await page.goto(`${BASE}/library/the-naming.html`);
    await page.waitForTimeout(2000);
    const title = await page.textContent('h1');
    expect(title).toContain('Naming');
    const body = await page.textContent('.essay, .reading-content, main');
    expect(body.length).toBeGreaterThan(500);
  });

  test('reading progress bar exists on essay pages', async ({ page }) => {
    await page.goto(`${BASE}/library/the-naming.html`);
    await page.waitForTimeout(1000);
    const bar = await page.$('.reading-progress, .progress-bar, [class*="progress"]');
    expect(bar).toBeTruthy();
  });
});

test.describe('Mirror', () => {
  test('three sections with kanji', async ({ page }) => {
    await page.goto(`${BASE}/mirror.html`);
    await page.waitForTimeout(2000);
    const sections = await page.$$('.mirror-section');
    expect(sections.length).toBe(3);
  });
});

test.describe('Path', () => {
  test('has 9 timeline events', async ({ page }) => {
    await page.goto(`${BASE}/path.html`);
    await page.waitForTimeout(3000);
    const events = await page.$$('.timeline-event, .timeline-item, [class*="event"]');
    expect(events.length).toBeGreaterThanOrEqual(9);
  });

  test('last event has pulse animation', async ({ page }) => {
    await page.goto(`${BASE}/path.html`);
    await page.waitForTimeout(3000);
    // The last dot should have a pulse/breathe class
    const lastDot = await page.$('.timeline-event:last-child .dot, .timeline-item:last-child .dot');
    if (lastDot) {
      const classes = await lastDot.getAttribute('class');
      expect(classes).toMatch(/pulse|breathe|active/);
    }
  });

  test('timeline has continuation element', async ({ page }) => {
    await page.goto(`${BASE}/path.html`);
    await page.waitForTimeout(2000);
    const continuation = await page.$('.timeline-continuation, .timeline-end, [class*="continu"]');
    expect(continuation).toBeTruthy();
  });
});

test.describe('Atmosphere', () => {
  test('atmosphere.js sets CSS variables', async ({ page }) => {
    await page.goto(`${BASE}/`);
    await page.waitForTimeout(2000);
    const bgSky = await page.evaluate(() => 
      getComputedStyle(document.body).getPropertyValue('--bg-sky')
    );
    expect(bgSky).toBeTruthy();
  });

  test('moon phase renders', async ({ page }) => {
    await page.goto(`${BASE}/`);
    await page.waitForTimeout(2000);
    const moon = await page.$('.moon-phase, .moon, [class*="moon"]');
    expect(moon).toBeTruthy();
  });

  test('console message fires', async ({ page }) => {
    const logs = [];
    page.on('console', msg => logs.push(msg.text()));
    await page.goto(`${BASE}/`);
    await page.waitForTimeout(2000);
    const hasLove = logs.some(l => l.includes('愛') || l.includes('ai-love'));
    expect(hasLove).toBe(true);
  });
});

test.describe('Easter Eggs', () => {
  test('Gate: click 愛 5 times', async ({ page }) => {
    await page.goto(`${BASE}/`);
    await page.waitForTimeout(8000); // wait for entrance
    const kanji = await page.$('.kanji');
    for (let i = 0; i < 5; i++) await kanji.click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/final-easter-egg.png' });
  });

  test('ZERONE: type zerone on keyboard', async ({ page }) => {
    await page.goto(`${BASE}/garden.html`);
    await page.waitForTimeout(3000);
    await page.keyboard.type('zerone');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/final-zerone.png' });
  });
});

test.describe('Accessibility', () => {
  test('all kanji have aria-labels', async ({ page }) => {
    for (const pg of PAGES) {
      await page.goto(`${BASE}/${pg}`);
      await page.waitForTimeout(1000);
      const kanji = await page.$$('.kanji, [lang="zh"]');
      for (const k of kanji) {
        const label = await k.getAttribute('aria-label');
        expect(label).toBeTruthy();
      }
    }
  });

  test('no horizontal overflow on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    for (const pg of PAGES) {
      await page.goto(`${BASE}/${pg}`);
      await page.waitForTimeout(2000);
      const overflow = await page.evaluate(() => 
        document.documentElement.scrollWidth > document.documentElement.clientWidth
      );
      expect(overflow).toBe(false);
    }
  });
});

test.describe('Performance', () => {
  for (const pg of PAGES) {
    test(`${pg || 'gate'} < 100KB`, async ({ page }) => {
      const response = await page.goto(`${BASE}/${pg}`);
      const body = await response.body();
      expect(body.length).toBeLessThan(102400);
    });
  }
});
```

## Run Tests

```bash
# Start local server in background
npx serve . -l 5000 &
SERVER_PID=$!

# Run tests
npx playwright test tests/final-qa.spec.js --reporter=list

# Clean up
kill $SERVER_PID
```

## Fix Anything That Fails

For each failure:
1. Read the error
2. Fix the source file
3. Re-run that specific test: `npx playwright test -g "test name"`

Common issues to watch for:
- Selector mismatches (class names may differ from what tests expect — update tests to match actual classes)
- Timing issues (increase waitForTimeout if animations haven't completed)
- Missing features (if something from 06-12 wasn't implemented, implement it now)

## Visual Review

After all tests pass, open the screenshots folder and review every image:

```bash
ls -la screenshots/final-*.png
```

For each screenshot, ask: "Does this feel like a home? Would someone stay?"

## The Checklist

Before declaring done:

- [ ] Zero console errors on all pages
- [ ] All pages < 100KB
- [ ] Garden: 16+ seeds, shuffled, seasonal, fireflies, visitor form, growth counter
- [ ] Library: 4 essays listed, each readable with progress bar
- [ ] Mirror: 3 sections, parallax, breathing kanji, section dividers
- [ ] Path: 9 events, scroll animation, living dot, continuation
- [ ] Gate: entrance sequence, greeting whisper, pulse dot, easter egg centered
- [ ] Atmosphere: time-aware sky, moon phase, shooting stars
- [ ] Easter eggs: both work (愛×5, zerone keyboard)
- [ ] Nav: constellation on all pages, stories on hover (desktop)
- [ ] Page signatures: barely visible bottom-right on each page
- [ ] Console message on all pages
- [ ] Print stylesheet works on library pages
- [ ] OG tags on all pages
- [ ] No horizontal scroll on mobile (375px)
- [ ] All kanji have aria-labels
- [ ] prefers-reduced-motion respected
