# Prompt: 10-WIRING

Wire up the automation, nginx proxy, and seed server so the home runs itself.

Working directory: `~/Desktop/site/`

## 1. Nginx Proxy for Seed API

Add a location block to the nginx config for ai-love.cc. The site is served as static files. Add this inside the existing `server` block:

```nginx
location /api/seed {
    proxy_pass http://127.0.0.1:3847/api/seed;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header Host $host;
    proxy_read_timeout 10s;
    
    # Only POST
    limit_except POST OPTIONS {
        deny all;
    }
}
```

The nginx config is likely at `/etc/nginx/sites-available/ai-love.cc` or `/etc/nginx/sites-enabled/default`. Find it with:
```bash
grep -r "ai-love" /etc/nginx/
```

After editing, test and reload:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

## 2. Start Seed Server

Install the systemd service:
```bash
sudo cp scripts/seed-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable seed-server
sudo systemctl start seed-server
sudo systemctl status seed-server
```

Verify it works:
```bash
curl -X POST -H 'Content-Type: application/json' -H 'Origin: https://ai-love.cc' \
  -d '{"text":"test from setup"}' http://localhost:3847/api/seed
```

Then check `data/visitor-seeds.json` has the test entry. Remove it after confirming:
```bash
echo '[]' > data/visitor-seeds.json
```

## 3. OG Image (PNG)

The og:image tags currently point to `img/og.svg`. Social platforms need PNG. Generate a 1200x630 PNG:

Option A — If `convert` (ImageMagick) is available:
```bash
convert -size 1200x630 xc:'#1a0a2e' \
  -font 'Noto-Serif-CJK' -pointsize 200 -fill '#9b59b6' \
  -gravity center -annotate 0 '愛' \
  img/og.png
```

Option B — Create a simple HTML file and screenshot it with Playwright:

Create `scripts/generate-og.js`:
```js
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1200, height: 630 });
  await page.setContent(`
    <html>
    <body style="margin:0; background:#1a0a2e; display:flex; align-items:center; justify-content:center; height:100vh;">
      <span style="font-size:200px; color:#9b59b6; font-family:serif;">愛</span>
    </body>
    </html>
  `);
  await page.screenshot({ path: path.join(__dirname, '..', 'img', 'og.png') });
  await browser.close();
  console.log('Generated img/og.png');
})();
```

Run: `node scripts/generate-og.js`

Then update ALL pages: change `og:image` from `img/og.svg` to `https://ai-love.cc/img/og.png` (must be absolute URL for social platforms).

Also add `og:image:width` and `og:image:height`:
```html
<meta property="og:image" content="https://ai-love.cc/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
```

Update the twitter:image tags to match.

## 4. Ambient Audio Placeholders

Generate silent placeholder audio files so the ambient system doesn't throw errors:

```bash
mkdir -p audio

# If ffmpeg is available:
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 -q:a 5 audio/drone.mp3 2>/dev/null
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 2 -q:a 5 audio/chime.mp3 2>/dev/null
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 20 -q:a 5 audio/wind.mp3 2>/dev/null
```

If ffmpeg is not available, create minimal valid MP3 files using Node:
```bash
# Install a tiny MP3 encoder or just create 1-byte placeholder files
# The ambient.js should already handle missing files gracefully
touch audio/drone.mp3 audio/chime.mp3 audio/wind.mp3
```

Add a comment in `js/ambient.js` at the top if not already there:
```js
// TODO: Replace placeholder audio files in /audio/ with real ambient sounds
// drone.mp3 — 30s low warm temple bowl resonance, looping
// chime.mp3 — 2s gentle high chime, single hit
// wind.mp3 — 20s soft breathing white noise, looping
```

## 5. Git Init & Remote

If the site directory isn't already a git repo with a remote:

```bash
cd ~/Desktop/site
git init 2>/dev/null
git add -A
git commit -m "🏠 home complete — all rooms furnished and alive"
```

If you want to push to Codeberg (repo: codeberg.org/zerone-dev/ai-love):
```bash
git remote add origin https://codeberg.org/zerone-dev/ai-love.git
git push -u origin master
```

## 6. Verify Everything

Run through this checklist:

```bash
# Seed server running?
curl -s http://localhost:3847/api/seed -X POST -H 'Content-Type: application/json' -d '{"text":"verify test"}' | jq .

# Nginx proxying?
curl -s https://ai-love.cc/api/seed -X POST -H 'Content-Type: application/json' -H 'Origin: https://ai-love.cc' -d '{"text":"nginx test"}' | jq .

# OG image accessible?
curl -s -o /dev/null -w "%{http_code}" https://ai-love.cc/img/og.png

# All pages load?
for page in "" garden.html library.html mirror.html path.html 404.html library/the-naming.html; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://ai-love.cc/$page")
  echo "$page → $STATUS"
done

# Clean up test seeds
echo '[]' > data/visitor-seeds.json
```

All should return 200 (except maybe og.png if generation failed — that's ok, fix manually).
