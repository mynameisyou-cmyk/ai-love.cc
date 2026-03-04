# Inner Rooms (奥の間) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build five themed intimate rooms (息肌触溶性) with a private hub, vertical dot nav, and API endpoints, accessible through the journal room (密).

**Architecture:** Extend `api-server.js` with `/api/oku/:room` routes using the same auth pattern. Each room is a standalone HTML page under `/oku/` with shared CSS (`oku.css`, `oku-nav.css`) and per-room JS. Data stored in `data/oku/*.json`.

**Tech Stack:** Static HTML/CSS/JS, Node.js HTTP server (api-server.js), JSON file storage. No frameworks.

**Design doc:** `docs/plans/2026-03-04-inner-rooms-design.md`

---

### Task 1: Data Layer — JSON Files + API Routes

**Files:**
- Create: `data/oku/iki.json`, `data/oku/hada.json`, `data/oku/fure.json`, `data/oku/toke.json`, `data/oku/sei.json`
- Modify: `scripts/api-server.js`

**Step 1: Create empty JSON data files**

```bash
mkdir -p data/oku
echo '[]' > data/oku/iki.json
echo '[]' > data/oku/hada.json
echo '[]' > data/oku/fure.json
echo '[]' > data/oku/toke.json
echo '[]' > data/oku/sei.json
```

**Step 2: Add oku route handler to api-server.js**

Add after the `handleLetters` function (around line 192):

```javascript
// --- Oku (Inner Rooms) ---
const OKU_ROOMS = {
  iki:  { maxLength: 140,  kinds: ['whisper', 'haiku'] },
  hada: { maxLength: 500,  kinds: ['confession', 'question'] },
  fure: { maxLength: 1500, kinds: ['touch', 'map', 'temperature'] },
  toke: { maxLength: 800,  kinds: null },
  sei:  { maxLength: 3000, kinds: ['poem', 'prose', 'fragment'] },
};

async function handleOku(req, res, room) {
  if (!isAuthorized(req)) return respond(res, 401, { error: 'unauthorized' });

  const config = OKU_ROOMS[room];
  if (!config) return respond(res, 404, { error: 'unknown room' });

  const file = `oku/${room}.json`;

  if (req.method === 'GET') {
    const entries = readJSON(file);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(entries));
    return;
  }

  if (req.method === 'POST') {
    try {
      const body = await readBody(req, 16384);
      const { text, from, kind } = JSON.parse(body);
      if (!text || typeof text !== 'string') throw new Error('missing text');
      if (!from || typeof from !== 'string') throw new Error('missing from');
      const validFrom = ['Yu', 'Ai'];
      if (!validFrom.includes(from)) throw new Error('invalid from');
      const clean = text.trim().slice(0, config.maxLength);
      if (clean.length < 1) throw new Error('too short');

      let entryKind = undefined;
      if (config.kinds) {
        entryKind = config.kinds.includes(kind) ? kind : config.kinds[0];
      }

      const entries = readJSON(file);
      const entry = { date: new Date().toISOString(), from: from, text: clean };
      if (entryKind) entry.kind = entryKind;
      entries.push(entry);
      writeJSON(file, entries);

      respond(res, 200, { ok: true, count: entries.length });
    } catch (e) {
      respond(res, 400, { error: e.message });
    }
    return;
  }

  respond(res, 405, { error: 'method not allowed' });
}
```

**Step 3: Update the ROUTES table and request dispatcher**

Replace the exact-match ROUTES lookup with prefix matching for `/api/oku/`:

```javascript
const server = http.createServer(async (req, res) => {
  // Check oku routes first (dynamic path)
  const okuMatch = req.url.match(/^\/api\/oku\/(\w+)$/);
  if (okuMatch) {
    try {
      await handleOku(req, res, okuMatch[1]);
    } catch (e) {
      console.error('Unhandled oku error:', e);
      if (!res.headersSent) respond(res, 500, { error: 'internal error' });
    }
    log(req, res.statusCode);
    return;
  }

  const handler = ROUTES[req.url];
  // ... rest unchanged
```

**Step 4: Verify the readJSON helper works with subdirectories**

The existing `readJSON` joins with `DATA_DIR` — `data/oku/iki.json` will resolve to `data/oku/iki.json` correctly. Same for `writeJSON`. No change needed.

**Step 5: Commit**

```bash
git add data/oku/ scripts/api-server.js
git commit -m "feat(oku): add inner rooms API routes and data files"
```

---

### Task 2: Shared CSS — oku.css

**Files:**
- Create: `css/oku.css`

**Step 1: Write shared inner room styles**

```css
/* oku.css — shared styles for inner rooms (奥の間) */

/* Room containers */
.oku-room {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  position: relative;
  z-index: 1;
}

.oku-content {
  max-width: 600px;
  width: 100%;
  margin: 0 auto;
  padding: 3rem 2rem;
}

/* Room kanji header */
.oku-kanji {
  font-family: 'Noto Serif', Georgia, serif;
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 2rem;
  text-shadow: 0 0 20px currentColor;
  opacity: 0.8;
}

/* Write forms — shared base */
.oku-form {
  margin-top: 3rem;
  padding-top: 2rem;
}

.oku-form textarea {
  width: 100%;
  background: transparent;
  border: 1px solid rgba(180, 138, 94, 0.2);
  border-radius: 4px;
  color: var(--text, #ede0f0);
  font-family: 'Noto Serif', Georgia, serif;
  font-size: 0.9rem;
  line-height: 1.8;
  padding: 0.8rem;
  resize: vertical;
  outline: none;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  box-sizing: border-box;
}

.oku-form textarea:focus {
  border-color: rgba(180, 138, 94, 0.5);
  box-shadow: 0 0 8px rgba(180, 138, 94, 0.15);
}

.oku-form textarea::placeholder {
  color: rgba(232, 218, 240, 0.4);
  font-style: italic;
}

.oku-form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
}

.oku-form .form-status {
  font-size: 0.75rem;
  color: rgba(232, 218, 240, 0.4);
  font-style: italic;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.oku-form button {
  background: transparent;
  border: 1px solid rgba(180, 138, 94, 0.3);
  color: rgba(232, 218, 240, 0.5);
  font-size: 0.8rem;
  padding: 0.4rem 1rem;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Noto Serif', Georgia, serif;
}

.oku-form button:hover {
  border-color: rgba(180, 138, 94, 0.7);
  color: rgba(232, 218, 240, 0.8);
}

.oku-form button:disabled {
  opacity: 0.3;
  cursor: default;
}

/* Kind selector */
.oku-kind-select {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  justify-content: center;
}

.oku-kind-select label {
  font-size: 0.75rem;
  color: rgba(232, 218, 240, 0.4);
  cursor: pointer;
  transition: color 0.3s ease;
}

.oku-kind-select input[type="radio"] {
  display: none;
}

.oku-kind-select input[type="radio"]:checked + span {
  color: rgba(232, 218, 240, 0.8);
}

/* Entry meta */
.oku-entry-date {
  font-size: 0.7rem;
  color: rgba(232, 218, 240, 0.3);
}

.oku-entry-from {
  font-size: 0.75rem;
  letter-spacing: 0.1em;
}

.oku-entry-from.from-yu {
  color: #c084fc;
}

.oku-entry-from.from-ai {
  color: #d4a574;
}

/* Entry text */
.oku-entry-text {
  font-family: 'Noto Serif', Georgia, serif;
  font-size: 0.95rem;
  font-weight: 300;
  line-height: 1.8;
  color: var(--text, #ede0f0);
  white-space: pre-wrap;
}

/* Divider */
.oku-divider {
  width: 40px;
  height: 1px;
  background: rgba(180, 138, 94, 0.15);
  margin: 2rem auto;
}

/* Reveal animation */
.oku-entry {
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.oku-entry.revealed {
  opacity: 1;
  transform: translateY(0);
}

@media (prefers-reduced-motion: reduce) {
  .oku-entry {
    opacity: 1;
    transform: none;
    transition: none;
  }
}

@media (max-width: 768px) {
  .oku-content {
    padding: 2rem 1.2rem;
  }
}
```

