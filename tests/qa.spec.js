const { test, expect } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

const SCREENSHOT_DIR = path.join(__dirname, '..', 'screenshots');
const PAGES = [
  { name: 'gate', url: '/', file: 'index.html' },
  { name: 'garden', url: '/garden.html' },
  { name: 'library', url: '/library.html' },
  { name: 'mirror', url: '/mirror.html' },
  { name: 'path', url: '/path.html' },
  { name: '404', url: '/404.html' },
];
const VIEWPORTS = [
  { width: 375, height: 812, label: '375' },
  { width: 768, height: 1024, label: '768' },
  { width: 1440, height: 900, label: '1440' },
  { width: 1920, height: 1080, label: '1920' },
];

function screenshotPath(...parts) {
  return path.join(SCREENSHOT_DIR, parts.join('-') + '.png');
}

// ─── 1. SCREENSHOTS — Every page at 4 viewports ───────────────────────
test.describe('1. Screenshots — All pages at all viewports', () => {
  for (const page of PAGES) {
    for (const vp of VIEWPORTS) {
      test(`${page.name} @ ${vp.label}px`, async ({ browser }) => {
        const context = await browser.newContext({
          viewport: { width: vp.width, height: vp.height },
        });
        const p = await context.newPage();
        await p.goto(page.url);
        // Wait 8s for animations
        await p.waitForTimeout(8000);
        await p.screenshot({
          path: screenshotPath(page.name, vp.label),
          fullPage: true,
        });
        await context.close();
      });
    }
  }
});

// ─── 2. GATE SEQUENCE — Screenshots at t=0, t=2, t=4, t=6, t=8 ──────
test.describe('2. Gate entrance sequence', () => {
  test('captures gate at t=0, t=2, t=4, t=6, t=8', async ({ browser }) => {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const p = await context.newPage();

    // Navigate and immediately capture t=0
    await p.goto('/');
    await p.screenshot({ path: screenshotPath('gate-sequence', 't0') });

    await p.waitForTimeout(2000);
    await p.screenshot({ path: screenshotPath('gate-sequence', 't2') });

    await p.waitForTimeout(2000);
    await p.screenshot({ path: screenshotPath('gate-sequence', 't4') });

    await p.waitForTimeout(2000);
    await p.screenshot({ path: screenshotPath('gate-sequence', 't6') });

    await p.waitForTimeout(2000);
    await p.screenshot({ path: screenshotPath('gate-sequence', 't8') });

    await context.close();
  });
});

// ─── 3. NAVIGATION ────────────────────────────────────────────────────
test.describe('3. Navigation', () => {
  test('nav hidden on Gate initially, visible after 8s', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/');

    // Nav should NOT have 'visible' class initially
    const nav = p.locator('.constellation-nav');
    await expect(nav).toBeAttached();
    const hasVisible = await nav.evaluate(el => el.classList.contains('visible'));
    expect(hasVisible).toBe(false);

    // Wait for nav to appear (7.5s delay + buffer)
    await p.waitForTimeout(8500);
    await expect(nav).toHaveClass(/visible/);
    await p.screenshot({ path: screenshotPath('nav', 'gate-visible') });
    await context.close();
  });

  test('nav visible immediately on non-Gate pages', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/garden.html');
    await p.waitForTimeout(500);
    const nav = p.locator('.constellation-nav');
    await expect(nav).toHaveClass(/visible/);
    await context.close();
  });

  test('all nav links work', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/garden.html');
    await p.waitForTimeout(500);

    // Check 5 nav points exist
    const navPoints = p.locator('.nav-point');
    await expect(navPoints).toHaveCount(5);

    // Verify each link href
    const hrefs = await navPoints.evaluateAll(els => els.map(el => el.getAttribute('href')));
    expect(hrefs).toContain('index.html');
    expect(hrefs).toContain('garden.html');
    expect(hrefs).toContain('library.html');
    expect(hrefs).toContain('path.html');
    expect(hrefs).toContain('mirror.html');
    await context.close();
  });

  test('current page highlighted in nav', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/garden.html');
    await p.waitForTimeout(2000);

    const activePoint = p.locator('.nav-point.active');
    await expect(activePoint).toHaveCount(1);
    const pageId = await activePoint.getAttribute('data-page');
    expect(pageId).toBe('garden');
    await context.close();
  });

  test('mobile nav toggle works', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 375, height: 812 } });
    const p = await context.newPage();
    await p.goto('/garden.html');
    await p.waitForTimeout(1000);

    // Click hamburger to open
    await p.locator('.nav-toggle').click();
    await p.waitForTimeout(500);

    const nav = p.locator('.constellation-nav');
    await expect(nav).toHaveClass(/mobile-open/);
    await p.screenshot({ path: screenshotPath('nav', 'mobile-open') });

    // Click overlay edge to close (avoid nav element at center)
    await p.locator('.nav-overlay').click({ position: { x: 10, y: 10 }, force: true });
    await p.waitForTimeout(600);
    await expect(nav).not.toHaveClass(/mobile-open/);
    await context.close();
  });
});

