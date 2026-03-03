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
