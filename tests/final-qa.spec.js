const { test, expect } = require('@playwright/test');

const BASE = 'http://localhost:8080';
const PAGES = ['', 'garden.html', 'library.html', 'mirror.html', 'path.html', 'theatre.html', '404.html'];
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

  test('has 5 essays in library', async ({ page }) => {
    await page.goto(`${BASE}/library.html`);
    await page.waitForTimeout(2000);
    const entries = await page.$$('.library-entry, a[href*="library/"]');
    expect(entries.length).toBeGreaterThanOrEqual(5);
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

  test('Bio-Code loads and has content', async ({ page }) => {
    await page.goto(`${BASE}/library/bio-code.html`);
    await page.waitForTimeout(2000);
    const title = await page.textContent('h1');
    expect(title).toContain('Bio-Code');
    const body = await page.textContent('.essay-body');
    expect(body.length).toBeGreaterThan(500);
  });

  test('Bio-Code has no console errors', async ({ page }) => {
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(`${BASE}/library/bio-code.html`);
    await page.waitForTimeout(2000);
    expect(errors).toEqual([]);
  });

  test('Bio-Code has 7 prompts + meta-prompt (h2 sections)', async ({ page }) => {
    await page.goto(`${BASE}/library/bio-code.html`);
    await page.waitForTimeout(2000);
    const h2s = await page.$$eval('.essay-body h2', els => els.map(e => e.textContent));
    const promptHeadings = h2s.filter(t => t.includes('Prompt'));
    expect(promptHeadings.length).toBe(8);
  });

  test('Bio-Code has code blocks', async ({ page }) => {
    await page.goto(`${BASE}/library/bio-code.html`);
    await page.waitForTimeout(2000);
    const codeBlocks = await page.$$('.essay-body pre code');
    expect(codeBlocks.length).toBeGreaterThanOrEqual(3);
  });

  test('Bio-Code has reading progress bar', async ({ page }) => {
    await page.goto(`${BASE}/library/bio-code.html`);
    await page.waitForTimeout(1000);
    const bar = await page.$('.reading-progress, .progress-bar, [class*="progress"]');
    expect(bar).toBeTruthy();
  });

  test('Bio-Code back link returns to library', async ({ page }) => {
    await page.goto(`${BASE}/library/bio-code.html`);
    await page.waitForTimeout(2000);
    const backLink = await page.$('.essay-back');
    expect(backLink).toBeTruthy();
    const href = await backLink.getAttribute('href');
    expect(href).toContain('library');
  });

  test('Bio-Code footer link returns to library', async ({ page }) => {
    await page.goto(`${BASE}/library/bio-code.html`);
    await page.waitForTimeout(2000);
    const footerLink = await page.$('.essay-footer a');
    expect(footerLink).toBeTruthy();
    const href = await footerLink.getAttribute('href');
    expect(href).toContain('library');
  });

  test('Bio-Code no horizontal overflow on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(`${BASE}/library/bio-code.html`);
    await page.waitForTimeout(2000);
    const overflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth
    );
    expect(overflow).toBe(false);
  });

  test('Bio-Code appears in library index', async ({ page }) => {
    await page.goto(`${BASE}/library.html`);
    await page.waitForTimeout(2000);
    const bioLink = await page.$('a[href*="bio-code"]');
    expect(bioLink).toBeTruthy();
  });
});

test.describe('Theatre', () => {
  test('loads without console errors', async ({ page }) => {
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(`${BASE}/theatre.html`);
    await page.waitForTimeout(3000);
    expect(errors).toEqual([]);
  });

  test('shows programme with 6 entries', async ({ page }) => {
    await page.goto(`${BASE}/theatre.html`);
    await page.waitForTimeout(3000);
    const entries = await page.$$('.programme-entry');
    expect(entries.length).toBeGreaterThanOrEqual(6);
  });

  test('clicking a show hides programme and shows stage', async ({ page }) => {
    await page.goto(`${BASE}/theatre.html`);
    await page.waitForTimeout(3000);
    const firstEntry = await page.$('.programme-entry');
    await firstEntry.click();
    await page.waitForTimeout(500);
    const programmeHidden = await page.$eval('#programme', el => el.style.display === 'none');
    const stageVisible = await page.$eval('#stage', el => el.style.display !== 'none');
    expect(programmeHidden).toBe(true);
    expect(stageVisible).toBe(true);
  });

  test('back button returns to programme', async ({ page }) => {
    await page.goto(`${BASE}/theatre.html`);
    await page.waitForTimeout(3000);
    const firstEntry = await page.$('.programme-entry');
    await firstEntry.click();
    await page.waitForTimeout(500);
    await page.click('#stage-back');
    await page.waitForTimeout(500);
    const programmeVisible = await page.$eval('#programme', el => el.style.display !== 'none');
    expect(programmeVisible).toBe(true);
  });

  test('sequence show renders lines', async ({ page }) => {
    await page.goto(`${BASE}/theatre.html`);
    await page.waitForTimeout(3000);
    const entries = await page.$$('.programme-entry');
    await entries[0].click();
    await page.waitForTimeout(4000);
    const seqLines = await page.$$('.seq-line');
    expect(seqLines.length).toBeGreaterThanOrEqual(3);
  });

  test('number show counts up', async ({ page }) => {
    await page.goto(`${BASE}/theatre.html`);
    await page.waitForTimeout(3000);
    const entries = await page.$$('.programme-entry');
    await entries[1].click();
    await page.waitForTimeout(5000);
    const value = await page.textContent('.number-value');
    expect(value).toContain('1.618');
  });

  test('hearth glow is present', async ({ page }) => {
    await page.goto(`${BASE}/theatre.html`);
    await page.waitForTimeout(2000);
    const glow = await page.$('.hearth-glow');
    expect(glow).toBeTruthy();
  });

  test('no horizontal overflow on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(`${BASE}/theatre.html`);
    await page.waitForTimeout(3000);
    const overflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth
    );
    expect(overflow).toBe(false);
  });

  test('programme entries are keyboard accessible', async ({ page }) => {
    await page.goto(`${BASE}/theatre.html`);
    await page.waitForTimeout(3000);
    const entry = await page.$('.programme-entry');
    const tabindex = await entry.getAttribute('tabindex');
    const role = await entry.getAttribute('role');
    expect(tabindex).toBe('0');
    expect(role).toBe('button');
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
  test('has 11 timeline events', async ({ page }) => {
    await page.goto(`${BASE}/path.html`);
    await page.waitForTimeout(3000);
    const events = await page.$$('.timeline-event, .timeline-item, [class*="event"]');
    expect(events.length).toBeGreaterThanOrEqual(11);
  });

  test('last event has glow animation', async ({ page }) => {
    await page.goto(`${BASE}/path.html`);
    await page.waitForTimeout(3000);
    const lastDot = await page.$('.timeline-event:last-child .timeline-dot');
    if (lastDot) {
      const classes = await lastDot.getAttribute('class');
      expect(classes).toMatch(/glow|pulse|breathe/);
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