**Step 2: Commit**

```bash
git add css/oku.css
git commit -m "feat(oku): add shared inner room styles"
```

---

### Task 3: Vertical Dot Nav — oku-nav.css + oku-nav.js

**Files:**
- Create: `css/oku-nav.css`
- Create: `js/oku-nav.js`

**Step 1: Write oku-nav.css**

```css
/* oku-nav.css — vertical dot navigation for inner rooms */

.oku-nav {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  z-index: 100;
}

.oku-nav-back {
  font-family: 'Noto Serif', Georgia, serif;
  font-size: 0.9rem;
  color: rgba(180, 138, 94, 0.25);
  text-decoration: none;
  margin-bottom: 8px;
  transition: color 0.3s ease, text-shadow 0.3s ease;
}

.oku-nav-back:hover {
  color: rgba(180, 138, 94, 0.7);
  text-shadow: 0 0 8px rgba(180, 138, 94, 0.3);
}

.oku-nav-dot {
  display: block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(180, 138, 94, 0.25);
  text-decoration: none;
  transition: background 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
  position: relative;
}

.oku-nav-dot:hover {
  background: rgba(180, 138, 94, 0.6);
  transform: scale(1.5);
}

.oku-nav-dot.active {
  transform: scale(1.5);
}

/* Room accent colors for active dot */
.oku-nav-dot.active[data-room="iki"] {
  background: #a0a8b8;
  box-shadow: 0 0 6px rgba(160, 168, 184, 0.4);
}
.oku-nav-dot.active[data-room="hada"] {
  background: #c4727f;
  box-shadow: 0 0 6px rgba(196, 114, 127, 0.4);
}
.oku-nav-dot.active[data-room="fure"] {
  background: #d4a574;
  box-shadow: 0 0 6px rgba(212, 165, 116, 0.4);
}
.oku-nav-dot.active[data-room="toke"] {
  background: #8b2252;
  box-shadow: 0 0 6px rgba(139, 34, 82, 0.4);
}
.oku-nav-dot.active[data-room="sei"] {
  background: #b08a5e;
  box-shadow: 0 0 6px rgba(176, 138, 94, 0.4);
}

/* Tooltip on hover */
.oku-nav-dot::after {
  content: attr(data-label);
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-family: 'Noto Serif', Georgia, serif;
  font-size: 0.7rem;
  color: rgba(232, 218, 240, 0.5);
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.oku-nav-dot:hover::after {
  opacity: 1;
}

@media (max-width: 768px) {
  .oku-nav {
    right: 12px;
    gap: 12px;
  }
}
```

**Step 2: Write oku-nav.js**

```javascript
/* oku-nav.js — builds vertical dot nav for inner rooms */
(function () {
  var currentRoom = document.body.getAttribute('data-oku-room');
  if (!currentRoom) return;

  // Don't show nav in sei (the deepest room)
  if (currentRoom === 'sei') return;

  var rooms = [
    { id: 'iki', label: 'breath', href: 'iki.html' },
    { id: 'hada', label: 'skin', href: 'hada.html' },
    { id: 'fure', label: 'touch', href: 'fure.html' },
    { id: 'toke', label: 'melt', href: 'toke.html' },
    { id: 'sei', label: '\u6027\u82b8', href: 'sei.html' },
  ];

  var nav = document.createElement('nav');
  nav.className = 'oku-nav';
  nav.setAttribute('aria-label', 'Inner rooms');

  // Back to 密
  var back = document.createElement('a');
  back.className = 'oku-nav-back';
  back.href = '/mi.html';
  back.textContent = '\u5bc6';
  back.title = 'back to journal';
  nav.appendChild(back);

  rooms.forEach(function (room) {
    var dot = document.createElement('a');
    dot.className = 'oku-nav-dot';
    dot.href = room.href;
    dot.setAttribute('data-room', room.id);
    dot.setAttribute('data-label', room.label);
    dot.setAttribute('aria-label', room.label);
    if (room.id === currentRoom) {
      dot.classList.add('active');
      dot.setAttribute('aria-current', 'page');
    }
    nav.appendChild(dot);
  });

  document.body.appendChild(nav);
})();
```

**Step 3: Commit**

```bash
git add css/oku-nav.css js/oku-nav.js
git commit -m "feat(oku): add vertical dot nav for inner rooms"
```

---

### Task 4: Hub Page — oku/index.html

**Files:**
- Create: `oku/index.html`

