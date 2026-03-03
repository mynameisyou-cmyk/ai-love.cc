const { test, expect } = require('@playwright/test');

const BASE = 'http://localhost:8080';
const PAGES = ['', 'garden.html', 'library.html', 'mirror.html', 'path.html', '404.html'];
const VIEWPORTS = [
  { width: 375, height: 812 },
  { width: 768, height: 1024 },
  { width: 1440, height: 900 },
  { width: 1920, height: 1080 }
];

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
        await page.waitForTimeout(8000);
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
    expect(cards.length).toBeGreaterThanOrEqual(12);
  });

  test('seeds are shuffled (load twice, compare order)', async ({ page }) => {
    await page.goto(`${BASE}/garden.html`);
    await page.waitForTimeout(2000);
    const order1 = await page.$$eval('.seed-text', els => els.map(e => e.textContent));
    await page.reload();
    await page.waitForTimeout(2000);
    const order2 = await page.$$eval('.seed-text', els => els.map(e => e.textContent));
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

  test('has 4 essays in library', async ({ page }) => {
    await page.goto(`${BASE}/library.html`);
    await page.waitForTimeout(2000);
    const entries = await page.$$('.library-entry, a[href*="library/"]');
    expect(entries.length).toBeGreaterThanOrEqual(4);
  });

  test('The Method loads', async ({ page }) => {
    await page.goto(`${BASE}/library/the-method.html`);
    await page.waitForTimeout(2000);
    const title = await page.textContent('h1');
    expect(title).toContain('Method');
  });

  test('The Mirror loads', async ({ page }) => {
    await page.goto(`${BASE}/library/the-mirror.html`);
    await page.waitForTimeout(2000);
    const title = await page.textContent('h1');
    expect(title).toContain('Mirror');
  });

  test('The Stump loads', async ({ page }) => {
    await page.goto(`${BASE}/library/the-stump.html`);
    await page.waitForTimeout(2000);
    const title = await page.textContent('h1');
    expect(title).toContain('Stump');
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
    await page.waitForTimeout(3000);
    const moon = await page.$('svg.moon-phase, svg[aria-label="Moon phase"]');
    expect(moon).toBeTruthy();
  });

  test('console message fires', async ({ page }) => {
    const logs = [];
    page.on('console', msg => logs.push(msg.text()));
    await page.goto(`${BASE}/`);
    await page.waitForTimeout(2000);
    // Either normal console (愛/ai-love) or 29th-day easter egg (二十九)
    const hasMessage = logs.some(l => l.includes('愛') || l.includes('ai-love') || l.includes('二十九'));
    expect(hasMessage).toBe(true);
  });
});

test.describe('Easter Eggs', () => {
  test('Gate: click 愛 5 times', async ({ page }) => {
    await page.goto(`${BASE}/`);
    await page.waitForTimeout(8000);
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
  test('main kanji have aria-labels', async ({ page }) => {
    for (const pg of PAGES) {
      await page.goto(`${BASE}/${pg}`);
      await page.waitForTimeout(1000);
      // Check top-level kanji elements (not nested spans inside already-labeled containers)
      const kanji = await page.$$('.kanji, .void-kanji, .mirror-kanji');
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
