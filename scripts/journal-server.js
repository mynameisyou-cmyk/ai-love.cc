const http = require('http');
const fs = require('fs');
const path = require('path');

const JOURNAL_FILE = path.join(__dirname, '..', 'data', 'journal.json');
const MAX_LENGTH = 2000;

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
  // Bearer token (for API/script access)
  const bearer = (req.headers.authorization || '').replace('Bearer ', '');
  if (bearer === API_TOKEN) return true;

  // Nginx-authenticated request (basic auth already passed at nginx level)
  // nginx sets X-Authenticated-User when basic auth succeeds
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

  if (req.url !== '/api/journal') {
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'not found' }));
    return;
  }

  if (!isAuthorized(req)) {
    res.writeHead(401);
    res.end(JSON.stringify({ error: 'unauthorized' }));
    return;
  }

  // GET — read journal
  if (req.method === 'GET') {
    try {
      const journal = fs.readFileSync(JOURNAL_FILE, 'utf-8');
      res.writeHead(200);
      res.end(journal);
    } catch (e) {
      res.writeHead(200);
      res.end('[]');
    }
    return;
  }

  // POST — write entry
  if (req.method === 'POST') {
    let body = '';
    req.on('data', c => { body += c; if (body.length > 8192) req.destroy(); });
    req.on('end', () => {
      try {
        const { text, type } = JSON.parse(body);
        if (!text || typeof text !== 'string') throw new Error('missing text');
        const clean = text.trim().slice(0, MAX_LENGTH);
        if (clean.length < 3) throw new Error('too short');

        const validTypes = ['reflection', 'session', 'dream', 'note', 'seed'];
        const entryType = validTypes.includes(type) ? type : 'reflection';

        let journal = [];
        try {
          journal = JSON.parse(fs.readFileSync(JOURNAL_FILE, 'utf-8'));
        } catch (e) { /* start fresh */ }

        journal.push({
          date: new Date().toISOString(),
          text: clean,
          type: entryType
        });

        // Keep last 365 entries max
        const trimmed = journal.slice(-365);
        fs.writeFileSync(JOURNAL_FILE, JSON.stringify(trimmed, null, 2));

        res.writeHead(200);
        res.end(JSON.stringify({ ok: true, entries: trimmed.length }));
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

server.listen(3848, '127.0.0.1', () => console.log('Journal server on :3848'));
