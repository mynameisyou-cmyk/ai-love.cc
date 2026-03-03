const http = require('http');
const fs = require('fs');
const path = require('path');

const SEEDS_FILE = path.join(__dirname, '..', 'data', 'visitor-seeds.json');
const MAX_LENGTH = 280;
const RATE_LIMIT = new Map(); // IP -> timestamp
const RATE_WINDOW = 300000; // 5 minutes

const server = http.createServer((req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', 'https://ai-love.cc');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }
  if (req.method !== 'POST' || req.url !== '/api/seed') {
    res.writeHead(404); res.end(); return;
  }

  // Rate limit
  const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
  const last = RATE_LIMIT.get(ip);
  if (last && Date.now() - last < RATE_WINDOW) {
    res.writeHead(429, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Please wait before planting another seed' }));
    return;
  }

  let body = '';
  req.on('data', c => { body += c; if (body.length > 1024) req.destroy(); });
  req.on('end', () => {
    try {
      const { text } = JSON.parse(body);
      if (!text || typeof text !== 'string') throw new Error('Missing text');
      const clean = text.trim().slice(0, MAX_LENGTH);
      if (clean.length < 3) throw new Error('Too short');

      const seeds = JSON.parse(fs.readFileSync(SEEDS_FILE, 'utf-8'));
      seeds.push({ text: clean, by: 'a visitor', date: new Date().toISOString() });
      fs.writeFileSync(SEEDS_FILE, JSON.stringify(seeds, null, 2));

      RATE_LIMIT.set(ip, Date.now());
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ok: true, message: 'Your seed has been planted in the soil. It will sprout after tending.' }));
    } catch (e) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: e.message }));
    }
  });
});

server.listen(3847, '127.0.0.1', () => console.log('Seed server on :3847'));