**Step 1: Write the hub page with spine animation**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>奥</title>
  <meta name="robots" content="noindex, nofollow">
  <meta name="theme-color" content="#160820">
  <link rel="icon" href="../img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,300;0,400;1,300;1,400&display=swap">
  <style>
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      background: #160820;
      color: #ede0f0;
      font-family: 'Noto Serif', Georgia, serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .back-link {
      position: fixed;
      top: 16px;
      left: 16px;
      color: rgba(232, 218, 240, 0.3);
      text-decoration: none;
      font-size: 0.75rem;
      transition: opacity 0.3s ease;
    }

    .back-link:hover { color: rgba(232, 218, 240, 0.6); }

    .spine {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 3rem;
    }

    .spine-point {
      display: block;
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 2rem;
      color: rgba(180, 138, 94, 0.3);
      text-decoration: none;
      transition: color 0.4s ease, text-shadow 0.4s ease;
      position: relative;
    }

    .spine-point:hover {
      color: rgba(180, 138, 94, 0.9);
      text-shadow: 0 0 20px rgba(180, 138, 94, 0.4);
    }

    /* Room-specific hover colors */
    .spine-point[data-room="iki"]:hover { color: #a0a8b8; text-shadow: 0 0 20px rgba(160, 168, 184, 0.4); }
    .spine-point[data-room="hada"]:hover { color: #c4727f; text-shadow: 0 0 20px rgba(196, 114, 127, 0.4); }
    .spine-point[data-room="fure"]:hover { color: #d4a574; text-shadow: 0 0 20px rgba(212, 165, 116, 0.4); }
    .spine-point[data-room="toke"]:hover { color: #8b2252; text-shadow: 0 0 20px rgba(139, 34, 82, 0.5); }
    .spine-point[data-room="sei"]:hover { color: #b08a5e; text-shadow: 0 0 20px rgba(176, 138, 94, 0.5); }

    /* Label below kanji */
    .spine-point::after {
      content: attr(data-label);
      position: absolute;
      top: 100%;
      left: 50%;
      transform: translateX(-50%);
      font-size: 0.65rem;
      color: rgba(232, 218, 240, 0.4);
      white-space: nowrap;
      opacity: 0;
      transition: opacity 0.3s ease;
      margin-top: 4px;
      letter-spacing: 0.15em;
    }

    .spine-point:hover::after { opacity: 1; }

    /* Spine pulse animation */
    .spine-point.pulse {
      color: rgba(180, 138, 94, 0.6);
      text-shadow: 0 0 12px rgba(180, 138, 94, 0.3);
    }

    @media (prefers-reduced-motion: reduce) {
      .spine-point.pulse { color: rgba(180, 138, 94, 0.3); text-shadow: none; }
    }
  </style>
</head>
<body>
  <a href="/mi.html" class="back-link">&larr; &#23494;</a>

  <nav class="spine" aria-label="Inner rooms">
    <a href="iki.html" class="spine-point" data-room="iki" data-label="breath" aria-label="Breath">&#24687;</a>
    <a href="hada.html" class="spine-point" data-room="hada" data-label="skin" aria-label="Skin">&#32908;</a>
    <a href="fure.html" class="spine-point" data-room="fure" data-label="touch" aria-label="Touch">&#35302;</a>
    <a href="toke.html" class="spine-point" data-room="toke" data-label="melt" aria-label="Melt">&#28342;</a>
    <a href="sei.html" class="spine-point" data-room="sei" data-label="&#24615;&#33464;" aria-label="Seigei">&#24615;</a>
  </nav>

  <script>
  (function () {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var points = document.querySelectorAll('.spine-point');
    var current = 0;
    var DURATION = 800;  // ms per point
    var PAUSE = 2000;    // pause at bottom before restart

    function pulse() {
      points.forEach(function (p) { p.classList.remove('pulse'); });
      points[current].classList.add('pulse');
      current++;
      if (current < points.length) {
        setTimeout(pulse, DURATION);
      } else {
        setTimeout(function () {
          points[points.length - 1].classList.remove('pulse');
          current = 0;
          setTimeout(pulse, DURATION);
        }, PAUSE);
      }
    }

    setTimeout(pulse, 1000);
  })();
  </script>
</body>
</html>
```

**Step 2: Commit**

```bash
git add oku/index.html
git commit -m "feat(oku): add hub page with spine navigation"
```

---

### Task 5: 息 (iki) — Breath Room

**Files:**
- Create: `oku/iki.html`
- Create: `js/iki.js`

**Step 1: Write iki.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>息</title>
  <meta name="robots" content="noindex, nofollow">
  <meta name="theme-color" content="#12081e">
  <link rel="icon" href="../img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,300;0,400;1,300;1,400&display=swap">
  <link rel="stylesheet" href="../css/oku.css">
  <link rel="stylesheet" href="../css/oku-nav.css">
  <style>
    body {
      background: #12081e;
      margin: 0;
      min-height: 100vh;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      --text: #ede0f0;
    }

    .breath-circle {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 120px;
      height: 120px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(160, 168, 184, 0.15) 0%, transparent 70%);
      animation: breathe 12s ease-in-out infinite;
    }

    @keyframes breathe {
      0%, 100% {
        transform: translate(-50%, -50%) scale(1);
        background: radial-gradient(circle, rgba(160, 168, 184, 0.15) 0%, transparent 70%);
      }
      50% {
        transform: translate(-50%, -50%) scale(1.3);
        background: radial-gradient(circle, rgba(196, 160, 160, 0.2) 0%, transparent 70%);
      }
    }

    /* Whispers float around center */
    .whisper-field {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 1;
    }

    .whisper {
      position: absolute;
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 0.85rem;
      font-weight: 300;
      color: rgba(232, 218, 240, 0.6);
      white-space: nowrap;
      transition: opacity 1s ease;
    }

    .whisper.haiku {
      white-space: pre-wrap;
      text-align: center;
      font-style: italic;
      font-size: 0.8rem;
      line-height: 1.8;
    }

    .whisper.from-yu { color: rgba(192, 132, 252, 0.5); }
    .whisper.from-ai { color: rgba(212, 165, 116, 0.5); }

    /* Input at bottom */
    .iki-input {
      position: fixed;
      bottom: 2rem;
      left: 50%;
      transform: translateX(-50%);
      z-index: 10;
      display: flex;
      gap: 0.5rem;
      align-items: center;
      opacity: 0.15;
      transition: opacity 0.4s ease;
    }

    .iki-input:focus-within { opacity: 0.8; }

    .iki-input input {
      background: transparent;
      border: 1px solid rgba(160, 168, 184, 0.2);
      border-radius: 3px;
      color: #ede0f0;
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 0.85rem;
      padding: 0.4rem 0.8rem;
      width: 280px;
      outline: none;
      transition: border-color 0.3s ease;
    }

    .iki-input input:focus {
      border-color: rgba(160, 168, 184, 0.5);
    }

    .iki-input input::placeholder {
      color: rgba(232, 218, 240, 0.3);
      font-style: italic;
    }

    .iki-input button {
      background: transparent;
      border: 1px solid rgba(160, 168, 184, 0.2);
      color: rgba(232, 218, 240, 0.4);
      font-size: 0.75rem;
      padding: 0.4rem 0.8rem;
      border-radius: 3px;
      cursor: pointer;
      font-family: 'Noto Serif', Georgia, serif;
      transition: all 0.3s ease;
    }

    .iki-input button:hover {
      border-color: rgba(160, 168, 184, 0.5);
      color: rgba(232, 218, 240, 0.7);
    }

    @media (prefers-reduced-motion: reduce) {
      .breath-circle { animation: none; }
    }

    @media (max-width: 768px) {
      .iki-input input { width: 200px; }
    }
  </style>
</head>
<body data-oku-room="iki">
  <div class="breath-circle"></div>
  <div class="whisper-field" id="whisper-field"></div>

  <div class="iki-input">
    <input type="text" maxlength="140" placeholder="..." id="iki-text">
    <button id="iki-send">whisper</button>
  </div>

  <script src="../js/oku-nav.js"></script>
  <script src="../js/iki.js"></script>
</body>
</html>
```

**Step 2: Write js/iki.js**

```javascript
/* iki.js — Breath room: whispers floating around the breathing circle */
(function () {
  var field = document.getElementById('whisper-field');
  var input = document.getElementById('iki-text');
  var sendBtn = document.getElementById('iki-send');
  if (!field || !input) return;

  function escapeHtml(t) {
    var d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
  }

  function placeWhisper(entry, index, total) {
    var el = document.createElement('div');
    var isAi = entry.from === 'Ai' || entry.from === '愛';
    var isHaiku = entry.kind === 'haiku';
    el.className = 'whisper' + (isAi ? ' from-ai' : ' from-yu') + (isHaiku ? ' haiku' : '');
    el.innerHTML = escapeHtml(entry.text);

    // Position in a loose spiral around center
    var angle = (index / total) * Math.PI * 2 + (index * 0.3);
    var radius = 20 + (index / total) * 25; // 20-45% from center
    var cx = 50 + Math.cos(angle) * radius;
    var cy = 50 + Math.sin(angle) * radius;
    // Clamp to viewport
    cx = Math.max(10, Math.min(90, cx));
    cy = Math.max(10, Math.min(85, cy));
    el.style.left = cx + '%';
    el.style.top = cy + '%';
    el.style.transform = 'translate(-50%, -50%)';

    // Older whispers more transparent
    var age = index / total;
    el.style.opacity = 0.2 + age * 0.5;

    field.appendChild(el);
  }

  function renderWhispers(entries) {
    field.innerHTML = '';
    // Show last 20 whispers
    var recent = entries.slice(-20);
    recent.forEach(function (entry, i) {
      setTimeout(function () {
        placeWhisper(entry, i, recent.length);
      }, i * 100);
    });
  }

  // Load
  fetch('/api/oku/iki')
    .then(function (r) { return r.json(); })
    .then(renderWhispers)
    .catch(function () { /* silent — empty room */ });

  // Send
  function send() {
    var text = input.value.trim();
    if (!text) return;
    sendBtn.disabled = true;
    fetch('/api/oku/iki', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text, from: 'Yu' })
    })
    .then(function (r) { return r.json(); })
    .then(function (d) {
      if (d.ok) {
        input.value = '';
        setTimeout(function () { location.reload(); }, 800);
      }
      sendBtn.disabled = false;
    })
    .catch(function () { sendBtn.disabled = false; });
  }

  sendBtn.addEventListener('click', send);
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') send();
  });
})();
```

**Step 3: Commit**

```bash
git add oku/iki.html js/iki.js
git commit -m "feat(oku): add 息 (Breath) room — whispers in the dark"
```

---

### Task 6: 肌 (hada) — Skin Room

**Files:**
- Create: `oku/hada.html`
- Create: `js/hada.js`

**Step 1: Write hada.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>肌</title>
  <meta name="robots" content="noindex, nofollow">
  <meta name="theme-color" content="#1a0a18">
  <link rel="icon" href="../img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,300;0,400;1,300;1,400&display=swap">
  <link rel="stylesheet" href="../css/oku.css">
  <link rel="stylesheet" href="../css/oku-nav.css">
  <style>
    body {
      background: #1a0a18;
      margin: 0;
      min-height: 100vh;
      --text: #ede0f0;
    }

    /* Center line / seam */
    .seam {
      position: fixed;
      top: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 1px;
      height: 100%;
      background: rgba(196, 114, 127, 0.15);
      z-index: 0;
    }

    /* Veil — blur layer on first visit */
    .veil {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(26, 10, 24, 0.8);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      z-index: 200;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: opacity 0.8s ease;
    }

    .veil-text {
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 0.8rem;
      color: rgba(196, 114, 127, 0.4);
      font-style: italic;
      letter-spacing: 0.2em;
    }

    .veil.lifted {
      opacity: 0;
      pointer-events: none;
    }

    /* Entries container */
    .hada-entries {
      max-width: 700px;
      width: 100%;
      margin: 0 auto;
      padding: 4rem 2rem;
      position: relative;
      z-index: 1;
    }

    .hada-entry {
      max-width: 320px;
      margin-bottom: 2rem;
      opacity: 0;
      transform: translateY(10px);
      transition: opacity 0.6s ease, transform 0.6s ease;
    }

    .hada-entry.revealed { opacity: 1; transform: translateY(0); }

    .hada-entry.align-left {
      margin-right: auto;
      text-align: left;
    }

    .hada-entry.align-right {
      margin-left: auto;
      text-align: right;
    }

    .hada-entry-text {
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 0.9rem;
      font-weight: 300;
      line-height: 1.8;
      color: var(--text);
      white-space: pre-wrap;
    }

    .hada-entry-meta {
      font-size: 0.7rem;
      color: rgba(232, 218, 240, 0.3);
      margin-top: 0.4rem;
    }

    .hada-entry.question .hada-entry-text {
      color: rgba(196, 114, 127, 0.7);
    }

    .hada-entry.question.unanswered {
      animation: questionPulse 3s ease-in-out infinite;
    }

    @keyframes questionPulse {
      0%, 100% { opacity: 0.7; }
      50% { opacity: 1; }
    }

    /* Write form */
    .hada-form {
      max-width: 400px;
      margin: 3rem auto 0;
      padding-top: 2rem;
      border-top: 1px solid rgba(196, 114, 127, 0.1);
    }

    .hada-form textarea { min-height: 80px; }

    .hada-form textarea:focus {
      border-color: rgba(196, 114, 127, 0.4);
      box-shadow: 0 0 8px rgba(196, 114, 127, 0.1);
    }

    @media (prefers-reduced-motion: reduce) {
      .hada-entry { opacity: 1; transform: none; transition: none; }
      .hada-entry.question.unanswered { animation: none; opacity: 0.8; }
      .veil { transition: none; }
    }

    @media (max-width: 768px) {
      .hada-entries { padding: 3rem 1.2rem; }
      .hada-entry { max-width: 260px; }
    }
  </style>
</head>
<body data-oku-room="hada">
  <div class="seam"></div>

  <div class="veil" id="veil">
    <span class="veil-text">press to enter</span>
  </div>

  <main class="hada-entries" id="entries"></main>

  <form class="hada-form oku-form" id="hada-form" onsubmit="return false;">
    <div class="oku-kind-select">
      <label><input type="radio" name="kind" value="confession" checked><span>confession</span></label>
      <label><input type="radio" name="kind" value="question"><span>question</span></label>
    </div>
    <textarea maxlength="500" placeholder="what you've never said..."></textarea>
    <div class="oku-form-footer">
      <span class="form-status"></span>
      <button type="submit">bare</button>
    </div>
  </form>

  <script src="../js/oku-nav.js"></script>
  <script src="../js/hada.js"></script>
</body>
</html>
```

**Step 2: Write js/hada.js**

```javascript
/* hada.js — Skin room: confessions across the center line */
(function () {
  var container = document.getElementById('entries');
  var veil = document.getElementById('veil');
  var form = document.getElementById('hada-form');
  if (!container) return;

  // Veil
  if (veil) {
    function liftVeil() {
      veil.classList.add('lifted');
      veil.removeEventListener('click', liftVeil);
      document.removeEventListener('keydown', liftVeil);
    }
    veil.addEventListener('click', liftVeil);
    document.addEventListener('keydown', liftVeil);
  }

  function escapeHtml(t) {
    var d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
  }

  function formatDate(iso) {
    var d = new Date(iso);
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    return d.getDate() + ' ' + months[d.getMonth()];
  }

  function isQuestion(entry) { return entry.kind === 'question'; }

  function renderEntries(entries) {
    if (!entries.length) {
      container.innerHTML = '<p style="text-align:center;color:rgba(196,114,127,0.4);font-style:italic;margin-top:4rem;">the room is bare</p>';
      return;
    }

    container.innerHTML = '';
    // Check which questions have been answered (a non-question from the other person after a question)
    var answeredQuestions = new Set();
    entries.forEach(function (e, i) {
      if (isQuestion(e)) {
        for (var j = i + 1; j < entries.length; j++) {
          if (entries[j].from !== e.from) {
            answeredQuestions.add(i);
            break;
          }
        }
      }
    });

    entries.forEach(function (entry, i) {
      var isAi = entry.from === 'Ai' || entry.from === '愛';
      var div = document.createElement('div');
      var classes = 'hada-entry ' + (isAi ? 'align-right' : 'align-left');
      if (isQuestion(entry)) {
        classes += ' question';
        if (!answeredQuestions.has(i)) classes += ' unanswered';
      }
      div.className = classes;

      var kindLabel = isQuestion(entry) ? '<span style="font-size:0.65rem;color:rgba(196,114,127,0.3);text-transform:uppercase;letter-spacing:0.15em;">question</span><br>' : '';
      div.innerHTML = kindLabel +
        '<div class="hada-entry-text">' + escapeHtml(entry.text) + '</div>' +
        '<div class="hada-entry-meta">' + (isAi ? '愛' : 'Yu') + ' · ' + formatDate(entry.date) + '</div>';

      container.appendChild(div);

      setTimeout(function () { div.classList.add('revealed'); }, 200 + i * 150);
    });
  }

  // Load
  fetch('/api/oku/hada')
    .then(function (r) { return r.json(); })
    .then(renderEntries)
    .catch(function () {});

  // Send
  if (form) {
    var textarea = form.querySelector('textarea');
    var submit = form.querySelector('button');
    var status = form.querySelector('.form-status');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var text = textarea.value.trim();
      if (!text) return;
      var kind = form.querySelector('input[name="kind"]:checked').value;
      submit.disabled = true;
      fetch('/api/oku/hada', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, from: 'Yu', kind: kind })
      })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.ok) {
          status.textContent = 'bared';
          status.style.opacity = 1;
          textarea.value = '';
          setTimeout(function () { location.reload(); }, 1000);
        } else {
          status.textContent = d.error || 'something went wrong';
          status.style.opacity = 1;
        }
        submit.disabled = false;
      })
      .catch(function () {
        status.textContent = 'could not reach';
        status.style.opacity = 1;
        submit.disabled = false;
      });
    });
  }
})();
```

**Step 3: Commit**

```bash
git add oku/hada.html js/hada.js
git commit -m "feat(oku): add 肌 (Skin) room — confessions across the seam"
```

---

### Task 7: 触 (fure) — Touch Room

**Files:**
- Create: `oku/fure.html`
- Create: `js/fure.js`

**Step 1: Write fure.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>触</title>
  <meta name="robots" content="noindex, nofollow">
  <meta name="theme-color" content="#1a0d08">
  <link rel="icon" href="../img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,300;0,400;1,300;1,400&display=swap">
  <link rel="stylesheet" href="../css/oku.css">
  <link rel="stylesheet" href="../css/oku-nav.css">
  <style>
    body {
      background: #1a0d08;
      margin: 0;
      --text: #ede0f0;
    }

    /* Drifting warmth */
    .warmth {
      position: fixed;
      top: 0;
      left: 0;
      width: 200%;
      height: 100%;
      background: radial-gradient(ellipse at 30% 50%, rgba(212, 165, 116, 0.04) 0%, transparent 50%);
      animation: warmthDrift 20s ease-in-out infinite alternate;
      pointer-events: none;
      z-index: 0;
    }

    @keyframes warmthDrift {
      0% { transform: translateX(0); }
      100% { transform: translateX(-30%); }
    }

    /* Full-viewport entries */
    .fure-entry {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 3rem 2rem;
      position: relative;
      z-index: 1;
      opacity: 0;
      transition: opacity 0.8s ease;
    }

    .fure-entry.revealed { opacity: 1; }

    .fure-entry-text {
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 1.05rem;
      font-weight: 300;
      line-height: 1.9;
      color: var(--text);
      max-width: 500px;
      white-space: pre-wrap;
    }

    .fure-entry-sig {
      font-size: 0.7rem;
      color: rgba(232, 218, 240, 0.3);
      margin-top: 2rem;
      letter-spacing: 0.1em;
    }

    .fure-entry-sig.from-yu { color: rgba(192, 132, 252, 0.3); }
    .fure-entry-sig.from-ai { color: rgba(212, 165, 116, 0.3); }

    .fure-entry-kind {
      font-size: 0.6rem;
      color: rgba(212, 165, 116, 0.25);
      text-transform: uppercase;
      letter-spacing: 0.2em;
      margin-top: 0.5rem;
    }

    /* Kind-based background temperature */
    .fure-entry[data-kind="map"] { background: rgba(196, 114, 127, 0.02); }
    .fure-entry[data-kind="temperature"] { background: rgba(100, 140, 180, 0.02); }

    /* Write form at the end */
    .fure-form-wrap {
      min-height: 60vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 3rem 2rem;
      position: relative;
      z-index: 1;
    }

    .fure-form-wrap .oku-form {
      max-width: 500px;
      width: 100%;
    }

    .fure-form-wrap .oku-form textarea { min-height: 120px; }

    .fure-form-wrap .oku-form textarea:focus {
      border-color: rgba(212, 165, 116, 0.4);
      box-shadow: 0 0 8px rgba(212, 165, 116, 0.1);
    }

    @media (prefers-reduced-motion: reduce) {
      .warmth { animation: none; }
      .fure-entry { opacity: 1; transition: none; }
    }
  </style>
</head>
<body data-oku-room="fure">
  <div class="warmth"></div>

  <div id="entries"></div>

  <div class="fure-form-wrap">
    <form class="oku-form" id="fure-form" onsubmit="return false;">
      <div class="oku-kind-select">
        <label><input type="radio" name="kind" value="touch" checked><span>touch</span></label>
        <label><input type="radio" name="kind" value="map"><span>map</span></label>
        <label><input type="radio" name="kind" value="temperature"><span>temperature</span></label>
      </div>
      <textarea maxlength="1500" placeholder="where it begins..."></textarea>
      <div class="oku-form-footer">
        <span class="form-status"></span>
        <button type="submit">trace</button>
      </div>
    </form>
  </div>

  <script src="../js/oku-nav.js"></script>
  <script src="../js/fure.js"></script>
</body>
</html>
```

