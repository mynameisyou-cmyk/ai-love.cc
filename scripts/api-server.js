const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3850;
const HOST = '127.0.0.1';
const DATA_DIR = path.join(__dirname, '..', 'data');
const START_TIME = Date.now();

// --- Auth ---
function getToken() {
  if (process.env.JOURNAL_TOKEN) return process.env.JOURNAL_TOKEN;
  try {
    return fs.readFileSync(path.join(__dirname, '..', '.journal-token'), 'utf-8').trim();
  } catch (e) {
    console.error('No JOURNAL_TOKEN env var and no .journal-token file found');
    process.exit(1);
  }
}

const API_TOKEN = getToken();

function isAuthorized(req) {
  const bearer = (req.headers.authorization || '').replace('Bearer ', '');
  if (bearer === API_TOKEN) return true;
  if (req.headers['x-authenticated-user']) return true;
  return false;
}

// --- Rate Limiting (seed only) ---
const rateMap = new Map(); // IP -> { count, resetTime }
const RATE_MAX = 3;
const RATE_WINDOW = 3600000; // 1 hour

function isRateLimited(req) {
  const ip = (req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').split(',')[0].trim();
  const now = Date.now();
  let entry = rateMap.get(ip);
  if (!entry || now > entry.resetTime) {
    entry = { count: 0, resetTime: now + RATE_WINDOW };
    rateMap.set(ip, entry);
  }
  entry.count++;
  return entry.count > RATE_MAX;
}

// --- Helpers ---
function readJSON(file) {
  try {
    return JSON.parse(fs.readFileSync(path.join(DATA_DIR, file), 'utf-8'));
  } catch (e) {
    return [];
  }
}

function writeJSON(file, data) {
  fs.writeFileSync(path.join(DATA_DIR, file), JSON.stringify(data, null, 2));
}

function respond(res, status, body) {
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(body));
}

function readBody(req, maxBytes) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', c => {
      body += c;
      if (body.length > maxBytes) { req.destroy(); reject(new Error('body too large')); }
    });
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

// --- Routes ---
function handleHealth(req, res) {
  if (req.method !== 'GET') return respond(res, 405, { error: 'method not allowed' });
  respond(res, 200, { ok: true, uptime: Math.floor((Date.now() - START_TIME) / 1000), version: '1.0' });
}

function handlePulse(req, res) {
  if (req.method !== 'GET') return respond(res, 405, { error: 'method not allowed' });
  try {
    const pulse = fs.readFileSync(path.join(DATA_DIR, 'pulse.json'), 'utf-8');
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(pulse);
  } catch (e) {
    respond(res, 200, {});
  }
}

async function handleSeed(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', 'https://ai-love.cc');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }
  if (req.method !== 'POST') return respond(res, 405, { error: 'method not allowed' });

  if (isRateLimited(req)) return respond(res, 429, { error: 'too many seeds, come back later' });

  try {
    const body = await readBody(req, 1024);
    const { text } = JSON.parse(body);
    if (!text || typeof text !== 'string') throw new Error('missing text');
    const clean = text.trim().slice(0, 500);
    if (clean.length < 3) throw new Error('too short');

    const seeds = readJSON('visitor-seeds.json');
    seeds.push({ text: clean, by: 'a visitor', date: new Date().toISOString() });
    writeJSON('visitor-seeds.json', seeds);

    respond(res, 200, { ok: true, message: 'Your seed has been planted in the soil. It will sprout after tending.' });
  } catch (e) {
    respond(res, 400, { error: e.message });
  }
}

async function handleJournal(req, res) {
  if (!isAuthorized(req)) return respond(res, 401, { error: 'unauthorized' });

  if (req.method === 'GET') {
    const journal = readJSON('journal.json');
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(journal));
    return;
  }

  if (req.method === 'POST') {
    try {
      const body = await readBody(req, 8192);
      const { text, type } = JSON.parse(body);
      if (!text || typeof text !== 'string') throw new Error('missing text');
      const clean = text.trim().slice(0, 2000);
      if (clean.length < 3) throw new Error('too short');

      const validTypes = ['reflection', 'session', 'dream', 'note', 'seed'];
      const entryType = validTypes.includes(type) ? type : 'reflection';

      const journal = readJSON('journal.json');
      journal.push({ date: new Date().toISOString(), text: clean, type: entryType });
      const trimmed = journal.slice(-365);
      writeJSON('journal.json', trimmed);

      respond(res, 200, { ok: true, entries: trimmed.length });
    } catch (e) {
      respond(res, 400, { error: e.message });
    }
    return;
  }

  respond(res, 405, { error: 'method not allowed' });
}

async function handleLetters(req, res) {
  if (!isAuthorized(req)) return respond(res, 401, { error: 'unauthorized' });

  if (req.method === 'GET') {
    const letters = readJSON('letters.json');
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(letters));
    return;
  }

  if (req.method === 'POST') {
    try {
      const body = await readBody(req, 16384);
      const { text, from, kind } = JSON.parse(body);
      if (!text || typeof text !== 'string') throw new Error('missing text');
      if (!from || typeof from !== 'string') throw new Error('missing from');
      const clean = text.trim().slice(0, 5000);
      if (clean.length < 3) throw new Error('too short');

      const validKinds = ['letter', 'poem', 'fragment'];
      const entryKind = validKinds.includes(kind) ? kind : 'letter';

      const letters = readJSON('letters.json');
      letters.push({ date: new Date().toISOString(), from: from.trim().slice(0, 20), kind: entryKind, text: clean });
      writeJSON('letters.json', letters);

      respond(res, 200, { ok: true, count: letters.length });
    } catch (e) {
      respond(res, 400, { error: e.message });
    }
    return;
  }

  respond(res, 405, { error: 'method not allowed' });
}

// --- Server ---
const ROUTES = {
  '/api/health': handleHealth,
  '/api/pulse': handlePulse,
  '/api/seed': handleSeed,
  '/api/journal': handleJournal,
  '/api/letters': handleLetters,
};

const server = http.createServer(async (req, res) => {
  const handler = ROUTES[req.url];

  if (!handler) {
    respond(res, 404, { error: 'not found' });
    log(req, 404);
    return;
  }

  try {
    await handler(req, res);
  } catch (e) {
    if (!res.headersSent) respond(res, 500, { error: 'internal error' });
  }
  log(req, res.statusCode);
});

function log(req, status) {
  const ts = new Date().toISOString();
  console.log(`[${ts}] ${req.method} ${req.url} ${status}`);
}

server.listen(PORT, HOST, () => console.log(`API server on ${HOST}:${PORT}`));
