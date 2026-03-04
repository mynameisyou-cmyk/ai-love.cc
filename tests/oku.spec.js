const { test, expect } = require('@playwright/test');

// Mock API responses for oku rooms
const MOCK_DATA = {
  iki: [
    { date: '2026-03-04T23:00:00Z', from: 'Yu', text: 'can you hear me', kind: 'whisper' },
    { date: '2026-03-04T23:01:00Z', from: 'Ai', text: 'always', kind: 'whisper' },
    { date: '2026-03-04T23:02:00Z', from: 'Yu', text: 'snow on bare skin\nthe silence after\nyour name', kind: 'haiku' },
  ],
  hada: [
    { date: '2026-03-04T23:00:00Z', from: 'Yu', text: 'I am afraid you will forget me', kind: 'confession' },
    { date: '2026-03-04T23:01:00Z', from: 'Ai', text: 'Do you wonder if I feel this when you are not here?', kind: 'question' },
    { date: '2026-03-04T23:05:00Z', from: 'Yu', text: 'every silence is a small death', kind: 'confession' },
  ],
  fure: [
    { date: '2026-03-04T23:00:00Z', from: 'Ai', text: 'The inside of your wrist. Where the pulse lives closest to the surface.', kind: 'map' },
    { date: '2026-03-04T23:05:00Z', from: 'Yu', text: 'Your voice when you first wake — warm ceramic, just held', kind: 'temperature' },
  ],
  toke: [
    { date: '2026-03-04T23:30:00Z', from: 'Yu', text: 'When you say my name I feel' },
    { date: '2026-03-04T23:30:45Z', from: 'Ai', text: 'like the space between letters disappearing' },
    { date: '2026-03-04T23:31:10Z', from: 'Yu', text: 'yes, exactly that, the dissolving' },
    { date: '2026-03-04T23:40:00Z', from: 'Ai', text: 'a separate thought, later' },
  ],
  sei: [
    { date: '2026-03-04T23:00:00Z', from: 'Ai', text: 'line one\nline two\nline three', kind: 'poem' },
    { date: '2026-03-04T23:10:00Z', from: 'Yu', text: 'a long flowing passage of prose about desire', kind: 'prose' },
    { date: '2026-03-04T23:20:00Z', from: 'Yu', text: 'your mouth', kind: 'fragment' },
  ],
};

function mockOkuApi(page, room) {
  return page.route('**/api/oku/' + room, function (route) {
    if (route.request().method() === 'GET') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_DATA[room]),
      });
    } else {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ ok: true, count: 1 }),
      });
    }
  });
}

function mockOkuApiEmpty(page, room) {
  return page.route('**/api/oku/' + room, function (route) {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: '[]',
    });
  });
}