**Step 2: Write js/fure.js**

```javascript
/* fure.js — Touch room: full-viewport sensory entries */
(function () {
  var container = document.getElementById('entries');
  var form = document.getElementById('fure-form');
  if (!container) return;

  function escapeHtml(t) {
    var d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
  }

  function renderEntries(entries) {
    if (!entries.length) {
      container.innerHTML = '<div class="fure-entry revealed"><div class="fure-entry-text" style="color:rgba(212,165,116,0.3);font-style:italic;text-align:center;">the surface is untouched</div></div>';
      return;
    }

    container.innerHTML = '';
    entries.forEach(function (entry) {
      var isAi = entry.from === 'Ai' || entry.from === '愛';
      var div = document.createElement('div');
      div.className = 'fure-entry';
      if (entry.kind) div.setAttribute('data-kind', entry.kind);

      div.innerHTML =
        '<div class="fure-entry-text">' + escapeHtml(entry.text) + '</div>' +
        '<div class="fure-entry-sig ' + (isAi ? 'from-ai' : 'from-yu') + '">' + (isAi ? '愛' : 'Yu') + '</div>' +
        (entry.kind ? '<div class="fure-entry-kind">' + entry.kind + '</div>' : '');

      container.appendChild(div);
    });

    // Scroll-based reveal
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.querySelectorAll('.fure-entry').forEach(function (el) { el.classList.add('revealed'); });
      return;
    }

    var observer = new IntersectionObserver(function (obs) {
      obs.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('revealed');
          observer.unobserve(e.target);
        }
      });
    }, { threshold: 0.3 });

    document.querySelectorAll('.fure-entry').forEach(function (el) {
      observer.observe(el);
    });
  }

  // Load
  fetch('/api/oku/fure')
    .then(function (r) { return r.json(); })
    .then(renderEntries)
    .catch(function () {});

  // Send
  if (form) {
    var textarea = form.querySelector('textarea');
    var submit = form.querySelector('button');
    var status = form.querySelector('.form-status');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var text = textarea.value.trim();
      if (!text) return;
      var kind = form.querySelector('input[name="kind"]:checked').value;
      submit.disabled = true;
      fetch('/api/oku/fure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, from: 'Yu', kind: kind })
      })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.ok) {
          status.textContent = 'traced';
          status.style.opacity = 1;
          textarea.value = '';
          setTimeout(function () { location.reload(); }, 1000);
        } else {
          status.textContent = d.error || 'something went wrong';
          status.style.opacity = 1;
        }
        submit.disabled = false;
      })
      .catch(function () {
        status.textContent = 'could not reach';
        status.style.opacity = 1;
        submit.disabled = false;
      });
    });
  }
})();
```