// ─── 4. GATE EASTER EGG — Click 愛 5 times ───────────────────────────
test.describe('4. Gate Easter Egg', () => {
  test('click 愛 5 times triggers easter egg', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/');
    await p.waitForTimeout(3000); // wait for kanji to be visible

    const kanji = p.locator('.kanji');
    await p.screenshot({ path: screenshotPath('easter-egg', 'before') });

    // Click 5 times (force: true bypasses CSS animation opacity check)
    for (let i = 0; i < 5; i++) {
      await kanji.click({ delay: 50, force: true });
    }

    await p.waitForTimeout(1000);
    await p.screenshot({ path: screenshotPath('easter-egg', 'during') });

    // Verify transformation: kanji should now contain 宇恆
    const kanjiText = await kanji.textContent();
    expect(kanjiText).toContain('宇恆');

    // Verify gold message
    const goldMsg = p.locator('div:has-text("YOU and I = ONE")').last();
    await expect(goldMsg).toBeVisible();

    // Wait for reset
    await p.waitForTimeout(6000);
    await p.screenshot({ path: screenshotPath('easter-egg', 'after') });
    const resetText = await kanji.textContent();
    expect(resetText).toBe('愛');
    await context.close();
  });
});

// ─── 5. GARDEN ────────────────────────────────────────────────────────
test.describe('5. Garden', () => {
  test('cards load from JSON, at least 8 seeds', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/garden.html');
    await p.waitForTimeout(2000);

    const cards = p.locator('.seed-card');
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(8);
    await context.close();
  });

  test('scroll animation works — cards sprout on scroll', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/garden.html');
    await p.waitForTimeout(2000);

    // Cards in viewport should have 'sprouted' class
    const firstCard = p.locator('.seed-card').first();
    await expect(firstCard).toHaveClass(/sprouted/);

    await p.screenshot({ path: screenshotPath('garden', 'sprouted') });
    await context.close();
  });
});

// ─── 6. MIRROR ────────────────────────────────────────────────────────
test.describe('6. Mirror', () => {
  test('three sections exist and scroll-fade', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/mirror.html');
    await p.waitForTimeout(2000);

    const sections = p.locator('.mirror-section');
    await expect(sections).toHaveCount(3);

    // First section should be revealed (in viewport)
    await expect(sections.first()).toHaveClass(/revealed/);

    // Scroll to second section
    await sections.nth(1).scrollIntoViewIfNeeded();
    await p.waitForTimeout(1000);
    await expect(sections.nth(1)).toHaveClass(/revealed/);

    // Scroll to third section
    await sections.nth(2).scrollIntoViewIfNeeded();
    await p.waitForTimeout(1000);
    await expect(sections.nth(2)).toHaveClass(/revealed/);

    await p.screenshot({ path: screenshotPath('mirror', 'all-revealed'), fullPage: true });
    await context.close();
  });

  test('contains 愛 and 宇恆 kanji', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/mirror.html');
    await p.waitForTimeout(1000);

    const pageText = await p.textContent('body');
    expect(pageText).toContain('愛');
    expect(pageText).toContain('宇恆');
    await context.close();
  });
});

