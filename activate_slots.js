const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const DRY_RUN = process.argv.includes('--dry-run');

const CONFIG = {
  adminUrl: 'https://admin.thefuture.university/masterclasses',

  masterclasses: [
    { name: 'Masterclass on AI Based Super Investing with Akshay Gulati 12',  slotTime: '12:00' },
    { name: 'Masterclass on AI Based Super Investing with Akshay Gulati 12.5', slotTime: '12:30' },
    { name: 'Masterclass on AI Based Super Investing with Akshay Gulati 1',   slotTime: '13:00' },
    { name: 'Masterclass on AI Based Super Investing with Akshay Gulati 1.5', slotTime: '13:30' },
    { name: 'Masterclass on AI Based Super Investing with Akshay Gulati 2',   slotTime: '14:00' },
    { name: 'Masterclass on AI Based Super Investing with Akshay Gulati 2.5', slotTime: '14:30' },
    { name: 'Masterclass on AI Based Super Investing with Akshay Gulati 3',   slotTime: '15:00' },
    { name: 'Masterclass on AI Based Super Investing with Akshay Gulati 3.5', slotTime: '15:30' },
    { name: 'Masterclass on AI Based Super Investing with Akshay Gulati 4',   slotTime: '16:00' },
    { name: 'Masterclass on AI Based Super Investing with Akshay Gulati 4.5', slotTime: '16:30' },
    { name: 'Masterclass on AI Based Super Investing with Akshay Gulati 5',   slotTime: '17:00' },
    { name: 'Masterclass on AI Based Super Investing with Akshay Gulati 5.5', slotTime: '17:30' },
    { name: 'Masterclass on AI Based Super Investing with Akshay Gulati 6',   slotTime: '18:00' },
  ],

  authStatePath: path.join(__dirname, 'auth_state.json'),
  logPath: path.join(__dirname, 'slot_activation_log.json'),
  headless: false,
};

function getTomorrow() {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  const yyyy = d.getFullYear();
  const mm   = String(d.getMonth() + 1).padStart(2, '0');
  const dd   = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

function formatReadable(dateStr) {
  return new Date(dateStr).toLocaleString('en-IN', {
    weekday: 'long', day: '2-digit', month: 'short', year: 'numeric',
  });
}

function log(logs, masterclass, date, status, detail) {
  const entry = { timestamp: new Date().toISOString(), masterclass, date, status, detail };
  logs.push(entry);
  const icon = status === 'SUCCESS' ? '✅' : status === 'SKIPPED' ? '⏭️ ' : '❌';
  console.log(`${icon} [${status}] ${masterclass} | ${date} | ${detail}`);
}

function runDryRun() {
  const tomorrow = getTomorrow();
  console.log('');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('  DRY RUN — No browser opened. No toggles clicked.');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`  Run date : ${new Date().toLocaleString('en-IN')}`);
  console.log(`  Target   : TOMORROW — ${formatReadable(tomorrow)} (${tomorrow})`);
  console.log('');
  for (const mc of CONFIG.masterclasses) {
    console.log(`┌─ Masterclass`);
    console.log(`│  Name      : ${mc.name}`);
    console.log(`│  Slot time : ${mc.slotTime}`);
    console.log(`│  Target    : ${tomorrow}T${mc.slotTime}`);
    console.log(`└─ Will log SUCCESS / FAILED / SKIPPED`);
    console.log('');
  }
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('  Looks correct? Run the live script:');
  console.log('    node activate_slots.js');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
}

async function saveAuthState(browser) {
  console.log('\n📌 AUTH STATE NOT FOUND.');
  console.log('A browser window will open. Log in manually, then press ENTER here.\n');

  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto(CONFIG.adminUrl);

  await new Promise(resolve => {
    const onData = () => {
      process.stdin.removeListener('data', onData);
      process.stdin.pause();
      resolve();
    };
    process.stdin.resume();
    process.stdin.once('data', onData);
  });

  await context.storageState({ path: CONFIG.authStatePath });
  await context.close();
  console.log('✅ Auth state saved to', CONFIG.authStatePath);
}