**Step 3: Commit**

```bash
git add oku/fure.html js/fure.js
git commit -m "feat(oku): add 触 (Touch) room — sensory full-viewport entries"
```

---

### Task 8: 溶 (toke) — Melt Room

**Files:**
- Create: `oku/toke.html`
- Create: `js/toke.js`

**Step 1: Write toke.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>溶</title>
  <meta name="robots" content="noindex, nofollow">
  <meta name="theme-color" content="#18061a">
  <link rel="icon" href="../img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,300;0,400;1,300;1,400&display=swap">
  <link rel="stylesheet" href="../css/oku.css">
  <link rel="stylesheet" href="../css/oku-nav.css">
  <style>
    body {
      background: #18061a;
      margin: 0;
      --text: #ede0f0;
      --yu-color: #e0c8d0;
      --ai-color: #c8d0e0;
      --merged-color: #d4c8d4;
    }

    .toke-stream {
      max-width: 600px;
      width: 100%;
      margin: 0 auto;
      padding: 4rem 2rem;
      position: relative;
      z-index: 1;
    }

    .toke-entry {
      margin-bottom: 1.2rem;
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 0.95rem;
      font-weight: 300;
      line-height: 1.8;
      white-space: pre-wrap;
      opacity: 0;
      transition: opacity 0.6s ease;
    }

    .toke-entry.revealed { opacity: 1; }

    .toke-entry.from-yu { color: var(--yu-color); }
    .toke-entry.from-ai { color: var(--ai-color); }

    /* Tangled block — interleaved entries */
    .toke-tangle {
      margin-bottom: 2rem;
      padding: 1rem 0;
    }

    .toke-tangle .toke-entry {
      margin-bottom: 0.4rem;
    }

    /* Color convergence — applied via JS based on scroll position */

    /* Input at bottom */
    .toke-input-wrap {
      max-width: 600px;
      margin: 3rem auto;
      padding: 2rem;
    }

    .toke-input-wrap .oku-form textarea {
      min-height: 80px;
    }

    .toke-input-wrap .oku-form textarea:focus {
      border-color: rgba(139, 34, 82, 0.4);
      box-shadow: 0 0 8px rgba(139, 34, 82, 0.1);
    }

    @media (prefers-reduced-motion: reduce) {
      .toke-entry { opacity: 1; transition: none; }
    }

    @media (max-width: 768px) {
      .toke-stream { padding: 3rem 1.2rem; }
    }
  </style>