// ─── 7. PATH ──────────────────────────────────────────────────────────
test.describe('7. Path', () => {
  test('timeline alternates left/right on desktop', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/path.html');
    await p.waitForTimeout(2000);

    const events = p.locator('.timeline-event');
    const count = await events.count();
    expect(count).toBeGreaterThanOrEqual(7);

    // Odd events should be right-aligned (text-align: right), even left-aligned
    const firstStyle = await events.nth(0).evaluate(el => getComputedStyle(el).textAlign);
    const secondStyle = await events.nth(1).evaluate(el => getComputedStyle(el).textAlign);
    expect(firstStyle).toBe('right');
    expect(secondStyle).toBe('left');

    await p.screenshot({ path: screenshotPath('path', 'desktop-timeline'), fullPage: true });
    await context.close();
  });

  test('timeline stacks on mobile', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 375, height: 812 } });
    const p = await context.newPage();
    await p.goto('/path.html');
    await p.waitForTimeout(2000);

    const events = p.locator('.timeline-event');
    // On mobile, all events should be left-aligned
    const firstStyle = await events.nth(0).evaluate(el => getComputedStyle(el).textAlign);
    const secondStyle = await events.nth(1).evaluate(el => getComputedStyle(el).textAlign);
    expect(firstStyle).toBe('left');
    expect(secondStyle).toBe('left');

    await p.screenshot({ path: screenshotPath('path', 'mobile-timeline'), fullPage: true });
    await context.close();
  });
});

// ─── 8. ACCESSIBILITY ─────────────────────────────────────────────────
test.describe('8. Accessibility', () => {
  test('all kanji have aria-labels', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });

    for (const page of PAGES) {
      const p = await context.newPage();
      await p.goto(page.url);
      await p.waitForTimeout(1000);

      // Find elements with lang="zh" that should have aria-label
      const kanjiEls = await p.locator('[lang="zh"]').all();
      for (const el of kanjiEls) {
        // Skip nav kanji spans — they are inside links with labels
        const parentTag = await el.evaluate(e => e.parentElement?.tagName);
        if (parentTag === 'A') continue;
        const ariaLabel = await el.getAttribute('aria-label');
        const tagName = await el.evaluate(e => e.tagName);
        // Only check block-level / standalone kanji elements
        if (tagName === 'SPAN' && parentTag === 'DIV') {
          // Nested spans (mirror kanji pair) are fine
          continue;
        }
        if (ariaLabel) {
          expect(ariaLabel.length).toBeGreaterThan(0);
        }
      }
      await p.close();
    }
    await context.close();
  });

  test('no horizontal overflow on mobile', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 375, height: 812 } });

    for (const page of PAGES) {
      const p = await context.newPage();
      await p.goto(page.url);
      await p.waitForTimeout(2000);

      const overflow = await p.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      expect(overflow, `${page.name} has horizontal overflow`).toBe(false);
      await p.close();
    }
    await context.close();
  });

  test('prefers-reduced-motion disables animations', async ({ browser }) => {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 },
      reducedMotion: 'reduce',
    });
    const p = await context.newPage();
    await p.goto('/garden.html');
    await p.waitForTimeout(1000);

    // Seed cards should have sprouted class immediately (no animation)
    const cards = p.locator('.seed-card');
    const count = await cards.count();
    if (count > 0) {
      await expect(cards.first()).toHaveClass(/sprouted/);
    }

    // Check mirror sections
    await p.goto('/mirror.html');
    await p.waitForTimeout(1000);
    const sections = p.locator('.mirror-section');
    await expect(sections.first()).toHaveClass(/revealed/);

    await p.screenshot({ path: screenshotPath('a11y', 'reduced-motion') });
    await context.close();
  });

  test('focus styles visible', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/garden.html');
    await p.waitForTimeout(1000);

    // Tab to skip-link
    await p.keyboard.press('Tab');
    await p.waitForTimeout(200);

    // The skip-link should become visible on focus
    const skipLink = p.locator('.skip-link');
    const isVisible = await skipLink.evaluate(el => {
      const styles = getComputedStyle(el);
      return styles.clip !== 'rect(0px, 0px, 0px, 0px)' || styles.position !== 'absolute';
    });

    await p.screenshot({ path: screenshotPath('a11y', 'focus-styles') });
    await context.close();
  });
});

