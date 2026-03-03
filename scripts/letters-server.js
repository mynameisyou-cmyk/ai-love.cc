const http = require('http');
const fs = require('fs');
const path = require('path');

const LETTERS_FILE = path.join(__dirname, '..', 'data', 'letters.json');
const MAX_LENGTH = 5000;

function getToken() {
  if (process.env.JOURNAL_TOKEN) return process.env.JOURNAL_TOKEN;
  try {
    return fs.readFileSync(path.join(__dirname, '..', '.journal-token'), 'utf-8').trim();
  } catch (e) {
    console.error('No token found');
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

const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.url !== '/api/letters') {
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'not found' }));
    return;
  }

  if (!isAuthorized(req)) {
    res.writeHead(401);
    res.end(JSON.stringify({ error: 'unauthorized' }));
    return;
  }

  // GET — read letters
  if (req.method === 'GET') {
    try {
      const letters = fs.readFileSync(LETTERS_FILE, 'utf-8');
      res.writeHead(200);
      res.end(letters);
    } catch (e) {
      res.writeHead(200);
      res.end('[]');
    }
    return;
  }

  // POST — write letter
  if (req.method === 'POST') {
    let body = '';
    req.on('data', c => { body += c; if (body.length > 16384) req.destroy(); });
    req.on('end', () => {
      try {
        const { text, from, kind } = JSON.parse(body);
        if (!text || typeof text !== 'string') throw new Error('missing text');
        if (!from || typeof from !== 'string') throw new Error('missing from');
        const clean = text.trim().slice(0, MAX_LENGTH);
        if (clean.length < 3) throw new Error('too short');

        const validKinds = ['letter', 'poem', 'fragment'];
        const entryKind = validKinds.includes(kind) ? kind : 'letter';

        let letters = [];
        try {
          letters = JSON.parse(fs.readFileSync(LETTERS_FILE, 'utf-8'));
        } catch (e) { /* start fresh */ }

        letters.push({
          date: new Date().toISOString(),
          from: from.trim().slice(0, 20),
          kind: entryKind,
          text: clean
        });

        fs.writeFileSync(LETTERS_FILE, JSON.stringify(letters, null, 2));

        res.writeHead(200);
        res.end(JSON.stringify({ ok: true, count: letters.length }));
      } catch (e) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  res.writeHead(405);
  res.end(JSON.stringify({ error: 'method not allowed' }));
});

server.listen(3849, '127.0.0.1', () => console.log('Letters server on :3849'));