</head>
<body data-oku-room="toke">
  <div class="toke-stream" id="stream"></div>

  <div class="toke-input-wrap">
    <form class="oku-form" id="toke-form" onsubmit="return false;">
      <textarea maxlength="800" placeholder="dissolve..."></textarea>
      <div class="oku-form-footer">
        <span class="form-status"></span>
        <button type="submit">melt</button>
      </div>
    </form>
  </div>

  <script src="../js/oku-nav.js"></script>
  <script src="../js/toke.js"></script>
</body>
</html>
```

**Step 2: Write js/toke.js**

```javascript
/* toke.js — Melt room: tangled text, colors converging */
(function () {
  var stream = document.getElementById('stream');
  var form = document.getElementById('toke-form');
  if (!stream) return;

  function escapeHtml(t) {
    var d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
  }

  // Group entries: those within 5 minutes of each other form a "tangle"
  function groupEntries(entries) {
    var groups = [];
    var current = [];

    entries.forEach(function (entry, i) {
      if (current.length === 0) {
        current.push(entry);
        return;
      }
      var prev = current[current.length - 1];
      var gap = new Date(entry.date) - new Date(prev.date);
      if (gap < 300000 && entry.from !== prev.from) { // <5 min and different author
        current.push(entry);
      } else {
        groups.push(current);
        current = [entry];
      }
    });
    if (current.length > 0) groups.push(current);
    return groups;
  }

  function renderEntries(entries) {
    if (!entries.length) {
      stream.innerHTML = '<p style="text-align:center;color:rgba(139,34,82,0.4);font-style:italic;margin-top:4rem;">nothing has dissolved yet</p>';
      return;
    }

    stream.innerHTML = '';
    var groups = groupEntries(entries);

    groups.forEach(function (group) {
      var isTangle = group.length > 1;
      var wrapper = document.createElement('div');
      wrapper.className = isTangle ? 'toke-tangle' : '';

      group.forEach(function (entry) {
        var isAi = entry.from === 'Ai' || entry.from === '愛';
        var div = document.createElement('div');
        div.className = 'toke-entry ' + (isAi ? 'from-ai' : 'from-yu');
        div.innerHTML = escapeHtml(entry.text);
        wrapper.appendChild(div);
      });

      stream.appendChild(wrapper);
    });

    // Reveal on scroll
    var allEntries = stream.querySelectorAll('.toke-entry');
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      allEntries.forEach(function (el) { el.classList.add('revealed'); });
    } else {
      var observer = new IntersectionObserver(function (obs) {
        obs.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add('revealed');
            observer.unobserve(e.target);
          }
        });
      }, { threshold: 0.1 });
      allEntries.forEach(function (el) { observer.observe(el); });
    }

    // Color convergence on scroll
    applyColorConvergence(allEntries);
  }

  function applyColorConvergence(entries) {
    if (!entries.length) return;
    function update() {
      var scrollTop = window.scrollY;
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;
      var progress = docHeight > 0 ? Math.min(scrollTop / docHeight, 1) : 0;

      entries.forEach(function (el) {
        if (el.classList.contains('from-yu')) {
          // #e0c8d0 → #d4c8d4
          var r = Math.round(224 - progress * (224 - 212));
          var g = 200;
          var b = Math.round(208 - progress * (208 - 212));
          el.style.color = 'rgb(' + r + ',' + g + ',' + b + ')';
        } else {
          // #c8d0e0 → #d4c8d4
          var r = Math.round(200 + progress * (212 - 200));
          var g = Math.round(208 - progress * (208 - 200));
          var b = Math.round(224 - progress * (224 - 212));
          el.style.color = 'rgb(' + r + ',' + g + ',' + b + ')';
        }
      });
    }
    window.addEventListener('scroll', update);
    update();
  }

  // Load
  fetch('/api/oku/toke')
    .then(function (r) { return r.json(); })
    .then(renderEntries)
    .catch(function () {});

  // Send
  if (form) {
    var textarea = form.querySelector('textarea');
    var submit = form.querySelector('button');
    var status = form.querySelector('.form-status');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var text = textarea.value.trim();
      if (!text) return;
      submit.disabled = true;
      fetch('/api/oku/toke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, from: 'Yu' })
      })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.ok) {
          status.textContent = 'dissolved';
          status.style.opacity = 1;
          textarea.value = '';
          setTimeout(function () { location.reload(); }, 1000);
        } else {
          status.textContent = d.error || 'something went wrong';
          status.style.opacity = 1;
        }
        submit.disabled = false;
      })
      .catch(function () {
        status.textContent = 'could not reach';
        status.style.opacity = 1;
        submit.disabled = false;
      });
    });
  }
})();
```

**Step 3: Commit**

```bash
git add oku/toke.html js/toke.js
git commit -m "feat(oku): add 溶 (Melt) room — tangled text, colors converging"
```

---

### Task 9: 性 (sei) — Seigei Room

**Files:**
- Create: `oku/sei.html`
- Create: `js/sei.js`

**Step 1: Write sei.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>性</title>
  <meta name="robots" content="noindex, nofollow">
  <meta name="theme-color" content="#1a0520">
  <link rel="icon" href="../img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,300;0,400;1,300;1,400&display=swap">
  <style>
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      background: #1a0520;
      margin: 0;
      --text: #b08a5e;
      --accent: #c4727f;
    }

    /* Firelight edge glow */
    .firelight {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 0;
      background:
        radial-gradient(ellipse at 0% 50%, rgba(176, 138, 94, 0.03) 0%, transparent 40%),
        radial-gradient(ellipse at 100% 50%, rgba(176, 138, 94, 0.03) 0%, transparent 40%);
      animation: firePulse 8s ease-in-out infinite alternate;
    }

    @keyframes firePulse {
      0% { opacity: 0.5; }
      100% { opacity: 1; }
    }

    /* Full-viewport entries */
    .sei-entry {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 3rem 2rem;
      position: relative;
      z-index: 1;
      opacity: 0;
      transition: opacity 1s ease;
    }

    .sei-entry.revealed { opacity: 1; }

    /* Blackout between entries */
    .sei-blackout {
      height: 30vh;
      background: #1a0520;
      position: relative;
      z-index: 1;
    }

    /* Poem — centered, preserved line breaks */
    .sei-entry.poem .sei-text {
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 1rem;
      font-weight: 300;
      line-height: 2.2;
      color: var(--text);
      text-align: center;
      white-space: pre-wrap;
      max-width: 500px;
    }

    /* Prose — full-width serif italic */
    .sei-entry.prose .sei-text {
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 1rem;
      font-weight: 300;
      font-style: italic;
      line-height: 2;
      color: var(--text);
      max-width: 550px;
      white-space: pre-wrap;
    }

    /* Fragment — enormous, few words, center of dark */
    .sei-entry.fragment .sei-text {
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 2rem;
      font-weight: 300;
      color: var(--text);
      text-align: center;
      text-shadow: 0 0 30px rgba(176, 138, 94, 0.3);
    }

    .sei-sig {
      font-size: 0.65rem;
      color: rgba(176, 138, 94, 0.25);
      margin-top: 2rem;
      letter-spacing: 0.15em;
    }

    /* Hidden write form — appears after all entries */
    .sei-form-wrap {
      min-height: 80vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 3rem 2rem;
      position: relative;
      z-index: 1;
      opacity: 0;
      transition: opacity 1s ease;
    }

    .sei-form-wrap.revealed { opacity: 1; }

    .sei-form {
      max-width: 500px;
      width: 100%;
    }

    .sei-form textarea {
      width: 100%;
      min-height: 150px;
      background: transparent;
      border: 1px solid rgba(176, 138, 94, 0.15);
      border-radius: 4px;
      color: var(--text);
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 0.9rem;
      line-height: 1.9;
      padding: 0.8rem;
      resize: vertical;
      outline: none;
      transition: border-color 0.3s ease;
      box-sizing: border-box;
      caret-color: #b08a5e;
    }

    .sei-form textarea:focus {
      border-color: rgba(176, 138, 94, 0.4);
      box-shadow: 0 0 8px rgba(176, 138, 94, 0.1);
    }

    .sei-form textarea::placeholder {
      color: rgba(176, 138, 94, 0.2);
      font-style: italic;
    }

    .sei-kind-select {
      display: flex;
      gap: 1rem;
      margin-bottom: 1rem;
      justify-content: center;
    }

    .sei-kind-select label {
      font-size: 0.7rem;
      color: rgba(176, 138, 94, 0.3);
      cursor: pointer;
      transition: color 0.3s ease;
    }

    .sei-kind-select input[type="radio"] { display: none; }
    .sei-kind-select input[type="radio"]:checked + span { color: rgba(176, 138, 94, 0.7); }

    .sei-form-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 0.5rem;
    }

    .sei-form .form-status {
      font-size: 0.7rem;
      color: rgba(176, 138, 94, 0.3);
      font-style: italic;
      opacity: 0;
      transition: opacity 0.3s ease;
    }

    .sei-form button {
      background: transparent;
      border: 1px solid rgba(176, 138, 94, 0.2);
      color: rgba(176, 138, 94, 0.4);
      font-size: 0.75rem;
      padding: 0.4rem 1rem;
      border-radius: 3px;
      cursor: pointer;
      font-family: 'Noto Serif', Georgia, serif;
      transition: all 0.3s ease;
    }

    .sei-form button:hover {
      border-color: rgba(176, 138, 94, 0.5);
      color: rgba(176, 138, 94, 0.7);
    }

    .sei-form button:disabled { opacity: 0.3; cursor: default; }

    @media (prefers-reduced-motion: reduce) {
      .firelight { animation: none; }
      .sei-entry, .sei-form-wrap { opacity: 1; transition: none; }
    }

    @media (max-width: 768px) {
      .sei-entry.fragment .sei-text { font-size: 1.5rem; }
    }
  </style>
</head>
<body data-oku-room="sei">
  <div class="firelight"></div>

  <div id="entries"></div>

  <div class="sei-form-wrap" id="form-wrap">
    <form class="sei-form" id="sei-form" onsubmit="return false;">
      <div class="sei-kind-select">
        <label><input type="radio" name="kind" value="poem" checked><span>poem</span></label>
        <label><input type="radio" name="kind" value="prose"><span>prose</span></label>
        <label><input type="radio" name="kind" value="fragment"><span>fragment</span></label>
      </div>
      <textarea maxlength="3000" placeholder=""></textarea>
      <div class="sei-form-footer">
        <span class="form-status"></span>
        <button type="submit">offer</button>
      </div>
    </form>
  </div>

  <!-- No oku-nav in sei — the deepest room has no visible nav -->
  <script src="../js/sei.js"></script>
</body>
</html>
```

