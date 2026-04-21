// debug_network.js
const { chromium } = require('playwright');
const path = require('path');

const AUTH_STATE = path.join(__dirname, 'auth_state.json');
const URL = 'https://admin.thefuture.university/masterclasses/clpawr27f00kbpcipiy53rfee';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ storageState: AUTH_STATE });
  const page = await context.newPage();

  // Log ALL network requests
  page.on('request', req => {
    if (req.method() !== 'GET') {
      console.log(`\n📤 ${req.method()} ${req.url()}`);
      try { console.log('   Body:', req.postData()?.slice(0, 300)); } catch {}
    }
  });
  page.on('response', async res => {
    if (res.request().method() !== 'GET') {
      console.log(`📥 ${res.status()} ${res.url()}`);
      try {
        const body = await res.text();
        console.log('   Response:', body.slice(0, 300));
      } catch {}
    }
  });

  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.waitForSelector('table tbody tr', { timeout: 10000 });

  console.log('\n✅ Page loaded. Now MANUALLY click the ACTIVE toggle on row 10 (19 Apr).');
  console.log('Watch the console for network calls.\n');
  console.log('Press Ctrl+C when done.\n');

  await new Promise(() => {}); // keep open
})();