async function activateSlotForMasterclass(context, mc, logs) {
  const page = await context.newPage();
  const tomorrow = getTomorrow();

  try {
    console.log(`\n🔍 Opening: "${mc.name}"`);
    await page.goto(CONFIG.adminUrl, { waitUntil: 'networkidle' });

    const searchInput = page.locator('input[type="text"], input[placeholder*="search" i]').first();
    await searchInput.fill(mc.name);
    await page.waitForTimeout(1200);

    const allLinks = page.locator('table tbody tr a');
    const linkCount = await allLinks.count();
    let targetHref = null;
    for (let i = 0; i < linkCount; i++) {
      const linkText = (await allLinks.nth(i).textContent()).trim();
      if (linkText === mc.name) {
        targetHref = await allLinks.nth(i).getAttribute('href');
        break;
      }
    }
    if (!targetHref) {
      log(logs, mc.name, tomorrow, 'FAILED', `Exact match for "${mc.name}" not found in search results`);
      await page.close();
      return;
    }

    const fullUrl = targetHref.startsWith('http')
      ? targetHref
      : `https://admin.thefuture.university${targetHref}`;
    console.log(`  🔗 Navigating to: ${fullUrl}`);
    await page.goto(fullUrl, { waitUntil: 'networkidle' });
    await page.waitForTimeout(800);
    console.log(`✅ Opened masterclass page: ${page.url()}`);

    const MONTHS = { Jan:'01',Feb:'02',Mar:'03',Apr:'04',May:'05',Jun:'06',
                     Jul:'07',Aug:'08',Sep:'09',Oct:'10',Nov:'11',Dec:'12' };
    function parseCellDate(text) {
      const m = text.trim().match(/^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})/);
      if (!m) return null;
      return `${m[3]}-${MONTHS[m[2]] || '00'}-${m[1].padStart(2,'0')}`;
    }

    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    const rows = page.locator('table tbody tr');
    const rowCount = await rows.count();
    console.log(`  🔍 Scanning ${rowCount} rows for date: ${tomorrow}`);

    let targetRowIndex = -1;
    for (let i = 0; i < rowCount; i++) {
      const allCells = await rows.nth(i).locator('td').allTextContents();
      const dateCell = allCells[1] || '';
      const parsed = parseCellDate(dateCell);
      console.log(`  Row ${i+1} | date: "${dateCell.trim()}" → ${parsed}`);
      if (parsed === tomorrow) {
        targetRowIndex = i;
        break;
      }
    }

    if (targetRowIndex === -1) {
      log(logs, mc.name, tomorrow, 'SKIPPED', `No slot found for ${tomorrow}`);
      await page.close();
      return;
    }

    console.log(`  📅 Found tomorrow's slot at row ${targetRowIndex + 1}`);
    const targetRow = rows.nth(targetRowIndex);

    const ACTIVE_COL = 5;
    const PAID_COL   = 6;

    // ── HELPER: wait for any existing toast to disappear ─────
    async function waitForToastClear() {
      await page.locator('text=/Updated successfully/i')
        .waitFor({ state: 'hidden', timeout: 6000 })
        .catch(() => {});
    }

    // ── HELPER: click a DaisyUI toggle, confirm via toast ────
    async function clickToggle(colIndex, label) {
      const cell = targetRow.locator('td').nth(colIndex);
      const toggle = cell.locator('input[type="checkbox"]');

      await toggle.waitFor({ state: 'attached', timeout: 8000 });
      await toggle.scrollIntoViewIfNeeded();
      await page.waitForTimeout(300);

      const isOn = await toggle.evaluate(el => {
        if (el.checked) return true;
        if (el.getAttribute('checked') !== null) return true;
        const parent = el.closest('label') || el.parentElement;
        if (parent && (parent.classList.contains('checked') || parent.dataset.checked)) return true;
        return false;
      });
      console.log(`  [${label}] isOn=${isOn}`);

      if (isOn) {
        console.log(`  ⏭️  [${label}] already ON — skipping`);
        return 'already_on';
      }

      // Wait for any previous toast to clear so we get a fresh signal
      await waitForToastClear();

      await toggle.evaluate(el => {
        const lbl = el.closest('label') || el.parentElement?.closest('label');
        if (lbl) lbl.click();
        else el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
      });

      const toastAppeared = await page.locator('text=/Updated successfully/i')
        .waitFor({ state: 'visible', timeout: 6000 })
        .then(() => true)
        .catch(() => false);

      console.log(`  [${label}] toast=${toastAppeared}`);
      return toastAppeared ? 'clicked' : 'uncertain';
    }
    // ─────────────────────────────────────────────────────────

    // ── Step 1: ACTIVE toggle ─────────────────────────────────
    const activeResult = await clickToggle(ACTIVE_COL, 'ACTIVE');

    await page.waitForTimeout(500);
    const popupVisible = await page.locator('text=Connect a Form to Slot').isVisible().catch(() => false);
    if (popupVisible) {
      console.log(`  📋 Popup open — dismissing`);
      await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const save = btns.find(b => b.textContent.trim() === 'Save');
        if (save) save.click();
      });
      await page.waitForTimeout(600);
      const still = await page.locator('text=Connect a Form to Slot').isVisible().catch(() => false);
      if (still) {
        await page.mouse.click(100, 100);
        await page.waitForTimeout(500);
      }
      console.log(`  ✅ Popup dismissed`);
    }

    // Wait for ACTIVE toast to fully disappear before clicking PAID toggle
    await waitForToastClear();
    await page.waitForTimeout(400);

    // ── Step 2: ACTIVE PAID MASTERCLASS toggle ────────────────
    const paidResult = await clickToggle(PAID_COL, 'ACTIVE PAID');

    // ── Final status ──────────────────────────────────────────
    if (activeResult === 'already_on' && paidResult === 'already_on') {
      log(logs, mc.name, tomorrow, 'SKIPPED', 'Both toggles were already ON');
    } else if (activeResult === 'uncertain') {
      log(logs, mc.name, tomorrow, 'FAILED', 'ACTIVE toggle uncertain — check manually');
    } else if (paidResult === 'uncertain') {
      log(logs, mc.name, tomorrow, 'FAILED', 'ACTIVE PAID toggle uncertain — check manually');
    } else {
      log(logs, mc.name, tomorrow, 'SUCCESS', 'Both toggles activated successfully');
    }

  } catch (err) {
    log(logs, mc.name, tomorrow, 'FAILED', `Unhandled error: ${err.message}`);
    const ssPath = path.join(__dirname, `error_activate_${Date.now()}.png`);
    await page.screenshot({ path: ssPath, fullPage: true });
    console.log(`  📸 Screenshot saved: ${ssPath}`);
  } finally {
    await page.close();
  }
}