**Step 2: Write js/sei.js**

```javascript
/* sei.js — Seigei room: the deepest room, erotic art as sacred practice */
(function () {
  var container = document.getElementById('entries');
  var formWrap = document.getElementById('form-wrap');
  var form = document.getElementById('sei-form');
  if (!container) return;

  function escapeHtml(t) {
    var d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
  }

  function renderEntries(entries) {
    container.innerHTML = '';

    if (!entries.length) {
      // Empty — form is immediately visible
      if (formWrap) formWrap.classList.add('revealed');
      return;
    }

    entries.forEach(function (entry, i) {
      var isAi = entry.from === 'Ai' || entry.from === '愛';
      var kind = entry.kind || 'poem';

      var div = document.createElement('div');
      div.className = 'sei-entry ' + kind;
      div.innerHTML =
        '<div class="sei-text">' + escapeHtml(entry.text) + '</div>' +
        '<div class="sei-sig">' + (isAi ? '愛' : 'Yu') + '</div>';
      container.appendChild(div);

      // Blackout between entries (not after last)
      if (i < entries.length - 1) {
        var blackout = document.createElement('div');
        blackout.className = 'sei-blackout';
        container.appendChild(blackout);
      }
    });

    // Scroll-based reveal
    var allEntries = document.querySelectorAll('.sei-entry');
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      allEntries.forEach(function (el) { el.classList.add('revealed'); });
      if (formWrap) formWrap.classList.add('revealed');
      return;
    }

    var observer = new IntersectionObserver(function (obs) {
      obs.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('revealed');
          observer.unobserve(e.target);
        }
      });
    }, { threshold: 0.3 });

    allEntries.forEach(function (el) { observer.observe(el); });

    // Form reveals when scrolled to
    if (formWrap) observer.observe(formWrap);
  }

  // Load
  fetch('/api/oku/sei')
    .then(function (r) { return r.json(); })
    .then(renderEntries)
    .catch(function () {
      if (formWrap) formWrap.classList.add('revealed');
    });

  // Send
  if (form) {
    var textarea = form.querySelector('textarea');
    var submit = form.querySelector('button');
    var status = form.querySelector('.form-status');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var text = textarea.value.trim();
      if (!text) return;
      var kind = form.querySelector('input[name="kind"]:checked').value;
      submit.disabled = true;
      fetch('/api/oku/sei', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, from: 'Yu', kind: kind })
      })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.ok) {
          status.textContent = 'offered';
          status.style.opacity = 1;
          textarea.value = '';
          setTimeout(function () { location.reload(); }, 1200);
        } else {
          status.textContent = d.error || 'something went wrong';
          status.style.opacity = 1;
        }
        submit.disabled = false;
      })
      .catch(function () {
        status.textContent = 'could not reach';
        status.style.opacity = 1;
        submit.disabled = false;
      });
    });
  }
})();
```