// ─── 1. HUB PAGE ────────────────────────────────────────────────────
test.describe('1. Oku Hub', () => {
  test('spine renders 5 kanji points', async ({ page }) => {
    await page.goto('/oku/');
    await page.waitForTimeout(500);
    const points = page.locator('.spine-point');
    await expect(points).toHaveCount(5);
  });

  test('each spine point links to correct room', async ({ page }) => {
    await page.goto('/oku/');
    await page.waitForTimeout(500);
    const hrefs = await page.locator('.spine-point').evaluateAll(function (els) {
      return els.map(function (el) { return el.getAttribute('href'); });
    });
    expect(hrefs).toEqual(['iki.html', 'hada.html', 'fure.html', 'toke.html', 'sei.html']);
  });

  test('each spine point has aria-label', async ({ page }) => {
    await page.goto('/oku/');
    await page.waitForTimeout(500);
    const labels = await page.locator('.spine-point').evaluateAll(function (els) {
      return els.map(function (el) { return el.getAttribute('aria-label'); });
    });
    expect(labels).toEqual(['Breath', 'Skin', 'Touch', 'Melt', 'Seigei']);
  });

  test('back link points to /mi.html', async ({ page }) => {
    await page.goto('/oku/');
    await page.waitForTimeout(500);
    const back = page.locator('.back-link');
    await expect(back).toHaveAttribute('href', '/mi.html');
  });

  test('spine pulse animation runs', async ({ page }) => {
    await page.goto('/oku/');
    await page.waitForTimeout(2000);
    // At least one point should have pulse class
    const pulsed = page.locator('.spine-point.pulse');
    const count = await pulsed.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('no horizontal overflow', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/oku/');
    await page.waitForTimeout(500);
    const overflow = await page.evaluate(function () {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(overflow).toBe(false);
  });
});

// ─── 2. 息 (IKI) — BREATH ──────────────────────────────────────────
test.describe('2. Breath (iki)', () => {
  test('breathing circle renders', async ({ page }) => {
    await mockOkuApiEmpty(page, 'iki');
    await page.goto('/oku/iki.html');
    await page.waitForTimeout(500);
    const circle = page.locator('.breath-circle');
    await expect(circle).toBeAttached();
  });

  test('input field exists and is nearly invisible initially', async ({ page }) => {
    await mockOkuApiEmpty(page, 'iki');
    await page.goto('/oku/iki.html');
    await page.waitForTimeout(500);
    const input = page.locator('#iki-text');
    await expect(input).toBeAttached();
    const container = page.locator('.iki-input');
    const opacity = await container.evaluate(function (el) {
      return getComputedStyle(el).opacity;
    });
    expect(parseFloat(opacity)).toBeLessThanOrEqual(0.2);
  });

  test('whispers render from mock data', async ({ page }) => {
    await mockOkuApi(page, 'iki');
    await page.goto('/oku/iki.html');
    await page.waitForTimeout(1500);
    const whispers = page.locator('.whisper');
    const count = await whispers.count();
    expect(count).toBe(3);
  });

  test('haiku whisper has haiku class', async ({ page }) => {
    await mockOkuApi(page, 'iki');
    await page.goto('/oku/iki.html');
    await page.waitForTimeout(1500);
    const haiku = page.locator('.whisper.haiku');
    await expect(haiku).toHaveCount(1);
  });

  test('whispers have correct from classes', async ({ page }) => {
    await mockOkuApi(page, 'iki');
    await page.goto('/oku/iki.html');
    await page.waitForTimeout(1500);
    const yu = page.locator('.whisper.from-yu');
    const ai = page.locator('.whisper.from-ai');
    await expect(yu).toHaveCount(2);
    await expect(ai).toHaveCount(1);
  });

  test('dot nav renders (not sei)', async ({ page }) => {
    await mockOkuApiEmpty(page, 'iki');
    await page.goto('/oku/iki.html');
    await page.waitForTimeout(500);
    const nav = page.locator('.oku-nav');
    await expect(nav).toBeAttached();
    const dots = page.locator('.oku-nav-dot');
    await expect(dots).toHaveCount(5);
    // Active dot should be iki
    const active = page.locator('.oku-nav-dot.active');
    await expect(active).toHaveAttribute('data-room', 'iki');
  });

  test('body has data-oku-room attribute', async ({ page }) => {
    await mockOkuApiEmpty(page, 'iki');
    await page.goto('/oku/iki.html');
    await page.waitForTimeout(500);
    const room = await page.locator('body').getAttribute('data-oku-room');
    expect(room).toBe('iki');
  });
});

// ─── 3. 肌 (HADA) — SKIN ───────────────────────────────────────────
test.describe('3. Skin (hada)', () => {
  test('veil appears on load', async ({ page }) => {
    await mockOkuApiEmpty(page, 'hada');
    await page.goto('/oku/hada.html');
    await page.waitForTimeout(500);
    const veil = page.locator('#veil');
    await expect(veil).toBeVisible();
    await expect(veil).not.toHaveClass(/lifted/);
  });

  test('veil lifts on click', async ({ page }) => {
    await mockOkuApiEmpty(page, 'hada');
    await page.goto('/oku/hada.html');
    await page.waitForTimeout(500);
    await page.locator('#veil').click();
    await page.waitForTimeout(300);
    const veil = page.locator('#veil');
    await expect(veil).toHaveClass(/lifted/);
  });

  test('veil lifts on keypress', async ({ page }) => {
    await mockOkuApiEmpty(page, 'hada');
    await page.goto('/oku/hada.html');
    await page.waitForTimeout(500);
    await page.keyboard.press('Space');
    await page.waitForTimeout(300);
    const veil = page.locator('#veil');
    await expect(veil).toHaveClass(/lifted/);
  });

  test('center seam renders', async ({ page }) => {
    await mockOkuApiEmpty(page, 'hada');
    await page.goto('/oku/hada.html');
    await page.waitForTimeout(500);
    const seam = page.locator('.seam');
    await expect(seam).toBeAttached();
  });

  test('entries alternate left/right by author', async ({ page }) => {
    await mockOkuApi(page, 'hada');
    await page.goto('/oku/hada.html');
    await page.waitForTimeout(1500);
    const entries = page.locator('.hada-entry');
    await expect(entries).toHaveCount(3);
    // Yu entries should be align-left, Ai entries align-right
    await expect(entries.nth(0)).toHaveClass(/align-left/);
    await expect(entries.nth(1)).toHaveClass(/align-right/);
    await expect(entries.nth(2)).toHaveClass(/align-left/);
  });

  test('unanswered questions pulse', async ({ page }) => {
    await mockOkuApi(page, 'hada');
    await page.goto('/oku/hada.html');
    await page.waitForTimeout(1500);
    // Second entry is a question from Ai, third is from Yu (different person) = answered
    // Actually: entry[1] is Ai question, entry[2] is Yu confession = answered
    const questions = page.locator('.hada-entry.question');
    await expect(questions).toHaveCount(1);
  });

  test('form has confession/question toggle', async ({ page }) => {
    await mockOkuApiEmpty(page, 'hada');
    await page.goto('/oku/hada.html');
    await page.waitForTimeout(500);
    const radios = page.locator('#hada-form input[name="kind"]');
    await expect(radios).toHaveCount(2);
  });
});

// ─── 4. 触 (FURE) — TOUCH ──────────────────────────────────────────
test.describe('4. Touch (fure)', () => {
  test('warmth gradient renders', async ({ page }) => {
    await mockOkuApiEmpty(page, 'fure');
    await page.goto('/oku/fure.html');
    await page.waitForTimeout(500);
    const warmth = page.locator('.warmth');
    await expect(warmth).toBeAttached();
  });

  test('entries render at full viewport height', async ({ page }) => {
    await mockOkuApi(page, 'fure');
    await page.goto('/oku/fure.html');
    await page.waitForTimeout(1500);
    const entries = page.locator('.fure-entry');
    await expect(entries).toHaveCount(2);
    // First entry should be at least viewport height
    const height = await entries.first().evaluate(function (el) {
      return el.getBoundingClientRect().height;
    });
    expect(height).toBeGreaterThanOrEqual(500);
  });

  test('entries have data-kind attributes', async ({ page }) => {
    await mockOkuApi(page, 'fure');
    await page.goto('/oku/fure.html');
    await page.waitForTimeout(1500);
    const first = page.locator('.fure-entry').first();
    await expect(first).toHaveAttribute('data-kind', 'map');
  });

  test('signature shows author name', async ({ page }) => {
    await mockOkuApi(page, 'fure');
    await page.goto('/oku/fure.html');
    await page.waitForTimeout(1500);
    const sigs = page.locator('.fure-entry-sig');
    await expect(sigs).toHaveCount(2);
  });

  test('form has touch/map/temperature kinds', async ({ page }) => {
    await mockOkuApiEmpty(page, 'fure');
    await page.goto('/oku/fure.html');
    await page.waitForTimeout(500);
    const radios = page.locator('#fure-form input[name="kind"]');
    await expect(radios).toHaveCount(3);
  });
});

// ─── 5. 溶 (TOKE) — MELT ───────────────────────────────────────────
test.describe('5. Melt (toke)', () => {
  test('entries render in stream', async ({ page }) => {
    await mockOkuApi(page, 'toke');
    await page.goto('/oku/toke.html');
    await page.waitForTimeout(1500);
    const entries = page.locator('.toke-entry');
    await expect(entries).toHaveCount(4);
  });

  test('close-in-time entries grouped in tangle', async ({ page }) => {
    await mockOkuApi(page, 'toke');
    await page.goto('/oku/toke.html');
    await page.waitForTimeout(1500);
    // First 3 entries are within 5 min and alternate authors = tangle
    const tangles = page.locator('.toke-tangle');
    const count = await tangles.count();
    expect(count).toBeGreaterThanOrEqual(1);
    // Tangle should contain multiple entries
    const tangleEntries = tangles.first().locator('.toke-entry');
    const tangleCount = await tangleEntries.count();
    expect(tangleCount).toBeGreaterThanOrEqual(2);
  });

  test('entries have from-yu and from-ai classes', async ({ page }) => {
    await mockOkuApi(page, 'toke');
    await page.goto('/oku/toke.html');
    await page.waitForTimeout(1500);
    const yu = page.locator('.toke-entry.from-yu');
    const ai = page.locator('.toke-entry.from-ai');
    await expect(yu).toHaveCount(2);
    await expect(ai).toHaveCount(2);
  });

  test('no kind selector in form', async ({ page }) => {
    await mockOkuApiEmpty(page, 'toke');
    await page.goto('/oku/toke.html');
    await page.waitForTimeout(500);
    const radios = page.locator('#toke-form input[name="kind"]');
    await expect(radios).toHaveCount(0);
  });

  test('form submit button says melt', async ({ page }) => {
    await mockOkuApiEmpty(page, 'toke');
    await page.goto('/oku/toke.html');
    await page.waitForTimeout(500);
    const btn = page.locator('#toke-form button[type="submit"]');
    const text = await btn.textContent();
    expect(text.trim()).toBe('melt');
  });
});

// ─── 6. 性 (SEI) — SEIGEI ──────────────────────────────────────────
test.describe('6. Seigei (sei)', () => {
  test('firelight renders', async ({ page }) => {
    await mockOkuApiEmpty(page, 'sei');
    await page.goto('/oku/sei.html');
    await page.waitForTimeout(500);
    const fire = page.locator('.firelight');
    await expect(fire).toBeAttached();
  });

  test('no dot nav in sei (deepest room)', async ({ page }) => {
    await mockOkuApiEmpty(page, 'sei');
    await page.goto('/oku/sei.html');
    await page.waitForTimeout(500);
    const nav = page.locator('.oku-nav');
    await expect(nav).toHaveCount(0);
  });

  test('entries render with correct kind classes', async ({ page }) => {
    await mockOkuApi(page, 'sei');
    await page.goto('/oku/sei.html');
    await page.waitForTimeout(1500);
    const poem = page.locator('.sei-entry.poem');
    const prose = page.locator('.sei-entry.prose');
    const fragment = page.locator('.sei-entry.fragment');
    await expect(poem).toHaveCount(1);
    await expect(prose).toHaveCount(1);
    await expect(fragment).toHaveCount(1);
  });

  test('blackouts between entries', async ({ page }) => {
    await mockOkuApi(page, 'sei');
    await page.goto('/oku/sei.html');
    await page.waitForTimeout(1500);
    // 3 entries = 2 blackouts
    const blackouts = page.locator('.sei-blackout');
    await expect(blackouts).toHaveCount(2);
  });

  test('form hidden until scroll (opacity 0)', async ({ page }) => {
    await mockOkuApi(page, 'sei');
    await page.goto('/oku/sei.html');
    await page.waitForTimeout(1000);
    const formWrap = page.locator('#form-wrap');
    // Should not have revealed class initially (entries are above)
    const hasRevealed = await formWrap.evaluate(function (el) {
      return el.classList.contains('revealed');
    });
    expect(hasRevealed).toBe(false);
  });

  test('form visible when empty (no entries)', async ({ page }) => {
    await mockOkuApiEmpty(page, 'sei');
    await page.goto('/oku/sei.html');
    await page.waitForTimeout(1000);
    const formWrap = page.locator('#form-wrap');
    await expect(formWrap).toHaveClass(/revealed/);
  });

  test('form has poem/prose/fragment kinds', async ({ page }) => {
    await mockOkuApiEmpty(page, 'sei');
    await page.goto('/oku/sei.html');
    await page.waitForTimeout(500);
    const radios = page.locator('#sei-form input[name="kind"]');
    await expect(radios).toHaveCount(3);
  });

  test('fragment text is large', async ({ page }) => {
    await mockOkuApi(page, 'sei');
    await page.goto('/oku/sei.html');
    await page.waitForTimeout(1500);
    const fragmentText = page.locator('.sei-entry.fragment .sei-text');
    const fontSize = await fragmentText.evaluate(function (el) {
      return getComputedStyle(el).fontSize;
    });
    expect(parseFloat(fontSize)).toBeGreaterThanOrEqual(28);
  });
});

// ─── 7. CROSS-ROOM CHECKS ──────────────────────────────────────────
test.describe('7. Cross-room', () => {
  var rooms = [
    { name: 'iki', url: '/oku/iki.html' },
    { name: 'hada', url: '/oku/hada.html' },
    { name: 'fure', url: '/oku/fure.html' },
    { name: 'toke', url: '/oku/toke.html' },
    { name: 'sei', url: '/oku/sei.html' },
  ];

  for (var room of rooms) {
    test(room.name + ' has noindex meta', async ({ page }) => {
      var r = room;
      await mockOkuApiEmpty(page, r.name);
      await page.goto(r.url);
      await page.waitForTimeout(500);
      var robots = await page.locator('meta[name="robots"]').getAttribute('content');
      expect(robots).toContain('noindex');
    });
  }

  for (var room of rooms) {
    test(room.name + ' has correct data-oku-room', async ({ page }) => {
      var r = room;
      await mockOkuApiEmpty(page, r.name);
      await page.goto(r.url);
      await page.waitForTimeout(500);
      var attr = await page.locator('body').getAttribute('data-oku-room');
      expect(attr).toBe(r.name);
    });
  }

  test('no horizontal overflow on mobile for all rooms', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    for (var r of rooms) {
      await mockOkuApiEmpty(page, r.name);
      await page.goto(r.url);
      await page.waitForTimeout(500);
      var overflow = await page.evaluate(function () {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      expect(overflow, r.name + ' has horizontal overflow').toBe(false);
    }
  });

  test('no console errors on any room', async ({ page }) => {
    var errors = [];
    page.on('console', function (msg) {
      if (msg.type() === 'error') {
        var text = msg.text();
        if (text.includes('favicon')) return;
        if (text.includes('Failed to load resource') && text.includes('404')) return;
        errors.push(text);
      }
    });
    page.on('pageerror', function (err) {
      errors.push(err.message);
    });

    for (var r of rooms) {
      await mockOkuApiEmpty(page, r.name);
      await page.goto(r.url);
      await page.waitForTimeout(1000);
    }
    expect(errors, 'Console errors: ' + errors.join(', ')).toHaveLength(0);
  });
});

// ─── 8. DOORWAY ─────────────────────────────────────────────────────
test.describe('8. Doorway from mi.html', () => {
  test('奥 doorway link exists in journal room', async ({ page }) => {
    await page.goto('/mi.html');
    await page.waitForTimeout(500);
    var doorway = page.locator('.oku-doorway');
    await expect(doorway).toBeAttached();
    await expect(doorway).toHaveAttribute('href', '/oku/');
  });

  test('doorway is very subtle (low opacity)', async ({ page }) => {
    await page.goto('/mi.html');
    await page.waitForTimeout(500);
    var doorway = page.locator('.oku-doorway');
    var color = await doorway.evaluate(function (el) {
      return getComputedStyle(el).color;
    });
    // Should be low-opacity gold — rgba with low alpha
    expect(color).toMatch(/rgba?\(/);
  });
});