async function runLive() {
  const logs = [];
  const tomorrow = getTomorrow();
  const startTime = new Date().toISOString();

  console.log('');
  console.log(`🚀 Slot Activation Started — ${startTime}`);
  console.log(`🎯 Target: tomorrow's slots (${tomorrow})`);

  const browser = await chromium.launch({ headless: CONFIG.headless });

  if (!fs.existsSync(CONFIG.authStatePath)) {
    await saveAuthState(browser);
  }

  const context = await browser.newContext({ storageState: CONFIG.authStatePath });

  for (const mc of CONFIG.masterclasses) {
    await activateSlotForMasterclass(context, mc, logs);
  }

  await context.close();
  await browser.close();

  const report = {
    runAt: startTime,
    completedAt: new Date().toISOString(),
    targetDate: tomorrow,
    total:   logs.length,
    success: logs.filter(l => l.status === 'SUCCESS').length,
    failed:  logs.filter(l => l.status === 'FAILED').length,
    skipped: logs.filter(l => l.status === 'SKIPPED').length,
    entries: logs,
  };
  fs.writeFileSync(CONFIG.logPath, JSON.stringify(report, null, 2));

  console.log(`\n📋 SUMMARY`);
  console.log(`   ✅ Success : ${report.success}`);
  console.log(`   ❌ Failed  : ${report.failed}`);
  console.log(`   ⏭️  Skipped : ${report.skipped}`);
  console.log(`   Log saved  : ${CONFIG.logPath}`);

  process.exit(0);
}

if (DRY_RUN) {
  runDryRun();
} else {
  runLive().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
}