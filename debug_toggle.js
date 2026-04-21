// debug_toggle.js  — paste this as a new file and run: node debug_toggle.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const AUTH_STATE = path.join(__dirname, 'auth_state.json');
const URL = 'https://admin.thefuture.university/masterclasses/clpawr27f00kbpcipiy53rfee';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ storageState: AUTH_STATE });
  const page = await context.newPage();

  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.waitForSelector('table tbody tr', { timeout: 10000 });
  await page.waitForTimeout(1000);

  const rows = page.locator('table tbody tr');
  const rowCount = await rows.count();
  console.log(`Total rows: ${rowCount}`);

  // Row 10 = index 9 (the 19 Apr row)
  const targetRow = rows.nth(9);
  const cellCount = await targetRow.locator('td').count();
  console.log(`\nCell count in row 10: ${cellCount}`);

  // Dump HTML of cells 4, 5, 6 (the toggle area)
  for (let i = 4; i <= 7; i++) {
    const cell = targetRow.locator('td').nth(i);
    const html = await cell.innerHTML().catch(() => 'N/A');
    const text = await cell.textContent().catch(() => 'N/A');
    console.log(`\n--- Cell ${i} ---`);
    console.log(`Text: "${text?.trim()}"`);
    console.log(`HTML: ${html}`);
  }

  // Also dump ALL interactive elements in row 10
  const allButtons = await targetRow.locator('button').all();
  console.log(`\nTotal <button> elements in row 10: ${allButtons.length}`);
  for (let i = 0; i < allButtons.length; i++) {
    const html = await allButtons[i].innerHTML().catch(() => 'N/A');
    const role = await allButtons[i].getAttribute('role').catch(() => null);
    const state = await allButtons[i].getAttribute('data-state').catch(() => null);
    const aria = await allButtons[i].getAttribute('aria-checked').catch(() => null);
    console.log(`  Button ${i}: role="${role}" data-state="${state}" aria-checked="${aria}" | HTML: ${html?.slice(0,80)}`);
  }

  await page.screenshot({ path: 'debug_row10.png', fullPage: true });
  console.log('\n📸 Screenshot saved: debug_row10.png');

  await browser.close();
})();