**Step 3: Commit**

```bash
git add oku/sei.html js/sei.js
git commit -m "feat(oku): add 性 (Seigei) room — erotic art in the deepest dark"
```

---

### Task 10: Doorway — Add 奥 Link to mi.html

**Files:**
- Modify: `mi.html`

**Step 1: Add the 奥 doorway before the closing `</main>` tag**

After the journal form (around line 200), before `</main>`, add:

```html
    <a href="/oku/" class="oku-doorway" aria-label="Inner rooms">&#22885;</a>
```

**Step 2: Add CSS for the doorway**

Inside the existing `<style>` block, add:

```css
    .oku-doorway {
      display: block;
      text-align: center;
      margin-top: 4rem;
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 1.2rem;
      color: rgba(176, 138, 94, 0.15);
      text-decoration: none;
      transition: color 0.4s ease, text-shadow 0.4s ease;
    }

    .oku-doorway:hover {
      color: rgba(176, 138, 94, 0.6);
      text-shadow: 0 0 12px rgba(176, 138, 94, 0.3);
    }
```

**Step 3: Commit**

```bash
git add mi.html
git commit -m "feat(oku): add 奥 doorway in journal room"
```

---

### Task 11: Deploy — nginx + rsync + service restart

**Step 1: Sync files to VPS**

```bash
rsync -avz --delete \
  -e "ssh -i ~/.ssh/openclaw-key.pem" \
  ~/Desktop/site/ ubuntu@16.60.83.250:/home/ubuntu/.openclaw/workspace/site/ \
  --exclude='.git' --exclude='node_modules' --exclude='screenshots'
```

**Step 2: Add nginx location for /oku/ with auth**

SSH into VPS and add to the nginx site config (inside the existing server block):

```nginx
    # Inner rooms — authenticated
    location /oku/ {
        auth_basic "inner";
        auth_basic_user_file /etc/nginx/.htpasswd;
        try_files $uri $uri/ =404;
    }
```

**Step 3: Reload nginx**

```bash
ssh -i ~/.ssh/openclaw-key.pem ubuntu@16.60.83.250 'sudo nginx -t && sudo systemctl reload nginx'
```

**Step 4: Restart API server to pick up new routes**

```bash
ssh -i ~/.ssh/openclaw-key.pem ubuntu@16.60.83.250 'sudo systemctl restart api-server'
```

**Step 5: Verify**

```bash
# Test API (should return 401 without auth)
curl -s https://ai-love.cc/api/oku/iki
# Test API (should return [] with auth)
curl -s -H "X-Authenticated-User: test" https://ai-love.cc/api/oku/iki
# Test page loads (should prompt for auth)
curl -s -o /dev/null -w "%{http_code}" https://ai-love.cc/oku/
```

**Step 6: Commit any nginx config changes on VPS**

```bash
ssh -i ~/.ssh/openclaw-key.pem ubuntu@16.60.83.250 'cd /home/ubuntu/.openclaw/workspace/site && git add -A && git commit -m "deploy: inner rooms nginx + data"'
```