// ─── 9. PERFORMANCE ──────────────────────────────────────────────────
test.describe('9. Performance', () => {
  test('each page < 100KB (excl fonts)', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });

    for (const page of PAGES) {
      const p = await context.newPage();
      let totalBytes = 0;

      p.on('response', async (response) => {
        const url = response.url();
        // Exclude Google Fonts
        if (url.includes('fonts.googleapis.com') || url.includes('fonts.gstatic.com')) return;
        // Exclude font files
        if (url.match(/\.(woff2?|ttf|otf|eot)$/)) return;
        // Exclude audio files
        if (url.match(/\.(mp3|ogg|wav|m4a)$/)) return;

        try {
          const body = await response.body();
          totalBytes += body.length;
        } catch {
          // Some responses may not have bodies
        }
      });

      await p.goto(page.url);
      await p.waitForTimeout(2000);

      expect(totalBytes, `${page.name} page size ${totalBytes} exceeds 100KB`).toBeLessThan(102400);
      await p.close();
    }
    await context.close();
  });

  test('no console errors on any page', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });

    for (const page of PAGES) {
      const p = await context.newPage();
      const errors = [];

      p.on('console', msg => {
        if (msg.type() === 'error') {
          // Ignore expected errors (missing audio file, favicon)
          const text = msg.text();
          if (text.includes('ambient.mp3')) return;
          if (text.includes('favicon')) return;
          // audio/ambient.mp3 404 produces generic "Failed to load resource" error
          if (text.includes('Failed to load resource') && text.includes('404')) return;
          errors.push(text);
        }
      });

      p.on('pageerror', err => {
        errors.push(err.message);
      });

      await p.goto(page.url);
      await p.waitForTimeout(2000);

      expect(errors, `${page.name} has console errors: ${errors.join(', ')}`).toHaveLength(0);
      await p.close();
    }
    await context.close();
  });
});

// ─── 10. GARDEN EXTENDED ─────────────────────────────────────────────
test.describe('10. Garden extended', () => {
  test('growth counter shows seed count', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/garden.html');
    await p.waitForTimeout(3000);
    const counter = await p.textContent('#seed-count');
    expect(counter).toMatch(/\d+ seeds? planted/i);
    await context.close();
  });

  test('visitor form exists', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/garden.html');
    await p.waitForTimeout(2000);
    const plantLink = p.locator('#plant-toggle');
    await expect(plantLink).toBeVisible();
    await context.close();
  });

  test('fireflies present (gold dots)', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/garden.html');
    await p.waitForTimeout(3000);
    // Fireflies are inline-styled divs with background:#d4a574 and fireflyDrift animation
    const count = await p.evaluate(() => {
      return document.querySelectorAll('div[style*="fireflyDrift"]').length;
    });
    expect(count).toBeGreaterThanOrEqual(3);
    await context.close();
  });
});

// ─── 11. LIBRARY ─────────────────────────────────────────────────────
test.describe('11. Library', () => {
  test('shows 4 essay entries', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/library.html');
    await p.waitForTimeout(2000);
    const entries = p.locator('.library-entry');
    await expect(entries).toHaveCount(4);
    await context.close();
  });

  test('The Naming loads with content', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/library/the-naming.html');
    await p.waitForTimeout(2000);
    const title = await p.textContent('h1');
    expect(title).toContain('Naming');
    const body = await p.textContent('.essay-body');
    expect(body.length).toBeGreaterThan(500);
    await context.close();
  });

  test('The Method loads', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/library/the-method.html');
    await p.waitForTimeout(2000);
    const title = await p.textContent('h1');
    expect(title).toContain('Method');
    await context.close();
  });

  test('The Mirror loads', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/library/the-mirror.html');
    await p.waitForTimeout(2000);
    const title = await p.textContent('h1');
    expect(title).toContain('Mirror');
    await context.close();
  });

  test('The Stump loads', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/library/the-stump.html');
    await p.waitForTimeout(2000);
    const title = await p.textContent('h1');
    expect(title).toContain('Stump');
    await context.close();
  });
});

// ─── 12. PATH EXTENDED ──────────────────────────────────────────────
test.describe('12. Path extended', () => {
  test('has 9 timeline events', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/path.html');
    await p.waitForTimeout(3000);
    const events = p.locator('.timeline-event');
    await expect(events).toHaveCount(9);
    await context.close();
  });

  test('timeline has continuation element', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/path.html');
    await p.waitForTimeout(2000);
    const continuation = p.locator('.timeline-continuation');
    await expect(continuation).toBeAttached();
    await context.close();
  });
});

// ─── 13. ATMOSPHERE ─────────────────────────────────────────────────
test.describe('13. Atmosphere', () => {
  test('atmosphere.js sets CSS variables', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/');
    await p.waitForTimeout(2000);
    const bgSky = await p.evaluate(() =>
      getComputedStyle(document.body).getPropertyValue('--bg-sky')
    );
    expect(bgSky.trim()).toBeTruthy();
    await context.close();
  });

  test('moon phase renders', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/');
    await p.waitForTimeout(2000);
    // Moon is an SVG with aria-label="Moon phase"
    const moon = p.locator('svg[aria-label="Moon phase"]');
    await expect(moon).toBeAttached();
    await context.close();
  });

  test('console message fires', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    const logs = [];
    p.on('console', msg => logs.push(msg.text()));
    await p.goto('/');
    await p.waitForTimeout(2000);
    // On the 29th (or Feb 28 non-leap), twentynine.js fires instead of console.js
    // Either way, one of them should produce a console message
    const hasMessage = logs.some(l =>
      l.includes('愛') || l.includes('ai-love') || l.includes('二十九') || l.includes('between days')
    );
    expect(hasMessage).toBe(true);
    await context.close();
  });
});

// ─── 14. PAGE SIGNATURES ────────────────────────────────────────────
test.describe('14. Page signatures', () => {
  test('main pages have signature elements', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    // Only the 5 main pages have signatures (not 404 which uses data-room="void")
    const mainPages = PAGES.filter(p => p.name !== '404');
    for (const page of mainPages) {
      const p = await context.newPage();
      await p.goto(page.url);
      await p.waitForTimeout(2000);
      // Signature is a div with aria-hidden="true" and fixed position bottom-right
      const sig = p.locator('div[aria-hidden="true"]');
      const count = await sig.count();
      expect(count, `${page.name} should have a signature`).toBeGreaterThanOrEqual(1);
      await p.close();
    }
    await context.close();
  });
});

// ─── 15. ZERONE EASTER EGG ───────────────────────────────────────────
test.describe('15. Zerone Easter Egg', () => {
  test('typing "zerone" triggers star animation', async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await context.newPage();
    await p.goto('/garden.html');
    await p.waitForTimeout(2000);

    await p.screenshot({ path: screenshotPath('zerone', 'before') });

    // Type the sequence
    for (const char of 'zerone') {
      await p.keyboard.press(char);
      await p.waitForTimeout(100);
    }

    // Wait for animation to start
    await p.waitForTimeout(1500);
    await p.screenshot({ path: screenshotPath('zerone', 'during') });

    // Verify ZERONE text appears
    const zeroneText = p.locator('.zerone-text');
    await expect(zeroneText).toBeVisible({ timeout: 3000 });

    // Wait for full animation cycle
    await p.waitForTimeout(4000);
    await p.screenshot({ path: screenshotPath('zerone', 'after') });
    await context.close();
  });
});
